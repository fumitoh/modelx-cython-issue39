from __future__ import annotations

"""Generic reuse bridge for modelx.export() + modelx-cython.

The graph compiler deliberately does not reimplement modelx-cython's strongest
feature: its transformation of exported ordinary Python formula methods into
typed Cython methods with direct Cell-to-Cell calls and typed caches.  This
module exposes that implementation as a measured performance floor and fallback.

The bridge is structural.  It derives the target Space/Cell from the captured
realized target and derives a type-trace sample from the actual portfolio.  No
domain model or formula name is privileged.
"""

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
import hashlib
import importlib
import json
import os
import pickle
import re
import shutil
import signal
import subprocess
import sys
import time

import numpy as np


class ModelxCythonBridgeError(RuntimeError):
    pass


_IDENTIFIER = re.compile(r"^[A-Za-z_]\w*$")


def _identifier(value: str, *, label: str) -> str:
    value = str(value)
    if not _IDENTIFIER.match(value):
        raise ModelxCythonBridgeError(f"{label} is not a valid Python identifier: {value!r}")
    return value


def _interface_value(value: Any) -> Any:
    """Unwrap modelx implementation objects without importing private classes."""
    try:
        return value.interface
    except Exception:
        return value


def _space_path_from_impl(space_impl: Any, model_impl: Any) -> tuple[str, ...]:
    parts: list[str] = []
    cur = space_impl
    seen: set[int] = set()
    while cur is not None and cur is not model_impl and id(cur) not in seen:
        seen.add(id(cur))
        try:
            dynamic = bool(cur.is_dynamic())
        except Exception:
            dynamic = False
        if not dynamic:
            name = getattr(cur, "name", None)
            if name and not str(name).startswith("__"):
                parts.append(_identifier(str(name), label="Space name"))
        cur = getattr(cur, "parent", None)
    if cur is not model_impl:
        raise ModelxCythonBridgeError("target Space is not rooted in the traced model")
    return tuple(reversed(parts))


def _representative_point_from_impl(space_impl: Any) -> tuple[Any, ...]:
    """Read the concrete arguments of the nearest dynamic ItemSpace."""
    cur = space_impl
    seen: set[int] = set()
    while cur is not None and id(cur) not in seen:
        seen.add(id(cur))
        try:
            dynamic = bool(cur.is_dynamic())
        except Exception:
            dynamic = False
        if dynamic:
            values = []
            for value in tuple(getattr(cur, "argvalues", ()) or ()):
                values.append(_interface_value(value))
            if values:
                return tuple(values)
            key = getattr(cur, "dynamic_key", None)
            if key:
                try:
                    return tuple(key[-1])
                except Exception:
                    pass
        cur = getattr(cur, "parent", None)
    return ()


@dataclass(frozen=True)
class ModelxCythonTarget:
    space_path: tuple[str, ...]
    point_parameter_count: int
    representative_point: tuple[Any, ...]
    cell_name: str
    cell_args: tuple[Any, ...]

    def normalize_point(self, value: Any) -> tuple[Any, ...]:
        if self.point_parameter_count == 0:
            if value in (None, (), []):
                return ()
            raise ModelxCythonBridgeError("unparameterized target does not accept point keys")
        if self.point_parameter_count == 1 and not isinstance(value, tuple):
            if isinstance(value, list):
                value = tuple(value)
            else:
                value = (value,)
        else:
            value = tuple(value)
        if len(value) != self.point_parameter_count:
            raise ModelxCythonBridgeError(
                f"expected {self.point_parameter_count} point arguments, got {value!r}"
            )
        return tuple(value)

    def resolve_space(self, model: Any) -> Any:
        cur = model
        for name in self.space_path:
            cur = getattr(cur, name)
        return cur

    def resolve_cell(self, model: Any, point: Any | None = None) -> Any:
        space = self.resolve_space(model)
        if self.point_parameter_count:
            p = self.normalize_point(point)
            item = space[p[0]] if len(p) == 1 else space[p]
        else:
            item = space
        return getattr(item, self.cell_name)


