# Proposal: Semantic Recurrence Optimization for modelx-cython

## The idea in simple terms

`modelx-cython` already makes modelx calculations much faster by compiling exported Cells and replacing Python-heavy caches with typed native structures. The proposed optimization adds one more tier before that: when a group of Cells is provably a time recurrence, compile the **whole recurrence as one loop** instead of compiling thousands of individual `Cell(t)` calls.

A formula can remain readable and recursive:

```python
def pols_if(t):
    if t == 0:
        return pols_if_init()
    return pols_if(t-1) - pols_death(t-1) - pols_lapse(t-1) - pols_maturity(t)
```

The compiler recognizes the recurrence and generates the equivalent native structure:

```text
state = initial_state
for t in projection_periods:
    calculate same-period values
    accumulate PV/reduction outputs
    update rolling state
```

This removes most function-call and per-time cache overhead. Independent model points are then distributed across CPU cores with OpenMP.

The proposal is **not to replace modelx-cython**. It is to add an optimizer tier:

```text
modelx model / exported semantic IR
           |
           v
   semantic optimizer
   recurrence + reductions
           |
      supported? ---------------- no ----------------+
           |                                        |
          yes                                       v
           |                             current modelx-cython
           v                             typed Cell/cache lowering
   fused Cython scan                                |
   rolling state + OpenMP                           |
           +--------------------+-------------------+
                                v
                      compatible exported package
                                |
                                v
                         Python fallback
```

## API compatibility

The prototype intentionally follows the existing workflow:

```python
from modelx_native import export_model
compiled = export_model(model, "BasicTerm_S_semantic", sample="sample.py", spec="spec.py")
```

and preserves the ordinary application-facing API:

```python
from BasicTerm_S_semantic import BasicTerm_S
pv = BasicTerm_S.Projection[1].pv_net_cf()
```

Suggested upstream shape:

```bash
model.export("BasicTerm_S_nomx", include_ir=True)   # proposed export option
mx2cy BasicTerm_S_nomx --optimizer auto --sample sample.py --spec spec.py
```

with `--optimizer cells|semantic|auto`. `auto` would use semantic lowering where it can prove correctness, then fall back to the existing modelx-cython compiler, then to exported Python.

## What the two semantic benchmark columns mean

**Semantic OpenMP, 9 cores** is the raw batch execution path. One Python call launches the generated native kernel over the full portfolio. It measures the native calculation with minimal compatibility overhead.

**Drop-in semantic API** uses the same OpenMP kernel but exposes results through the familiar modelx-export API such as `Projection[i].pv_net_cf()`. The package uses lightweight proxies rather than constructing full exported ItemSpaces. Its extra time is therefore Python API/proxy iteration, not a different calculation engine.

## Same-machine benchmark

10,000 model points, `pv_net_cf()`, Python 3.13.5, modelx 0.32.0, modelx-cython 0.0.9, Cython 3.2.4, GCC 14.2, AMD EPYC host with 9 exposed cores.

| Model | Exported Python | modelx-cython | Semantic 1 core | Semantic OpenMP | Drop-in semantic |
|---|---:|---:|---:|---:|---:|
| BasicTerm_S | 21.569 s | 9.408 s | 223.2 ms | **40.6 ms** | 47.0 ms |
| BasicTerm_SE | 18.998 s | 8.736 s | 71.3 ms | **15.2 ms** | 23.7 ms |
| BasicTerm_SC | 15.168 s | 0.863 s | 222.2 ms | **40.4 ms** | 46.0 ms |

Across these models, the geometric-mean speed-up versus modelx-cython is **27.2x single-core** and **141.8x with 9-core OpenMP**. The single-core result is important because it isolates graph transformation from multicore scaling.

Peak RSS for the semantic OpenMP paths is about **124-125 MB**, compared with approximately **593 MB to 1.1 GB** for modelx-cython in these tests.

## What was learned from modelx-cython

The prototype now follows several existing modelx-cython ideas rather than inventing a parallel ecosystem:

- preserve the exported model API;
- retain `sample.py` for workload selection and runtime type/shape hints;
- retain `spec.py` for explicit overrides;
- separate translation from native compilation;
- keep current typed Cell/cache compilation as the generic fallback;
- keep exported Python as the ultimate compatibility fallback.

A useful finding from `BasicTerm_SE`: a `t=241` modelx-cython cache-size spec compiled successfully but failed at runtime because future business required a maximum projection length of 277. Scan-lowered Cells do not need a fixed time cache, while generic Cell compilation can continue to use validated cache bounds.

## Correctness and limits

The full 10,000-point vectors were compared against exported Python. BasicTerm_S and BasicTerm_SC pass `2e-12` absolute/relative tolerance. BasicTerm_SE requires `5e-12`; its largest observed discrepancy is consistent with changed floating-point evaluation order after scan fusion. Portfolio totals agree at displayed precision.

For an upstream implementation I would add strict floating-point mode, automatic sampled reference validation, a compiler diagnostic showing lowered/fallback regions, deterministic reductions, and artifact hashes based on formulas/IR, types/shapes, compiler version and flags.

The semantic optimizer should remain conservative. Unsupported dynamic Python should fall through to the existing modelx-cython path instead of causing the whole model to fail.

## Proposed next step

The smallest upstream experiment would be:

1. let `model.export()` optionally emit a compact semantic manifest/IR beside the exported package;
2. add `--optimizer cells|semantic|auto` to `mx2cy`;
3. support forward time recurrences and PV/reduction fusion for a deliberately small subset;
4. fall back to current modelx-cython for every unsupported subgraph;
5. use the lifelib regression models as correctness/performance gates.

This keeps modelx Cells as the readable source of truth, keeps the existing modelx-cython workflow and compatibility advantages, and gives recurrence-heavy actuarial models a substantially higher optimization ceiling.
