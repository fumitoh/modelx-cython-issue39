from __future__ import annotations

import ast
import json
import os
import pathlib
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, asdict
from typing import Iterable, Any

from .frontend import ModelxModelCompiler, ModelxCompileError


@dataclass
class ExportResult:
    path: pathlib.Path
    package_name: str
    outputs: list[str]
    translated: bool
    compiled: bool
    export_seconds: float
    analysis_seconds: float
    translation_seconds: float
    compilation_seconds: float
    manifest_path: pathlib.Path

    def as_dict(self):
        out = asdict(self)
        out["path"] = str(self.path)
        out["manifest_path"] = str(self.manifest_path)
        return out


def _literal_spec(spec: Any, no_spec: bool = False) -> dict:
    if no_spec or spec is None:
        return {}
    if isinstance(spec, dict):
        return spec
    path = pathlib.Path(spec)
    return ast.literal_eval(path.read_text(encoding="utf-8"))


def infer_outputs_from_sample(sample: str | os.PathLike | None, available: Iterable[str]) -> list[str]:
    """Infer directly requested zero-argument Cells from an mx2cy-style sample.

    This deliberately uses the sample as a *workload selector*, not as the sole
    source of type truth. Semantic recurrence compilation can infer scalar types
    and dependencies statically/live from modelx; the sample tells us which
    public results the user intends to make hot.
    """
    if sample is None:
        return []
    tree = ast.parse(pathlib.Path(sample).read_text(encoding="utf-8"))
    available = set(available)
    found: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            name = node.func.attr
            if name in available and not node.args and not node.keywords and name not in found:
                found.append(name)
    return found


def _backup_path(path: pathlib.Path, max_backups: int = 1):
    if not path.exists():
        return
    for n in range(max_backups, 0, -1):
        old = pathlib.Path(str(path) + f"_BAK{n}")
        if old.exists():
            if n == max_backups:
                shutil.rmtree(old) if old.is_dir() else old.unlink()
            else:
                old.rename(pathlib.Path(str(path) + f"_BAK{n+1}"))
    path.rename(pathlib.Path(str(path) + "_BAK1"))