def infer_modelx_cython_target(compiler: Any) -> ModelxCythonTarget:
    """Infer an interchangeable modelx-cython target from a realized compiler."""
    runtime_nodes = tuple(compiler.trace.target_runtime_nodes)
    if len(runtime_nodes) != 1:
        raise ModelxCythonBridgeError("performance floor currently requires one realized target")
    cell_impl, cell_args = runtime_nodes[0]
    cell_name = _identifier(getattr(cell_impl, "name", ""), label="Cell name")
    containing = getattr(cell_impl, "parent", None)
    model_impl = getattr(compiler.trace.model, "_impl", None)
    if containing is None or model_impl is None:
        raise ModelxCythonBridgeError("could not resolve target implementation hierarchy")
    path = _space_path_from_impl(containing, model_impl)
    representative = _representative_point_from_impl(containing)
    base = compiler.trace.model
    for name in path:
        base = getattr(base, name)
    parameters = tuple(getattr(base, "parameters", ()) or ())
    if len(representative) != len(parameters):
        if parameters and not representative:
            raise ModelxCythonBridgeError("could not recover representative ItemSpace arguments")
        if not parameters:
            representative = ()
        else:
            raise ModelxCythonBridgeError(
                "representative ItemSpace argument count differs from base Space parameters"
            )
    return ModelxCythonTarget(
        space_path=path,
        point_parameter_count=len(parameters),
        representative_point=tuple(representative),
        cell_name=cell_name,
        cell_args=tuple(cell_args),
    )


def _dedupe_points(points: Iterable[Any], target: ModelxCythonTarget) -> tuple[tuple[Any, ...], ...]:
    out: list[tuple[Any, ...]] = []
    seen: set[bytes] = set()
    for value in points:
        point = target.normalize_point(value)
        try:
            key = pickle.dumps(point, protocol=5)
        except Exception:
            key = repr(point).encode("utf-8", "backslashreplace")
        if key not in seen:
            seen.add(key)
            out.append(point)
    return tuple(out)


def _spread_positions(length: int, count: int) -> tuple[int, ...]:
    if length <= 0 or count <= 0:
        return ()
    if count >= length:
        return tuple(range(length))
    return tuple(dict.fromkeys(int(round(i * (length - 1) / (count - 1))) for i in range(count)))


def _iter_numeric_tables(space: Any, *, max_depth: int = 2):
    """Yield direct pandas tables from a Space and referenced Spaces."""
    try:
        import pandas as pd
    except Exception:
        return
    queue: list[tuple[str, Any, int]] = [("", space, 0)]
    seen: set[int] = set()
    while queue:
        prefix, cur, depth = queue.pop(0)
        if id(cur) in seen:
            continue
        seen.add(id(cur))
        try:
            refs = cur.refs
        except Exception:
            refs = {}
        try:
            items = list(refs.items())
        except Exception:
            items = []
        for name, raw in items:
            value = _interface_value(raw)
            label = f"{prefix}.{name}" if prefix else str(name)
            if isinstance(value, (pd.DataFrame, pd.Series)):
                yield label, value
            elif depth < max_depth and hasattr(value, "refs") and hasattr(value, "cells"):
                queue.append((label, value, depth + 1))


