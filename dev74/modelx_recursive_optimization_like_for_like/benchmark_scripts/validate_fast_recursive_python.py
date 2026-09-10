from __future__ import annotations
import argparse, importlib, importlib.util, json, math, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = {
    "BasicTerm_S":"pv_net_cf",
    "Term_UK_A":"bench_net_cf",
    "WOL_UK_S":"bench_net_cf",
    "ULSG_US_S":"bench_net_cf",
    "VA_US_S":"bench_net_cf",
}

def load_file(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod

def main():
    sys.setrecursionlimit(20000)
    ap = argparse.ArgumentParser()
    ap.add_argument("model")
    ap.add_argument("--limit", type=int, default=None)
    ns = ap.parse_args()
    model = ns.model
    target = TARGET[model]
    pkgroot = ROOT / "generated_exports" / model
    sys.path.insert(0, str(pkgroot))
    mm = importlib.import_module(model + "._mx_model")
    Model = getattr(mm, "_c_" + model)
    m = Model()
    fr = load_file("fr_" + model, ROOT / "fast_recursive_python" / (model + ".py"))
    rt = fr.FastRecursiveRuntime()
    if model == "BasicTerm_S":
        keys = list(m.Projection.model_point_table.index)
    else:
        keys = list(m.Data.model_point_table().index)
    if ns.limit is not None:
        keys = keys[:ns.limit]

    t = time.perf_counter()
    exp = []
    for k in keys:
        ctx = m.Projection[k]
        exp.append(float(getattr(ctx, target)()))
        try:
            del m.Projection[k]
        except Exception:
            pass
    export_s = time.perf_counter() - t

    t = time.perf_counter()
    got = []
    for k in keys:
        ctx = m.Projection[k]
        got.append(float(fr.evaluate(rt, ctx)))
        try:
            del m.Projection[k]
        except Exception:
            pass
    fr_s = time.perf_counter() - t

    diffs = [abs(a-b) for a,b in zip(exp, got)]
    max_abs = max(diffs, default=0.0)
    ok = all(math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-12) for a,b in zip(exp,got))
    row = {
        "model": model,
        "target": target,
        "policies": len(keys),
        "export_s": export_s,
        "fast_recursive_reference_s": fr_s,
        "max_abs_error": max_abs,
        "allclose_1e12": ok,
        "checksum_expected": sum(exp),
        "checksum_recursive": sum(got),
        "values_expected": exp if len(keys) <= 20 else None,
        "values_recursive": got if len(keys) <= 20 else None,
    }
    print(json.dumps(row))
    if not ok:
        raise SystemExit(2)

if __name__ == "__main__":
    main()
