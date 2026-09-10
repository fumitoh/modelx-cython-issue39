# modelx recursive optimization: corrected like-for-like benchmark package

This package accompanies the corrected benchmark rerun of pure-Python `model.export()`, current modelx-cython, the fast-recursive Cython prototype, and compact sequential references.

## What changed from the earlier package

The earlier native table mixed complete heterogeneous policy sets with representative-policy replicated native kernels. This package removes that ambiguity. Every headline runtime in `results/LIKE_FOR_LIKE_RESULTS.csv` uses the complete shipped policy set for the product.

Representative-policy-only sequential figures are intentionally **not** in the corrected headline table.

## Headline policy populations

- BasicTerm_S: 10,000 distinct policies
- Term_UK_A: 8/8 shipped policies
- WOL_UK_S: 7/7
- ULSG_US_S: 4/4
- VA_US_S: 9/9

See `RESULTS.md` for methodology, corrected timings, build status and correctness gates.

## Contents

- `RESULTS.md` - detailed corrected benchmark report.
- `GITHUB_ISSUE_COMMENT.md` - ready-to-post GitHub summary.
- `results/` - normalized execution/build/correctness tables.
- `raw_evidence/` - fresh benchmark JSON/JSONL evidence.
- `helpers/` - pure-Python lookup helpers, native Cython lookup primitives, and helper tests.
- `MODEL_SYNTAX_GUIDE.md` - source syntax intended to serve both pure-Python and native execution.
- `compiler/modelx_graph/` - dev73 benchmark compiler snapshot plus the dev74 static fast-recursive graph extension.
- `benchmark_scripts/` - exact scripts used for export, modelx-cython builds, full-domain compilation and timing.
- `native_sources/` - successful full-domain fast-recursive sources and the BasicTerm compact sequential comparator, plus normalized input/reference snapshots.
- `generated_exports/` - standalone `model.export()` packages and small input files used by the pure-Python rerun.
- `modelx_cython_generated/` - generated Python/Cython source snapshots and build logs, with compiled binaries/C files removed.
- `failures/` - full-domain backend failure evidence for rows where no timing is reported.

## Dependencies deliberately not bundled

The package does **not** vendor the modelx, modelx-cython, lifelib, NumPy, pandas or Cython source trees. It also contains no `.so`, generated `.c`, object files, or Python bytecode.

The generated pure-Python export packages are included because they are benchmark artifacts, not copies of the source libraries.

## Benchmark environment

- Python 3.13.5
- Cython 3.2.4
- NumPy 2.3.5
- pandas 2.2.3
- GCC 14.2.0
- Linux 6.18.35 x86-64
- native prototypes: `-O2`, one execution thread

## Important interpretation

A missing native timing means the full-domain build/coverage contract did not complete; it must not be replaced by an older representative-policy number. The corresponding diagnostic is retained under `failures/`.

The fast-recursive WOL artifact is compiled from policies 1, 5 and 6 and then validated over all seven policies. ULSG uses policies 1, 3 and 4 and validates all four. The compilation sample does not define the benchmark population.

## dev74 fast-recursive graph extension

This package now also contains the next implementation stage described in `FAST_RECURSIVE_GRAPH_IMPLEMENTATION.md` and `FAST_RECURSIVE_GRAPH_RESULTS.md`.

The compiler version is bumped to `0.23.0.dev74` for this extension. The corrected performance numbers under `results/LIKE_FOR_LIKE_*` remain the previously rerun dev73-lineage benchmark; dev74 changes graph construction, not those historical timing rows.

New dev74 files:

- `compiler/modelx_graph/fast_recursive_graph.py` — static exported-source recursive IR;
- `compiler/modelx_graph/fast_recursive_python.py` — executable recursive reference emitter;
- `benchmark_scripts/audit_fast_recursive_graph.py` — five-product graph census;
- `benchmark_scripts/validate_fast_recursive_python.py` — reference-runtime parity harness;
- `tests/test_fast_recursive_graph.py` — structural and executable acceptance tests;
- `fast_recursive_graph/` — complete per-product graph manifests;
- `fast_recursive_python/` — generated direct-recursive Python artifacts;
- `results/FAST_RECURSIVE_GRAPH_COVERAGE.*` and `results/FAST_RECURSIVE_PYTHON_VALIDATION.jsonl` — evidence.

For Term/WOL/ULSG/VA the small CSV inputs required by the bundled generated exports are now included beside those exports, so the new reference-runtime validation is self-contained apart from normal Python package dependencies.

The dev74 graph stage also includes `fast_recursive_cython_object/`: generated Cython object-mode recursive modules for all five products. These are an ABI/graph proof, not the final numeric performance backend. Internal Cell functions are `cdef object` and call each other directly; provider/table operations intentionally remain Python-object operations. Build products are deliberately excluded from the ZIP and can be reproduced with the bundled `setup.py`.