def derive_modelx_cython_trace_sample(
    compiler: Any,
    portfolio_point_keys: Sequence[Any],
    *,
    explicit_point_keys: Iterable[Any] = (),
    max_points: int = 64,
    spread_points: int = 32,
    max_categories: int = 16,
) -> tuple[tuple[tuple[Any, ...], ...], dict[str, Any]]:
    """Derive a portfolio-safe type-trace sample for modelx-cython.

    modelx-cython sizes typed Cell caches from the sample execution.  Sampling a
    few adjacent policies can therefore produce a package that compiles but later
    indexes beyond the inferred horizon.  The sample covers first/last/spread
    points, low-cardinality categories and numeric extrema from model-point-like
    tables reachable from the target Space.
    """
    target = infer_modelx_cython_target(compiler)
    portfolio = _dedupe_points(portfolio_point_keys, target)
    explicit = _dedupe_points(explicit_point_keys, target)
    if target.point_parameter_count and not portfolio:
        raise ModelxCythonBridgeError("portfolio point keys are required for a parameterized target")
    selected: list[tuple[Any, ...]] = []
    reasons: dict[str, set[str]] = {}

    def add(point: tuple[Any, ...], reason: str) -> None:
        if point not in selected and len(selected) < max_points:
            selected.append(point)
        reasons.setdefault(reason, set()).add(repr(point))

    if target.representative_point:
        add(target.normalize_point(target.representative_point), "representative")
    for p in explicit:
        add(p, "explicit")
    if portfolio:
        add(portfolio[0], "portfolio_first")
        add(portfolio[-1], "portfolio_last")

    first_coord: dict[Any, tuple[Any, ...]] = {}
    for p in portfolio:
        try:
            first_coord.setdefault(p[0], p)
        except Exception:
            pass

    base = target.resolve_space(compiler.trace.model)
    reference_profiles: list[dict[str, Any]] = []
    low_card_tables: list[tuple[str, Any, list[Any], list[Any]]] = []
    for ref_name, table in _iter_numeric_tables(base):
        try:
            index_values = set(table.index)
        except Exception:
            continue
        covered = [label for label in first_coord if label in index_values]
        if not covered:
            continue
        profile: dict[str, Any] = {
            "reference": ref_name,
            "covered_points": len(covered),
            "columns": [],
        }
        if getattr(table, "ndim", 1) == 1:
            columns = [(getattr(table, "name", "value"), table)]
        else:
            columns = [(str(c), table[c]) for c in table.columns]
        low_cols: list[Any] = []
        numeric_cols: list[Any] = []
        for column_name, series in columns:
            try:
                aligned = series.loc[covered]
                unique_count = int(aligned.nunique(dropna=False))
            except Exception:
                continue
            profile["columns"].append({"name": column_name, "unique_count": unique_count})
            if 0 < unique_count <= max_categories:
                low_cols.append(getattr(series, "name", column_name))
                try:
                    groups = aligned.groupby(aligned, dropna=False, sort=False)
                    for _value, group in groups:
                        label = group.index[0]
                        add(first_coord[label], f"{ref_name}.{column_name}:category")
                except Exception:
                    pass
            try:
                if np.issubdtype(aligned.dtype, np.number):
                    numeric_cols.append(getattr(series, "name", column_name))
                    for suffix, label in (("min", aligned.idxmin()), ("max", aligned.idxmax())):
                        if label in first_coord:
                            add(first_coord[label], f"{ref_name}.{column_name}:{suffix}")
            except Exception:
                pass
        if getattr(table, "ndim", 1) == 2 and low_cols:
            # Keep the actual table column keys. Stringifying is useful for the
            # profile, but using the original keys is required for non-string
            # DataFrame columns. Numeric extrema inside categorical groups cover
            # interactions such as maximum term combined with minimum elapsed
            # duration, which determine modelx-cython's typed cache bounds.
            low_card_tables.append((ref_name, table, low_cols[:3], numeric_cols))
        reference_profiles.append(profile)

    for ref_name, table, columns, numeric_columns in low_card_tables:
        try:
            labels = [label for label in first_coord if label in table.index]
            subset = table.loc[labels]
            grouped = list(subset.groupby(columns, dropna=False, sort=False))
            for _combo, group in grouped:
                label = group.index[0]
                if label in first_coord:
                    add(first_coord[label], f"{ref_name}:category_combination")

            # Global extrema are not enough when a loop horizon depends on more
            # than one model-point field. Select numeric extrema within each
            # low-cardinality combination. The pass is column-major so every
            # numeric dimension gets coverage before one large group consumes
            # the bounded sample budget.
            for numeric_col in numeric_columns:
                if numeric_col in columns or numeric_col not in subset.columns:
                    continue
                for _combo, group in grouped:
                    series = group[numeric_col]
                    try:
                        for suffix, label in (("min", series.idxmin()), ("max", series.idxmax())):
                            if label in first_coord:
                                add(
                                    first_coord[label],
                                    f"{ref_name}.{numeric_col}:group_{suffix}",
                                )
                    except Exception:
                        pass
        except Exception:
            pass

    for pos in _spread_positions(len(portfolio), min(spread_points, max_points)):
        add(portfolio[pos], "portfolio_spread")
    for p in portfolio:
        if len(selected) >= max_points:
            break
        if len(selected) < min(max_points, 3):
            add(p, "portfolio_fill")

    sample = tuple(selected)
    profile = {
        "portfolio_point_count": len(portfolio),
        "explicit_point_count": len(explicit),
        "selected_point_count": len(sample),
        "max_points": max_points,
        "point_parameter_count": target.point_parameter_count,
        "reference_profiles": reference_profiles,
        "reason_counts": {name: len(points) for name, points in sorted(reasons.items())},
        "selected_points": [list(p) for p in sample],
    }
    return sample, profile


