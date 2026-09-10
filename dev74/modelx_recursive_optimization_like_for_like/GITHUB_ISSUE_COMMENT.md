Thanks - I reran the benchmarks under a strict like-for-like protocol, and I also changed the recursive prototype so its dependency program is no longer discovered from representative runtime traces.

The results now separate three questions that had become mixed together:

1. how much `model.export()` can improve while keeping recursive Cells;
2. how fast a typed recursive Cython runtime can be when native provider lowering is available; and
3. whether the recursive graph itself can represent the more complex products, especially VA, without converting them into staged loops.

## 1. Like-for-like pure-Python benchmark

Every number below uses the complete shipped policy vector for the product, in the same order, with build/preparation excluded from execution timing.

| model | policies | current `model.export()` | optimized recursive Python | speedup |
|---|---:|---:|---:|---:|
| BasicTerm_S | 10,000 | 18.575 s | **6.378 s** | 2.91x |
| Term_UK_A | 8 | 10.241 ms | **2.088 ms** | 4.91x |
| WOL_UK_S | 7 | 599.705 ms | **37.708 ms** | 15.90x |
| ULSG_US_S | 4 | 187.240 ms | **64.399 ms** | 2.91x |
| VA_US_S | 9 | 2.532 s | **235.920 ms** | 10.73x |

The main optimization is to prepare scalar lookup providers once rather than repeatedly executing pandas/MultiIndex/step-table operations inside hot Cells. Recursive Cell evaluation is unchanged.

I included a small helper vocabulary for making those semantics explicit, for example:

```python
from modelx_fast_lookup import exact4, grouped_step2


def mort_rate(t):
    return exact4(
        mort_table_fast,
        basis(), sex(), smoker(), attained_age(t),
    )


def gross_return(t):
    return grouped_step2(
        return_scenario_fast,
        scenario_id(), subaccount_id(), duration_mth(t),
    )
```

In pure Python these helpers use prepared dictionaries/sorted axes. A native backend can recognize the same operations and lower them to encoded keys, typed arrays and inline search.

## 2. Like-for-like native benchmark

I rebuilt current modelx-cython and reran the complete heterogeneous policy sets. The table below deliberately excludes the earlier representative-policy-only Term/WOL/ULSG sequential timings.

| model | policies | current modelx-cython | typed fast-recursive Cython | compact sequential Cython |
|---|---:|---:|---:|---:|
| BasicTerm_S | 10,000 | 8.763 s | **0.2443 s** | **0.2308 s** |
| Term_UK_A | 8 | 8.203 ms | not produced: categorical table lowering blocker | same frontend blocker |
| WOL_UK_S | 7 | 546.893 ms | **1.004 ms** | full-domain compact backend currently rejects required 2-D table input |
| ULSG_US_S | 4 | build failed | **1.963 ms** | full-domain compact backend currently rejects a schedule/storage case |
| VA_US_S | 9 | 2.320 s | old trace-derived frontend did not produce a bounded full-domain artifact | no comparable compact multistage kernel |

These are complete portfolio totals, not representative-policy throughput figures.

Correctness gates:

- BasicTerm fast-recursive and compact-sequential arrays are bit-exact over all 10,000 policies.
- WOL passes all 7 policies at `rtol=atol=1e-12`.
- ULSG passes all 4 policies at the same tolerance.
- Fresh modelx-cython reproduces the complete policy vectors for BasicTerm, Term, WOL and VA. ULSG still fails current modelx-cython compilation because Cython infers an ordered comparison involving a complex value.

The clean BasicTerm comparison is particularly useful: once the recursive runtime is reduced to direct typed functions and compact numeric state, converting the recurrence to an explicit sequential kernel changes 0.2443 s to 0.2308 s over 10,000 distinct policies.

## 3. The VA gap was a frontend problem, not a recursion problem

The typed fast-recursive prototype above reused the graph compiler's trace-derived Stage artifact as its frontend. That worked for full-domain WOL and ULSG, but not for VA: different policies exposed additional branches, including a VIX-specific path, and attempting to obtain one complete program by unioning realized Stage traces became expensive.

I therefore replaced trace-based program discovery for the recursive path with a static recursive graph built directly from the exported source.

The new path does **not** use recurrence stages, scan scheduling, fences, materialized Stage histories, or representative-policy trace closure. It statically includes every syntactic Cell call in every branch, binds calls to the callee's full signature, and uses the complete Cell argument tuple as memo identity. Unsupported pandas/table/module syntax is recorded as downstream provider/formula-lowering work but does not block graph construction.

The resulting full target closures are:

| model | Cells | Cell call sites | max Cell arity | recursive SCCs | largest SCC | graph blockers |
|---|---:|---:|---:|---:|---:|---:|
| BasicTerm_S | 35 | 68 | 1 | 1 | 4 | 0 |
| Term_UK_A | 57 | 127 | 2 | 6 | 7 | 0 |
| WOL_UK_S | 52 | 126 | 2 | 6 | 1 | 0 |
| ULSG_US_S | 102 | 223 | 2 | 8 | 6 | 0 |
| VA_US_S | **169** | **492** | 3 | 7 | **53** | **0** |

VA is the useful stress case. The static graph contains the VIX-specific `phi_glwb_vix` path without first executing a VIX policy, and it contains a 53-Cell recursive SCC. There is no three-stage representation in this recursive path.

I then emitted the same static IR in two executable proof forms:

1. a direct-recursive Python reference runtime; and
2. Cython object mode, where each internal Cell is a `cdef` recursive function and Cell-to-Cell calls are direct C-level calls, while provider/table expressions intentionally remain Python objects.

All five recursive Cython modules build successfully. The generated modules are bit-exact against the bundled exported models for:

- Term_UK_A: 8/8 policies;
- WOL_UK_S: 7/7;
- ULSG_US_S: 4/4;
- VA_US_S: **9/9**;
- BasicTerm_S: first 1,000 policies in this generic graph/ABI gate.

So the complete **169-Cell VA program, including its 53-Cell recursive SCC, now compiles and executes as one recursive Cython module without a Stage scheduler**.

This object-mode result is a graph/ABI proof, not a new performance number. The next native work is provider/type lowering on top of this static recursive program.

## Suggested implementation direction

My current preferred path for modelx-cython would be:

1. start from the exported recursive formulas and build the static Cell graph/signatures;
2. normalize model-point data and exact/step/grouped-step lookup providers;
3. lower numeric Cells to direct typed recursive C functions;
4. use compact typed memo/context storage;
5. execute independent model points in a C-level portfolio loop, with `nogil` where the reachable closure permits it;
6. keep the existing modelx-cython/exported-Python path as fallback for unsupported Python operations.

The source-model changes needed for the fast subset can stay small: use explicit exact/step/grouped-step lookup semantics with primitive scalar keys and avoid constructing pandas/Series/list objects inside hot numeric Cells when a prepared provider is available.

## Attachment

I attached the updated standalone package used for these results. It includes:

- the corrected like-for-like benchmark tables and raw timing evidence;
- fresh modelx-cython build/execution evidence;
- the static fast-recursive compiler implementation;
- graph manifests for all five products;
- generated recursive Python and Cython sources;
- parity evidence, including VA 9/9;
- the pure-Python lookup helper library and native Cython lookup primitives;
- regeneration/build scripts and tests;
- generated export packages/input data needed to reproduce the graph/ABI results.

The package excludes compiled binaries, generated C/object files, and the modelx/modelx-cython/lifelib source trees.