def _write_runtime_facade(path: pathlib.Path, compiler: ModelxModelCompiler, *, default_threads: int = 0):
    outputs = list(compiler.outputs)
    output_map = {name: i for i, name in enumerate(outputs)}
    mp_ref = compiler.model_point_ref
    mp_fields = dict(compiler.model_point_fields)
    ref_arrays = sorted(compiler.ref_array_keys)
    external_arrays = sorted(compiler.external_specs)
    space_attr = compiler.space_name.split(".")[-1]

    code = f'''\
"""Generated semantic-native accelerator facade.

The surrounding package is the ordinary modelx pure-Python export. This module
patches only compiler-selected public Cells, preserving the exported model API
and leaving every other Cell as the Python fallback.
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd
from . import _mx_native_ext

_OUTPUTS = {outputs!r}
_OUTPUT_MAP = {output_map!r}
_DEFAULT_THREADS = {int(default_threads)!r}
_values = None
_index_to_pos = None


def _dense_series(series):
    if isinstance(series.index, pd.MultiIndex):
        coords = [(int(a), int(b)) for a, b in series.index]
        arr = np.zeros((max(a for a, _ in coords) + 1, max(b for _, b in coords) + 1), dtype=np.float64)
        for (a, b), v in series.items():
            arr[int(a), int(b)] = float(v)
        return np.ascontiguousarray(arr)
    idx = [int(x) for x in series.index]
    arr = np.zeros(max(idx) + 1, dtype=np.float64)
    for x, v in series.items():
        arr[int(x)] = float(v)
    return np.ascontiguousarray(arr)


def _dense_dataframe(df):
    rows = [int(x) for x in df.index]
    cols = [int(x) for x in df.columns]
    arr = np.zeros((max(rows) + 1, max(cols) + 1), dtype=np.float64)
    for src_col, c in zip(df.columns, cols):
        for r, v in df[src_col].items():
            arr[int(r), int(c)] = float(v)
    return np.ascontiguousarray(arr)


def _build_inputs(model):
    space = getattr(model, {space_attr!r})
    kwargs = {{}}
'''
    if mp_fields:
        code += f"    mp = getattr(space, {mp_ref!r})\n"
        for field, key in mp_fields.items():
            dtype = compiler.core.inputs[key]["dtype"]
            npdtype = "np.int64" if dtype == "int64" else "np.float64"
            code += f"    kwargs[{key!r}] = np.ascontiguousarray(mp[{field!r}].to_numpy(dtype={npdtype}))\n"
    for refname in ref_arrays:
        key = f"ref__{refname}"
        code += f"    value = getattr(space, {refname!r})\n"
        code += "    if isinstance(value, pd.Series):\n"
        code += f"        kwargs[{key!r}] = _dense_series(value)\n"
        code += "    elif isinstance(value, pd.DataFrame):\n"
        code += f"        kwargs[{key!r}] = _dense_dataframe(value)\n"
        code += "    else:\n"
        code += f"        kwargs[{key!r}] = np.ascontiguousarray(np.asarray(value, dtype=np.float64))\n"
    for key in external_arrays:
        if "__" not in key:
            continue
        refname, cellname = key.split("__", 1)
        dtype = compiler.core.inputs[key]["dtype"]
        npdtype = "np.int64" if dtype == "int64" else "np.float64"
        code += f"    ext_space = getattr(space, {refname!r})\n"
        code += f"    kwargs[{key!r}] = np.ascontiguousarray(np.asarray(getattr(ext_space, {cellname!r})(), dtype={npdtype}))\n"

    code += f'''\
    return kwargs


def clear_cache():
    global _values
    _values = None


def set_threads(threads):
    global _DEFAULT_THREADS
    _DEFAULT_THREADS = int(threads)
    clear_cache()


def calculate(model, threads=None, force=False):
    global _values, _index_to_pos
    if force or _values is None:
        space = getattr(model, {space_attr!r})
        if threads is None:
            threads = _DEFAULT_THREADS
        _values = _mx_native_ext.run(**_build_inputs(model), threads=int(threads))
        if {mp_ref is not None!r}:
            idx = list(getattr(space, {mp_ref!r}).index)
            _index_to_pos = {{v: i for i, v in enumerate(idx)}}
        else:
            _index_to_pos = None
    return _values


def _row_for_key(key):
    if _index_to_pos is None:
        return int(key)
    return _index_to_pos[key]


def _row_for_space(space):
    return _row_for_key(getattr(space, {compiler.space_param!r}))


def install(model):
    space = getattr(model, {space_attr!r})
    cls = type(space)
    for name, col in _OUTPUT_MAP.items():
        def compiled_cell(self, _col=col):
            vals = calculate(self._model)
            return float(vals[_row_for_space(self), _col])
        compiled_cell.__name__ = name
        compiled_cell.__qualname__ = cls.__name__ + "." + name
        setattr(cls, name, compiled_cell)

    # Preserve the exported model API without eagerly allocating one heavyweight
    # exported ItemSpace (and dozens of Cell caches) per model point. Compiled
    # outputs are served by a tiny proxy. Any uncompiled attribute transparently
    # realizes the ordinary exported-Python ItemSpace and delegates to it.
    if {compiler.space_param is not None!r} and not getattr(cls, "_mx_native_proxy_installed", False):
        orig_call = cls.__call__
        proxies = {{}}

        class _NativeItemProxy:
            __slots__ = ("_parent", "_key", "_real")
            def __init__(self, parent, key):
                self._parent = parent
                self._key = key
                self._real = None
            def _realize(self):
                if self._real is None:
                    self._real = orig_call(self._parent, self._key)
                return self._real
            def __getattr__(self, name):
                if name == {compiler.space_param!r}:
                    return self._key
                if name in _OUTPUT_MAP:
                    col = _OUTPUT_MAP[name]
                    return lambda: float(calculate(self._parent._model)[_row_for_key(self._key), col])
                return getattr(self._realize(), name)
            def __repr__(self):
                return repr(self._realize())

        for _name, _col in _OUTPUT_MAP.items():
            def _proxy_compiled_cell(self, _col=_col):
                return float(calculate(self._parent._model)[_row_for_key(self._key), _col])
            _proxy_compiled_cell.__name__ = _name
            setattr(_NativeItemProxy, _name, _proxy_compiled_cell)

        def native_call(self, key):
            # Only the root dynamic Space gets proxies. A realized ItemSpace keeps
            # ordinary exported-model behavior if someone indexes it unusually.
            if getattr(self, "_space", self) is not self:
                return orig_call(self, key)
            try:
                return proxies[key]
            except KeyError:
                p = _NativeItemProxy(self, key)
                proxies[key] = p
                return p

        def native_getitem(self, key):
            return native_call(self, key)

        cls.__call__ = native_call
        cls.__getitem__ = native_getitem
        cls._mx_native_proxy_installed = True
        model._mx_native_proxies = proxies

    model._mx_native_clear_cache = clear_cache
    model._mx_native_set_threads = set_threads
    model._mx_native_calculate = lambda threads=None, force=False: calculate(model, threads=threads, force=force)
    return model
'''
    (path / "_mx_native.py").write_text(code, encoding="utf-8")


def _write_build_script(path: pathlib.Path, *, native_arch: bool = True, openmp: bool = True, setup=None) -> pathlib.Path:
    pkg = path.name
    compile_args = ["-O3"]
    link_args: list[str] = []
    if native_arch:
        compile_args.append("-march=native")
    if openmp:
        compile_args.append("-fopenmp")
        link_args.append("-fopenmp")
    script = f'''\
from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy as np
ext = Extension(
    {pkg!r} + "._mx_native_ext",
    [{(pkg + '/_mx_native_ext.pyx')!r}],
    include_dirs=[np.get_include()],
    extra_compile_args={compile_args!r},
    extra_link_args={link_args!r},
)
setup(
    name={pkg!r} + "-semantic-native",
    ext_modules=cythonize([ext], compiler_directives={{"language_level": 3}}, annotate=True),
)
'''
    setup_path = pathlib.Path(setup).resolve() if setup else (path / "_mx_native_build.py")
    setup_path.parent.mkdir(parents=True, exist_ok=True)
    setup_path.write_text(script, encoding="utf-8")
    return setup_path