def _sample_fingerprint(sample: Sequence[Any]) -> str:
    return hashlib.sha256(pickle.dumps(tuple(sample), protocol=5)).hexdigest()


def _safe_package_stem(name: str) -> str:
    stem = re.sub(r"\W+", "_", str(name)).strip("_") or "Model"
    if stem[0].isdigit():
        stem = "M_" + stem
    return stem


def _package_token(model_name: str, target: ModelxCythonTarget, fingerprint: str) -> str:
    payload = pickle.dumps((model_name, target, fingerprint), protocol=5)
    return hashlib.sha256(payload).hexdigest()[:10]


def _subprocess_environment(*prepend_paths: str | Path) -> dict[str, str]:
    env = os.environ.copy()
    existing = [p for p in sys.path if p]
    paths = [str(Path(p).resolve()) for p in prepend_paths] + existing
    old = env.get("PYTHONPATH")
    if old:
        paths.extend(x for x in old.split(os.pathsep) if x)
    env["PYTHONPATH"] = os.pathsep.join(dict.fromkeys(paths))
    return env


def _target_access_source(target: ModelxCythonTarget, model_expr: str, point_expr: str) -> str:
    lines = [f"space = {model_expr}"]
    for name in target.space_path:
        lines.append(f"space = getattr(space, {name!r})")
    if target.point_parameter_count == 0:
        lines.append("item = space")
    elif target.point_parameter_count == 1:
        lines.append(f"item = space[{point_expr}[0]]")
    else:
        lines.append(f"item = space[tuple({point_expr})]")
    lines.append(f"cell = getattr(item, {target.cell_name!r})")
    return "\n".join(lines)


def _sample_source(export_package: str, target: ModelxCythonTarget) -> str:
    access = _target_access_source(target, "mx_model", "point")
    return (
        "from pathlib import Path\n"
        "import pickle\n"
        f"from {export_package} import mx_model\n"
        "root = Path(__file__).resolve().parent\n"
        "points = pickle.loads((root / 'sample_points.pkl').read_bytes())\n"
        "cell_args = pickle.loads((root / 'cell_args.pkl').read_bytes())\n"
        "for point in points:\n"
        + "\n".join("    " + line for line in access.splitlines()) + "\n"
        "    cell(*cell_args)\n"
    )


@dataclass(frozen=True)
class ModelxCythonBridgeBuildReport:
    export_package: str
    compiled_package: str
    target: Mapping[str, Any]
    sample_point_count: int
    sample_point_fingerprint: str
    export_seconds: float
    translate_compile_seconds: float
    total_seconds: float
    package_bytes: int
    shared_library_bytes: int
    stdout_path: str
    stderr_path: str
    staged_external_files: tuple[str, ...] = ()


