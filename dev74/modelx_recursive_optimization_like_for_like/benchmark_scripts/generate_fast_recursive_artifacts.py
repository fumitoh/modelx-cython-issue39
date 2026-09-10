from __future__ import annotations
import argparse, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'compiler'))
from modelx_graph import (
    build_fast_recursive_program,
    write_fast_recursive_python,
    write_fast_recursive_cython_object,
)

TARGETS = {
    'BasicTerm_S': 'pv_net_cf',
    'Term_UK_A': 'bench_net_cf',
    'WOL_UK_S': 'bench_net_cf',
    'ULSG_US_S': 'bench_net_cf',
    'VA_US_S': 'bench_net_cf',
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('models', nargs='*', choices=tuple(TARGETS), help='default: all models')
    ns = ap.parse_args()
    models = ns.models or list(TARGETS)
    for model in models:
        source = ROOT / 'generated_exports' / model / model / '_mx_classes.py'
        p = build_fast_recursive_program(source, target=TARGETS[model])
        if not p.graph_supported:
            raise RuntimeError(f'{model}: graph blockers: {p.graph_blockers}')
        graph = ROOT / 'fast_recursive_graph' / f'{model}.json'
        graph.parent.mkdir(parents=True, exist_ok=True)
        graph.write_text(json.dumps(p.manifest(), indent=2), encoding='utf-8')
        py = write_fast_recursive_python(p, ROOT / 'fast_recursive_python' / f'{model}.py')
        pyx = write_fast_recursive_cython_object(p, ROOT / 'fast_recursive_cython_object' / f'{model}.pyx')
        print(json.dumps({
            'model': model,
            'cells': len(p.cells),
            'call_sites': len(p.call_sites),
            'recursive_sccs': len(p.recursive_sccs),
            'max_recursive_scc_size': p.max_scc_size,
            'python_source': str(py.relative_to(ROOT)),
            'cython_object_source': str(pyx.relative_to(ROOT)),
        }))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
