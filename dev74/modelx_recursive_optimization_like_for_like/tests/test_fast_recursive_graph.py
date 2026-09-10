from __future__ import annotations
import json, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'compiler'))
from modelx_graph.fast_recursive_graph import build_fast_recursive_program
from modelx_graph.fast_recursive_python import emit_fast_recursive_python

EXPECTED = {
    'BasicTerm_S': ('pv_net_cf', 35, 68, 63, 1, 4),
    'Term_UK_A': ('bench_net_cf', 57, 127, 114, 6, 7),
    'WOL_UK_S': ('bench_net_cf', 52, 126, 110, 6, 1),
    'ULSG_US_S': ('bench_net_cf', 102, 223, 209, 8, 6),
    'VA_US_S': ('bench_net_cf', 169, 492, 454, 7, 53),
}

class FastRecursiveGraphTests(unittest.TestCase):
    def test_all_benchmark_products_have_static_recursive_graph(self):
        for model, (target, cells, calls, unique, recursive_sccs, max_scc) in EXPECTED.items():
            with self.subTest(model=model):
                src = ROOT / 'generated_exports' / model / model / '_mx_classes.py'
                p = build_fast_recursive_program(src, target=target)
                self.assertTrue(p.graph_supported, p.graph_blockers)
                self.assertEqual(len(p.cells), cells)
                self.assertEqual(len(p.call_sites), calls)
                self.assertEqual(len(p.unique_dependency_pairs), unique)
                self.assertEqual(len(p.recursive_sccs), recursive_sccs)
                self.assertEqual(p.max_scc_size, max_scc)

    def test_va_large_recursive_component_is_admitted_without_stages(self):
        src = ROOT / 'generated_exports' / 'VA_US_S' / 'VA_US_S' / '_mx_classes.py'
        p = build_fast_recursive_program(src, target='bench_net_cf')
        largest = max(p.recursive_sccs, key=lambda s: len(s.cells))
        self.assertEqual(len(largest.cells), 53)
        self.assertIn('av_pp', largest.cells)
        self.assertIn('gwb_pp', largest.cells)
        self.assertIn('wd_pp', largest.cells)
        self.assertIn('phi_glwb_vix', p.cells)  # static source closure, not trace-dependent
        # Fast-recursive IR carries graph/call ABI only; stage scheduling is deliberately absent.
        self.assertFalse(hasattr(p, 'stages'))
        self.assertFalse(hasattr(p, 'execution_blocks'))

    def test_multi_argument_calls_and_defaults_are_bound(self):
        src = ROOT / 'generated_exports' / 'VA_US_S' / 'VA_US_S' / '_mx_classes.py'
        p = build_fast_recursive_program(src, target='bench_net_cf')
        self.assertEqual(p.max_call_arity, 3)
        # At least one call must carry all three arguments in the direct recursive ABI.
        three = [c for c in p.call_sites if c.arity == 3]
        self.assertTrue(three)
        self.assertTrue(all(len(c.bound_args) == 3 for c in three))

        term_src = ROOT / 'generated_exports' / 'Term_UK_A' / 'Term_UK_A' / '_mx_classes.py'
        term = build_fast_recursive_program(term_src, target='bench_net_cf')
        default_sites = [
            a for c in term.call_sites for a in c.bound_args if a.origin == 'default'
        ]
        self.assertTrue(default_sites)
        self.assertTrue(any(a.source == 'None' for a in default_sites))


    def test_generated_reference_runtime_executes_recursive_multiarg_program(self):
        source = """
class _c_Projection:
    def _f_a(self, t, kind='A'):
        if t <= 0:
            return 1 if kind == 'A' else 2
        return self.a(t - 1, kind) + self.b(t, kind)
    def _f_b(self, t, kind='A'):
        return t if kind == 'A' else 2 * t
    def _f_out(self):
        return self.a(4) + self.a(3, 'B')
"""
        with tempfile.TemporaryDirectory() as td:
            pth = Path(td) / '_mx_classes.py'
            pth.write_text(source)
            program = build_fast_recursive_program(pth, target='out')
            emitted = emit_fast_recursive_python(program)
            ns = {}
            exec(compile(emitted, '<fast-recursive-test>', 'exec'), ns, ns)
            class Ctx: pass
            rt = ns['FastRecursiveRuntime'](Ctx())
            self.assertEqual(ns['fr_out'](rt), 25)

    def test_provider_syntax_does_not_block_graph(self):
        src = ROOT / 'generated_exports' / 'VA_US_S' / 'VA_US_S' / '_mx_classes.py'
        p = build_fast_recursive_program(src, target='bench_net_cf')
        self.assertTrue(p.graph_supported)
        self.assertTrue(any(x.kind == 'provider' for x in p.external_calls))
        self.assertIn('provider-call', p.formula_notes)

    def test_first_class_cell_reference_fails_closed(self):
        source = '''\nclass _c_Projection:\n    def _f_a(self, t):\n        return self.b\n    def _f_b(self, t):\n        return t\n'''
        with tempfile.TemporaryDirectory() as td:
            pth = Path(td) / '_mx_classes.py'
            pth.write_text(source)
            p = build_fast_recursive_program(pth, target='a')
            self.assertFalse(p.graph_supported)
            self.assertTrue(any('first-class Cell reference' in x for x in p.graph_blockers))

if __name__ == '__main__':
    unittest.main()