def _package_bytes(path: Path) -> int:
    return int(sum(p.stat().st_size for p in path.rglob("*") if p.is_file()))


def _stage_external_model_files(model: Any, build_dir: Path) -> tuple[str, ...]:
    """Stage file-backed model inputs beside the exported package.

    modelx exports formula code and references, but it deliberately does not copy
    arbitrary CSV/XLSX inputs read by user formulas.  Modern file-backed
    models resolve those files from ``_model.path.parent``.  After export that
    parent is the bridge build directory, so the untouched modelx-cython sample
    fails unless the original sibling data files are staged there as well.

    Only regular sibling files are copied.  The live model folder and unrelated
    sibling model directories are never duplicated.
    """
    raw_path = getattr(model, "path", None)
    if raw_path is None:
        return ()
    try:
        source_parent = Path(raw_path).resolve().parent
    except Exception:
        return ()
    staged: list[str] = []
    for source in sorted(source_parent.iterdir()):
        if not source.is_file():
            continue
        destination = build_dir / source.name
        if source.resolve() == destination.resolve():
            continue
        shutil.copy2(source, destination)
        staged.append(source.name)
    return tuple(staged)


@dataclass
class ModelxCythonBridgeProgram:
    root: Path
    package_name: str
    target: ModelxCythonTarget
    build_report: ModelxCythonBridgeBuildReport

    def _module(self):
        root = str(self.root)
        if root not in sys.path:
            sys.path.insert(0, root)
        return importlib.import_module(self.package_name)

    def execute_points(self, points: Sequence[Any]) -> np.ndarray:
        module = self._module()
        model = module.mx_model
        values = []
        for raw in points:
            cell = self.target.resolve_cell(model, raw)
            values.append(cell(*self.target.cell_args))
        return np.asarray(values)

    def execute_prefix(self, count: int, *, start: int | None = None) -> np.ndarray:
        if self.target.point_parameter_count != 1:
            raise ModelxCythonBridgeError("automatic prefix execution requires one point parameter")
        if start is None:
            start = 1
        points = [(start + i,) for i in range(int(count))]
        return self.execute_points(points)

    def validate_against(self, compiler: Any, point_keys: Sequence[Any]) -> dict[str, Any]:
        points = _dedupe_points(point_keys, self.target)
        actual = np.asarray(self.execute_points(points), dtype=np.float64).reshape(-1)
        live_model = compiler.trace.model
        expected = np.asarray([
            self.target.resolve_cell(live_model, point)(*self.target.cell_args)
            for point in points
        ], dtype=np.float64).reshape(-1)
        return {
            "count": len(points),
            "exact": bool(np.array_equal(actual, expected, equal_nan=True)),
            "max_abs_error": float(np.nanmax(np.abs(actual - expected))) if len(points) else 0.0,
            "actual": actual,
            "expected": expected,
        }


