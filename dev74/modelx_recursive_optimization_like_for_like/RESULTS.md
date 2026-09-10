# Like-for-like rerun: model.export(), modelx-cython, fast recursive Cython, and compact sequential references

## Purpose

This rerun replaces earlier mixed-protocol benchmark tables. Every reported runtime now uses the same complete shipped policy vector for that product, in the same order, for the same scalar target. Representative-policy-only native timings are not carried into the headline table.

Policy sets:

- `BasicTerm_S`: 10,000 distinct policies; target `pv_net_cf()`.
- `Term_UK_A`: all 8 shipped policies; target `bench_net_cf() = sum(net_cf(t))`.
- `WOL_UK_S`: all 7 shipped policies; same `bench_net_cf()` target.
- `ULSG_US_S`: all 4 shipped policies; same `bench_net_cf()` target.
- `VA_US_S`: all 9 shipped policies; same `bench_net_cf()` target.

Build/preparation is excluded from execution timing and reported separately. Current modelx-cython execution is the median of five fresh-process portfolio valuations for each successful build. Pure-Python export timings use five repetitions for Term/WOL/ULSG/VA and three full 10,000-policy runs for BasicTerm. Fast-recursive WOL/ULSG timing repeats the complete heterogeneous portfolio 2,000 times per process and reports the median of five process-level medians. BasicTerm native timing uses seven complete 10,000-policy repetitions.

## Environment

- Python 3.13.5
- Cython 3.2.4
- NumPy 2.3.5
- pandas 2.2.3
- GCC 14.2.0
- Linux 6.18.35 x86-64
- native prototypes compiled with `-O2`
- one execution thread

## Corrected full-domain execution table

| Model | Policies | current `model.export()` | optimized recursive Python | current modelx-cython | trace-derived typed recursive Cython (dev73) | compact sequential Cython |
|---|---:|---:|---:|---:|---:|---:|
| BasicTerm_S | 10,000 | 18.575 s | **6.378 s** | 8.763 s | **0.2443 s** | **0.2308 s** |
| Term_UK_A | 8 | 10.241 ms | **2.088 ms** | 8.203 ms | not produced: categorical table axis | not produced: same frontend blocker |
| WOL_UK_S | 7 | 599.705 ms | **37.708 ms** | 546.893 ms | **1.004 ms** | full-domain compact backend rejected 2-D table input |
| ULSG_US_S | 4 | 187.240 ms | **64.399 ms** | build failed | **1.963 ms** | full-domain compact backend rejected schedule/storage disagreement |
| VA_US_S | 9 | 2.532 s | **235.920 ms** | 2.320 s | old trace-derived frontend did not produce a bounded full-domain artifact | no compact multistage backend |

These are portfolio totals. Per-policy figures are available in `LIKE_FOR_LIKE_RESULTS.csv`.

## Pure-Python result

The pure-Python optimization remains robust under the corrected protocol:

| Model | Speedup vs current export |
|---|---:|
| BasicTerm_S | 2.91x |
| Term_UK_A | 4.91x |
| WOL_UK_S | 15.90x |
| ULSG_US_S | 2.91x |
| VA_US_S | 10.73x |

For Term/WOL/ULSG/VA the optimized variant is the provider-normalized + prepared model-point + merged-wrapper variant used in the earlier attribution work. The complete output vector and checksum remain unchanged.

## dev73 typed fast-recursive Cython benchmark result

The corrected performance rerun predates the dev74 static recursive graph implementation below. Three products had valid full-domain **typed numeric** fast-recursive artifacts through the old trace-derived frontend:

- BasicTerm_S: 0.2443 s / 10,000 policies = 24.43 us/policy.
- WOL_UK_S: 1.004 ms / 7 policies = 143.42 us/policy.
- ULSG_US_S: 1.963 ms / 4 policies = 490.84 us/policy.

Correctness:

- BasicTerm fast recursive and compact sequential arrays are bit-identical over all 10,000 policies.
- WOL max absolute difference vs full live-model reference is `9.276845958083868e-11`; `allclose(rtol=atol=1e-12)` passes on all 7 policies.
- ULSG max absolute difference is `5.820766091346741e-11`; the same `1e-12` gate passes on all 4 policies.

The WOL fast-recursive compiler trace uses policies 1, 5, and 6, then validates the frozen generated artifact across all seven run policies. ULSG uses 1, 3, and 4, then validates all four policies. The sample is therefore a compilation input, not the runtime population.

## Fresh modelx-cython

Fresh full-policy builds were run from the same model/export source:

| Model | Build | Median execution |
|---|---:|---:|
| BasicTerm_S | 25.790 s | 8.763 s |
| Term_UK_A | 24.390 s | 8.203 ms |
| WOL_UK_S | 27.031 s | 546.893 ms |
| ULSG_US_S | **failed**: Cython inferred complex ordering | n/a |
| VA_US_S | 81.841 s | 2.320 s |

