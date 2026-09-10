# Fast-recursive graph results

The new dev74 path builds the recursive program **statically from exported source**. No modelx execution trace, representative-policy sample, recurrence schedule, or Stage graph is used to discover dependencies.

| Model | Cells in target closure | Cell call sites | Unique dependencies | Max Cell arity | Recursive SCCs | Largest SCC | Graph build | Graph blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| BasicTerm_S | 35 | 68 | 63 | 1 | 1 | 4 | 0.018 s | 0 |
| Term_UK_A | 57 | 127 | 114 | 2 | 6 | 7 | 0.055 s | 0 |
| WOL_UK_S | 52 | 126 | 110 | 2 | 6 | 1 | 0.050 s | 0 |
| ULSG_US_S | 102 | 223 | 209 | 2 | 8 | 6 | 0.159 s | 0 |
| VA_US_S | 169 | 492 | 454 | 3 | 7 | 53 | 0.414 s | 0 |

## Executable recursive-reference gate

The same IR now emits a pure-Python recursive reference runtime. It rewrites direct Cell calls to direct `fr_<cell>(runtime, ...)` calls and memoizes every Cell by its complete argument tuple. Provider/table/module syntax is left untouched. This is not the performance backend; it is an executable proof that the graph ABI itself is sufficient.

| Model | Policies validated | Result |
|---|---:|---|
| BasicTerm_S | first 1,000 of the existing 10,000-policy corpus | bit-exact |
| Term_UK_A | 8/8 | bit-exact |
| WOL_UK_S | 7/7 | bit-exact |
| ULSG_US_S | 4/4 | bit-exact |
| VA_US_S | 9/9 | bit-exact |

For BasicTerm, the earlier fast-recursive Cython experiment already validated all 10,000 distinct policies. The new generic Python reference gate was bounded at 1,000 policies because its purpose is graph correctness, not throughput measurement.

## Cython graph/ABI proof

The same generated recursive program was also emitted as Cython **object mode**: every `_calc_*` and `fr_*` Cell is a `cdef object` function, so Cell-to-Cell recursion is a C-level call while pandas/table/module operations remain Python-object operations. This is deliberately not the final performance backend; it isolates graph/codegen feasibility from provider/type lowering.

All five modules compiled successfully with Cython 3.2.4 / GCC `-O2`, and the resulting extensions matched the exported package exactly:

| Model | Policies validated | Cython object-mode result |
|---|---:|---|
| BasicTerm_S | first 1,000 | bit-exact |
| Term_UK_A | 8/8 | bit-exact |
| WOL_UK_S | 7/7 | bit-exact |
| ULSG_US_S | 4/4 | bit-exact |
| VA_US_S | 9/9 | bit-exact |

No generated recursive Cython module contains Stage execution, fences, or recurrence scheduling. The compiled VA module contains direct C-level recursive functions for the complete 169-Cell target closure, including `gawa_pp(t, timing)`-style multi-argument dispatch and the VIX recurrence.

## VA result

VA is no longer a graph special case. The static target closure contains 169 Cells and a 53-Cell recursive SCC. The VIX-specific `phi_glwb_vix` Cell is present without running a VIX policy, because every syntactic Cell call in every source branch is included.

That means the earlier VA difficulty was caused by using trace-derived Stage artifacts as the *frontend* to the recursive prototype. The recursive execution model itself does not require VA's three-stage schedule.

## Deferred blockers

The following are intentionally recorded but do not block graph construction:

- DataFrame/MultiIndex/provider lookups;
- `np`/`pd`/`math` calls;
- lists/comprehensions/generators;
- `raise` branches and other Python syntax not yet in the native subset.

Those belong to formula/provider lowering. They should be handled after the recursive graph and ABI, rather than forcing recurrence scheduling back into the architecture.