def build_modelx_cython_bridge(
    compiler: Any,
    build_dir: str | Path,
    *,
    sample_point_keys: Iterable[Any] | None = None,
    force_rebuild: bool = False,
    build_timeout_seconds: float | None = 600.0,
) -> ModelxCythonBridgeProgram:
    """Export, transform and compile the realized target with modelx-cython."""
    target = infer_modelx_cython_target(compiler)
    sample = _dedupe_points(sample_point_keys or (), target)
    if target.point_parameter_count and not sample:
        raise ModelxCythonBridgeError(
            "sample_point_keys are required for a parameterized target; modelx-cython "
            "sizes typed caches from the traced sample"
        )
    build_dir = Path(build_dir).resolve()
    build_dir.mkdir(parents=True, exist_ok=True)
    staged_external_files = _stage_external_model_files(
        compiler.trace.model, build_dir
    )
    model_name = getattr(compiler.trace.model, "name", "Model")
    sample_fp = _sample_fingerprint(sample)
    token = _package_token(model_name, target, sample_fp)
    export_name = f"{_safe_package_stem(model_name)}_mxg_{token}_nomx"
    compiled_name = export_name + "_cy"
    export_path = build_dir / export_name
    compiled_path = build_dir / compiled_name
    report_path = build_dir / "mxg_bridge_report.json"

    if not force_rebuild and report_path.exists() and compiled_path.exists():
        try:
            payload = json.loads(report_path.read_text())
            if payload.get("sample_point_fingerprint") == sample_fp and payload.get("compiled_package") == compiled_name:
                report = ModelxCythonBridgeBuildReport(**payload)
                return ModelxCythonBridgeProgram(build_dir, compiled_name, target, report)
        except Exception:
            pass
    for path in (export_path, compiled_path, Path(str(compiled_path) + "_BAK1")):
        if path.exists():
            shutil.rmtree(path)
    for path in (build_dir / "build", build_dir / "setup.py"):
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()

    t_all = time.perf_counter()
    t0 = time.perf_counter()
    compiler.trace.model.export(export_path)
    export_seconds = time.perf_counter() - t0
    (build_dir / "sample_points.pkl").write_bytes(pickle.dumps(sample, protocol=5))
    (build_dir / "cell_args.pkl").write_bytes(pickle.dumps(target.cell_args, protocol=5))
    sample_path = build_dir / "mxg_bridge_sample.py"
    sample_path.write_text(_sample_source(export_name, target), encoding="utf-8")
    stdout_path = build_dir / "mxg_bridge_build.stdout.txt"
    stderr_path = build_dir / "mxg_bridge_build.stderr.txt"
    cmd = [
        sys.executable, "-m", "modelx_cython", export_name,
        "--sample", sample_path.name, "--no-spec",
    ]
    t0 = time.perf_counter()
    proc = subprocess.Popen(
        cmd,
        cwd=build_dir,
        env=_subprocess_environment(build_dir),
        stdout=stdout_path.open("w"),
        stderr=stderr_path.open("w"),
        text=True,
        start_new_session=True,
    )
    try:
        returncode = proc.wait(timeout=build_timeout_seconds)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except Exception:
            proc.kill()
        proc.wait()
        failure = {
            "status": "timeout",
            "timeout_seconds": build_timeout_seconds,
            "command": cmd,
            "sample_point_count": len(sample),
            "sample_point_fingerprint": sample_fp,
        }
        (build_dir / "mxg_bridge_failure.json").write_text(json.dumps(failure, indent=2))
        raise ModelxCythonBridgeError(
            f"modelx-cython build exceeded the configured {build_timeout_seconds} seconds"
        )
    compile_seconds = time.perf_counter() - t0
    if returncode != 0 or not compiled_path.exists():
        tail = ""
        try:
            tail = stderr_path.read_text(errors="replace")[-4000:]
        except Exception:
            pass
        raise ModelxCythonBridgeError(
            f"modelx-cython build failed with exit code {returncode}: {tail}"
        )
    report = ModelxCythonBridgeBuildReport(
        export_package=export_name,
        compiled_package=compiled_name,
        target={
            "space_path": list(target.space_path),
            "point_parameter_count": target.point_parameter_count,
            "representative_point": list(target.representative_point),
            "cell_name": target.cell_name,
            "cell_args": list(target.cell_args),
        },
        sample_point_count=len(sample),
        sample_point_fingerprint=sample_fp,
        export_seconds=export_seconds,
        translate_compile_seconds=compile_seconds,
        total_seconds=time.perf_counter() - t_all,
        package_bytes=_package_bytes(compiled_path),
        shared_library_bytes=int(sum(p.stat().st_size for p in compiled_path.rglob("*.so"))),
        stdout_path=str(stdout_path),
        stderr_path=str(stderr_path),
        staged_external_files=staged_external_files,
    )
    report_path.write_text(json.dumps(asdict(report), indent=2, default=str))
    return ModelxCythonBridgeProgram(build_dir, compiled_name, target, report)
