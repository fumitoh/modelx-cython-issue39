# Fast-recursive graph implementation — dev74

## Objective

Make fast recursion graph-complete for the five benchmark products without inheriting the sequential compiler's stage/schedule machinery. Formula/data lowering is deliberately a separate capability: pandas/table/module/container syntax can remain unsupported for native emission without blocking recursive graph construction.

## Implemented architecture

```text
model.export() _mx_classes.py
        |
        v
Static exported Cell catalogue
        |
        v
target closure over every syntactic self.<Cell>(...) call
        |
        +--> signature/default binding for every call site
        +--> arbitrary Cell arity (0..N; benchmark max = 3)
        +--> cache key = complete Cell argument tuple
        +--> provider/module calls recorded as external leaves
        |
        v
FastRecursiveProgram
        |
        +--> SCC analysis for diagnostics only
        +--> NO stage construction
        +--> NO monotone scan proof
        +--> NO fences/materialized stage histories
        +--> NO representative-policy trace closure
```

The SCC analysis does **not** schedule or reject recursive components. It only describes the static recursive graph. A 53-Cell SCC in `VA_US_S` is therefore admitted exactly the same way as a one-Cell recurrence.

## Graph acceptance contract

The graph layer fails closed only when recursive dispatch itself cannot be represented statically, for example:

- first-class/dynamic Cell references rather than direct calls;
- unbindable Cell call signatures (`*args`, `**kwargs`, unknown keywords, missing required arguments);
- unresolved target Cells.

The following are *not graph blockers*:

- DataFrame/MultiIndex/table access;
- `np`, `pd`, `math` operations;
- lists/comprehensions/generators;
- `raise` branches;
- provider lookup semantics.

Those are retained as formula/provider lowering notes for the next native-emission layer.

## Full target-closure results

| Model | Target | Cells | Call sites | Unique dependency pairs | Max Cell call arity | Recursive SCCs | Largest recursive SCC | Graph blockers |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| BasicTerm_S | `pv_net_cf` | 35 | 68 | 63 | 1 | 1 | 4 | 0 |
| Term_UK_A | `bench_net_cf` | 57 | 127 | 114 | 2 | 6 | 7 | 0 |
| WOL_UK_S | `bench_net_cf` | 52 | 126 | 110 | 2 | 6 | 1 | 0 |
| ULSG_US_S | `bench_net_cf` | 102 | 223 | 209 | 2 | 8 | 6 | 0 |
| VA_US_S | `bench_net_cf` | 169 | 492 | 454 | 3 | 7 | 53 | 0 |

`VA_US_S` is the decisive graph test. The 53-Cell recursive component includes account value, benefit-base, withdrawal, charge and guarantee state. `phi_glwb_vix` is present in the static closure even when the representative policies used by the earlier trace compiler do not execute the VIX branch.

## Why this changes the VA diagnosis

The earlier fast-recursive benchmark generator consumed a trace-normalized Stage artifact. That made program discovery policy-dependent and inherited a zero/time-argument assumption from the old physical generator.

The dev74 graph path instead consumes exported source directly. It sees all syntactic Cell calls in all branches and binds them to the callee's complete exported signature. Therefore:

- no policy sample is needed to discover the recursive graph;
- multi-argument Cells such as `(t, i)` or `(t, timing, ...)` are valid graph edges;
- default arguments are materialized in the direct recursive ABI;
- memoization semantics can key on the full argument tuple;
- SCC size/direction has no effect on admission.

## Executable reference runtime

`fast_recursive_python.py` lowers the same IR to one direct recursive Python function per Cell:

```text
fr_cell(runtime, args...)
    -> memo lookup keyed by the complete argument tuple
    -> _calc_cell(runtime, args...)
    -> direct fr_dependency(runtime, ...) calls
```

All non-Cell syntax is preserved. This makes it possible to validate the recursion/graph ABI before native expression lowering. The generated reference runtime is bit-exact against the exported package on:

- Term_UK_A: 8/8 policies;
- WOL_UK_S: 7/7;
- ULSG_US_S: 4/4;
- VA_US_S: 9/9;
- BasicTerm_S: first 1,000 policies of the existing 10,000-policy corpus.

The full 10,000-policy BasicTerm native recursive prototype had already been validated in the preceding stage; the new generic Python reference is a correctness gate, not a throughput target.

The same source is also emitted as Cython object mode with internal `cdef object` Cell functions. All five generated modules compile successfully and reproduce the same validation vectors. This proves that the complete recursive graph can be lowered to C-level direct Cell calls before any pandas/provider operation is converted to a native numeric representation.

## Files

- `compiler/modelx_graph/fast_recursive_graph.py` — static recursive graph/ABI implementation.
- `compiler/modelx_graph/fast_recursive_python.py` — executable Python reference emitter.
- `compiler/modelx_graph/fast_recursive_cython.py` — Cython object-mode graph/ABI emitter.
- `benchmark_scripts/audit_fast_recursive_graph.py` — five-product graph census and manifest generator.
- `benchmark_scripts/validate_fast_recursive_python.py` — full shipped-policy reference parity harness.
- `benchmark_scripts/validate_fast_recursive_cython_object.py` — compiled recursive object-mode parity harness.
- `tests/test_fast_recursive_graph.py` — acceptance tests, including VA's 53-Cell SCC and trace-independent VIX branch.
- `fast_recursive_graph/*.json` — per-product complete recursive manifests.
- `results/FAST_RECURSIVE_GRAPH_COVERAGE.json` — compact census.

## Remaining work, intentionally outside this stage

This stage does **not** claim that every Cell body can already be emitted as `noexcept nogil` Cython. The next layer should lower formula bodies and providers against this static graph, using explicit exact/step/grouped-step lookup semantics where possible and existing modelx-cython/Python fallback otherwise.

The important result here is narrower: **there is no graph/scheduling reason preventing fast-recursive execution for any of the five benchmark products.**