VA required raising the Python recursion limit during modelx-cython tracing; the resulting compiled package then reproduced all nine policy results.

## Compact sequential correction

Earlier Term/WOL/ULSG compact-sequential timings were representative-policy physical-runtime experiments. They must not be put next to full heterogeneous portfolio numbers as if they were the same benchmark.

Fresh full-domain attempts found:

- BasicTerm_S: succeeds and remains the clean recursive-vs-sequential comparison (0.2443 s vs 0.2308 s; sequential is 1.058x faster).
- Term_UK_A: frontend stops on the dynamic categorical mortality-table axis.
- WOL_UK_S: full-domain compact backend stops on a required 2-D table input.
- ULSG_US_S: full-domain compact backend stops on canonical schedule/PureMap-storage disagreement.
- VA_US_S: no equivalent compact multistage sequential backend exists in this benchmark.

The prior one-policy Term/WOL/ULSG sequential numbers are retained only in historical evidence, not the corrected headline comparison.

## What the dev73 rerun exposed, and what dev74 changes

The old typed numeric prototype reused the graph compiler's trace-derived Stage artifact as its frontend. That exposed two distinct classes of limitation:

- `Term_UK_A` reached a categorical exact-lookup lowering blocker. This is a formula/provider problem, not a recursive-graph problem.
- `VA_US_S` could not obtain a bounded full-domain program by unioning realized Stage traces; policies 1 and 2 missed `phi_glwb_vix`, while adding more policies made Stage preparation grow sharply. This was a **program-discovery/frontend problem**, not evidence that recursive execution requires VA's three-stage schedule.

The dev74 implementation separates those concerns. It constructs the recursive Cell program statically from the exported source and deliberately treats unsupported table/provider syntax as downstream lowering work. All five products now have complete recursive graphs with zero graph blockers.

## dev74 static fast-recursive graph implementation

The new path does not consume `StageExecutionPlan`, recurrence schedules, scan directions, fences, materialized stage histories, or representative-policy trace closure. It parses exported `_f_<cell>` methods, includes every syntactic Cell call in every branch, binds calls to the callee's full signature, and defines memo identity as the complete Cell argument tuple.

| Model | Cells | Cell call sites | Max Cell arity | Recursive SCCs | Largest recursive SCC | Graph blockers |
|---|---:|---:|---:|---:|---:|---:|
| BasicTerm_S | 35 | 68 | 1 | 1 | 4 | 0 |
| Term_UK_A | 57 | 127 | 2 | 6 | 7 | 0 |
| WOL_UK_S | 52 | 126 | 2 | 6 | 1 | 0 |
| ULSG_US_S | 102 | 223 | 2 | 8 | 6 | 0 |
| VA_US_S | 169 | 492 | 3 | 7 | **53** | 0 |

VA is the decisive graph test. Its static closure includes the VIX-specific `phi_glwb_vix` path without executing a VIX policy first, and its 53-Cell recursive SCC is represented directly rather than converted into stages.

The same IR emits two executable proof backends:

1. a direct-recursive Python reference runtime; and
2. a Cython object-mode recursive module in which Cell-to-Cell calls are direct `cdef` calls while pandas/table/module operations remain Python objects.

Both are bit-exact against the bundled exported packages for all shipped Term/WOL/ULSG/VA policies; BasicTerm is bit-exact on the first 1,000 policies in the generic dev74 proof harness. All five Cython object-mode modules build successfully. In particular, the complete VA 169-Cell program compiles into one recursive Cython module and validates **9/9 policies with no Stage scheduler**.

This is a graph/ABI acceptance result, not a new typed-native performance benchmark. The next step is to lower provider/table operations and primitive numeric values inside this static recursive program; the old dev73 typed performance rows remain the performance evidence until that work is complete.

## Build/preparation evidence

See `LIKE_FOR_LIKE_BUILD_RESULTS.csv`. Important successful fast-recursive preparation/build figures are:

- BasicTerm_S native C build: 5.90 s (fast recursive), 5.28 s (compact sequential).
- WOL_UK_S: trace 5.55 s + Stage normalization/validation 10.60 s + Cython/C build 6.97 s.
- ULSG_US_S: trace 11.42 s + Stage normalization/validation 32.40 s + Cython/C build 10.01 s.

These times are not included in valuation runtime.

## Conclusion

The corrected benchmark supports two claims cleanly:

1. Pure-Python `model.export()` performance can improve substantially by normalizing lookup providers and preparing scalar inputs while retaining recursive Cells.
2. A compact recursive Cython runtime can be dramatically faster than current modelx-cython where typed numeric lowering is available. The dev74 implementation now establishes that the **recursive graph itself** covers all five products, including full VA, independently of provider/table lowering.

It does **not** support using the earlier representative-policy Term/WOL/ULSG sequential timings as full-domain comparisons. Those values have been removed from the corrected table.
