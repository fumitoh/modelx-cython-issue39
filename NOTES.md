# modelx-cython issue #39 — reading notes

Source: https://github.com/fumitoh/modelx-cython/issues/39
Folder created 2026-09-08 to review alexeybaran's contribution. Nothing here is part of the
modelx-cython repo.

## Layout

| Path | What it is |
|---|---|
| `downloads/` | The two zips exactly as attached to the issue |
| `proposal_2026-08-18/` | First attachment (issue body). The "modelx-native" semantic optimizer already reviewed in comment 5381729591 |
| `dev74/` | Second attachment, from comment 5562848497 (2026-09-06). `modelx_recursive_optimization_like_for_like/` |

## The thesis changed between the two attachments

**August (`proposal_2026-08-18/`)**: detect a time recurrence `x(t) -> x(t-1)`, lower the
subgraph to one Cython loop with rolling state, fuse PV reductions, parallelize with OpenMP.

**September (`dev74/`)**: recursion-to-loop is *dropped*. The package repeatedly states that
Cells keep ordinary demand-driven recursive semantics — "no stage construction", "no monotone
scan proof", "no recurrence scheduling", "no fences". OpenMP is gone too. The new claim is that
the speed never needed the loop transformation; it comes from the *physical runtime* around the
Cells (typed memo, direct C-level calls, normalized inputs, prepared lookups).

This matters because the Aug 24 reply (5398438872) argued about the value of a transformation
that is no longer being proposed.

## The comment has four independent parts, with very different maturity

### 1. Pure-Python speedups, 2.9x–15.9x

Produced by `benchmark_scripts/bench_export_variant_lfl.py`, variant `providers_mpdict_merged`.
Three stacked changes:

1. `patch_providers()` — **hand-written, per-model** monkeypatches (`if NAME=='WOL_UK_S': ...`)
   replacing pandas `.loc`/MultiIndex lookups with plain dicts and `bisect`.
2. `patch_modelpoint()` — `model_point` returns a dict instead of a pandas Series. General.
3. `merge_wrappers()` — AST pass inlining each `_f_cell` body into its memo wrapper `cell()`,
   removing one Python call per Cell evaluation. General.

Ablation from `raw_evidence/PYTHON_EXPORT_RESULTS.jsonl` — almost all of it is (1):

| model | baseline | + providers | + mpdict+merged |
|---|---:|---:|---:|
| Term_UK_A | 10.241 ms | 2.763 ms (3.71x) | 2.088 ms (1.32x more) |
| WOL_UK_S | 599.7 ms | 43.5 ms (13.8x) | 37.7 ms (1.15x more) |
| ULSG_US_S | 187.2 ms | 77.5 ms (2.42x) | 64.4 ms (1.20x more) |
| VA_US_S | 2531.9 ms | 263.8 ms (9.60x) | 235.9 ms (1.12x more) |

So this section is mostly a statement about **model authoring style**, not about the export
machinery. The mechanically automatable part is worth 1.12x–1.32x.

BasicTerm's 18.575 s -> 6.378 s (2.91x) row is a *different* thing again: it is
`benchmark_scripts/fast_recursive_basicterm_python.py`, a `FastRecursiveBasicTerm` class with
`__slots__`, flat lists, integer Cell IDs and generation stamps. No modelx wrapper at all.
Not reachable by any change to `export()`.

**Its provenance is not established by the package.** There is no generator for it in either
attachment: `FastRecursiveBasicTerm` appears in exactly two files (its own definition and
`bench_basicterm_python_lfl.py`, which imports it), the file carries no provenance header, and
no document describes it as generated. Its distinctive memo idiom (`self.generation`,
`self.tg[i]==g`, flat `tv`/`sv` lists) appears nowhere in the 67-file `compiler/modelx_graph/`
snapshot, so it is not the output of any bundled emitter. It is a near-exact Python mirror of
`native_sources/BasicTerm_S/fast_recursive.pyx` — same `MAX_T=241`, `N_TIME=16`, `N_SCALAR=17`,
and the same Cell-ID numbering in the same order (`AGE=0`, `CLAIM_PP=1`, `CLAIMS=2`, ...) — so
the two share an origin, but whether that origin was hand transcription, an unshipped tool, or
LLM assistance cannot be determined from what was attached.