def _patch_init(path: pathlib.Path):
    init = path / "__init__.py"
    marker = "# modelx-native semantic accelerator"
    text = init.read_text(encoding="utf-8")
    if marker in text:
        return
    text += f'''\n\n{marker}\nfrom . import _mx_native as _mx_native_runtime\n_mx_native_runtime.install(mx_model)\nclear_native_cache = _mx_native_runtime.clear_cache\nset_native_threads = _mx_native_runtime.set_threads\n'''
    init.write_text(text, encoding="utf-8")


def translate_model(
    model,
    path,
    *,
    space="Projection",
    outputs: Iterable[str] | None = None,
    sample: str | os.PathLike | None = None,
    spec: dict | str | os.PathLike | None = None,
    no_spec: bool = False,
    native_arch: bool = True,
    openmp: bool = True,
    threads: int = 0,
    setup: str | os.PathLike | None = None,
    backup: bool = True,
) -> ExportResult:
    """Export a modelx model and translate selected Cells to a semantic Cython kernel.

    The output package is API-compatible with modelx's pure-Python export: it
    exposes ``mx_model`` and the original model name, and all uncompiled Cells
    remain the exported-Python implementations.
    """
    path = pathlib.Path(path).resolve()
    if backup and path.exists():
        _backup_path(path)
    elif path.exists():
        shutil.rmtree(path)

    t0 = time.perf_counter()
    model.export(path)
    export_seconds = time.perf_counter() - t0

    raw_compiler = ModelxModelCompiler(model, space=space, outputs=outputs)
    chosen = list(outputs) if outputs is not None else infer_outputs_from_sample(sample, raw_compiler.raw_funcs)
    if not chosen:
        chosen = list(raw_compiler.outputs)

    t0 = time.perf_counter()
    compiler = ModelxModelCompiler(model, space=space, outputs=chosen)
    analysis_seconds = time.perf_counter() - t0

    spec_dict = _literal_spec(spec, no_spec=no_spec)
    t0 = time.perf_counter()
    compiler.generate_cython(path / "_mx_native_ext.pyx", module_name="_mx_native_ext")
    _write_runtime_facade(path, compiler, default_threads=threads)
    build_script = _write_build_script(path, native_arch=native_arch, openmp=openmp, setup=setup)
    _patch_init(path)
    manifest = compiler.manifest()
    manifest.update({
        "api": "modelx-export-compatible",
        "package_name": path.name,
        "fallback": "modelx-exported-python",
        "sample": str(sample) if sample else None,
        "sample_selected_outputs": chosen,
        "spec": spec_dict,
        "native_arch": native_arch,
        "openmp": openmp,
        "default_threads": int(threads),
        "setup_file": str(build_script),
    })
    manifest_path = path / "_mx_native_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    translation_seconds = time.perf_counter() - t0

    return ExportResult(
        path=path,
        package_name=path.name,
        outputs=chosen,
        translated=True,
        compiled=False,
        export_seconds=export_seconds,
        analysis_seconds=analysis_seconds,
        translation_seconds=translation_seconds,
        compilation_seconds=0.0,
        manifest_path=manifest_path,
    )


def compile_export(path, setup: str | os.PathLike | None = None) -> float:
    """Compile a package previously produced by :func:`translate_model`.

    ``setup`` mirrors modelx-cython's ``--setup`` option. If omitted, the
    generated manifest is consulted before falling back to the package-local
    ``_mx_native_build.py`` script.
    """
    path = pathlib.Path(path).resolve()
    if setup:
        build_script = pathlib.Path(setup).resolve()
    else:
        manifest_path = path / "_mx_native_manifest.json"
        if manifest_path.exists():
            setup_file = json.loads(manifest_path.read_text(encoding="utf-8")).get("setup_file")
            build_script = pathlib.Path(setup_file) if setup_file else (path / "_mx_native_build.py")
        else:
            build_script = path / "_mx_native_build.py"
    if not build_script.exists():
        raise FileNotFoundError(f"Semantic translation metadata not found: {build_script}")
    t0 = time.perf_counter()
    proc = subprocess.run(
        [sys.executable, str(build_script), "build_ext", "--inplace"],
        cwd=path.parent,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if proc.returncode:
        raise RuntimeError("Cython compilation failed:\n" + proc.stdout)
    return time.perf_counter() - t0


def export_model(model, path, **kwargs) -> ExportResult:
    """modelx.export_model-like convenience API that also compiles the native path."""
    result = translate_model(model, path, **kwargs)
    dt = compile_export(result.path)
    result.compilation_seconds = dt
    result.compiled = True
    return result


# Alias intentionally named after the established modelx-cython workflow.
cythonize_model = export_model
