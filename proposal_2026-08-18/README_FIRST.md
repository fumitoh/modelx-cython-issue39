# Read first

This compact package is intended to be sent to the modelx/modelx-cython maintainer.

Start with `MODELX_SEMANTIC_OPTIMIZER_PROPOSAL.docx` (or `PROPOSAL.md`).

Contents:
- `MODELX_SEMANTIC_OPTIMIZER_PROPOSAL.docx` - concise maintainer-facing proposal.
- `PROPOSAL.md` - plain-text equivalent.
- `MAINTAINER_MESSAGE.txt` - short email/message draft.
- `benchmark_summary.csv` / `.json` - same-machine benchmark data.
- `modelx_semantic_compiler-0.3.0-py3-none-any.whl` - prototype package.
- `source/` - compact source and API regression tests.

The proposal does not suggest replacing modelx-cython. It proposes adding semantic recurrence/reduction lowering as an optimization tier with the existing modelx-cython compiler as fallback.