### 2. Cython speedups, 35.9x vs modelx-cython on BasicTerm

These are **dev73** artifacts, produced by the *old trace-derived frontend* the comment says it
replaced. Sources in `native_sources/`; the compiled `.so` files are deliberately not in the zip,
so this section cannot be re-run from the package.

- `native_sources/BasicTerm_S/fast_recursive.pyx` — hard-coded `MAX_T=241`, `N_TIME=16`,
  `N_SCALAR=17`, `cdef enum TimeCell`, a `RecContext` struct whose fields are literally
  `policy_term / sum_assured / age_at_entry / disc_factor / mort_table`, and one giant
  `if cell == TC_AGE: ... elif ...` dispatcher. Recursion is preserved (the dispatcher re-enters
  itself), memo is a dense `double[N_TIME][MAX_T]`. Per-policy context lives on the stack, so
  this one is `nogil`-parallelizable.
- `native_sources/{WOL_UK_S,ULSG_US_S}/fast_recursive_full.pyx` — machine-generated (numbered
  globals `p_1`, `g_3`, `exttn_18`), but with **module-level global** `_cache`/`_valid`/`_epoch`.
  Not reentrant, one model per process — collides with the free-threading direction.

The benchmark driver `bench_basicterm_native_lfl.py` calls `m.run(pt, sa, aa, dr, mt)` — a
hard-coded five-argument BasicTerm-specific ABI, not a general compiler interface.

### 3+4. The static recursive graph. This is the actual new engineering.

`compiler/modelx_graph/fast_recursive_graph.py` (19 KB, pure `ast`, no modelx dependency).
Parses `_mx_classes.py`, finds `_f_<cell>` methods, walks every syntactic `self.<Cell>(...)` call
in every branch, binds each call against the callee's full signature (positional, keyword,
defaults), takes the target closure, runs Tarjan for SCCs (diagnostics only), and defines memo
identity as the complete argument tuple. Fails closed only on first-class Cell references,
`*args`/`**kwargs`, unknown keywords, missing required args. pandas/`np`/comprehensions/`raise`
are recorded as notes, not blockers.

`fast_recursive_python.py` emits one `_calc_<cell>` + one memoizing `fr_<cell>` per Cell;
`fast_recursive_cython.py` is 20 lines that take that output and rewrite `def _calc_`/`def fr_`
to `cdef object ...`.

**This part delivers no speedup and does not claim to.** Verified locally: the emitted reference
runtime runs at ~1.0x the exported package (WOL 1.028 s vs 1.058 s; VA 3.348 s vs 3.345 s).
Its value is the feasibility claim: nothing about recursive execution requires VA's three-stage
schedule, and program discovery no longer depends on which policies happened to be traced.

**Nothing in the package connects this frontend to section 2's numbers.** The author says so
("structural proof rather than the performance implementation"), but the comment orders the
numbers before the caveat.

### 5. The `exact4` / `grouped_step2` lookup vocabulary

`helpers/modelx_fast_lookup.py` (stdlib only): `ExactTable`/`StepTable`/`GroupedStepTable` +
`exactN`/`step1`/`grouped_stepN`/`column_value`, built once outside hot Cells.
`helpers/native_lookup_helpers.pxd`: two `noexcept nogil` binary searches.
This is the productized form of section 1's hand-written `patch_providers`, and the real ask of
the whole comment: a small semantic ABI a native backend can recognize.

## Independent verification (2026-09-08, py313, Cython 3.2.4)

