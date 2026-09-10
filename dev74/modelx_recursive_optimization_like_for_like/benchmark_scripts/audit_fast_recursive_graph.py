from __future__ import annotations
import argparse, json, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / 'compiler'))
from modelx_graph.fast_recursive_graph import build_fast_recursive_program

TARGETS = {
    'BasicTerm_S': 'pv_net_cf',
    'Term_UK_A': 'bench_net_cf',
    'WOL_UK_S': 'bench_net_cf',
    'ULSG_US_S': 'bench_net_cf',
    'VA_US_S': 'bench_net_cf',
}
EXPECTED = {
    'BasicTerm_S': {'cells': 35, 'calls': 68, 'unique': 63, 'max_arity': 1, 'recursive_sccs': 1, 'max_scc': 4},
    'Term_UK_A': {'cells': 57, 'calls': 127, 'unique': 114, 'max_arity': 2, 'recursive_sccs': 6, 'max_scc': 7},
    'WOL_UK_S': {'cells': 52, 'calls': 126, 'unique': 110, 'max_arity': 2, 'recursive_sccs': 6, 'max_scc': 1},
    'ULSG_US_S': {'cells': 102, 'calls': 223, 'unique': 209, 'max_arity': 2, 'recursive_sccs': 8, 'max_scc': 6},
    'VA_US_S': {'cells': 169, 'calls': 492, 'unique': 454, 'max_arity': 3, 'recursive_sccs': 7, 'max_scc': 53},
}

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, default=HERE / 'results' / 'FAST_RECURSIVE_GRAPH_COVERAGE.json')
    ap.add_argument('--no-assert', action='store_true')
    ns = ap.parse_args()
    results = []
    for model, target in TARGETS.items():
        source = HERE / 'generated_exports' / model / model / '_mx_classes.py'
        t0=time.perf_counter(); p = build_fast_recursive_program(source, target=target); build_s=time.perf_counter()-t0
        m = p.manifest()
        row = {
            'model': model,
            'target': target,
            'graph_supported': p.graph_supported,
            'build_s': build_s,
            'graph_blockers': list(p.graph_blockers),
            'cells': len(p.cells),
            'call_sites': len(p.call_sites),
            'unique_dependencies': len(p.unique_dependency_pairs),
            'max_call_arity': p.max_call_arity,
            'sccs': len(p.sccs),
            'recursive_sccs': len(p.recursive_sccs),
            'max_recursive_scc_size': p.max_scc_size,
            'external_calls': len(p.external_calls),
            'formula_notes': list(p.formula_notes),
            'recursive_components': [list(s.cells) for s in sorted(p.recursive_sccs, key=lambda s: (-len(s.cells), s.cells))],
            'manifest_file': f'fast_recursive_graph/{model}.json',
        }
        if not ns.no_assert:
            e = EXPECTED[model]
            assert p.graph_supported, (model, p.graph_blockers)
            assert row['cells'] == e['cells'], (model, 'cells', row['cells'], e['cells'])
            assert row['call_sites'] == e['calls'], (model, 'calls', row['call_sites'], e['calls'])
            assert row['unique_dependencies'] == e['unique'], (model, 'unique', row['unique_dependencies'], e['unique'])
            assert row['max_call_arity'] == e['max_arity'], (model, 'arity', row['max_call_arity'], e['max_arity'])
            assert row['recursive_sccs'] == e['recursive_sccs'], (model, 'scc', row['recursive_sccs'], e['recursive_sccs'])
            assert row['max_recursive_scc_size'] == e['max_scc'], (model, 'max_scc', row['max_recursive_scc_size'], e['max_scc'])
        manifest_path = HERE / 'fast_recursive_graph' / f'{model}.json'
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(m, indent=2), encoding='utf-8')
        results.append(row)
        print(json.dumps(row), flush=True)
    ns.out.parent.mkdir(parents=True, exist_ok=True)
    ns.out.write_text(json.dumps({'contract': 'static exported-source recursive graph; no trace/stages', 'models': results}, indent=2), encoding='utf-8')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