- The graph census table reproduces **exactly** — 35/68/63/1/1/4, 57/127/114/2/6/7,
  52/126/110/2/6/1, 102/223/209/2/8/6, 169/492/454/3/7/53, zero blockers for all five.
  VA's 53-Cell SCC and the trace-independent `phi_glwb_vix` both confirmed.
- `tests/test_fast_recursive_graph.py` — 6/6 pass.
- `validate_fast_recursive_python.py` — Term 8/8, WOL 7/7, ULSG 4/4, VA 9/9, all
  `max_abs_error == 0.0` (bit-exact, not just within 1e-12).
- ULSG modelx-cython build failure reproduces and has a one-line fix (below).

## Benchmark-model caveat

Only `BasicTerm_S` is lifelib, and only it has a real portfolio (10,000 policies).
`Term_UK_A` / `WOL_UK_S` / `ULSG_US_S` / `VA_US_S` are custom models bundled in the zip, with
**8 / 7 / 4 / 9 policies**. Their docstrings carry `[S1][S2][S3]` spec-citation markers, i.e.
they were written from specification documents (LLM-assisted). They are excellent *stress tests
for the graph* — VA's 169 Cells / 492 call sites / 53-Cell SCC is far beyond anything in lifelib.
They are weak *performance baselines*: at 4–9 policies the per-policy cost runs 78 ms (WOL) to
258 ms (VA) under current modelx-cython, and those totals are dominated by exactly the repeated
pandas MultiIndex lookups that section 1 optimizes away.

## Concrete, actionable for modelx-cython

1. **`cpow` bug — verified reproducible.** ULSG's build dies on
   `max((1 + self.crediting_rate_ann(t)) ** (1 / 12) - 1, self.guar_rate_mth())` with
   `complex types are unordered`. With Cython 3's default `cpow=False`, `double ** float` is
   inferred as possibly-complex, and `max()` then compares complex values.
   `modelx_cython/cli.py:579` currently emits only
   `compiler_directives={"freethreading_compatible": True}`.
   Adding `"cpow": True` fixes it — confirmed here with a minimal `cdef double` repro:
   fails without, transpiles with. Any model using fractional powers of a Cell value hits this.
2. **Wrapper merge** — inline `_f_cell` into `cell()` in the exported package. General,
   ~1.12x–1.32x in pure Python. Probably smaller once cythonized, since the wrapper call is
   already cheap there.
3. **`model_point` as dict** rather than a pandas Series. General.
4. **Prepared-lookup Refs** — the open design question: should modelx offer a way to declare
   "this Ref is an exact / step / grouped-step table" so both export and mx2cy can drop pandas
   from the hot path?

## Things worth pushing back on / asking about

- The 35.9x headline and the new compiler are not the same system. Ask for one end-to-end
  artifact: static graph -> typed lowering -> measured, on BasicTerm_S at 10,000 policies.
- Global `_cache`/`_epoch` in the WOL/ULSG generated sources is incompatible with free threading.
  BasicTerm's stack-allocated `RecContext` is the right shape; ask whether the generator can be
  moved to that.
- All fast-path numbers assume whole-portfolio, output-only evaluation. modelx's interactive
  value (inspect any intermediate Cell, `.series`, dependency tracing) is not addressed. The
  dev74 memo dicts do preserve it; the dev73 typed artifacts do not.
- Nothing here is a patch against modelx-cython. `FAST_RECURSIVE_GRAPH_IMPLEMENTATION.patch`
  (79 KB) is a diff inside the author's own compiler tree, not against this repo.

## Reproducing

```bash
cd dev74/modelx_recursive_optimization_like_for_like
python -m unittest discover -s tests -v
python benchmark_scripts/audit_fast_recursive_graph.py
python benchmark_scripts/validate_fast_recursive_python.py WOL_UK_S
```

`fast_recursive_graph.py` only needs the stdlib. The validation harnesses need pandas/numpy and
the bundled `generated_exports/`, but not modelx.
