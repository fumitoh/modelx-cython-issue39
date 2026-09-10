from __future__ import annotations

import ast
import copy
import hashlib
import inspect
import math
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Sequence

import numpy as np
import pandas as pd

from .trace import TraceCapture, VariantKey, VariantTrace, CellSchema
from .trace import capture_trace
from .ir import build_graph_ir
from .template_ir import (
    ExecutableGraph, ExecutablePureMapSpec, build_executable_graph,
    prove_executable_pure_maps, TemplateError,
)
from .domain_graph import DomainGraph, ValueSemanticsEvidence, build_shadow_domain_graph, classify_source_value_semantics
from .canonical_semantic_graph import (
    CanonicalLoopTopologyFact, RecoveredLoopTopologyFact, CanonicalSemanticGraph,
    freeze_graph_ir_loop_topology, freeze_recovered_loop_topology,
    build_canonical_semantic_graph,
)
from .canonical_schedule import (
    CanonicalComponentScheduleAnalysis, CanonicalExecutionSchedule,
    analyze_canonical_component_schedule, build_canonical_execution_schedule,
)
from .stage_execution_plan import StageExecutionPlan, build_stage_execution_plan
from .stage_storage_plan import StageStoragePlan, build_stage_storage_plan
from .safety import validate_formula_control_flow, SemanticSafetyError
from .program_inputs import (
    NormalizedTableAxis, NormalizedTableInput, NormalizedPointRowSource,
    NormalizedLookup1D,
)
from .invocation import OutputInvocation, RunDomain, ResultDomain
from .normalized_operator import NormalizedOperator
from .program_semantics import (
    GuardSpec, StaticScalarFact, ValidatedStaticFact, FiniteDomainFact, FixedCoordinateFact,
    CoordinateRecurrenceDomainFact, RuntimeScalarHelperFact, SourceBackedScheduledFact,
    StepLookupDomainFact, ProgramSemanticError,
    normalize_formula_guards,
)
from .modelx_cython_formula_engine import unroll_finite_literal_generators
from .affine_domain import (
    AffineIntForm, AffineRangeConstraint, affine_bounds_under_range,
)


class FrontendError(RuntimeError):
    pass


RUNTIME_SCALAR_HELPER_EXPANSION_LIMIT = 20000


@dataclass(frozen=True)
class HierarchicalItemSpaceParameterBinding:
    """Structural proof that a child Space Cells value inherits owner coordinates.

    The binding is deliberately about modelx hierarchy identity, not identifier
    spelling.  ``parameter_names`` are declared by the selected RunDomain Space and
    become concrete references only on the corresponding ItemSpace descendant.
    """

    ref_name: str
    cell_name: str
    owner_space_fullname: str
    child_space_fullname: str
    parameter_names: tuple[str, ...]
    parameter_positions: tuple[int, ...]
    dependency_cells: tuple[str, ...] = ()


@dataclass
class InputSpec:
    key: str
    dtype: str
    ndim: int
    scope: str  # point | global
    getter: Callable[[Sequence[Any]], Any]
    description: str
    domain_guard: Callable[[], str | None] | None = None
    domain_token: str | None = None
    expected_shape: tuple[int, ...] | None = None
    normalized_table: NormalizedTableInput | None = None
    # Optional shared-batch path.  Multiple inputs may reuse one exact indexer
    # calculation inside a single raw_inputs() call without introducing a
    # persistent cache or changing invalidation semantics.
    fast_getter: Callable[[Sequence[Any], dict[Any, Any]], Any] | None = None
    point_row_source: NormalizedPointRowSource | None = None
    point_field: Any | None = None
    enum_labels: tuple[str, ...] | None = None
    normalized_lookup_1d: NormalizedLookup1D | None = None
    lookup_1d_role: str | None = None
    hierarchical_itemspace_binding: HierarchicalItemSpaceParameterBinding | None = None


@dataclass(frozen=True)
class PointRowBinding:
    """Preparation-time binding for a normalized point-row table source."""

    cell_name: str
    semantic: NormalizedPointRowSource
    provider: Callable[[], pd.DataFrame] = field(compare=False, repr=False)




@dataclass(frozen=True)
class ValidatedEnumCell:
    """Preparation-time description of a validated categorical selector Cell."""

    field: str
    allowed_values: tuple[str, ...]


@dataclass(frozen=True)
class ValidatedPointScalarCell:
    """Guard-bearing numeric/bool selector safely specialized by exact value.

    The source value comes directly from one model-point field (optionally through
    bool/int/float).  Specialization is allowed only when substituting the proven
    value makes every guard predicate in the selector unconditionally false.
    Runtime input validation then requires the field to remain exactly that value.
    """

    field: str
    cast: str | None



@dataclass(frozen=True)
class _IntDomain:
    """Inclusive finite integer interval used only for compile-time source proofs."""

    lo: int
    hi: int

    def __post_init__(self):
        if int(self.lo) > int(self.hi):
            raise ValueError("empty integer domain")

    def union(self, other: "_IntDomain") -> "_IntDomain":
        return _IntDomain(min(int(self.lo), int(other.lo)), max(int(self.hi), int(other.hi)))

    def intersect(self, lo: int | None = None, hi: int | None = None) -> "_IntDomain | None":
        left = int(self.lo) if lo is None else max(int(self.lo), int(lo))
        right = int(self.hi) if hi is None else min(int(self.hi), int(hi))
        return None if left > right else _IntDomain(left, right)

    @property
    def singleton(self) -> int | None:
        return int(self.lo) if int(self.lo) == int(self.hi) else None


@dataclass
class ReductionSpec:
    init: ast.AST
    target: str
    loop_var: str
    range_args: tuple[ast.AST, ...]
    body_expr: ast.AST
    filters: tuple[ast.AST, ...] = ()


@dataclass
class CanonicalVariant:
    uid: str
    source_name: str
    source_fullname: str
    dtype: str
    role: str  # coordinate | scalar | reduction | vector
    function: ast.FunctionDef | None
    reduction: ReductionSpec | None = None
    time_param_source: str | None = None
    aux_values: tuple[Any, ...] = ()
    guards: tuple[GuardSpec, ...] = ()


@dataclass
class CanonicalModel:
    model: Any
    space: Any
    output_name: str
    output_uid: str
    output_invocation: OutputInvocation
    run_domain: RunDomain
    result_domain: ResultDomain
    sample_keys: tuple[Any, ...]
    run_keys: tuple[Any, ...]
    trace: TraceCapture
    variants: dict[str, CanonicalVariant]
    inputs: dict[str, InputSpec]
    executable: ExecutableGraph | None = None
    domain_graph_shadow: DomainGraph | None = None
    canonical_semantic_graph: CanonicalSemanticGraph | None = None
    canonical_schedule_analysis: CanonicalComponentScheduleAnalysis | None = None
    canonical_execution_schedule: CanonicalExecutionSchedule | None = None
    stage_execution_plan: StageExecutionPlan | None = None
    stage_storage_plan: StageStoragePlan | None = None
    normalized_operators: tuple[NormalizedOperator, ...] = ()
    diagnostics: list[str] = field(default_factory=list)
    static_facts: tuple[StaticScalarFact, ...] = ()
    validated_static_facts: tuple[ValidatedStaticFact, ...] = ()
    finite_domain_facts: tuple[FiniteDomainFact, ...] = ()
    fixed_coordinate_facts: tuple[FixedCoordinateFact, ...] = ()
    coordinate_recurrence_facts: tuple[CoordinateRecurrenceDomainFact, ...] = ()
    runtime_scalar_helper_facts: tuple[RuntimeScalarHelperFact, ...] = ()
    source_backed_scheduled_facts: tuple[SourceBackedScheduledFact, ...] = ()
    step_lookup_domain_facts: tuple[StepLookupDomainFact, ...] = ()

    def raw_inputs(self, keys: Sequence[Any] | None = None, overrides: dict[str, Any] | None = None) -> dict[str, Any]:
        keys = tuple(self.run_keys if keys is None else keys)
        overrides = overrides or {}
        unknown = set(overrides) - set(self.inputs)
        if unknown:
            raise FrontendError(f"unknown input override keys: {sorted(unknown)!r}")
        # Per-call only.  This lets related getters share exact lookup/index work
        # without creating a second cache-invalidation system.
        batch_cache: dict[Any, Any] = {}
        out: dict[str, Any] = {}
        for name, spec in self.inputs.items():
            if name in overrides:
                out[name] = overrides[name]
            elif spec.fast_getter is not None:
                out[name] = spec.fast_getter(keys, batch_cache)
            else:
                out[name] = spec.getter(keys)
        return out

    def coerce_inputs(self, values: dict[str, Any]) -> dict[str, Any]:
        unknown = set(values) - set(self.inputs)
        missing = set(self.inputs) - set(values)
        if unknown or missing:
            raise FrontendError(f"input value keys mismatch; missing={sorted(missing)!r} unknown={sorted(unknown)!r}")
        out = {}
        for name, spec in self.inputs.items():
            value = values[name]
            if spec.ndim == 0:
                if spec.dtype == "int64":
                    out[name] = int(value)
                elif spec.dtype == "bool":
                    out[name] = bool(value)
                else:
                    out[name] = float(value)
            else:
                dt = np.int64 if spec.dtype == "int64" else np.bool_ if spec.dtype == "bool" else np.float64
                arr = np.ascontiguousarray(np.asarray(value, dtype=dt))
                if spec.enum_labels is not None:
                    # -1 is the reserved finite-enum ``other/missing`` sentinel.
                    # Exact table selectors validate it before indexing; equality
                    # dispatch naturally falls through to the source ``else`` path.
                    if np.any(arr < -1) or np.any(arr >= len(spec.enum_labels)):
                        raise FrontendError(
                            f"enum input {name!r} contains a code outside [-1, {len(spec.enum_labels)})"
                        )
                out[name] = arr
        for fact in self.validated_static_facts:
            spec = self.inputs.get(fact.validation_input_key)
            if spec is None:
                raise FrontendError(
                    f"validated static fact {fact.source_name!r} has no validation input"
                )
            arr = np.asarray(out[fact.validation_input_key])
            if spec.enum_labels is not None:
                try:
                    expected = spec.enum_labels.index(fact.value)
                except ValueError as exc:
                    raise FrontendError(
                        f"validated static fact {fact.source_name!r} value is outside its enum domain"
                    ) from exc
                kind = "enum"
            else:
                expected = int(fact.value) if spec.dtype == "int64" else bool(fact.value) if spec.dtype == "bool" else float(fact.value)
                kind = "scalar"
            if np.any(arr != expected):
                raise FrontendError(
                    f"validated static {kind} {fact.source_name!r} changed from proven value {fact.value!r}"
                )
        return out

    def bind_inputs(self, keys: Sequence[Any] | None = None, overrides: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.coerce_inputs(self.raw_inputs(keys, overrides))

@dataclass(frozen=True)
class CanonicalProofSnapshot:
    """Immutable proof bundle at the canonical/pre-scheduler boundary.

    V02347 strengthens the snapshot so an observational canonical semantic graph
    can be built without first constructing ``ExecutableGraph``.  The object still
    grants no execution permission: source semantics, PureMap proofs and loop
    topology are evidence only until a later scheduler authorizes them.
    """

    output_uid: str
    run_key_count: int
    variants: dict[str, CanonicalVariant] = field(compare=False, repr=False)
    formula_hash: str = ""
    structural_hash: str = ""
    coordinate_domains: tuple[tuple[str, int, int], ...] = ()
    static_facts: tuple[StaticScalarFact, ...] = ()
    validated_static_facts: tuple[ValidatedStaticFact, ...] = ()
    finite_domain_facts: tuple[FiniteDomainFact, ...] = ()
    fixed_coordinate_facts: tuple[FixedCoordinateFact, ...] = ()
    coordinate_recurrence_facts: tuple[CoordinateRecurrenceDomainFact, ...] = ()
    runtime_scalar_helper_facts: tuple[RuntimeScalarHelperFact, ...] = ()
    source_backed_scheduled_facts: tuple[SourceBackedScheduledFact, ...] = ()
    step_lookup_domain_facts: tuple[StepLookupDomainFact, ...] = ()
    normalized_operators: tuple[NormalizedOperator, ...] = ()
    source_value_semantics: tuple[ValueSemanticsEvidence, ...] = ()
    pure_map_specs: tuple[ExecutablePureMapSpec, ...] = ()
    loop_topology_facts: tuple[CanonicalLoopTopologyFact, ...] = ()
    recovered_loop_topology_facts: tuple[RecoveredLoopTopologyFact, ...] = ()
    scheduler_evidence_status: str = "complete_without_recovered_evidence"
    executable_schedule_built: bool = False
    failure_reason: str | None = None

    def _copy(self, **changes: Any) -> "CanonicalProofSnapshot":
        data = {
            "output_uid": self.output_uid,
            "run_key_count": self.run_key_count,
            "variants": self.variants,
            "formula_hash": self.formula_hash,
            "structural_hash": self.structural_hash,
            "coordinate_domains": self.coordinate_domains,
            "static_facts": self.static_facts,
            "validated_static_facts": self.validated_static_facts,
            "finite_domain_facts": self.finite_domain_facts,
            "fixed_coordinate_facts": self.fixed_coordinate_facts,
            "coordinate_recurrence_facts": self.coordinate_recurrence_facts,
            "runtime_scalar_helper_facts": self.runtime_scalar_helper_facts,
            "source_backed_scheduled_facts": self.source_backed_scheduled_facts,
            "step_lookup_domain_facts": self.step_lookup_domain_facts,
            "normalized_operators": self.normalized_operators,
            "source_value_semantics": self.source_value_semantics,
            "pure_map_specs": self.pure_map_specs,
            "loop_topology_facts": self.loop_topology_facts,
            "recovered_loop_topology_facts": self.recovered_loop_topology_facts,
            "scheduler_evidence_status": self.scheduler_evidence_status,
            "executable_schedule_built": self.executable_schedule_built,
            "failure_reason": self.failure_reason,
        }
        data.update(changes)
        return CanonicalProofSnapshot(**data)

    def with_failure(self, reason: str) -> "CanonicalProofSnapshot":
        return self._copy(failure_reason=str(reason))

    def with_executable_schedule(self) -> "CanonicalProofSnapshot":
        return self._copy(executable_schedule_built=True)

    def with_recovered_loop_evidence(self, evidence: Any | None) -> "CanonicalProofSnapshot":
        facts = freeze_recovered_loop_topology(evidence)
        status = (
            "complete_with_recovered_evidence" if facts
            else "complete_without_recovered_evidence"
        )
        return self._copy(
            recovered_loop_topology_facts=facts,
            scheduler_evidence_status=status,
        )

    def manifest(self) -> dict[str, Any]:
        return {
            "schema": "modelx_graph.canonical_proof_snapshot.v3",
            "output_uid": self.output_uid,
            "run_key_count": int(self.run_key_count),
            "formula_hash": self.formula_hash,
            "structural_hash": self.structural_hash,
            "variant_count": len(self.variants),
            "variants": [
                {
                    "uid": uid,
                    "source_name": cv.source_name,
                    "source_fullname": cv.source_fullname,
                    "role": cv.role,
                    "dtype": cv.dtype,
                    "time_param_source": cv.time_param_source,
                    "aux_values": list(cv.aux_values),
                }
                for uid, cv in sorted(self.variants.items())
            ],
            "coordinate_domains": [
                {"uid": uid, "lo": lo, "hi": hi}
                for uid, lo, hi in self.coordinate_domains
            ],
            "static_facts": [x.manifest() for x in self.static_facts],
            "validated_static_facts": [x.manifest() for x in self.validated_static_facts],
            "finite_domain_facts": [x.manifest() for x in self.finite_domain_facts],
            "fixed_coordinate_facts": [x.manifest() for x in self.fixed_coordinate_facts],
            "coordinate_recurrence_facts": [x.manifest() for x in self.coordinate_recurrence_facts],
            "runtime_scalar_helper_facts": [x.manifest() for x in self.runtime_scalar_helper_facts],
            "source_backed_scheduled_facts": [x.manifest() for x in self.source_backed_scheduled_facts],
            "step_lookup_domain_facts": [x.manifest() for x in self.step_lookup_domain_facts],
            "normalized_operators": [x.manifest() for x in self.normalized_operators],
            "source_value_semantics": [x.manifest() for x in self.source_value_semantics],
            "pure_map_specs": [x.manifest() for x in self.pure_map_specs],
            "loop_topology_facts": [x.manifest() for x in self.loop_topology_facts],
            "recovered_loop_topology_facts": [x.manifest() for x in self.recovered_loop_topology_facts],
            "scheduler_evidence_status": self.scheduler_evidence_status,
            "executable_schedule_built": bool(self.executable_schedule_built),
            "failure_reason": self.failure_reason,
        }


class _Substitute(ast.NodeTransformer):
    def __init__(self, mapping: dict[str, ast.AST]):
        self.mapping = mapping

    def visit_Name(self, node: ast.Name):
        if isinstance(node.ctx, ast.Load) and node.id in self.mapping:
            return ast.copy_location(copy.deepcopy(self.mapping[node.id]), node)
        return node


class _ConservativeFolder(ast.NodeTransformer):
    """Fold only expressions made entirely from Python literals.

    The compiler never uses model-specific names or values to decide a branch.
    """
    def visit_UnaryOp(self, node: ast.UnaryOp):
        node = self.generic_visit(node)
        if isinstance(node.op, ast.Not) and isinstance(node.operand, ast.Constant):
            return ast.copy_location(ast.Constant(not bool(node.operand.value)), node)
        if isinstance(node.operand, ast.Constant) and isinstance(node.op, (ast.UAdd, ast.USub)):
            try:
                value = +node.operand.value if isinstance(node.op, ast.UAdd) else -node.operand.value
                return ast.copy_location(ast.Constant(value), node)
            except Exception:
                pass
        return node

    def visit_BoolOp(self, node: ast.BoolOp):
        node = self.generic_visit(node)
        values = list(node.values)
        if isinstance(node.op, ast.And):
            for value in values:
                if isinstance(value, ast.Constant) and not bool(value.value):
                    return ast.copy_location(ast.Constant(False), node)
            values = [v for v in values if not (isinstance(v, ast.Constant) and bool(v.value))]
        elif isinstance(node.op, ast.Or):
            for value in values:
                if isinstance(value, ast.Constant) and bool(value.value):
                    return ast.copy_location(ast.Constant(True), node)
            values = [v for v in values if not (isinstance(v, ast.Constant) and not bool(v.value))]
        if not values:
            return ast.copy_location(ast.Constant(isinstance(node.op, ast.And)), node)
        if len(values) == 1:
            return values[0]
        node.values = values
        return node
    def visit_If(self, node: ast.If):
        node = self.generic_visit(node)
        try:
            test = ast.literal_eval(node.test)
        except Exception:
            return node
        return node.body if bool(test) else node.orelse

    def visit_IfExp(self, node: ast.IfExp):
        node = self.generic_visit(node)
        try:
            test = ast.literal_eval(node.test)
        except Exception:
            return node
        return node.body if bool(test) else node.orelse

    def visit_Compare(self, node: ast.Compare):
        node = self.generic_visit(node)
        try:
            expr = ast.Expression(node)
            val = eval(compile(ast.fix_missing_locations(expr), "<const>", "eval"), {"__builtins__": {}}, {})
        except Exception:
            return node
        return ast.copy_location(ast.Constant(bool(val)), node)



class _CoordinateConstantFolder(ast.NodeTransformer):
    """Fold literal arithmetic used only for coordinate specialization.

    This deliberately does not run over general numerical formulas.  It is a small
    proof engine for index/coordinate expressions after already-proven static facts
    have been substituted.
    """

    def visit_BinOp(self, node: ast.BinOp):
        node = self.generic_visit(node)
        if not (isinstance(node.left, ast.Constant) and isinstance(node.right, ast.Constant)):
            return node
        try:
            value = eval(
                compile(ast.fix_missing_locations(ast.Expression(copy.deepcopy(node))), "<coordinate-const>", "eval"),
                {"__builtins__": {}}, {},
            )
        except Exception:
            return node
        if isinstance(value, np.generic):
            value = value.item()
        if isinstance(value, (bool, int, float, str)):
            return ast.copy_location(ast.Constant(value=value), node)
        return node

    def visit_UnaryOp(self, node: ast.UnaryOp):
        node = self.generic_visit(node)
        if not isinstance(node.operand, ast.Constant):
            return node
        try:
            value = eval(
                compile(ast.fix_missing_locations(ast.Expression(copy.deepcopy(node))), "<coordinate-const>", "eval"),
                {"__builtins__": {}}, {},
            )
        except Exception:
            return node
        if isinstance(value, np.generic):
            value = value.item()
        if isinstance(value, (bool, int, float, str)):
            return ast.copy_location(ast.Constant(value=value), node)
        return node

    def visit_Call(self, node: ast.Call):
        node = self.generic_visit(node)
        if not (
            isinstance(node.func, ast.Name) and node.func.id in {"int", "float"}
            and len(node.args) == 1 and not node.keywords and isinstance(node.args[0], ast.Constant)
        ):
            return node
        try:
            value = int(node.args[0].value) if node.func.id == "int" else float(node.args[0].value)
        except Exception:
            return node
        return ast.copy_location(ast.Constant(value=value), node)



def _strip_docstring(fn: ast.FunctionDef) -> ast.FunctionDef:
    if fn.body and isinstance(fn.body[0], ast.Expr) and isinstance(fn.body[0].value, ast.Constant) and isinstance(fn.body[0].value.value, str):
        fn.body = fn.body[1:]
    return fn


def _prune_source_unreachable_tails(fn: ast.FunctionDef) -> ast.FunctionDef:
    """Remove statements unreachable by Python source control flow.

    This is deliberately weaker than general control-flow simplification.  It
    understands only unconditional ``return``/``raise`` termination and the case
    where both branches of an ``if`` terminate.  In particular it never uses
    representative trace absence as evidence.  The pass runs *after* literal
    auxiliary/static substitution, so a specialized branch folded to a direct
    return also cuts the source tail that can no longer execute.
    """

    def block(stmts: list[ast.stmt]) -> tuple[list[ast.stmt], bool]:
        out: list[ast.stmt] = []
        terminated = False
        for original in stmts:
            if terminated:
                break
            st = copy.deepcopy(original)
            if isinstance(st, ast.If):
                st.body, body_term = block(list(st.body))
                st.orelse, else_term = block(list(st.orelse))
                out.append(st)
                # An if without an else always has a fall-through path.
                terminated = bool(st.orelse) and body_term and else_term
                continue
            out.append(st)
            if isinstance(st, (ast.Return, ast.Raise)):
                terminated = True
        return out, terminated

    out = copy.deepcopy(fn)
    out.body, _ = block(list(out.body))
    return ast.fix_missing_locations(out)


def _literal(node: ast.AST):
    try:
        return ast.literal_eval(node)
    except Exception as exc:
        raise FrontendError(f"non-time specialization argument is not a literal: {ast.unparse(node)}") from exc


def _safe_numeric_axis(labels: Iterable[Any]) -> tuple[list[int], int, int]:
    vals = []
    for x in labels:
        if isinstance(x, str):
            try:
                x = int(x)
            except Exception as exc:
                raise FrontendError(f"non-numeric table label {x!r} is not yet supported natively") from exc
        if not isinstance(x, (int, np.integer)):
            raise FrontendError(f"non-integral table label {x!r} is not yet supported natively")
        vals.append(int(x))
    uniq = sorted(set(vals))
    if len(uniq) != len(vals):
        raise FrontendError("duplicate table labels are not supported")
    if len(uniq) <= 1:
        step = 1
    else:
        diffs = {b-a for a,b in zip(uniq,uniq[1:])}
        if len(diffs) != 1 or next(iter(diffs)) <= 0:
            raise FrontendError(f"irregular numeric table labels require a fallback lookup: {uniq[:8]}...")
        step = next(iter(diffs))
    return vals, uniq[0] if uniq else 0, step


def _axis_index_expr(expr: ast.AST, start: int, step: int) -> ast.AST:
    out = copy.deepcopy(expr)
    if start:
        out = ast.BinOp(out, ast.Sub(), ast.Constant(start))
    if step != 1:
        out = ast.BinOp(out, ast.FloorDiv(), ast.Constant(step))
    return out


class InputRegistry:
    def __init__(self, frontend: "GraphModelCompiler"):
        self.frontend = frontend
        self.specs: dict[str, InputSpec] = {}
        self.counter = 0
        self.memo: dict[tuple, str] = {}

    def _key(self, prefix: str) -> str:
        self.counter += 1
        return f"{prefix}_{self.counter}"

    @staticmethod
    def _numeric_scalar(value: Any, description: str) -> tuple[str, Any]:
        if isinstance(value, np.generic):
            value = value.item()
        if isinstance(value, (bool, np.bool_)):
            return "bool", bool(value)
        if isinstance(value, (int, np.integer)):
            return "int64", int(value)
        if isinstance(value, (float, np.floating)):
            value = float(value)
            if not np.isfinite(value):
                raise FrontendError(f"{description} returned a non-finite scalar")
            return "float64", value
        raise FrontendError(
            f"{description} returned unsupported non-numeric {type(value).__name__}"
        )

    @classmethod
    def _numeric_dtype(cls, values: Sequence[Any], description: str) -> str:
        if not values:
            raise FrontendError(f"{description} has an empty materialization domain")
        dtypes = [cls._numeric_scalar(value, description)[0] for value in values]
        if "float64" in dtypes:
            return "float64"
        if "int64" in dtypes:
            return "int64"
        return "bool"

    @classmethod
    def _coerce_numeric_values(
        cls, values: Sequence[Any], dtype: str, description: str
    ) -> np.ndarray:
        normalized: list[Any] = []
        for value in values:
            observed, numeric = cls._numeric_scalar(value, description)
            if dtype == "bool" and observed != "bool":
                raise FrontendError(f"{description} changed from bool to {observed}")
            if dtype == "int64" and observed not in {"bool", "int64"}:
                raise FrontendError(f"{description} changed from integer to {observed}")
            normalized.append(numeric)
        np_dtype = np.bool_ if dtype == "bool" else np.int64 if dtype == "int64" else np.float64
        return np.asarray(normalized, dtype=np_dtype)

    def regional_fallback_point(self, cell_name: str, dtype: str) -> str:
        token=("regional_fallback_point", cell_name)
        if token in self.memo:
            return self.memo[token]
        key=self._key("fb")
        self.memo[token]=key
        if dtype not in ("int64", "bool", "float64"):
            raise FrontendError(f"regional fallback Cell {cell_name} has unsupported observed dtype {dtype}")
        def getter(keys, space=self.frontend.space, name=cell_name):
            return np.asarray([getattr(self.frontend._space_instance(k), name)() for k in keys])
        self.specs[key]=InputSpec(
            key, dtype, 1, "point", getter,
            f"regional fallback point scalar {cell_name}; overrideable by a callback"
        )
        return key

    def reference_metadata_scalar(self, cell_name: str) -> str:
        """Bind one point-independent finite reference-metadata Cell as scalar input.

        Admission is performed by ``GraphModelCompiler``.  Binding re-evaluates the
        Cell over the exact run domain and requires one identical numeric value, so
        table/reference changes cannot silently reuse a stale compile-time literal.
        """
        token=("reference_metadata_scalar", cell_name)
        if token in self.memo:
            return self.memo[token]
        if not self.frontend.run_keys:
            raise FrontendError("reference metadata scalar requires a non-empty run domain")

        def evaluate(keys, name=cell_name):
            values=[]
            for key in keys:
                value=getattr(self.frontend._space_instance(key), name)()
                if isinstance(value, np.generic):
                    value=value.item()
                if not isinstance(value,(bool,int,float)):
                    raise FrontendError(
                        f"reference metadata Cell {name!r} returned non-numeric {type(value).__name__}"
                    )
                values.append(value)
            if not values:
                raise FrontendError(f"reference metadata Cell {name!r} has an empty run domain")
            first=values[0]
            if not all(type(value) is type(first) and value == first for value in values[1:]):
                raise FrontendError(
                    f"reference metadata Cell {name!r} is not point-independent over the frozen run domain"
                )
            return first

        sample=evaluate(self.frontend.run_keys)
        if isinstance(sample,bool): dtype="bool"
        elif isinstance(sample,int): dtype="int64"
        else: dtype="float64"
        key=self._key("meta")
        self.memo[token]=key
        self.specs[key]=InputSpec(
            key,dtype,0,"global",evaluate,
            f"finite point-independent reference metadata Cell {cell_name}",
            domain_token=f"reference_metadata:{cell_name}:{len(self.frontend.run_keys)}",
            expected_shape=(),
        )
        return key

    def scalar_ref(self, ref_name: str, ref_obj) -> str:
        token=("scalar_ref",ref_name)
        if token in self.memo: return self.memo[token]
        key = self._key("g")
        self.memo[token]=key
        dtype = "int64" if isinstance(ref_obj, (int, np.integer, bool, np.bool_)) else "float64"
        def getter(keys, space=self.frontend.space, name=ref_name):
            return space.refs[name]
        self.specs[key] = InputSpec(key, dtype, 0, "global", getter, f"Reference {ref_name}")
        return key

    def point_field(
        self, source: PointRowBinding, field: Any, *, enum_labels: tuple[str, ...] | None = None
    ) -> str:
        semantic = source.semantic
        enum_labels = None if enum_labels is None else tuple(enum_labels)
        token=(
            "point_field", semantic.source_kind, semantic.source_ref,
            semantic.source_cell, semantic.key_position, repr(field), enum_labels,
        )
        if token in self.memo:
            return self.memo[token]
        frame = source.provider()
        if not isinstance(frame, pd.DataFrame):
            raise FrontendError("normalized point-row source no longer returns a DataFrame")
        if field not in frame.columns:
            raise FrontendError(
                f"normalized point-row source has no field {field!r}"
            )
        vals = frame[field]
        enum_codes: dict[str, int] | None = None
        if enum_labels is not None:
            if not enum_labels or len(enum_labels) > 16 or len(set(enum_labels)) != len(enum_labels):
                raise FrontendError("validated enum point field requires 1..16 unique labels")
            if not all(isinstance(label, str) for label in enum_labels):
                raise FrontendError("validated enum labels must be strings")
            enum_codes = {label: i for i, label in enumerate(enum_labels)}
            dtype = "int64"
        elif vals.dtype.kind in "iub":
            dtype = "int64"
        elif vals.dtype.kind in "fc":
            dtype = "float64"
        else:
            raise FrontendError(
                f"point field {field!r} has unsupported non-numeric dtype {vals.dtype}"
            )
        key = self._key("p")
        self.memo[token]=key
        row_pos = int(semantic.key_position)
        nparams = len(self.frontend.space_params)
        run_keys = self.frontend.run_keys
        expected_index = frame.index.copy()
        expected_columns = frame.columns.copy()

        def rows_for(keys, pos=row_pos, nparams=nparams):
            if nparams > 1:
                return [k[pos] if isinstance(k, tuple) else k for k in keys]
            return keys

        run_pos = frame.index.get_indexer(rows_for(run_keys))
        if np.any(run_pos < 0):
            raise FrontendError(
                f"run_keys contain labels not present in normalized point-row source "
                f"{semantic.source_ref!r}"
            )
        run_slice = None
        if len(run_pos):
            first = int(run_pos[0])
            if np.array_equal(run_pos, np.arange(first, first + len(run_pos))):
                run_slice = slice(first, first + len(run_pos))

        def current_frame(provider=source.provider, ei=expected_index, ec=expected_columns):
            table = provider()
            if not isinstance(table, pd.DataFrame):
                raise FrontendError("normalized point-row provider changed type after compilation")
            if not table.index.equals(ei) or not table.columns.equals(ec):
                raise FrontendError("normalized point-row table domain changed after compilation")
            return table

        def encode_enum(values, *, codes=enum_codes, f=field):
            if codes is None:
                return values
            out = np.empty(len(values), dtype=np.int64)
            for j, value in enumerate(values):
                # A finite selector may be undefined on points where source control
                # flow proves the corresponding lookup unreachable.  Preserve that
                # distinction numerically with -1.  The emitted lookup selector is
                # always wrapped in ``__exact_axis_code__`` so an actually executed
                # out-of-domain selector raises instead of becoming Python's valid
                # negative index.
                out[j] = codes.get(value, -1)
            return out

        def getter(keys, f=field, rows_for=rows_for, current=current_frame, encode=encode_enum):
            table = current()
            rows = list(rows_for(keys))
            values = table.loc[rows, f].to_numpy()
            return encode(values)

        def fast_getter(
            keys, cache, *, f=field, rows_for=rows_for, current=current_frame,
            run_keys=run_keys, run_pos=run_pos, run_slice=run_slice,
            cache_id=(semantic.source_kind, semantic.source_ref, semantic.source_cell),
        ):
            table_key = ("point_row_table", cache_id)
            table = cache.get(table_key)
            if table is None:
                table = current()
                cache[table_key] = table
            selector_key = ("point_row_rows", cache_id, row_pos, tuple(keys))
            selector = cache.get(selector_key)
            if selector is None:
                if keys is run_keys or keys == run_keys:
                    selector = run_slice if run_slice is not None else run_pos
                else:
                    pos_arr = table.index.get_indexer(rows_for(keys))
                    if np.any(pos_arr < 0):
                        raise KeyError("ItemSpace key is missing from normalized point-row table index")
                    selector = pos_arr
                    if len(pos_arr):
                        first = int(pos_arr[0])
                        if np.array_equal(pos_arr, np.arange(first, first + len(pos_arr))):
                            selector = slice(first, first + len(pos_arr))
                cache[selector_key] = selector
            values = table[f].to_numpy(copy=False)[selector]
            return encode_enum(values)

        def domain_guard(current=current_frame):
            try:
                current()
            except FrontendError as exc:
                return f"point_row_domain:{exc}"
            return None

        domain_token = repr((tuple(frame.index.tolist()), tuple(frame.columns.tolist())))
        self.specs[key] = InputSpec(
            key, dtype, 1, "point", getter, f"point row field {field!r} by ItemSpace key",
            domain_guard=domain_guard, domain_token=domain_token, expected_shape=None,
            fast_getter=fast_getter, point_row_source=semantic, point_field=field,
            enum_labels=enum_labels,
        )
        return key

    def external_dataframe_step_lookup(
        self, ref_name: str, cell_name: str, cell, *, row_key: Any, column: Any,
        below_first: str, default_value: float | None = None, whole_table: bool = False,
    ) -> tuple[str, str]:
        """Materialize a sorted numeric 1-D axis/value pair for step lookup.

        Source-table interpretation stays in preparation.  Runtime backends receive
        two ordinary global float64 arrays plus normalized lookup provenance.
        """
        if below_first not in {"default", "first"}:
            raise FrontendError(f"unsupported step-lookup below-first policy {below_first!r}")
        if below_first == "default" and default_value is None:
            raise FrontendError("step lookup default policy requires a default value")
        token = (
            "external_dataframe_step_lookup", ref_name, cell_name, bool(whole_table), repr(row_key), repr(column),
            below_first, None if default_value is None else float(default_value),
        )
        if token in self.memo:
            axis_key, value_key = self.memo[token]
            return axis_key, value_key
        frame = cell()
        if not isinstance(frame, pd.DataFrame):
            raise FrontendError(f"external table {ref_name}.{cell_name} no longer returns a DataFrame")
        if whole_table:
            if isinstance(frame.index, pd.MultiIndex):
                raise FrontendError("whole-table step lookup requires a one-dimensional index")
            sub = frame
        else:
            try:
                sub = frame.loc[row_key]
            except Exception as exc:
                raise FrontendError(
                    f"external step lookup slice {ref_name}.{cell_name}.loc[{row_key!r}] failed"
                ) from exc
            if isinstance(sub, pd.Series):
                sub = sub.to_frame().T
        if not isinstance(sub, pd.DataFrame):
            raise FrontendError("normalized step lookup requires a DataFrame row slice")
        if column not in sub.columns:
            raise FrontendError(f"external step lookup has no column {column!r}")
        try:
            axis = np.asarray([float(x) for x in sub.index], dtype=np.float64)
        except Exception as exc:
            raise FrontendError("normalized step lookup axis must be numeric") from exc
        if axis.ndim != 1 or axis.size == 0 or not np.all(np.isfinite(axis)):
            raise FrontendError("normalized step lookup axis must be a non-empty finite 1-D numeric axis")
        if len(np.unique(axis)) != len(axis):
            raise FrontendError("normalized step lookup axis must be unique")
        vals_raw = np.asarray(sub[column])
        if vals_raw.dtype.kind not in "iufc":
            raise FrontendError(f"normalized step lookup column {column!r} must be numeric")
        values = np.asarray(vals_raw, dtype=np.float64)
        order = np.argsort(axis, kind="stable")
        axis = np.ascontiguousarray(axis[order], dtype=np.float64)
        values = np.ascontiguousarray(values[order], dtype=np.float64)
        if np.any(np.diff(axis) <= 0):
            raise FrontendError("normalized step lookup axis must be strictly increasing")

        expected_index = frame.index.copy()
        expected_columns = frame.columns.copy()
        semantic = NormalizedLookup1D(
            kind="step", source_ref=ref_name, source_cell=cell_name, source_shape=tuple(frame.shape),
            row_selector=row_key, selected_column=column, axis_labels=tuple(float(x) for x in axis),
            below_first=below_first,
            default_value=(None if default_value is None else float(default_value)),
        )
        axis_key = self._key("lkx")
        value_key = self._key("lky")
        self.memo[token] = (axis_key, value_key)

        def current(c=cell, ei=expected_index, ec=expected_columns, rk=row_key, col=column, whole=whole_table):
            table = c()
            if not isinstance(table, pd.DataFrame):
                raise FrontendError("external lookup provider changed type after compilation")
            if not table.index.equals(ei) or not table.columns.equals(ec):
                raise FrontendError("external lookup table domain changed after compilation")
            if whole:
                ss = table
            else:
                ss = table.loc[rk]
                if isinstance(ss, pd.Series):
                    ss = ss.to_frame().T
            if not isinstance(ss, pd.DataFrame) or col not in ss.columns:
                raise FrontendError("external lookup slice changed after compilation")
            return ss

        def axis_getter(keys, current=current):
            ss = current()
            aa = np.asarray([float(x) for x in ss.index], dtype=np.float64)
            oo = np.argsort(aa, kind="stable")
            return np.ascontiguousarray(aa[oo], dtype=np.float64)

        def values_getter(keys, current=current, col=column):
            ss = current()
            aa = np.asarray([float(x) for x in ss.index], dtype=np.float64)
            oo = np.argsort(aa, kind="stable")
            return np.ascontiguousarray(np.asarray(ss[col], dtype=np.float64)[oo], dtype=np.float64)

        def domain_guard(current=current, expected_axis=axis, rn=ref_name, cn=cell_name):
            try:
                ss = current()
                aa = np.asarray([float(x) for x in ss.index], dtype=np.float64)
                oo = np.argsort(aa, kind="stable")
                aa = np.ascontiguousarray(aa[oo], dtype=np.float64)
            except Exception as exc:
                return f"lookup1d_domain:{rn}.{cn}:{exc}"
            if aa.shape != expected_axis.shape or not np.array_equal(aa, expected_axis):
                return f"lookup1d_domain:{rn}.{cn}:axis_changed"
            return None

        domain_token = repr((tuple(frame.index.tolist()), tuple(frame.columns.tolist()), row_key, column))
        self.specs[axis_key] = InputSpec(
            axis_key, "float64", 1, "global", axis_getter,
            f"normalized step lookup axis {ref_name}.{cell_name}[{row_key!r}]",
            domain_guard=domain_guard, domain_token=domain_token, expected_shape=tuple(axis.shape),
            normalized_lookup_1d=semantic, lookup_1d_role="axis",
        )
        self.specs[value_key] = InputSpec(
            value_key, "float64", 1, "global", values_getter,
            f"normalized step lookup values {ref_name}.{cell_name}[{row_key!r}, {column!r}]",
            domain_guard=domain_guard, domain_token=domain_token, expected_shape=tuple(values.shape),
            normalized_lookup_1d=semantic, lookup_1d_role="values",
        )
        return axis_key, value_key

    def external_dataframe_interp_lookup(
        self, ref_name: str, cell_name: str, cell, *, row_key: Any, column: Any,
        interpolation: str, extrapolation: str = "endpoint_segment",
    ) -> tuple[str, str]:
        """Materialize a sorted numeric 1-D axis/value pair for interpolation.

        Preparation owns all pandas/modelx interpretation.  Runtime backends see
        only contiguous float64 arrays and a small mathematical intrinsic.  The
        supported extrapolation continues the nearest endpoint segment, matching
        the CI_UK_S pivot-table formula.
        """
        if interpolation not in {"linear", "log_linear"}:
            raise FrontendError(f"unsupported interpolation mode {interpolation!r}")
        if extrapolation != "endpoint_segment":
            raise FrontendError(f"unsupported interpolation extrapolation {extrapolation!r}")
        token = (
            "external_dataframe_interp_lookup", ref_name, cell_name, repr(row_key), repr(column),
            interpolation, extrapolation,
        )
        if token in self.memo:
            return self.memo[token]
        frame = cell()
        if not isinstance(frame, pd.DataFrame):
            raise FrontendError(f"external table {ref_name}.{cell_name} no longer returns a DataFrame")
        try:
            sub = frame.loc[row_key]
        except Exception as exc:
            raise FrontendError(
                f"external interpolation slice {ref_name}.{cell_name}.loc[{row_key!r}] failed"
            ) from exc
        if isinstance(sub, pd.Series):
            sub = sub.to_frame().T
        if not isinstance(sub, pd.DataFrame):
            raise FrontendError("normalized interpolation requires a DataFrame row slice")
        if column not in sub.columns:
            raise FrontendError(f"external interpolation has no column {column!r}")
        try:
            axis = np.asarray([float(x) for x in sub.index], dtype=np.float64)
        except Exception as exc:
            raise FrontendError("normalized interpolation axis must be numeric") from exc
        raw = np.asarray(sub[column])
        if raw.dtype.kind not in "iuf":
            raise FrontendError(f"normalized interpolation column {column!r} must be real numeric")
        values = np.asarray(raw, dtype=np.float64)
        if axis.ndim != 1 or axis.size < 2 or values.shape != axis.shape:
            raise FrontendError("normalized interpolation requires at least two 1-D axis/value points")
        if not (np.all(np.isfinite(axis)) and np.all(np.isfinite(values))):
            raise FrontendError("normalized interpolation axis and values must be finite")
        if len(np.unique(axis)) != len(axis):
            raise FrontendError("normalized interpolation axis must be unique")
        order = np.argsort(axis, kind="stable")
        axis = np.ascontiguousarray(axis[order], dtype=np.float64)
        values = np.ascontiguousarray(values[order], dtype=np.float64)
        if np.any(np.diff(axis) <= 0):
            raise FrontendError("normalized interpolation axis must be strictly increasing")
        if interpolation == "log_linear" and np.any(values <= 0.0):
            raise FrontendError("log-linear interpolation requires strictly positive values")

        expected_index = frame.index.copy()
        expected_columns = frame.columns.copy()
        semantic = NormalizedLookup1D(
            kind="interp", source_ref=ref_name, source_cell=cell_name, source_shape=tuple(frame.shape),
            row_selector=row_key, selected_column=column, axis_labels=tuple(float(x) for x in axis),
            interpolation=interpolation, extrapolation=extrapolation,
        )
        axis_key = self._key("lkx")
        value_key = self._key("lky")
        self.memo[token] = (axis_key, value_key)

        def current(c=cell, ei=expected_index, ec=expected_columns, rk=row_key, col=column):
            table = c()
            if not isinstance(table, pd.DataFrame):
                raise FrontendError("external interpolation provider changed type after compilation")
            if not table.index.equals(ei) or not table.columns.equals(ec):
                raise FrontendError("external interpolation table domain changed after compilation")
            ss = table.loc[rk]
            if isinstance(ss, pd.Series):
                ss = ss.to_frame().T
            if not isinstance(ss, pd.DataFrame) or col not in ss.columns:
                raise FrontendError("external interpolation slice changed after compilation")
            return ss

        def normalized_pair(current=current):
            ss = current()
            aa = np.asarray([float(x) for x in ss.index], dtype=np.float64)
            vv = np.asarray(ss[column], dtype=np.float64)
            oo = np.argsort(aa, kind="stable")
            return (
                np.ascontiguousarray(aa[oo], dtype=np.float64),
                np.ascontiguousarray(vv[oo], dtype=np.float64),
            )

        def axis_getter(keys, pair=normalized_pair):
            return pair()[0]

        def values_getter(keys, pair=normalized_pair):
            return pair()[1]

        def domain_guard(
            pair=normalized_pair, expected_axis=axis, mode=interpolation, rn=ref_name, cn=cell_name
        ):
            try:
                aa, vv = pair()
            except Exception as exc:
                return f"lookup1d_domain:{rn}.{cn}:{exc}"
            if aa.shape != expected_axis.shape or not np.array_equal(aa, expected_axis):
                return f"lookup1d_domain:{rn}.{cn}:axis_changed"
            if not np.all(np.isfinite(vv)):
                return f"lookup1d_domain:{rn}.{cn}:values_nonfinite"
            if mode == "log_linear" and np.any(vv <= 0.0):
                return f"lookup1d_domain:{rn}.{cn}:values_nonpositive"
            return None

        domain_token = repr((
            tuple(frame.index.tolist()), tuple(frame.columns.tolist()), row_key, column,
            interpolation, extrapolation,
        ))
        common = dict(
            domain_guard=domain_guard, domain_token=domain_token, expected_shape=tuple(axis.shape),
            normalized_lookup_1d=semantic,
        )
        self.specs[axis_key] = InputSpec(
            axis_key, "float64", 1, "global", axis_getter,
            f"normalized interpolation axis {ref_name}.{cell_name}[{row_key!r}]",
            lookup_1d_role="axis", **common,
        )
        self.specs[value_key] = InputSpec(
            value_key, "float64", 1, "global", values_getter,
            f"normalized interpolation values {ref_name}.{cell_name}[{row_key!r}, {column!r}]",
            lookup_1d_role="values", **common,
        )
        return axis_key, value_key

    def external_dataframe_interval_lookup(
        self, ref_name: str, cell_name: str, cell, *, lower_column: Any, upper_column: Any,
        value_column: Any, closure: str = "(lo,hi]", fallback: str = "last",
    ) -> tuple[str, str, str]:
        """Normalize a numeric interval table to lower/upper/value float64 arrays.

        The supported semantic is intentionally narrow: rows are tested in source
        order with ``lower < query <= upper`` and the final row value is returned
        when no interval matches.  This exactly matches the Term_US shock-lapse
        formula while keeping pandas iteration out of both runtime backends.
        """
        if closure != "(lo,hi]":
            raise FrontendError(f"unsupported interval closure {closure!r}")
        if fallback != "last":
            raise FrontendError(f"unsupported interval fallback {fallback!r}")
        token = (
            "external_dataframe_interval_lookup", ref_name, cell_name, repr(lower_column),
            repr(upper_column), repr(value_column), closure, fallback,
        )
        if token in self.memo:
            return self.memo[token]
        frame = cell()
        if not isinstance(frame, pd.DataFrame):
            raise FrontendError(f"external table {ref_name}.{cell_name} no longer returns a DataFrame")
        for col in (lower_column, upper_column, value_column):
            if col not in frame.columns:
                raise FrontendError(f"external interval lookup has no column {col!r}")
            raw = np.asarray(frame[col])
            if raw.dtype.kind not in "iufc":
                raise FrontendError(f"normalized interval lookup column {col!r} must be numeric")
        lower = np.ascontiguousarray(np.asarray(frame[lower_column], dtype=np.float64), dtype=np.float64)
        upper = np.ascontiguousarray(np.asarray(frame[upper_column], dtype=np.float64), dtype=np.float64)
        values = np.ascontiguousarray(np.asarray(frame[value_column], dtype=np.float64), dtype=np.float64)
        if lower.ndim != 1 or lower.size == 0 or upper.shape != lower.shape or values.shape != lower.shape:
            raise FrontendError("normalized interval lookup requires non-empty equal-length 1-D columns")
        if not (np.all(np.isfinite(lower)) and np.all(np.isfinite(upper)) and np.all(np.isfinite(values))):
            raise FrontendError("normalized interval lookup columns must be finite")
        if np.any(lower >= upper):
            raise FrontendError("normalized interval lookup requires lower < upper for every row")

        expected_index = frame.index.copy()
        expected_columns = frame.columns.copy()
        semantic = NormalizedLookup1D(
            kind="interval", source_ref=ref_name, source_cell=cell_name, source_shape=tuple(frame.shape),
            selected_column=value_column, lower_column=lower_column, upper_column=upper_column,
            lower_labels=tuple(float(x) for x in lower), upper_labels=tuple(float(x) for x in upper),
            closure=closure, fallback=fallback,
        )
        lower_key = self._key("lklo")
        upper_key = self._key("lkhi")
        value_key = self._key("lky")
        self.memo[token] = (lower_key, upper_key, value_key)

        def current(c=cell, ei=expected_index, ec=expected_columns):
            table = c()
            if not isinstance(table, pd.DataFrame):
                raise FrontendError("external interval lookup provider changed type after compilation")
            if not table.index.equals(ei) or not table.columns.equals(ec):
                raise FrontendError("external interval lookup table domain changed after compilation")
            return table

        def column_getter(keys, current=current, col=None):
            table = current()
            return np.ascontiguousarray(np.asarray(table[col], dtype=np.float64), dtype=np.float64)

        def domain_guard(current=current, elo=lower, ehi=upper, rn=ref_name, cn=cell_name):
            try:
                table = current()
                lo = np.ascontiguousarray(np.asarray(table[lower_column], dtype=np.float64), dtype=np.float64)
                hi = np.ascontiguousarray(np.asarray(table[upper_column], dtype=np.float64), dtype=np.float64)
            except Exception as exc:
                return f"lookup1d_domain:{rn}.{cn}:{exc}"
            if lo.shape != elo.shape or hi.shape != ehi.shape or not np.array_equal(lo, elo) or not np.array_equal(hi, ehi):
                return f"lookup1d_domain:{rn}.{cn}:interval_changed"
            return None

        domain_token = repr((tuple(frame.index.tolist()), tuple(frame.columns.tolist()), lower_column, upper_column, value_column))
        common = dict(
            domain_guard=domain_guard, domain_token=domain_token, expected_shape=tuple(lower.shape),
            normalized_lookup_1d=semantic,
        )
        self.specs[lower_key] = InputSpec(
            lower_key, "float64", 1, "global", lambda keys, g=column_getter, c=lower_column: g(keys, col=c),
            f"normalized interval lookup lower bounds {ref_name}.{cell_name}[{lower_column!r}]",
            lookup_1d_role="lower", **common,
        )
        self.specs[upper_key] = InputSpec(
            upper_key, "float64", 1, "global", lambda keys, g=column_getter, c=upper_column: g(keys, col=c),
            f"normalized interval lookup upper bounds {ref_name}.{cell_name}[{upper_column!r}]",
            lookup_1d_role="upper", **common,
        )
        self.specs[value_key] = InputSpec(
            value_key, "float64", 1, "global", lambda keys, g=column_getter, c=value_column: g(keys, col=c),
            f"normalized interval lookup values {ref_name}.{cell_name}[{value_column!r}]",
            lookup_1d_role="values", **common,
        )
        return lower_key, upper_key, value_key

    def point_coordinate(self, position: int) -> str:
        token=("point_coordinate", int(position))
        if token in self.memo:
            return self.memo[token]
        if position < 0 or position >= len(self.frontend.space_params):
            raise FrontendError(f"invalid ItemSpace coordinate position {position}")
        key=self._key("key")
        self.memo[token]=key
        sample=self.frontend.run_keys
        def extract(k):
            if len(self.frontend.space_params) == 1:
                return k
            if not isinstance(k, tuple) or len(k) != len(self.frontend.space_params):
                raise FrontendError(
                    f"multi-parameter ItemSpace key must be a tuple of length {len(self.frontend.space_params)}"
                )
            return k[position]
        vals=[extract(k) for k in sample]
        if not all(isinstance(x,(int,np.integer)) and not isinstance(x,(bool,np.bool_)) for x in vals):
            raise FrontendError("direct use of a non-integral ItemSpace coordinate requires a Python fallback")
        def getter(keys, pos=position, nparams=len(self.frontend.space_params)):
            if nparams == 1:
                vals=keys
            else:
                vals=[k[pos] for k in keys]
            return np.asarray(vals,dtype=np.int64)
        pname=self.frontend.space_params[position]
        self.specs[key]=InputSpec(key,"int64",1,"point",getter,f"ItemSpace coordinate {position} ({pname})")
        return key

    def point_keys(self) -> str:
        # Compatibility helper for the original one-parameter path.
        return self.point_coordinate(0)

    def global_series(self, ref_name: str, series: pd.Series) -> tuple[str, Callable[[ast.AST], ast.AST]]:
        if isinstance(series.index, pd.MultiIndex):
            return self.global_multiindex_series(ref_name, series)
        labels, start, step = _safe_numeric_axis(series.index)
        token=("series",ref_name,start,step,len(labels))
        if token in self.memo:
            key=self.memo[token]
            return key, lambda expr: _axis_index_expr(expr, start, step)
        order = np.asarray(sorted(range(len(labels)), key=lambda i: labels[i]), dtype=np.intp)
        identity_order = np.array_equal(order, np.arange(len(order), dtype=np.intp))
        key = self._key("a1")
        self.memo[token]=key
        def getter(keys, space=self.frontend.space, rn=ref_name, order=order, identity_order=identity_order):
            s = space.refs[rn]
            arr = s.to_numpy(dtype=np.float64, copy=False)
            return arr if identity_order else arr[order]
        expected_index_obj = series.index
        expected_index = tuple(series.index.tolist())
        def domain_guard(space=self.frontend.space, rn=ref_name, expected_obj=expected_index_obj):
            current = space.refs[rn]
            return None if (current.index is expected_obj or current.index.equals(expected_obj)) else f"table_domain:{rn}:index_changed"
        self.specs[key] = InputSpec(key, "float64", 1, "global", getter, f"Series Reference {ref_name}", domain_guard, repr(expected_index), (len(expected_index),))
        return key, lambda expr: _axis_index_expr(expr, start, step)

    def global_dataframe_exact_nd(
        self,
        ref_name: str,
        df: pd.DataFrame,
        *,
        fixed_axes: Mapping[int, Any],
        dynamic_axes: Sequence[NormalizedTableAxis],
    ) -> str:
        """Normalize an exact labelled DataFrame reference to numeric N-D ABI.

        Unlike ``global_dataframe`` this path does not require numeric column
        labels.  Each physical dimension is either fixed at compile time or is
        supplied through a proven finite categorical / regular numeric selector.
        The runtime sees only a dense numeric ndarray whose axis order is frozen by
        the normalized selector labels.
        """
        if not isinstance(df, pd.DataFrame):
            raise FrontendError(f"Reference {ref_name} is no longer a DataFrame")
        if df.ndim != 2:
            raise FrontendError("exact DataFrame reference normalization requires rank 2")
        axes = tuple(dynamic_axes)
        fixed = {int(k): v for k, v in fixed_axes.items()}
        if any(k not in (0, 1) for k in fixed):
            raise FrontendError("exact DataFrame reference fixed axis must be 0 or 1")
        by_level = {int(a.level): a for a in axes}
        if set(by_level).intersection(fixed):
            raise FrontendError("exact DataFrame reference axis cannot be both fixed and dynamic")
        if set(by_level).union(fixed) != {0, 1}:
            raise FrontendError("exact DataFrame reference must account for both row and column axes")

        source_domains = (tuple(df.index.tolist()), tuple(df.columns.tolist()))
        selected: list[tuple[Any, ...]] = []
        for level, domain in enumerate(source_domains):
            if level in fixed:
                label = fixed[level]
                if label not in domain:
                    raise FrontendError(
                        f"DataFrame Reference {ref_name} axis {level} has no label {label!r}"
                    )
                selected.append((label,))
            else:
                labels = tuple(by_level[level].labels)
                if not labels or any(label not in domain for label in labels):
                    raise FrontendError(
                        f"DataFrame Reference {ref_name} dynamic axis {level} is outside the frozen domain"
                    )
                selected.append(labels)

        token = (
            "dataframe_exact_nd", ref_name,
            tuple((k, repr(v)) for k, v in sorted(fixed.items())),
            tuple((a.level, a.selector_kind, tuple(map(repr, a.labels))) for a in axes),
        )
        if token in self.memo:
            return self.memo[token]

        try:
            sample = df.loc[list(selected[0]), list(selected[1])].to_numpy(copy=False)
            numeric = np.asarray(sample, dtype=np.float64)
        except Exception as exc:
            raise FrontendError(
                f"DataFrame Reference {ref_name} exact lookup values must be numeric"
            ) from exc
        if numeric.shape != (len(selected[0]), len(selected[1])):
            raise FrontendError(f"DataFrame Reference {ref_name} exact lookup shape proof failed")

        key = self._key("a2x")
        self.memo[token] = key
        expected_index_obj = df.index
        expected_columns_obj = df.columns

        def current(space=self.frontend.space, rn=ref_name, ei=expected_index_obj, ec=expected_columns_obj):
            frame = space.refs[rn]
            if not isinstance(frame, pd.DataFrame):
                raise FrontendError(f"DataFrame Reference {rn} changed type after compilation")
            if not (frame.index is ei or frame.index.equals(ei)):
                raise FrontendError(f"DataFrame Reference {rn} index changed after compilation")
            if not (frame.columns is ec or frame.columns.equals(ec)):
                raise FrontendError(f"DataFrame Reference {rn} columns changed after compilation")
            return frame

        def getter(keys, current=current, rows=selected[0], cols=selected[1]):
            frame = current()
            return np.ascontiguousarray(
                np.asarray(frame.loc[list(rows), list(cols)].to_numpy(copy=False), dtype=np.float64)
            )

        def domain_guard(current=current, rn=ref_name):
            try:
                current()
            except FrontendError as exc:
                return f"table_domain:{rn}:{exc}"
            return None

        semantic = NormalizedTableInput(
            source_ref=ref_name, source_cell="<reference>", source_shape=tuple(df.shape),
            index_names=(df.index.name, "__columns__"), selected_column=None,
            fixed_row_labels=tuple(sorted(fixed.items())), dynamic_level=None,
            dynamic_labels=(), axis_start=None, axis_step=None, result_kind="exact_nd",
            layout="dense_cartesian", dynamic_axes=axes, sparse_key_input=None,
        )
        self.specs[key] = InputSpec(
            key, "float64", 2, "global", getter,
            f"normalized exact DataFrame Reference {ref_name}",
            domain_guard=domain_guard, domain_token=repr(source_domains),
            expected_shape=(len(selected[0]), len(selected[1])), normalized_table=semantic,
        )
        return key

    def global_dataframe(self, ref_name: str, df: pd.DataFrame) -> tuple[str, Callable[[ast.AST], ast.AST], Callable[[ast.AST], ast.AST]]:
        rows, r0, rs = _safe_numeric_axis(df.index)
        cols, c0, cs = _safe_numeric_axis(df.columns)
        token=("dataframe",ref_name,r0,rs,c0,cs,len(rows),len(cols))
        if token in self.memo:
            key=self.memo[token]
            return key, lambda e: _axis_index_expr(e, r0, rs), lambda e: _axis_index_expr(e, c0, cs)
        rorder = np.asarray(sorted(range(len(rows)), key=lambda i: rows[i]), dtype=np.intp)
        corder = np.asarray(sorted(range(len(cols)), key=lambda i: cols[i]), dtype=np.intp)
        r_identity = np.array_equal(rorder, np.arange(len(rorder), dtype=np.intp))
        c_identity = np.array_equal(corder, np.arange(len(corder), dtype=np.intp))
        key = self._key("a2")
        self.memo[token]=key
        def getter(keys, space=self.frontend.space, rn=ref_name, ro=rorder, co=corder, ri=r_identity, ci=c_identity):
            frame = space.refs[rn]
            arr = frame.to_numpy(dtype=np.float64, copy=False)
            if not ri:
                arr = arr[ro, :]
            if not ci:
                arr = arr[:, co]
            return arr
        expected_index_obj = df.index; expected_columns_obj = df.columns
        expected_index = tuple(df.index.tolist()); expected_columns = tuple(df.columns.tolist())
        def domain_guard(space=self.frontend.space, rn=ref_name, er=expected_index_obj, ec=expected_columns_obj):
            current = space.refs[rn]
            if not (current.index is er or current.index.equals(er)):
                return f"table_domain:{rn}:index_changed"
            if not (current.columns is ec or current.columns.equals(ec)):
                return f"table_domain:{rn}:columns_changed"
            return None
        self.specs[key] = InputSpec(key, "float64", 2, "global", getter, f"DataFrame Reference {ref_name}", domain_guard, repr((expected_index, expected_columns)), (len(expected_index), len(expected_columns)))
        return key, lambda e: _axis_index_expr(e, r0, rs), lambda e: _axis_index_expr(e, c0, cs)

    def global_multiindex_series(self, ref_name: str, series: pd.Series) -> tuple[str, Callable[[ast.AST], ast.AST]]:
        if series.index.nlevels != 2:
            raise FrontendError("only two-level numeric MultiIndex Series are supported by the native table frontend")
        lev0 = sorted(set(series.index.get_level_values(0)))
        lev1 = sorted(set(series.index.get_level_values(1)))
        _, r0, rs = _safe_numeric_axis(lev0)
        _, c0, cs = _safe_numeric_axis(lev1)
        # Require a complete Cartesian grid so missing labels cannot silently turn into zeros.
        if len(series) != len(lev0) * len(lev1):
            raise FrontendError("sparse MultiIndex Series requires a lookup fallback; native dense conversion would change missing-key semantics")
        token=("multiindex",ref_name,r0,rs,c0,cs,len(lev0),len(lev1))
        if token in self.memo:
            key=self.memo[token]
            self.frontend.multiindex_axes[key]=(r0,rs,c0,cs)
            return key, (lambda expr: expr)
        key = self._key("a2")
        self.memo[token]=key
        desired = [(a, b) for a in lev0 for b in lev1]
        order = series.index.get_indexer(desired)
        if np.any(order < 0):
            raise FrontendError("MultiIndex Cartesian-domain proof failed")
        order = np.asarray(order, dtype=np.intp)
        identity_order = np.array_equal(order, np.arange(len(order), dtype=np.intp))
        def getter(keys, space=self.frontend.space, rn=ref_name, l0=lev0, l1=lev1, order=order, identity_order=identity_order):
            s = space.refs[rn]
            arr = s.to_numpy(dtype=np.float64, copy=False)
            if not identity_order:
                arr = arr[order]
            return arr.reshape((len(l0), len(l1)))
        expected_index_obj = series.index
        expected_index = tuple(series.index.tolist())
        def domain_guard(space=self.frontend.space, rn=ref_name, expected_obj=expected_index_obj):
            current = space.refs[rn]
            return None if (current.index is expected_obj or current.index.equals(expected_obj)) else f"table_domain:{rn}:multiindex_changed"
        self.specs[key] = InputSpec(key, "float64", 2, "global", getter, f"MultiIndex Series Reference {ref_name}", domain_guard, repr(expected_index), (len(lev0), len(lev1)))
        # Caller handles tuple indices; returned mapper is unused for 2-D.
        def mapper(expr):
            return expr
        self.frontend.multiindex_axes[key] = (r0, rs, c0, cs)
        return key, mapper

    def local_cell_multiindex_series(self, cell_name: str, cell) -> str:
        """Normalize a zero-argument local Cell returning a dense numeric 2-D Series.

        The pandas/modelx object is preparation-only.  Backends receive one dense
        numeric table input whose exact MultiIndex domain is validated whenever
        inputs are bound.
        """
        value = cell()
        if not isinstance(value, pd.Series) or not isinstance(value.index, pd.MultiIndex):
            raise FrontendError(
                f"local Cells value {cell_name!r} is not a MultiIndex Series"
            )
        if value.index.nlevels != 2:
            raise FrontendError(
                f"local Cells value {cell_name!r} requires exactly two index levels"
            )
        raw = value.to_numpy(copy=False)
        if raw.dtype.kind != "f":
            raise FrontendError(
                f"local Cells value {cell_name!r} requires float dtype for indexed-input normalization; got {raw.dtype}"
            )
        lev0 = sorted(set(value.index.get_level_values(0)))
        lev1 = sorted(set(value.index.get_level_values(1)))
        _, r0, rs = _safe_numeric_axis(lev0)
        _, c0, cs = _safe_numeric_axis(lev1)
        if len(value) != len(lev0) * len(lev1):
            raise FrontendError(
                f"local Cells value {cell_name!r} is sparse; dense indexed-input normalization would change missing-key semantics"
            )
        token=("local_cell_multiindex", cell_name, r0, rs, c0, cs, len(lev0), len(lev1))
        if token in self.memo:
            key=self.memo[token]
            self.frontend.multiindex_axes[key]=(r0,rs,c0,cs)
            return key
        desired=[(a,b) for a in lev0 for b in lev1]
        order=value.index.get_indexer(desired)
        if np.any(order < 0):
            raise FrontendError(
                f"local Cells value {cell_name!r} failed Cartesian-domain proof"
            )
        order=np.asarray(order,dtype=np.intp)
        identity=np.array_equal(order,np.arange(len(order),dtype=np.intp))
        expected_index=value.index.copy()
        expected_shape=(len(lev0),len(lev1))
        key=self._key("lc2")
        self.memo[token]=key

        def current(c=cell, ei=expected_index, cn=cell_name):
            series=c()
            if not isinstance(series,pd.Series) or not isinstance(series.index,pd.MultiIndex):
                raise FrontendError(f"local Cells indexed input {cn!r} changed type")
            if not series.index.equals(ei):
                raise FrontendError(f"local Cells indexed input {cn!r} changed domain")
            arr=series.to_numpy(copy=False)
            if arr.dtype.kind != "f":
                raise FrontendError(f"local Cells indexed input {cn!r} changed dtype")
            return arr

        def getter(keys,current=current,order=order,identity=identity,shape=expected_shape):
            arr=current()
            if not identity:
                arr=arr[order]
            return np.ascontiguousarray(arr,dtype=np.float64).reshape(shape)

        def domain_guard(current=current,cn=cell_name):
            try:
                current()
            except FrontendError as exc:
                return f"local_cell_indexed_input:{cn}:{exc}"
            return None

        self.specs[key]=InputSpec(
            key,"float64",2,"global",getter,
            f"dense MultiIndex Series from local Cells {cell_name}",
            domain_guard=domain_guard,
            domain_token=repr((tuple(expected_index.tolist()), expected_shape)),
            expected_shape=expected_shape,
        )
        self.frontend.multiindex_axes[key]=(r0,rs,c0,cs)
        return key

    def external_scalar(self, ref_name: str, cell_name: str, cell) -> str:
        """Marshal a zero-argument numeric Cells value from another Space.

        A structurally relative child Space may inherit one or more coordinates from
        the active RunDomain ItemSpace.  In that case the Cells value is a point
        input, not a global scalar.  The child/modelx object remains preparation-only;
        generated code receives only the numeric ABI value.
        """
        binding = self.frontend._hierarchical_itemspace_parameter_binding(ref_name, cell_name)
        if binding is not None:
            token=(
                "external_scalar_hierarchical", ref_name, cell_name,
                binding.owner_space_fullname, binding.child_space_fullname,
                binding.parameter_names, binding.parameter_positions,
                binding.dependency_cells,
            )
            if token in self.memo:
                return self.memo[token]
            description = (
                f"hierarchical ItemSpace-bound external Cells scalar {ref_name}.{cell_name} "
                f"via {binding.parameter_names!r}"
            )

            def evaluate(keys, b=binding, description=description):
                keys = tuple(keys)
                self.frontend._validate_hierarchical_itemspace_binding(b, keys)
                values=[]
                for run_key in keys:
                    concrete = self.frontend._context_cell_for_key(
                        b.ref_name, b.cell_name, run_key
                    )
                    if tuple(getattr(concrete, "parameters", ()) or ()):
                        raise FrontendError(
                            f"{description} changed to a parameterized Cells member"
                        )
                    try:
                        values.append(concrete())
                    except Exception as exc:
                        raise FrontendError(
                            f"{description} could not be evaluated in its owning ItemSpace: "
                            f"{type(exc).__name__}: {exc}"
                        ) from exc
                return values

            sample_values = evaluate(self.frontend.run_keys)
            dtype = self._numeric_dtype(sample_values, description)
            key=self._key("extp")
            self.memo[token]=key

            def getter(keys, evaluate=evaluate, dtype=dtype, description=description):
                return self._coerce_numeric_values(evaluate(keys), dtype, description)

            self.specs[key]=InputSpec(
                key, dtype, 1, "point", getter, description,
                domain_token=repr((
                    binding.owner_space_fullname, binding.child_space_fullname,
                    binding.parameter_names, binding.parameter_positions,
                )),
                hierarchical_itemspace_binding=binding,
            )
            return key

        token=("external_scalar", ref_name, cell_name)
        if token in self.memo:
            return self.memo[token]
        key=self._key("exts")
        self.memo[token]=key
        value=cell()
        if isinstance(value,(bool,np.bool_,int,np.integer)):
            dtype="int64"
        elif isinstance(value,(float,np.floating)):
            dtype="float64"
        else:
            raise FrontendError(f"external Cells scalar {ref_name}.{cell_name} has unsupported type {type(value).__name__}")
        def getter(keys, c=cell):
            return c()
        self.specs[key]=InputSpec(key,dtype,0,"global",getter,f"external Cells scalar {ref_name}.{cell_name}")
        return key

    def external_array(self, ref_name: str, cell_name: str, cell, point_position: int | None) -> str:
        """Marshal an external numeric Cells array.

        ``point_position`` identifies the ItemSpace coordinate used to index the
        array.  It is deliberately positional/name-agnostic: a multi-parameter
        Space may use any coordinate as the independent array index.  ``None``
        means the complete array is a global kernel input.
        """
        point_indexed = point_position is not None
        token=("external",ref_name,cell_name,point_position)
        if token in self.memo: return self.memo[token]
        key = self._key("extp" if point_indexed else "ext")
        self.memo[token]=key
        value = np.asarray(cell())
        if value.dtype.kind not in "iufb" or value.ndim not in (1,2):
            raise FrontendError(f"external Cells array {ref_name}.{cell_name} has unsupported dtype/shape {value.dtype} {value.shape}")
        dtype = "int64" if value.dtype.kind in "iub" else "float64"
        fast_getter = None
        if point_indexed:
            run_keys = self.frontend.run_keys
            pos = int(point_position)
            nparams = len(self.frontend.space_params)
            def coordinate(keys, pos=pos, nparams=nparams):
                if nparams == 1:
                    return np.asarray(keys, dtype=np.int64)
                return np.asarray([k[pos] if isinstance(k, tuple) else k for k in keys], dtype=np.int64)
            run_idx = coordinate(run_keys)
            run_slice = None
            if len(run_idx):
                start = int(run_idx[0])
                if np.array_equal(run_idx, np.arange(start, start + len(run_idx), dtype=np.int64)):
                    run_slice = slice(start, start + len(run_idx))
            def getter(keys, c=cell, coordinate=coordinate):
                arr = np.asarray(c())
                idx = coordinate(keys)
                return arr[idx]
            def fast_getter(keys, cache, c=cell, run_keys=run_keys, run_idx=run_idx, run_slice=run_slice, coordinate=coordinate):
                arr = np.asarray(c())
                if keys is run_keys or keys == run_keys:
                    selector = run_slice if run_slice is not None else run_idx
                else:
                    idx = coordinate(keys)
                    selector = idx
                    if len(idx):
                        start = int(idx[0])
                        if np.array_equal(idx, np.arange(start, start + len(idx), dtype=np.int64)):
                            selector = slice(start, start + len(idx))
                return arr[selector]
            ndim = max(1, value.ndim - 0)
            scope = "point"
        else:
            def getter(keys, c=cell):
                return np.asarray(c())
            ndim = value.ndim
            scope = "global"
        self.specs[key] = InputSpec(
            key, dtype, ndim, scope, getter, f"external Cells array {ref_name}.{cell_name}",
            expected_shape=(tuple(value.shape) if scope == "global" else None),
            domain_token=(repr(tuple(value.shape)) if scope == "global" else None),
            fast_getter=fast_getter,
        )
        return key

    def _bound_numeric_expr_value(
        self,
        node: ast.AST,
        run_key: Any,
        coordinate_binding: tuple[str, int] | None = None,
    ) -> Any:
        """Evaluate one already-lowered ABI scalar expression for one RunDomain key.

        This is intentionally *not* a Python/source evaluator.  It accepts only
        primitive constants, arithmetic, and scalar values already owned by the
        existing ``global_input``/``point_input`` ABI.  V02387 optionally admits one
        explicitly supplied integer coordinate name/value pair.  Parameterized-Space
        materialization therefore composes existing input bindings instead of
        introducing a second model-expression interpreter or discovering coordinates
        from arbitrary source names.
        """
        if isinstance(node, ast.Constant):
            ok, value = self.frontend._context_primitive(node.value)
            if not ok:
                raise FrontendError("bound numeric expression contains a non-primitive constant")
            return value
        if isinstance(node, ast.Name):
            if (
                coordinate_binding is not None
                and isinstance(node.ctx, ast.Load)
                and node.id == coordinate_binding[0]
            ):
                return int(coordinate_binding[1])
            raise FrontendError(
                f"bound numeric expression contains unsupported runtime name {node.id!r}"
            )
        if isinstance(node, ast.UnaryOp):
            value = self._bound_numeric_expr_value(node.operand, run_key, coordinate_binding)
            try:
                if isinstance(node.op, ast.UAdd): return +value
                if isinstance(node.op, ast.USub): return -value
            except Exception as exc:
                raise FrontendError("bound numeric unary expression could not be evaluated") from exc
            raise FrontendError("bound numeric expression has an unsupported unary operator")
        if isinstance(node, ast.BinOp):
            left = self._bound_numeric_expr_value(node.left, run_key, coordinate_binding)
            right = self._bound_numeric_expr_value(node.right, run_key, coordinate_binding)
            try:
                if isinstance(node.op, ast.Add): return left + right
                if isinstance(node.op, ast.Sub): return left - right
                if isinstance(node.op, ast.Mult): return left * right
                if isinstance(node.op, ast.Div): return left / right
                if isinstance(node.op, ast.FloorDiv): return left // right
                if isinstance(node.op, ast.Mod): return left % right
                if isinstance(node.op, ast.Pow): return left ** right
            except Exception as exc:
                raise FrontendError("bound numeric binary expression could not be evaluated") from exc
            raise FrontendError("bound numeric expression has an unsupported binary operator")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and not node.keywords:
            name = node.func.id
            if name in {"global_input", "point_input"} and len(node.args) == 1:
                key_node = node.args[0]
                if not isinstance(key_node, ast.Constant) or not isinstance(key_node.value, str):
                    raise FrontendError(f"{name} requires a literal registered input key")
                key = key_node.value
                spec = self.specs.get(key)
                if spec is None:
                    raise FrontendError(f"bound numeric expression references unknown input {key!r}")
                if name == "global_input":
                    if spec.scope != "global" or spec.ndim != 0:
                        raise FrontendError(f"input {key!r} is not a global scalar")
                    value = spec.getter((run_key,))
                else:
                    if spec.scope != "point" or spec.ndim != 1:
                        raise FrontendError(f"input {key!r} is not a point scalar")
                    # Point ordinal is relative to a bound batch, not an intrinsic
                    # semantic point value.  It cannot be replayed one key at a time.
                    if str(spec.domain_token or "").startswith("point_ordinal:"):
                        raise FrontendError("point ordinal is not a materializable semantic argument")
                    arr = np.asarray(spec.getter((run_key,)))
                    if arr.ndim != 1 or len(arr) != 1:
                        raise FrontendError(f"point input {key!r} did not bind one scalar")
                    value = arr[0]
                if isinstance(value, np.generic):
                    value = value.item()
                ok, value = self.frontend._context_primitive(value)
                if not ok:
                    raise FrontendError(f"input {key!r} did not bind a primitive scalar")
                return value
            if name in {"int", "float", "bool", "abs", "min", "max"}:
                values = [
                    self._bound_numeric_expr_value(arg, run_key, coordinate_binding)
                    for arg in node.args
                ]
                fn = {"int": int, "float": float, "bool": bool, "abs": abs, "min": min, "max": max}[name]
                try:
                    return fn(*values)
                except Exception as exc:
                    raise FrontendError(f"bound numeric intrinsic {name} failed") from exc
        raise FrontendError(
            f"unsupported bound numeric ABI expression: {ast.dump(node, include_attributes=False)}"
        )

    def bound_numeric_expr_supported(
        self, node: ast.AST, coordinate_name: str | None = None
    ) -> bool:
        """Structural check for the bounded ABI-expression subset above.

        ``coordinate_name`` is deliberately explicit.  A random source ``Name`` never
        becomes materializable merely because a caller happened to have an integer for
        it at trace time.
        """
        if isinstance(node, ast.Constant):
            return self.frontend._context_primitive(node.value)[0]
        if isinstance(node, ast.Name):
            return (
                coordinate_name is not None
                and isinstance(node.ctx, ast.Load)
                and node.id == coordinate_name
            )
        if isinstance(node, ast.UnaryOp):
            return isinstance(node.op, (ast.UAdd, ast.USub)) and self.bound_numeric_expr_supported(
                node.operand, coordinate_name
            )
        if isinstance(node, ast.BinOp):
            return isinstance(
                node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow)
            ) and self.bound_numeric_expr_supported(
                node.left, coordinate_name
            ) and self.bound_numeric_expr_supported(node.right, coordinate_name)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and not node.keywords:
            if node.func.id in {"global_input", "point_input"}:
                return (
                    len(node.args) == 1
                    and isinstance(node.args[0], ast.Constant)
                    and isinstance(node.args[0].value, str)
                    and node.args[0].value in self.specs
                )
            if node.func.id in {"int", "float", "bool", "abs", "min", "max"}:
                return bool(node.args) and all(
                    self.bound_numeric_expr_supported(arg, coordinate_name) for arg in node.args
                )
        return False

    @staticmethod
    def bound_numeric_expr_uses_coordinate(node: ast.AST, coordinate_name: str) -> bool:
        return any(
            isinstance(child, ast.Name)
            and isinstance(child.ctx, ast.Load)
            and child.id == coordinate_name
            for child in ast.walk(node)
        )

    def context_static_attribute(self, ref_name: str, attr_name: str) -> str:
        """Bind one primitive model-ref attribute without baking its observed value.

        The attribute is re-resolved on every ``bind_inputs`` call and must remain a
        point-independent numeric primitive with a stable dtype.
        """
        token = ("context_static_attribute", ref_name, attr_name)
        if token in self.memo:
            return self.memo[token]
        node = ast.Attribute(ast.Name(ref_name, ast.Load()), attr_name, ast.Load())
        description = f"model-bound primitive attribute {ref_name}.{attr_name}"

        def evaluate(keys):
            values: list[Any] = []
            for run_key in keys:
                ok, value = self.frontend._context_static_value(node, run_key)
                if not ok:
                    raise FrontendError(f"{description} is no longer a primitive resolvable attribute")
                self._numeric_scalar(value, description)
                values.append(value)
            if not values:
                raise FrontendError(f"{description} has an empty bound RunDomain")
            first = values[0]
            if not all(type(value) is type(first) and value == first for value in values[1:]):
                raise FrontendError(f"{description} is not point-independent over the bound RunDomain")
            return values

        sample = evaluate(self.frontend.run_keys)
        dtype = self._numeric_dtype(sample, description)
        key = self._key("ctxattr")
        self.memo[token] = key

        def getter(keys, evaluate=evaluate, dtype=dtype, description=description):
            values = evaluate(keys)
            arr = self._coerce_numeric_values(values, dtype, description)
            if np.any(arr != arr[0]):
                raise FrontendError(f"{description} changed across the bound RunDomain")
            return arr[0].item() if hasattr(arr[0], "item") else arr[0]

        self.specs[key] = InputSpec(
            key, dtype, 0, "global", getter, description,
            expected_shape=(),
            domain_token=repr((ref_name, attr_name, "primitive_static_attribute")),
        )
        return key

    def parameterized_space_method_point(
        self,
        ref_name: str,
        selector_nodes: Sequence[ast.AST],
        member_name: str,
        argument_nodes: Sequence[ast.AST],
    ) -> str:
        """Materialize ``Space[selectors].Cells(args...)`` over the frozen RunDomain.

        The selected ItemSpace and Cells objects exist only during preparation.
        Generated code receives one numeric point input for the semantic call.
        """
        selector_nodes = tuple(copy.deepcopy(node) for node in selector_nodes)
        argument_nodes = tuple(copy.deepcopy(node) for node in argument_nodes)
        selector_token = tuple(ast.dump(node, include_attributes=False) for node in selector_nodes)
        argument_token = tuple(ast.dump(node, include_attributes=False) for node in argument_nodes)
        token = (
            "parameterized_space_method_point", ref_name, selector_token, member_name, argument_token,
        )
        if token in self.memo:
            return self.memo[token]
        if not selector_nodes:
            raise FrontendError("parameterized Space selection requires at least one selector")
        if not all(self.bound_numeric_expr_supported(node) for node in selector_nodes):
            raise FrontendError(f"parameterized Space {ref_name} has an unsupported selector expression")
        if not all(self.bound_numeric_expr_supported(node) for node in argument_nodes):
            raise FrontendError(
                f"parameterized Space method {ref_name}[...].{member_name} has a non-point-scalar argument"
            )
        description = f"model-bound parameterized Space numeric method {ref_name}[...].{member_name}"

        def evaluate(keys):
            values: list[Any] = []
            for run_key in keys:
                selectors = [self._bound_numeric_expr_value(node, run_key) for node in selector_nodes]
                item = self.frontend._context_selected_itemspace(ref_name, selectors, run_key)
                member = self.frontend._context_itemspace_cell(item, ref_name, member_name)
                args = [self._bound_numeric_expr_value(node, run_key) for node in argument_nodes]
                try:
                    value = member(*args)
                except Exception as exc:
                    raise FrontendError(
                        f"{description} could not be materialized: {type(exc).__name__}: {exc}"
                    ) from exc
                self._numeric_scalar(value, description)
                values.append(value)
            return values

        sample = evaluate(self.frontend.run_keys)
        dtype = self._numeric_dtype(sample, description)
        key = self._key("ctxmethod")
        self.memo[token] = key

        def getter(keys, evaluate=evaluate, dtype=dtype, description=description):
            return self._coerce_numeric_values(evaluate(keys), dtype, description)

        self.specs[key] = InputSpec(
            key, dtype, 1, "point", getter, description,
            domain_token=repr((ref_name, selector_token, member_name, argument_token)),
        )
        return key

    def parameterized_space_method_coordinate(
        self,
        ref_name: str,
        selector_nodes: Sequence[ast.AST],
        member_name: str,
        argument_nodes: Sequence[ast.AST],
        coordinate_name: str,
        coordinate_lo: int,
        coordinate_hi: int,
        coordinate_owner_uid: str,
        coordinate_step: int = 1,
    ) -> tuple[str, str]:
        """Materialize one selected-Cells call over point x exact coordinate.

        Rows are frozen RunDomain points.  Columns are the exact finite integer
        coordinate domain already proven for ``coordinate_owner_uid``.  The selected
        ItemSpace and Cells objects remain preparation-only; generated code uses the
        ordinary two-dimensional ``table_input`` ABI plus ``point_ordinal``.
        """
        selector_nodes = tuple(copy.deepcopy(node) for node in selector_nodes)
        argument_nodes = tuple(copy.deepcopy(node) for node in argument_nodes)
        coordinate_name = str(coordinate_name)
        coordinate_lo = int(coordinate_lo)
        coordinate_hi = int(coordinate_hi)
        coordinate_step = int(coordinate_step)
        coordinate_owner_uid = str(coordinate_owner_uid)

        if not selector_nodes:
            raise FrontendError("parameterized Space selection requires at least one selector")
        if coordinate_step != 1:
            raise FrontendError("parameterized Space coordinate materialization requires unit step")
        if coordinate_lo > coordinate_hi:
            raise FrontendError("parameterized Space coordinate materialization has an empty domain")
        if not all(self.bound_numeric_expr_supported(node) for node in selector_nodes):
            raise FrontendError(f"parameterized Space {ref_name} has an unsupported selector expression")
        if not argument_nodes or not all(
            self.bound_numeric_expr_supported(node, coordinate_name) for node in argument_nodes
        ):
            raise FrontendError(
                f"parameterized Space method {ref_name}[...].{member_name} has an unsupported coordinate argument"
            )
        if not any(
            self.bound_numeric_expr_uses_coordinate(node, coordinate_name)
            for node in argument_nodes
        ):
            raise FrontendError(
                f"parameterized Space method {ref_name}[...].{member_name} is not coordinate dependent"
            )

        width = ((coordinate_hi - coordinate_lo) // coordinate_step) + 1
        if width * len(self.frontend.run_keys) > RUNTIME_SCALAR_HELPER_EXPANSION_LIMIT:
            raise FrontendError(
                f"parameterized Space method {ref_name}[...].{member_name} materialization exceeds safety limit"
            )

        selector_token = tuple(ast.dump(node, include_attributes=False) for node in selector_nodes)
        argument_token = tuple(ast.dump(node, include_attributes=False) for node in argument_nodes)
        coordinate_domain_identity = (
            coordinate_owner_uid, coordinate_name, coordinate_lo, coordinate_hi, coordinate_step,
            "exact_rank1_coordinate_v1",
        )
        token = (
            "parameterized_space_method_coordinate",
            ref_name,
            selector_token,
            member_name,
            argument_token,
            coordinate_domain_identity,
        )
        if token in self.memo:
            return self.memo[token], self.point_ordinal()

        description = (
            f"model-bound parameterized Space numeric coordinate method "
            f"{ref_name}[...].{member_name}"
        )

        def validate_coordinate_domain() -> None:
            tr = self.frontend.variant_trace_by_uid.get(coordinate_owner_uid)
            if tr is None or tr.key.time_pos is None:
                raise FrontendError(f"{description} coordinate owner is no longer available")
            pos = int(tr.key.time_pos)
            if pos < 0 or pos >= len(tr.schema.parameters):
                raise FrontendError(f"{description} coordinate owner has invalid parameter geometry")
            if tr.schema.parameters[pos] != coordinate_name:
                raise FrontendError(f"{description} coordinate parameter identity changed")
            current = (
                self.frontend.specialized_coordinate_domains.get(coordinate_owner_uid)
                or self.frontend.coordinate_domains.get(coordinate_owner_uid)
            )
            if current is None:
                raise FrontendError(f"{description} coordinate domain is no longer proven")
            if int(current.lo) != coordinate_lo or int(current.hi) != coordinate_hi:
                raise FrontendError(f"{description} coordinate domain changed after compilation")

        def evaluate(keys):
            validate_coordinate_domain()
            rows: list[list[Any]] = []
            for run_key in keys:
                selectors = [
                    self._bound_numeric_expr_value(node, run_key) for node in selector_nodes
                ]
                item = self.frontend._context_selected_itemspace(ref_name, selectors, run_key)
                member = self.frontend._context_itemspace_cell(item, ref_name, member_name)
                row: list[Any] = []
                for coordinate in range(coordinate_lo, coordinate_hi + 1, coordinate_step):
                    binding = (coordinate_name, int(coordinate))
                    args = [
                        self._bound_numeric_expr_value(node, run_key, binding)
                        for node in argument_nodes
                    ]
                    try:
                        value = member(*args)
                    except Exception as exc:
                        raise FrontendError(
                            f"{description} could not be materialized at {coordinate_name}={coordinate}: "
                            f"{type(exc).__name__}: {exc}"
                        ) from exc
                    self._numeric_scalar(value, description)
                    row.append(value)
                rows.append(row)
            return rows

        sample_rows = evaluate(self.frontend.run_keys)
        flat_sample = [value for row in sample_rows for value in row]
        dtype = self._numeric_dtype(flat_sample, description)
        table_key = self._key("ctxmethodcurve")
        self.memo[token] = table_key

        def getter(keys, evaluate=evaluate, dtype=dtype, description=description, width=width):
            rows = evaluate(keys)
            if any(len(row) != width for row in rows):
                raise FrontendError(f"{description} coordinate table width changed")
            flat = [value for row in rows for value in row]
            arr = self._coerce_numeric_values(flat, dtype, description)
            return np.ascontiguousarray(arr.reshape((len(rows), width)))

        self.specs[table_key] = InputSpec(
            table_key,
            dtype,
            2,
            "global",
            getter,
            description,
            domain_token=repr(
                (ref_name, selector_token, member_name, argument_token, coordinate_domain_identity)
            ),
            expected_shape=(len(self.frontend.run_keys), width),
        )
        return table_key, self.point_ordinal()

    def context_scalar_accessor(
        self, ref_name: str, cell_name: str, argument_nodes: Sequence[ast.AST]
    ) -> str:
        """Materialize one direct model-bound Cells call over point/global ABI scalars.

        V02390 deliberately reuses the bounded numeric ABI-expression evaluator used
        by parameterized-Space methods.  The context/Cells object semantics remain
        unchanged: ``_context_cell_for_key`` is still the sole concrete-member
        authority, while only numeric argument binding is generalized.
        """
        arg_nodes = tuple(copy.deepcopy(node) for node in argument_nodes)
        arg_token = tuple(ast.dump(node, include_attributes=False) for node in arg_nodes)
        token = ("context_scalar_accessor", ref_name, cell_name, arg_token)
        if token in self.memo:
            return self.memo[token]
        if not all(self.bound_numeric_expr_supported(node) for node in arg_nodes):
            raise FrontendError(
                f"model-bound context accessor {ref_name}.{cell_name} has an unsupported bounded argument"
            )

        description = f"model-bound numeric scalar accessor {ref_name}.{cell_name}"

        def evaluate(keys):
            values: list[Any] = []
            for run_key in keys:
                cell = self.frontend._context_cell_for_key(ref_name, cell_name, run_key)
                args = [self._bound_numeric_expr_value(node, run_key) for node in arg_nodes]
                try:
                    value = cell(*args)
                except Exception as exc:
                    raise FrontendError(
                        f"{description} could not be materialized: {type(exc).__name__}: {exc}"
                    ) from exc
                self._numeric_scalar(value, description)
                values.append(value)
            return values

        sample = evaluate(self.frontend.run_keys)
        dtype = self._numeric_dtype(sample, description)
        normalized_sample = self._coerce_numeric_values(sample, dtype, description)
        stable = bool(
            len(normalized_sample)
            and all(
                type(sample[i]) is type(sample[0]) and sample[i] == sample[0]
                for i in range(1, len(sample))
            )
        )
        key = self._key("ctxs" if stable else "ctxp")
        self.memo[token] = key
        if stable:
            def getter(keys, evaluate=evaluate, dtype=dtype, description=description):
                values = evaluate(keys)
                arr = self._coerce_numeric_values(values, dtype, description)
                if not len(arr):
                    raise FrontendError(f"{description} has an empty bound RunDomain")
                if np.any(arr != arr[0]):
                    raise FrontendError(
                        f"{description} is no longer point-independent over the bound RunDomain"
                    )
                return arr[0].item() if hasattr(arr[0], "item") else arr[0]
            self.specs[key] = InputSpec(
                key, dtype, 0, "global", getter, description,
                domain_token=repr((ref_name, cell_name, arg_token, "stable")),
                expected_shape=(),
            )
        else:
            def getter(keys, evaluate=evaluate, dtype=dtype, description=description):
                return self._coerce_numeric_values(evaluate(keys), dtype, description)
            self.specs[key] = InputSpec(
                key, dtype, 1, "point", getter, description,
                domain_token=repr((ref_name, cell_name, arg_token, "point")),
            )
        return key

    def context_point_accessor(
        self,
        ref_name: str,
        cell_name: str,
        argument_nodes: Sequence[ast.AST],
        point_position: int,
    ) -> str:
        """Materialize ``ref.member(static...)[point_coordinate]`` as point input."""
        arg_nodes = tuple(copy.deepcopy(node) for node in argument_nodes)
        arg_token = tuple(ast.dump(node, include_attributes=False) for node in arg_nodes)
        point_position = int(point_position)
        if point_position < 0 or point_position >= len(self.frontend.space_params):
            raise FrontendError("model-bound point accessor has an invalid point coordinate position")
        token = (
            "context_point_accessor", ref_name, cell_name, arg_token, point_position,
        )
        if token in self.memo:
            return self.memo[token]
        for node in arg_nodes:
            if not self.frontend._context_static_argument_is_fixed(node):
                raise FrontendError(
                    f"model-bound context accessor {ref_name}.{cell_name} has a dynamic argument"
                )
        description = f"model-bound numeric point accessor {ref_name}.{cell_name}"

        def selector(run_key):
            if len(self.frontend.space_params) == 1:
                return run_key
            if not isinstance(run_key, tuple) or len(run_key) != len(self.frontend.space_params):
                raise FrontendError(
                    f"{description} requires a tuple RunDomain key of length {len(self.frontend.space_params)}"
                )
            return run_key[point_position]

        def evaluate(keys):
            values: list[Any] = []
            for run_key in keys:
                cell = self.frontend._context_cell_for_key(ref_name, cell_name, run_key)
                args: list[Any] = []
                for node in arg_nodes:
                    ok, value = self.frontend._context_static_value(node, run_key)
                    if not ok:
                        raise FrontendError(
                            f"{description} static argument is no longer resolvable"
                        )
                    args.append(value)
                try:
                    container = cell(*args)
                    value = container[selector(run_key)]
                except Exception as exc:
                    raise FrontendError(
                        f"{description} could not be indexed/materialized: {type(exc).__name__}: {exc}"
                    ) from exc
                self._numeric_scalar(value, description)
                values.append(value)
            return values

        sample = evaluate(self.frontend.run_keys)
        dtype = self._numeric_dtype(sample, description)
        key = self._key("ctxp")
        self.memo[token] = key

        def getter(keys, evaluate=evaluate, dtype=dtype, description=description):
            return self._coerce_numeric_values(evaluate(keys), dtype, description)

        self.specs[key] = InputSpec(
            key, dtype, 1, "point", getter, description,
            domain_token=repr((ref_name, cell_name, arg_token, point_position)),
        )
        return key

    def point_ordinal(self) -> str:
        """Return the existing point-input ABI representation of row ordinal."""
        token = ("point_ordinal",)
        if token in self.memo:
            return self.memo[token]
        key = self._key("ctxord")
        self.memo[token] = key
        self.specs[key] = InputSpec(
            key, "int64", 1, "point",
            lambda keys: np.arange(len(keys), dtype=np.int64),
            "bound RunDomain point ordinal for model-bound coordinate input",
            domain_token=f"point_ordinal:{len(self.frontend.run_keys)}",
        )
        return key

    def context_coordinate_accessor(
        self,
        ref_name: str,
        cell_name: str,
        argument_nodes: Sequence[ast.AST],
        coordinate_name: str,
        coordinate_lo: int,
        coordinate_hi: int,
        coordinate_owner_uid: str,
        coordinate_step: int = 1,
    ) -> tuple[str, str]:
        """Materialize one direct context Cells call over point x exact coordinate.

        Every method argument is evaluated by the same bounded ABI-expression
        evaluator as V02387 selected-Space methods.  The exact coordinate domain
        remains owned by the canonical coordinate variant and is revalidated at
        bind time; generated code sees only the ordinary table/point ABI.
        """
        arg_nodes = tuple(copy.deepcopy(node) for node in argument_nodes)
        coordinate_name = str(coordinate_name)
        coordinate_lo = int(coordinate_lo)
        coordinate_hi = int(coordinate_hi)
        coordinate_owner_uid = str(coordinate_owner_uid)
        coordinate_step = int(coordinate_step)
        if coordinate_step != 1:
            raise FrontendError("model-bound coordinate accessor requires unit step")
        if coordinate_lo > coordinate_hi:
            raise FrontendError("model-bound coordinate accessor has an empty coordinate domain")
        if not arg_nodes or not all(
            self.bound_numeric_expr_supported(node, coordinate_name) for node in arg_nodes
        ):
            raise FrontendError(
                f"model-bound coordinate accessor {ref_name}.{cell_name} has an unsupported bounded argument"
            )
        if not any(
            self.bound_numeric_expr_uses_coordinate(node, coordinate_name) for node in arg_nodes
        ):
            raise FrontendError(
                f"model-bound coordinate accessor {ref_name}.{cell_name} is not coordinate dependent"
            )

        width = ((coordinate_hi - coordinate_lo) // coordinate_step) + 1
        if width * len(self.frontend.run_keys) > RUNTIME_SCALAR_HELPER_EXPANSION_LIMIT:
            raise FrontendError(
                f"model-bound coordinate accessor {ref_name}.{cell_name} materialization exceeds safety limit"
            )

        arg_token = tuple(ast.dump(node, include_attributes=False) for node in arg_nodes)
        coordinate_domain_identity = (
            coordinate_owner_uid, coordinate_name, coordinate_lo, coordinate_hi, coordinate_step,
            "exact_rank1_coordinate_v1",
        )
        token = (
            "context_coordinate_accessor", ref_name, cell_name, arg_token,
            coordinate_domain_identity,
        )
        if token in self.memo:
            return self.memo[token], self.point_ordinal()

        description = f"model-bound numeric coordinate accessor {ref_name}.{cell_name}"

        def validate_coordinate_domain() -> None:
            tr = self.frontend.variant_trace_by_uid.get(coordinate_owner_uid)
            if tr is None or tr.key.time_pos is None:
                raise FrontendError(f"{description} coordinate owner is no longer available")
            pos = int(tr.key.time_pos)
            if pos < 0 or pos >= len(tr.schema.parameters):
                raise FrontendError(f"{description} coordinate owner has invalid parameter geometry")
            if tr.schema.parameters[pos] != coordinate_name:
                raise FrontendError(f"{description} coordinate parameter identity changed")
            current = (
                self.frontend.specialized_coordinate_domains.get(coordinate_owner_uid)
                or self.frontend.coordinate_domains.get(coordinate_owner_uid)
            )
            if current is None:
                raise FrontendError(f"{description} coordinate domain is no longer proven")
            if int(current.lo) != coordinate_lo or int(current.hi) != coordinate_hi:
                raise FrontendError(f"{description} coordinate domain changed after compilation")

        def evaluate(keys):
            validate_coordinate_domain()
            rows: list[list[Any]] = []
            for run_key in keys:
                cell = self.frontend._context_cell_for_key(ref_name, cell_name, run_key)
                row: list[Any] = []
                for coordinate in range(coordinate_lo, coordinate_hi + 1, coordinate_step):
                    binding = (coordinate_name, int(coordinate))
                    args = [
                        self._bound_numeric_expr_value(node, run_key, binding)
                        for node in arg_nodes
                    ]
                    try:
                        value = cell(*args)
                    except Exception as exc:
                        raise FrontendError(
                            f"{description} could not be materialized at {coordinate_name}={coordinate}: "
                            f"{type(exc).__name__}: {exc}"
                        ) from exc
                    self._numeric_scalar(value, description)
                    row.append(value)
                rows.append(row)
            return rows

        sample_rows = evaluate(self.frontend.run_keys)
        flat_sample = [value for row in sample_rows for value in row]
        dtype = self._numeric_dtype(flat_sample, description)
        table_key = self._key("ctxcurve")
        self.memo[token] = table_key

        def getter(keys, evaluate=evaluate, dtype=dtype, description=description, width=width):
            rows = evaluate(keys)
            if any(len(row) != width for row in rows):
                raise FrontendError(f"{description} coordinate table width changed")
            flat = [value for row in rows for value in row]
            arr = self._coerce_numeric_values(flat, dtype, description)
            return np.ascontiguousarray(arr.reshape((len(rows), width)))

        self.specs[table_key] = InputSpec(
            table_key, dtype, 2, "global", getter, description,
            expected_shape=(len(self.frontend.run_keys), width),
            domain_token=repr((ref_name, cell_name, arg_token, coordinate_domain_identity)),
        )
        return table_key, self.point_ordinal()

    def external_dataframe_scalar(
        self, ref_name: str, cell_name: str, cell, row_key: Any, column: Any
    ) -> str:
        """Normalize one labelled external-DataFrame lookup to a numeric scalar input."""
        token = ("external_dataframe_scalar", ref_name, cell_name, repr(row_key), repr(column))
        if token in self.memo:
            return self.memo[token]
        frame = cell()
        if not isinstance(frame, pd.DataFrame):
            raise FrontendError(
                f"external table {ref_name}.{cell_name} no longer returns a DataFrame"
            )
        if column not in frame.columns:
            raise FrontendError(
                f"external table {ref_name}.{cell_name} has no column {column!r}"
            )
        try:
            sample = frame.loc[row_key, column]
        except Exception as exc:
            raise FrontendError(
                f"external table lookup {ref_name}.{cell_name}.loc[{row_key!r}, {column!r}] failed"
            ) from exc
        if isinstance(sample, (bool, np.bool_, int, np.integer)):
            dtype = "int64"
        elif isinstance(sample, (float, np.floating)):
            dtype = "float64"
        else:
            raise FrontendError(
                f"external table lookup {ref_name}.{cell_name} column {column!r} is non-numeric"
            )
        key = self._key("extt0")
        self.memo[token] = key
        expected_index = frame.index.copy()
        expected_columns = frame.columns.copy()

        def getter(keys, c=cell, rk=row_key, col=column, ei=expected_index, ec=expected_columns):
            current = c()
            if not isinstance(current, pd.DataFrame):
                raise FrontendError("external table provider changed type after compilation")
            if not current.index.equals(ei) or not current.columns.equals(ec):
                raise FrontendError("external table domain changed after compilation")
            return current.loc[rk, col]

        def domain_guard(c=cell, ei=expected_index, ec=expected_columns, rn=ref_name, cn=cell_name):
            current = c()
            if not isinstance(current, pd.DataFrame):
                return f"table_domain:{rn}.{cn}:type_changed"
            if not current.index.equals(ei):
                return f"table_domain:{rn}.{cn}:index_changed"
            if not current.columns.equals(ec):
                return f"table_domain:{rn}.{cn}:columns_changed"
            return None

        nlevels = int(frame.index.nlevels) if isinstance(frame.index, pd.MultiIndex) else 1
        row_parts = row_key if isinstance(row_key, tuple) else (row_key,)
        fixed = tuple((i, row_parts[i]) for i in range(min(nlevels, len(row_parts))))
        semantic = NormalizedTableInput(
            source_ref=ref_name, source_cell=cell_name, source_shape=tuple(frame.shape),
            index_names=tuple(frame.index.names), selected_column=column,
            fixed_row_labels=fixed, dynamic_level=None, dynamic_labels=(),
            axis_start=None, axis_step=None, result_kind="scalar",
        )
        self.specs[key] = InputSpec(
            key, dtype, 0, "global", getter,
            f"normalized external DataFrame scalar {ref_name}.{cell_name}[{column!r}]",
            domain_guard=domain_guard,
            domain_token=repr((tuple(frame.index.tolist()), tuple(frame.columns.tolist()))),
            expected_shape=(), normalized_table=semantic,
        )
        return key

    def external_dataframe_axis(
        self, ref_name: str, cell_name: str, cell, *, fixed_levels: dict[int, Any],
        dynamic_level: int, column: Any,
    ) -> tuple[str, int, int]:
        """Normalize a labelled table slice with one dynamic numeric row axis.

        Categorical/static row levels are selected during preparation.  The remaining
        numeric level becomes a dense 1-D numeric input plus an affine label->position
        mapping shared by Python and Cython through the canonical ``array_input`` op.
        """
        fixed_tuple = tuple(sorted((int(k), v) for k, v in fixed_levels.items()))
        token = (
            "external_dataframe_axis", ref_name, cell_name,
            tuple((k, repr(v)) for k, v in fixed_tuple), int(dynamic_level), repr(column),
        )
        if token in self.memo:
            key = self.memo[token]
            sem = self.specs[key].normalized_table
            assert sem is not None and sem.axis_start is not None and sem.axis_step is not None
            return key, int(sem.axis_start), int(sem.axis_step)
        frame = cell()
        if not isinstance(frame, pd.DataFrame):
            raise FrontendError(
                f"external table {ref_name}.{cell_name} no longer returns a DataFrame"
            )
        if column not in frame.columns:
            raise FrontendError(
                f"external table {ref_name}.{cell_name} has no column {column!r}"
            )
        nlevels = int(frame.index.nlevels) if isinstance(frame.index, pd.MultiIndex) else 1
        if dynamic_level < 0 or dynamic_level >= nlevels:
            raise FrontendError("external table dynamic level is outside the row index")
        if any(level < 0 or level >= nlevels or level == dynamic_level for level, _ in fixed_tuple):
            raise FrontendError("invalid fixed level in normalized external table lookup")
        positions: list[int] = []
        labels: list[Any] = []
        for pos, label in enumerate(frame.index):
            parts = label if isinstance(label, tuple) else (label,)
            if all(parts[level] == value for level, value in fixed_tuple):
                positions.append(pos)
                labels.append(parts[dynamic_level])
        if not positions:
            raise FrontendError(
                f"external table {ref_name}.{cell_name} has no rows for fixed labels {fixed_tuple!r}"
            )
        numeric_labels, start, step = _safe_numeric_axis(labels)
        if len(set(numeric_labels)) != len(numeric_labels):
            raise FrontendError("external table dynamic row axis is not unique after fixed-level selection")
        order = np.asarray(sorted(range(len(numeric_labels)), key=lambda i: numeric_labels[i]), dtype=np.intp)
        positions_arr = np.asarray(positions, dtype=np.intp)[order]
        sorted_labels = tuple(numeric_labels[i] for i in order)
        col_kind = np.asarray(frame[column]).dtype.kind
        if col_kind in "iub":
            dtype = "int64"
        elif col_kind in "fc":
            dtype = "float64"
        else:
            raise FrontendError(
                f"external table {ref_name}.{cell_name} column {column!r} is non-numeric"
            )
        key = self._key("extt1")
        self.memo[token] = key
        expected_index = frame.index.copy()
        expected_columns = frame.columns.copy()

        def getter(keys, c=cell, col=column, pos=positions_arr, ei=expected_index, ec=expected_columns):
            current = c()
            if not isinstance(current, pd.DataFrame):
                raise FrontendError("external table provider changed type after compilation")
            if not current.index.equals(ei) or not current.columns.equals(ec):
                raise FrontendError("external table domain changed after compilation")
            arr = current[col].to_numpy(copy=False)[pos]
            return np.ascontiguousarray(arr)

        def domain_guard(c=cell, ei=expected_index, ec=expected_columns, rn=ref_name, cn=cell_name):
            current = c()
            if not isinstance(current, pd.DataFrame):
                return f"table_domain:{rn}.{cn}:type_changed"
            if not current.index.equals(ei):
                return f"table_domain:{rn}.{cn}:index_changed"
            if not current.columns.equals(ec):
                return f"table_domain:{rn}.{cn}:columns_changed"
            return None

        semantic = NormalizedTableInput(
            source_ref=ref_name, source_cell=cell_name, source_shape=tuple(frame.shape),
            index_names=tuple(frame.index.names), selected_column=column,
            fixed_row_labels=fixed_tuple, dynamic_level=int(dynamic_level),
            dynamic_labels=sorted_labels, axis_start=int(start), axis_step=int(step),
            result_kind="axis1d",
        )
        self.specs[key] = InputSpec(
            key, dtype, 1, "global", getter,
            f"normalized external DataFrame axis {ref_name}.{cell_name}[{column!r}]",
            domain_guard=domain_guard,
            domain_token=repr((tuple(frame.index.tolist()), tuple(frame.columns.tolist()))),
            expected_shape=(len(sorted_labels),), normalized_table=semantic,
        )
        return key, int(start), int(step)

    def external_dataframe_exact_nd(
        self,
        ref_name: str,
        cell_name: str,
        cell,
        *,
        fixed_levels: dict[int, Any],
        dynamic_axes: Sequence[NormalizedTableAxis],
        column: Any,
    ) -> tuple[str, str | None, str]:
        """Normalize an exact N-D labelled lookup to numeric backend inputs.

        Static row levels are removed during preparation.  Runtime selector axes
        are already encoded as integer positions by the source normalizer.  A
        Cartesian table becomes one dense ndarray; a non-Cartesian finite table
        becomes an integer key matrix plus a value vector.  Missing sparse keys
        therefore retain source ``.loc`` semantics rather than being silently
        filled with a numeric sentinel.
        """
        if not dynamic_axes:
            raise FrontendError("exact N-D table normalization requires at least one dynamic axis")
        fixed_tuple = tuple(sorted((int(k), v) for k, v in fixed_levels.items()))
        axes = tuple(dynamic_axes)
        token = (
            "external_dataframe_exact_nd", ref_name, cell_name,
            tuple((k, repr(v)) for k, v in fixed_tuple), repr(column),
            tuple((a.level, a.selector_kind, tuple(map(repr, a.labels))) for a in axes),
        )
        if token in self.memo:
            value_key, sparse_key, layout = self.memo[token]
            return value_key, sparse_key, layout

        frame = cell()
        if not isinstance(frame, pd.DataFrame):
            raise FrontendError(f"external table {ref_name}.{cell_name} no longer returns a DataFrame")
        if column not in frame.columns:
            raise FrontendError(f"external table {ref_name}.{cell_name} has no column {column!r}")
        nlevels = int(frame.index.nlevels) if isinstance(frame.index, pd.MultiIndex) else 1
        dynamic_levels = tuple(int(a.level) for a in axes)
        if len(set(dynamic_levels)) != len(dynamic_levels):
            raise FrontendError("normalized exact table lookup repeats a dynamic index level")
        if any(level < 0 or level >= nlevels for level in dynamic_levels):
            raise FrontendError("normalized exact table lookup has a dynamic level outside the table index")
        if any(level < 0 or level >= nlevels or level in dynamic_levels for level, _ in fixed_tuple):
            raise FrontendError("normalized exact table lookup has an invalid fixed level")

        label_codes: list[dict[Any, int]] = []
        for axis in axes:
            if not axis.labels or len(set(axis.labels)) != len(axis.labels):
                raise FrontendError(
                    f"normalized exact table axis {axis.index_name!r} must have a non-empty unique label domain"
                )
            label_codes.append({label: i for i, label in enumerate(axis.labels)})

        positions: list[int] = []
        encoded_keys: list[tuple[int, ...]] = []
        for pos, label in enumerate(frame.index):
            parts = label if isinstance(label, tuple) else (label,)
            if not all(parts[level] == value for level, value in fixed_tuple):
                continue
            try:
                key_tuple = tuple(
                    label_codes[j][parts[axis.level]] for j, axis in enumerate(axes)
                )
            except KeyError:
                # The source table may contain labels outside the proven runtime
                # selector domain. They are irrelevant to this compiled lookup.
                continue
            positions.append(pos)
            encoded_keys.append(key_tuple)
        if not positions:
            raise FrontendError(
                f"external table {ref_name}.{cell_name} has no rows in the normalized selector domain"
            )
        if len(set(encoded_keys)) != len(encoded_keys):
            raise FrontendError("normalized exact table lookup does not have unique dynamic keys")

        shape = tuple(len(a.labels) for a in axes)
        expected_count = int(np.prod(shape, dtype=np.int64))
        full_keys = set(__import__("itertools").product(*(range(n) for n in shape)))
        dense = len(encoded_keys) == expected_count and set(encoded_keys) == full_keys
        layout = "dense_cartesian" if dense else "sparse_finite_keys"

        col_kind = np.asarray(frame[column]).dtype.kind
        if col_kind in "iub":
            dtype = "int64"
            np_dtype = np.int64
        elif col_kind in "fc":
            dtype = "float64"
            np_dtype = np.float64
        else:
            raise FrontendError(
                f"external table {ref_name}.{cell_name} column {column!r} is non-numeric"
            )

        expected_index = frame.index.copy()
        expected_columns = frame.columns.copy()
        positions_arr = np.asarray(positions, dtype=np.intp)

        def current(c=cell, ei=expected_index, ec=expected_columns):
            table = c()
            if not isinstance(table, pd.DataFrame):
                raise FrontendError("external exact table provider changed type after compilation")
            if not table.index.equals(ei) or not table.columns.equals(ec):
                raise FrontendError("external exact table domain changed after compilation")
            return table

        def domain_guard(current=current, rn=ref_name, cn=cell_name):
            try:
                current()
            except FrontendError as exc:
                return f"table_domain:{rn}.{cn}:{exc}"
            return None

        value_key = self._key("exttn")
        sparse_key: str | None = None
        semantic = NormalizedTableInput(
            source_ref=ref_name,
            source_cell=cell_name,
            source_shape=tuple(frame.shape),
            index_names=tuple(frame.index.names),
            selected_column=column,
            fixed_row_labels=fixed_tuple,
            dynamic_level=None,
            dynamic_labels=(),
            axis_start=None,
            axis_step=None,
            result_kind="exact_nd",
            layout=layout,
            dynamic_axes=axes,
        )

        if dense:
            position_by_key = {key: pos for key, pos in zip(encoded_keys, positions)}
            order = np.asarray(
                [position_by_key[key] for key in __import__("itertools").product(*(range(n) for n in shape))],
                dtype=np.intp,
            )

            def getter(keys, current=current, col=column, order=order, shape=shape, dt=np_dtype):
                arr = current()[col].to_numpy(copy=False)[order]
                return np.ascontiguousarray(arr, dtype=dt).reshape(shape)

            self.specs[value_key] = InputSpec(
                value_key, dtype, len(shape), "global", getter,
                f"normalized dense exact table {ref_name}.{cell_name}[{column!r}]",
                domain_guard=domain_guard,
                domain_token=repr((tuple(frame.index.tolist()), tuple(frame.columns.tolist()), layout, shape)),
                expected_shape=shape,
                normalized_table=semantic,
            )
        else:
            encoded_arr = np.ascontiguousarray(np.asarray(encoded_keys, dtype=np.int64))
            sparse_key = self._key("exttk")
            semantic = NormalizedTableInput(
                **{**semantic.__dict__, "sparse_key_input": sparse_key}
            )

            def key_getter(keys, arr=encoded_arr):
                return arr

            def value_getter(keys, current=current, col=column, pos=positions_arr, dt=np_dtype):
                arr = current()[col].to_numpy(copy=False)[pos]
                return np.ascontiguousarray(arr, dtype=dt)

            self.specs[sparse_key] = InputSpec(
                sparse_key, "int64", 2, "global", key_getter,
                f"normalized sparse exact table keys {ref_name}.{cell_name}[{column!r}]",
                domain_token=repr((layout, tuple(encoded_keys))),
                expected_shape=tuple(encoded_arr.shape),
            )
            self.specs[value_key] = InputSpec(
                value_key, dtype, 1, "global", value_getter,
                f"normalized sparse exact table values {ref_name}.{cell_name}[{column!r}]",
                domain_guard=domain_guard,
                domain_token=repr((tuple(frame.index.tolist()), tuple(frame.columns.tolist()), layout)),
                expected_shape=(len(positions),),
                normalized_table=semantic,
            )

        self.memo[token] = (value_key, sparse_key, layout)
        return value_key, sparse_key, layout

    def external_dataframe_row_axis_extreme(
        self,
        ref_name: str,
        cell_name: str,
        cell,
        *,
        fixed_levels: Mapping[int, Any],
        dynamic_axes: Sequence[NormalizedTableAxis],
        residual_level: int,
        extreme: str,
    ) -> tuple[str, str | None, str]:
        """Normalize ``row_view.index.min/max`` to numeric metadata ABI.

        The source row view must fix every MultiIndex level except one residual
        integral axis.  Runtime selectors address only the fixed-prefix domain;
        preparation derives the exact min/max residual label for every admitted
        prefix.  Pandas objects therefore remain preparation-only.
        """
        if extreme not in {"min", "max"}:
            raise FrontendError(f"unsupported row-view index extreme {extreme!r}")
        fixed_tuple = tuple(sorted((int(k), v) for k, v in fixed_levels.items()))
        axes = tuple(dynamic_axes)
        token = (
            "external_dataframe_row_axis_extreme", ref_name, cell_name,
            tuple((k, repr(v)) for k, v in fixed_tuple),
            tuple((a.level, a.selector_kind, tuple(map(repr, a.labels))) for a in axes),
            int(residual_level), extreme,
        )
        if token in self.memo:
            value_key, sparse_key, layout = self.memo[token]
            return value_key, sparse_key, layout

        frame = cell()
        if not isinstance(frame, pd.DataFrame) or not isinstance(frame.index, pd.MultiIndex):
            raise FrontendError(
                f"external table {ref_name}.{cell_name} row-axis metadata requires a MultiIndex DataFrame"
            )
        nlevels = int(frame.index.nlevels)
        residual_level = int(residual_level)
        dynamic_levels = tuple(int(a.level) for a in axes)
        if residual_level < 0 or residual_level >= nlevels:
            raise FrontendError("row-view residual axis is outside the table index")
        if len(set(dynamic_levels)) != len(dynamic_levels):
            raise FrontendError("row-view metadata repeats a dynamic prefix level")
        accounted = set(dynamic_levels) | {k for k, _ in fixed_tuple} | {residual_level}
        if accounted != set(range(nlevels)):
            raise FrontendError(
                "row-view axis metadata requires every non-residual index level to be fixed or dynamic"
            )
        if residual_level in dynamic_levels or any(k == residual_level for k, _ in fixed_tuple):
            raise FrontendError("row-view residual axis cannot also be a prefix selector")

        label_codes: list[dict[Any, int]] = []
        for axis in axes:
            if not axis.labels or len(set(axis.labels)) != len(axis.labels):
                raise FrontendError("row-view metadata dynamic axis must have unique labels")
            label_codes.append({label: i for i, label in enumerate(axis.labels)})

        grouped: dict[tuple[int, ...], list[int]] = {}
        for label in frame.index:
            parts = label if isinstance(label, tuple) else (label,)
            if not all(parts[level] == value for level, value in fixed_tuple):
                continue
            try:
                key_tuple = tuple(
                    label_codes[j][parts[axis.level]] for j, axis in enumerate(axes)
                )
            except KeyError:
                continue
            raw = parts[residual_level]
            if not isinstance(raw, (int, np.integer)) or isinstance(raw, (bool, np.bool_)):
                raise FrontendError(
                    f"external table {ref_name}.{cell_name} residual index level "
                    f"{residual_level} must be integral for row-view min/max metadata"
                )
            grouped.setdefault(key_tuple, []).append(int(raw))
        if not grouped:
            raise FrontendError(
                f"external table {ref_name}.{cell_name} has no rows in the normalized row-view prefix domain"
            )

        encoded_keys = tuple(sorted(grouped))
        values_by_key = {
            key: (min(values) if extreme == "min" else max(values))
            for key, values in grouped.items()
        }
        shape = tuple(len(a.labels) for a in axes)
        full_keys = set(__import__("itertools").product(*(range(n) for n in shape)))
        dense = set(encoded_keys) == full_keys
        layout = "dense_cartesian" if dense else "sparse_finite_keys"

        expected_index = frame.index.copy()
        expected_columns = frame.columns.copy()

        def current(c=cell, ei=expected_index, ec=expected_columns):
            table = c()
            if not isinstance(table, pd.DataFrame):
                raise FrontendError("row-view metadata provider changed type after compilation")
            if not table.index.equals(ei) or not table.columns.equals(ec):
                raise FrontendError("row-view metadata table domain changed after compilation")
            return table

        def domain_guard(current=current, rn=ref_name, cn=cell_name):
            try:
                current()
            except FrontendError as exc:
                return f"table_domain:{rn}.{cn}:{exc}"
            return None

        value_key = self._key("extmeta")
        sparse_key: str | None = None
        semantic = NormalizedTableInput(
            source_ref=ref_name,
            source_cell=cell_name,
            source_shape=tuple(frame.shape),
            index_names=tuple(frame.index.names),
            selected_column=None,
            fixed_row_labels=fixed_tuple,
            dynamic_level=None,
            dynamic_labels=(),
            axis_start=None,
            axis_step=None,
            result_kind="axis_metadata_scalar",
            layout=layout,
            dynamic_axes=axes,
            sparse_key_input=None,
            metadata_kind=f"index_{extreme}",
            metadata_level=residual_level,
        )

        if dense:
            order = tuple(__import__("itertools").product(*(range(n) for n in shape)))
            dense_values = np.asarray([values_by_key[key] for key in order], dtype=np.int64).reshape(shape)

            def getter(keys, current=current, arr=dense_values):
                current()
                return np.ascontiguousarray(arr, dtype=np.int64)

            self.specs[value_key] = InputSpec(
                value_key, "int64", len(shape), "global", getter,
                f"normalized row-view index {extreme} metadata {ref_name}.{cell_name}",
                domain_guard=domain_guard,
                domain_token=repr((tuple(frame.index.tolist()), tuple(frame.columns.tolist()), extreme, residual_level, shape)),
                expected_shape=shape,
                normalized_table=semantic,
            )
        else:
            encoded_arr = np.ascontiguousarray(np.asarray(encoded_keys, dtype=np.int64))
            values_arr = np.ascontiguousarray(
                np.asarray([values_by_key[key] for key in encoded_keys], dtype=np.int64)
            )
            sparse_key = self._key("extmetak")
            semantic = NormalizedTableInput(
                **{**semantic.__dict__, "sparse_key_input": sparse_key}
            )

            def key_getter(keys, current=current, arr=encoded_arr):
                current()
                return arr

            def value_getter(keys, current=current, arr=values_arr):
                current()
                return arr

            self.specs[sparse_key] = InputSpec(
                sparse_key, "int64", 2, "global", key_getter,
                f"normalized sparse row-view metadata keys {ref_name}.{cell_name}",
                domain_guard=domain_guard,
                domain_token=repr((layout, encoded_keys)),
                expected_shape=tuple(encoded_arr.shape),
            )
            self.specs[value_key] = InputSpec(
                value_key, "int64", 1, "global", value_getter,
                f"normalized sparse row-view index {extreme} metadata {ref_name}.{cell_name}",
                domain_guard=domain_guard,
                domain_token=repr((tuple(frame.index.tolist()), tuple(frame.columns.tolist()), extreme, residual_level, layout)),
                expected_shape=(len(encoded_keys),),
                normalized_table=semantic,
            )

        self.memo[token] = (value_key, sparse_key, layout)
        return value_key, sparse_key, layout


class GraphModelCompiler:
    """Graph-guided, name-agnostic frontend for the native optimizer.

    The caller identifies the Space, output Cell and representative ItemSpace keys.
    All semantic properties (time parameter, variants, types, lags and phase
    boundaries) are inferred from the modelx calculation graph and formulas.
    """

    def __init__(
        self,
        model,
        *,
        space,
        output: str,
        sample_keys: Sequence[Any],
        run_keys: Sequence[Any] | None = None,
        output_invocation: OutputInvocation | None = None,
        run_domain: RunDomain | None = None,
        fallback_cells: Sequence[str] = (),
        trace_capture: TraceCapture | None = None,
        realized_graph_only: bool = False,
        recovered_loop_evidence: Any | None = None,
        recovered_loop_evidence_provider: Any | None = None,
        canonical_schedule_authority: bool = False,
        legacy_comparison: bool | None = None,
    ):
        self.model = model
        self.space = space
        self.output_invocation = (
            output_invocation
            if output_invocation is not None
            else OutputInvocation.fixed(str(output), (), ())
        )
        if self.output_invocation.output_name != str(output):
            raise FrontendError(
                "OutputInvocation output name does not match GraphModelCompiler output"
            )
        self.output = self.output_invocation.output_name
        self.sample_keys = tuple(sample_keys)
        self.fallback_cells = frozenset(fallback_cells)
        self.realized_graph_only = bool(realized_graph_only)
        self.recovered_loop_evidence = recovered_loop_evidence
        self.recovered_loop_evidence_provider = recovered_loop_evidence_provider
        self.canonical_schedule_authority_enabled = bool(canonical_schedule_authority)
        # Canonical-authority compilation is production-direct by default.  Mature
        # ExecutableGraph construction survives only for the pre-canonical
        # compatibility path or when comparison mode is explicitly requested.
        self.legacy_comparison_enabled = (
            not self.canonical_schedule_authority_enabled
            if legacy_comparison is None else bool(legacy_comparison)
        )
        unknown_fallbacks = self.fallback_cells - set(space.cells)
        if unknown_fallbacks:
            raise FrontendError(f"unknown fallback Cells: {sorted(unknown_fallbacks)!r}")
        for name in self.fallback_cells:
            if space.cells[name].parameters:
                raise FrontendError(
                    f"regional fallback Cell {name!r} must currently be zero-argument within the ItemSpace"
                )
        self.fallback_input_by_name: dict[str, str] = {}
        self.refs = dict(space.refs)
        self.space_params = tuple(space.parameters or ())
        self.space_param = self.space_params[0] if self.space_params else None
        if run_domain is not None:
            if tuple(run_domain.itemspace_parameter_names) != self.space_params:
                raise FrontendError(
                    "RunDomain ItemSpace parameters do not match the selected Space"
                )
            if str(getattr(space, "fullname", None) or getattr(space, "name", "<space>")) != run_domain.space_fullname:
                raise FrontendError(
                    "RunDomain structural Space does not match the selected Space"
                )
            if run_keys is not None and tuple(run_keys) != tuple(run_domain.run_keys):
                raise FrontendError("run_keys disagree with explicit RunDomain")
            self.run_domain = run_domain
            self.run_keys = tuple(run_domain.run_keys)
        else:
            resolved_keys = tuple(run_keys) if run_keys is not None else self._infer_run_keys()
            try:
                self.run_domain = RunDomain.finite(
                    space_fullname=str(getattr(space, "fullname", None) or getattr(space, "name", "<space>")),
                    itemspace_parameter_names=self.space_params,
                    run_keys=resolved_keys,
                )
            except (TypeError, ValueError) as exc:
                raise FrontendError(str(exc)) from exc
            self.run_keys = tuple(self.run_domain.run_keys)
        self.result_domain = ResultDomain.scalar_per_run_key(self.run_domain)
        self.multiindex_axes: dict[str, tuple[int,int,int,int]] = {}
        self.registry = InputRegistry(self)
        self.model_point_row = self._detect_point_row_cell()

        self.trace = (
            trace_capture
            if trace_capture is not None
            else capture_trace(
                model,
                lambda k: getattr(self._space_instance(k), self.output).node(
                    *self.output_invocation.argument_values
                ),
                self.sample_keys,
            )
        )
        self.trace_source = "realized_trace" if trace_capture is not None else "capture_trace"

        # Trace closures may contain Cells from external Spaces with the same
        # short name as a Cell in the selected Space.  Compiler identity is the
        # full Cell schema, never the name alone.  This map is also intentionally
        # source-sensitive so an inherited/overridden formula cannot be mistaken
        # for another Space's implementation.
        self.selected_schema_uid_by_name = {
            name: CellSchema(
                cell.fullname, name, tuple(cell.parameters), cell.formula.source
            ).uid
            for name, cell in space.cells.items()
            if cell.formula is not None
        }
        self.selected_trace_variants = {
            vk: tr for vk, tr in self.trace.variants.items()
            if self.selected_schema_uid_by_name.get(tr.schema.name) == tr.schema.uid
        }

        explicit = [
            tr.schema.fullname for tr in self.selected_trace_variants.values()
            if tr.has_input_values and tr.schema.name not in self.fallback_cells
        ]
        if explicit:
            raise FrontendError(
                "explicit Cell input values are present in the sampled closure; native seed/input lowering "
                "is not implemented, so fallback is required: " + ", ".join(sorted(set(explicit)))
            )
        self.base_funcs = {name: ast.parse(cell.formula.source).body[0] for name, cell in space.cells.items() if cell.formula is not None}
        # Source ValueSemantics is a positive admission gate for execution PureMaps.
        # Reconstruct one source module from the exact selected-Space formulas; free
        # model inputs remain immutable source evidence, while inter-Cell calls retain
        # their real names and recurrence structure.  This evidence never replaces
        # canonical specialization; it only prevents StateDerivedMaps from being
        # promoted by an accidentally acyclic specialized closure.
        _semantics_source = ast.unparse(
            ast.fix_missing_locations(
                ast.Module(
                    body=[copy.deepcopy(self.base_funcs[name]) for name in sorted(self.base_funcs)],
                    type_ignores=[],
                )
            )
        )
        self.source_value_semantics = {
            row.uid: row
            for row in classify_source_value_semantics(_semantics_source)
        }
        self.source_pure_map_names = frozenset(
            uid for uid, row in self.source_value_semantics.items()
            if row.semantic_class == "pure_map"
        )

        # A regional fallback Cell is a terminal dependency from the compiled
        # artifact's perspective.  Compute the source-level closure with those
        # identities cut before lowering any formulas.  This prevents unsupported
        # formulas upstream of a fallback boundary from being needlessly parsed as
        # native code (and is essential when several fallback islands exist in one
        # original modelx trace).
        self.compiled_source_names: set[str] = set()
        stack = [self.output]
        while stack:
            name = stack.pop()
            if name in self.compiled_source_names or name in self.fallback_cells:
                continue
            if name not in self.base_funcs:
                continue
            self.compiled_source_names.add(name)
            fn = self.base_funcs[name]
            for node in ast.walk(fn):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    dep = node.func.id
                    if dep in self.base_funcs and dep not in self.fallback_cells:
                        stack.append(dep)
                elif isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name):
                    dep = node.value.id
                    if dep in self.base_funcs and dep not in self.fallback_cells:
                        stack.append(dep)

        self.schema_by_name = {}
        for tr in self.selected_trace_variants.values():
            self.schema_by_name.setdefault(tr.schema.name, tr.schema)
        self.variant_trace_by_uid = {tr.uid: tr for tr in self.selected_trace_variants.values()}
        self.variants_by_cell_aux: dict[tuple[str, tuple[Any,...]], str] = {}
        for tr in self.selected_trace_variants.values():
            self.variants_by_cell_aux[(tr.schema.name, tr.key.aux_values)] = tr.uid
        self.validated_enum_cells = self._discover_validated_enum_cells()
        self.validated_point_scalar_cells = self._discover_validated_point_scalar_cells()
        self._static_variant_value_cache: dict[str, tuple[bool, Any]] = {}
        self._finite_variant_domain_cache: dict[str, tuple[bool, tuple[Any, ...]]] = {}
        self._static_reference_value_cache: dict[str, tuple[bool, Any]] = {}
        self._used_static_facts: dict[tuple[str, str], StaticScalarFact] = {}
        self._normalized_operators: dict[str, NormalizedOperator] = {}
        self._used_validated_static_facts: dict[str, ValidatedStaticFact] = {}
        self._used_finite_domain_facts: dict[tuple[str, str], FiniteDomainFact] = {}
        self._fixed_coordinate_uid_by_key: dict[tuple[str, int], str] = {}
        self._fixed_coordinate_requests: dict[str, tuple[str, int]] = {}
        self._used_fixed_coordinate_facts: dict[str, FixedCoordinateFact] = {}
        self._fixed_coordinate_limit = 128
        self._future_coordinate_source_cache: dict[str, bool] = {}
        self.coordinate_recurrence_facts: tuple[CoordinateRecurrenceDomainFact, ...] = ()
        self._runtime_scalar_helper_inline_stack: list[str] = []
        self._runtime_scalar_helper_expansion_limit = RUNTIME_SCALAR_HELPER_EXPANSION_LIMIT
        self._used_runtime_scalar_helper_facts: dict[str, RuntimeScalarHelperFact] = {}
        self._static_point_field_cache: dict[str, tuple[bool, Any]] = {}
        self._coordinate_constant_cache: dict[str, tuple[bool, Any]] = {}
        self.coordinate_domains: dict[str, _IntDomain] = {}
        # A later, demand-graph proof over already-specialized canonical source.
        # Unlike ``coordinate_domains`` above, this pass can consume literal
        # auxiliary specialization, source-semantic dead-tail pruning and
        # source-backed scheduled variants discovered during canonical demand.
        # It exists specifically to prove call-site preconditions such as an
        # irregular step lookup's first-anchor lower bound.  It must never be
        # populated from representative observed times.
        self.specialized_coordinate_domains: dict[str, _IntDomain] = {}
        self.primary_coordinate_domain: _IntDomain | None = None
        # Partial source-proven bounds for lookup/domain proofs when the physical
        # reduction range is not exact over the full RunDomain (for example a
        # policy-varying stop with a fixed positive start).  Scheduling continues
        # to use only ``primary_coordinate_domain`` exact intervals.
        self.primary_coordinate_bounds: tuple[int | None, int | None] = (None, None)
        self.primary_coordinate_affine_constraint: AffineRangeConstraint | None = None
        self.coordinate_domain_notes: list[str] = []
        self._source_recursive_reach_cache: dict[str, bool] = {}
        self._source_backed_helper_cache: dict[str, bool] = {}
        self._source_backed_scheduled_uid_by_key: dict[tuple[str, tuple[Any, ...]], str] = {}
        self._used_source_backed_scheduled_facts: dict[str, SourceBackedScheduledFact] = {}
        self._used_step_lookup_domain_facts: dict[tuple[Any, ...], StepLookupDomainFact] = {}
        self._canonical_proof_snapshot: CanonicalProofSnapshot | None = None

        # The broad frontend remains source-complete.  NativeBatch has a narrower
        # contract: one compiled artifact represents one realized graph family.
        # Source branches absent from that graph are not pulled into the artifact;
        # a policy that takes another graph belongs to another backend/artifact.
        if not self.realized_graph_only:
            self._preflight_observed_dependencies()

        self.ir = build_graph_ir(self.trace)
        self.vector_elements = self._discover_vector_helpers()
        # Coordinate-domain discovery is a proof prepass.  It may consult the same
        # static-value machinery used by real specialization, but must not itself
        # perturb the generated ABI/input order.  Retain caches, restore registrations.
        saved_registry=(dict(self.registry.specs),dict(self.registry.memo),int(self.registry.counter))
        saved_static=dict(self._used_static_facts)
        saved_validated=dict(self._used_validated_static_facts)
        saved_finite=dict(self._used_finite_domain_facts)
        recurrence_facts: tuple[CoordinateRecurrenceDomainFact, ...] = ()
        try:
            self.coordinate_domains = self._derive_coordinate_domains()
            recurrence_facts = self._derive_coordinate_recurrence_facts(
                self.coordinate_domains
            )
        finally:
            self.registry.specs,self.registry.memo,self.registry.counter=saved_registry
            self._used_static_facts=saved_static
            self._used_validated_static_facts=saved_validated
            self._used_finite_domain_facts=saved_finite
        self.coordinate_recurrence_facts = recurrence_facts
        self.canonical = self._build_canonical()


    def _discover_validated_enum_cells(self) -> dict[str, ValidatedEnumCell]:
        """Recognize a tiny validated categorical-selector source pattern.

        The accepted form is intentionally structural and name-agnostic::

            v = model_point()["field"]
            if v not in ("A", "B", ...):
                raise ValueError(...)
            return v

        The selector may then be proven static over the explicit ``run_keys``
        domain without erasing the original validation contract: a numeric enum
        validation input is retained in the optimized program.
        """
        if self.model_point_row is None:
            return {}
        point_name = self.model_point_row.cell_name
        out: dict[str, ValidatedEnumCell] = {}
        for name, original in self.base_funcs.items():
            fn = _strip_docstring(copy.deepcopy(original))
            if fn.args.args or fn.args.posonlyargs or fn.args.kwonlyargs or fn.args.vararg or fn.args.kwarg:
                continue
            body = list(fn.body)
            if len(body) != 3:
                continue
            assign, guard, ret = body
            if not (
                isinstance(assign, ast.Assign) and len(assign.targets) == 1
                and isinstance(assign.targets[0], ast.Name)
                and isinstance(assign.value, ast.Subscript)
                and isinstance(assign.value.value, ast.Call)
                and isinstance(assign.value.value.func, ast.Name)
                and assign.value.value.func.id == point_name
                and not assign.value.value.args and not assign.value.value.keywords
                and isinstance(assign.value.slice, ast.Constant)
                and isinstance(assign.value.slice.value, str)
            ):
                continue
            local = assign.targets[0].id
            if not (
                isinstance(guard, ast.If) and not guard.orelse
                and isinstance(guard.test, ast.Compare)
                and isinstance(guard.test.left, ast.Name) and guard.test.left.id == local
                and len(guard.test.ops) == 1 and isinstance(guard.test.ops[0], ast.NotIn)
                and len(guard.test.comparators) == 1
                and isinstance(ret, ast.Return)
                and isinstance(ret.value, ast.Name) and ret.value.id == local
                and any(isinstance(node, ast.Raise) for node in ast.walk(guard))
            ):
                continue
            domain_node = guard.test.comparators[0]
            if not isinstance(domain_node, (ast.Tuple, ast.List, ast.Set)):
                continue
            labels: list[str] = []
            for elt in domain_node.elts:
                if not isinstance(elt, ast.Constant) or not isinstance(elt.value, str):
                    break
                labels.append(elt.value)
            else:
                if 1 <= len(labels) <= 16 and len(set(labels)) == len(labels):
                    out[name] = ValidatedEnumCell(
                        field=str(assign.value.slice.value), allowed_values=tuple(labels)
                    )
        return out

    def _discover_validated_point_scalar_cells(self) -> dict[str, ValidatedPointScalarCell]:
        """Recognize exact-value-safe numeric/bool point selectors with guards.

        Accepted selectors have one point-field assignment, one or more guard Ifs
        containing a raise, and a final return of the assigned local.  The guard is
        not discarded here: `_proven_static_cell_value` later substitutes the proven
        scalar and requires each guard test to fold to literal False.
        """
        if self.model_point_row is None:
            return {}
        point_name = self.model_point_row.cell_name
        out: dict[str, ValidatedPointScalarCell] = {}

        def point_field_expr(expr: ast.AST):
            cast = None
            inner = expr
            if (
                isinstance(inner, ast.Call) and isinstance(inner.func, ast.Name)
                and inner.func.id in {"bool", "int", "float"}
                and len(inner.args) == 1 and not inner.keywords
            ):
                cast = inner.func.id
                inner = inner.args[0]
            if not (
                isinstance(inner, ast.Subscript)
                and isinstance(inner.value, ast.Call)
                and isinstance(inner.value.func, ast.Name)
                and inner.value.func.id == point_name
                and not inner.value.args and not inner.value.keywords
                and isinstance(inner.slice, ast.Constant)
                and isinstance(inner.slice.value, str)
            ):
                return None
            return str(inner.slice.value), cast

        for name, original in self.base_funcs.items():
            if name in self.validated_enum_cells:
                continue
            fn = _strip_docstring(copy.deepcopy(original))
            if fn.args.args or fn.args.posonlyargs or fn.args.kwonlyargs or fn.args.vararg or fn.args.kwarg:
                continue
            if len(fn.body) < 3:
                continue
            assign, *middle, ret = fn.body
            if not (
                isinstance(assign, ast.Assign) and len(assign.targets) == 1
                and isinstance(assign.targets[0], ast.Name)
                and isinstance(ret, ast.Return) and isinstance(ret.value, ast.Name)
                and ret.value.id == assign.targets[0].id
            ):
                continue
            parsed = point_field_expr(assign.value)
            if parsed is None:
                continue
            local = assign.targets[0].id
            guards = [
                st for st in middle
                if isinstance(st, ast.If) and any(isinstance(node, ast.Raise) for node in ast.walk(st))
            ]
            if not guards or len(guards) != len(middle):
                continue
            # Every guard must actually depend on the assigned selector.
            if not all(any(isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load) and n.id == local for n in ast.walk(g.test)) for g in guards):
                continue
            field, cast = parsed
            out[name] = ValidatedPointScalarCell(field=field, cast=cast)
        return out

    def _proven_static_variant_value(self, uid: str) -> tuple[bool, Any]:
        """Prove one non-coordinate Cell variant is constant over the build run domain.

        This is compile-time preparation only.  It is used narrowly by table-key
        normalization so categorical labels can disappear before Python/Cython
        emission.  If values differ across ``run_keys`` the proof fails closed.
        """
        cached = self._static_variant_value_cache.get(uid)
        if cached is not None:
            return cached
        tr = self.variant_trace_by_uid.get(uid)
        if tr is None or tr.key.time_pos is not None:
            out = (False, None)
            self._static_variant_value_cache[uid] = out
            return out
        allowed = (str, bool, int, float, np.bool_, np.integer, np.floating)
        values: list[Any] = []
        try:
            for key in self.run_keys:
                item = self._space_instance(key)
                cell = getattr(item, tr.schema.name)
                value = cell(*tr.key.aux_values) if tr.key.aux_values else cell()
                if not isinstance(value, allowed):
                    out = (False, None)
                    self._static_variant_value_cache[uid] = out
                    return out
                if isinstance(value, np.generic):
                    value = value.item()
                values.append(value)
        except Exception:
            out = (False, None)
            self._static_variant_value_cache[uid] = out
            return out
        if not values:
            out = (False, None)
        else:
            first = values[0]
            try:
                stable = all(type(v) is type(first) and v == first for v in values[1:])
            except Exception:
                stable = False
            out = (bool(stable), first if stable else None)
        self._static_variant_value_cache[uid] = out
        return out

    def _proven_static_cell_value(self, name: str) -> tuple[bool, Any]:
        base = self.base_funcs.get(name)
        guarded = base is not None and any(isinstance(node, ast.Raise) for node in ast.walk(base))
        enum_spec = self.validated_enum_cells.get(name) if guarded else None
        scalar_spec = self.validated_point_scalar_cells.get(name) if guarded else None
        # Ordinary guard-bearing Cells remain runtime semantic operations.  Two
        # structurally verified exceptions retain explicit point-input validation:
        # validated enums and exact numeric/bool point selectors whose guard becomes
        # unreachable after substituting the proven selector value.
        if guarded and enum_spec is None and scalar_spec is None:
            return False, None
        uid = self.variants_by_cell_aux.get((name, ()))
        if uid is None:
            return False, None
        ok, value = self._proven_static_variant_value(uid)
        if not ok:
            return False, None
        if enum_spec is not None:
            if value not in enum_spec.allowed_values or self.model_point_row is None:
                return False, None
            validation_key = self.registry.point_field(
                self.model_point_row, enum_spec.field, enum_labels=enum_spec.allowed_values
            )
            self._used_validated_static_facts[name] = ValidatedStaticFact(
                source_name=name, value=value, allowed_values=enum_spec.allowed_values,
                proof_domain_size=len(self.run_keys), validation_input_key=validation_key,
            )
            return True, value
        if scalar_spec is not None:
            if self.model_point_row is None or isinstance(value, str):
                return False, None
            # Exact-value specialization is safe only when the selector value alone
            # proves every source guard unreachable.  Other runtime values therefore
            # cannot resurrect a discarded raise while this exact selector holds.
            base_fn = _strip_docstring(copy.deepcopy(base))
            local = base_fn.body[0].targets[0].id
            guards = [st for st in base_fn.body[1:-1] if isinstance(st, ast.If)]
            for guard in guards:
                test = _Substitute({local: ast.Constant(value=value)}).visit(copy.deepcopy(guard.test))
                test = _ConservativeFolder().visit(ast.fix_missing_locations(test))
                if not (isinstance(test, ast.Constant) and not bool(test.value)):
                    return False, None
            validation_key = self.registry.point_field(self.model_point_row, scalar_spec.field)
            self._used_validated_static_facts[name] = ValidatedStaticFact(
                source_name=name, value=value, allowed_values=(),
                proof_domain_size=len(self.run_keys), validation_input_key=validation_key,
            )
            return True, value
        self._used_static_facts[("cell", name)] = StaticScalarFact(
            "cell", name, value, len(self.run_keys)
        )
        return True, value

    def _proven_static_reference_value(self, name: str) -> tuple[bool, Any]:
        cached = self._static_reference_value_cache.get(name)
        if cached is not None:
            ok, value = cached
        else:
            if name not in self.refs:
                return False, None
            value = self.refs[name]
            if isinstance(value, np.generic):
                value = value.item()
            allowed = (str, bool, int, float, type(None))
            ok = isinstance(value, allowed)
            cached = (ok, value if ok else None)
            self._static_reference_value_cache[name] = cached
            ok, value = cached
        if ok:
            self._used_static_facts[("reference", name)] = StaticScalarFact(
                "reference", name, value, len(self.run_keys)
            )
        return ok, value

    def _proven_numeric_point_field_bounds(
        self, field: str
    ) -> tuple[float | None, float | None]:
        """Return sound finite numeric bounds for one point field over ``run_keys``.

        Unlike representative-trace extrema, these bounds are derived from the exact
        frozen RunDomain used to build the artifact.  Missing/non-numeric/non-finite
        values fail closed.  This is a domain proof only; it never specializes the
        runtime point input to one value.
        """
        if self.model_point_row is None:
            return None, None
        try:
            frame = self.model_point_row.provider()
            if not isinstance(frame, pd.DataFrame) or field not in frame.columns:
                return None, None
            semantic = self.model_point_row.semantic
            pos = int(semantic.key_position)
            if len(self.space_params) > 1:
                rows = [k[pos] if isinstance(k, tuple) else k for k in self.run_keys]
            else:
                rows = list(self.run_keys)
            if not rows:
                return None, None
            values = np.asarray(frame.loc[rows, field])
            if values.ndim != 1 or values.size != len(rows):
                return None, None
            if not np.issubdtype(values.dtype, np.number) or np.issubdtype(values.dtype, np.bool_):
                return None, None
            numeric = values.astype(np.float64, copy=False)
            if not np.all(np.isfinite(numeric)):
                return None, None
            return float(np.min(numeric)), float(np.max(numeric))
        except Exception:
            return None, None

    def _proven_integer_point_field_bounds(
        self, field: str
    ) -> tuple[int | None, int | None]:
        """Return exact integer-valued point-field bounds over the frozen RunDomain.

        Affine correlation is sound only when the source value is genuinely integral,
        not merely when its extrema happen to be whole numbers.  This helper therefore
        validates every selected RunDomain row and fails closed for fractional,
        missing, boolean, object, or non-finite values.
        """
        if self.model_point_row is None:
            return None, None
        try:
            frame = self.model_point_row.provider()
            if not isinstance(frame, pd.DataFrame) or field not in frame.columns:
                return None, None
            semantic = self.model_point_row.semantic
            pos = int(semantic.key_position)
            if len(self.space_params) > 1:
                rows = [k[pos] if isinstance(k, tuple) else k for k in self.run_keys]
            else:
                rows = list(self.run_keys)
            if not rows:
                return None, None
            values = np.asarray(frame.loc[rows, field])
            if values.ndim != 1 or values.size != len(rows):
                return None, None
            if not np.issubdtype(values.dtype, np.number) or np.issubdtype(values.dtype, np.bool_):
                return None, None
            numeric = values.astype(np.float64, copy=False)
            if not np.all(np.isfinite(numeric)) or not np.all(numeric == np.trunc(numeric)):
                return None, None
            return int(np.min(numeric)), int(np.max(numeric))
        except Exception:
            return None, None

    def _proven_static_point_field_value(self, field: str) -> tuple[bool, Any]:
        """Prove one normalized model-point field exact over every build run key.

        Unlike representative-trace specialization, this proof reads the normalized
        point table over the complete artifact run-key domain and retains an explicit
        point input as a runtime equality guard.  It is therefore safe to use only for
        source topology/predicate specialization; arithmetic point inputs are not
        silently baked into generated formulas.
        """
        if self.model_point_row is None:
            return False, None
        cached = self._static_point_field_cache.get(field)
        if cached is None:
            try:
                frame = self.model_point_row.provider()
                if not isinstance(frame, pd.DataFrame) or field not in frame.columns:
                    cached = (False, None)
                else:
                    semantic = self.model_point_row.semantic
                    pos = int(semantic.key_position)
                    if len(self.space_params) > 1:
                        rows = [k[pos] if isinstance(k, tuple) else k for k in self.run_keys]
                    else:
                        rows = list(self.run_keys)
                    values = list(frame.loc[rows, field])
                    if not values:
                        cached = (False, None)
                    else:
                        normalized: list[Any] = []
                        for value in values:
                            if isinstance(value, np.generic):
                                value = value.item()
                            normalized.append(value)
                        first = normalized[0]
                        # Missing values are intentionally not specialized here:
                        # NaN equality is not a valid exact runtime guard.
                        missing = bool(pd.isna(first)) if not isinstance(first, (tuple, list, dict)) else True
                        stable = (
                            not missing
                            and isinstance(first, (str, bool, int, float))
                            and all(type(v) is type(first) and v == first for v in normalized[1:])
                        )
                        cached = (bool(stable), first if stable else None)
            except Exception:
                cached = (False, None)
            self._static_point_field_cache[field] = cached
        ok, value = cached
        if not ok:
            return False, None

        if isinstance(value, str):
            try:
                frame = self.model_point_row.provider()
                labels = tuple(dict.fromkeys(
                    str(v) for v in frame[field].tolist()
                    if isinstance(v, str)
                ))
            except Exception:
                return False, None
            if not labels or len(labels) > 16 or value not in labels:
                return False, None
            validation_key = self.registry.point_field(
                self.model_point_row, field, enum_labels=labels
            )
            allowed_values = labels
        else:
            validation_key = self.registry.point_field(self.model_point_row, field)
            allowed_values = ()
        source_name = f"model_point[{field!r}]"
        self._used_validated_static_facts[source_name] = ValidatedStaticFact(
            source_name=source_name,
            value=value,
            allowed_values=allowed_values,
            proof_domain_size=len(self.run_keys),
            validation_input_key=validation_key,
        )
        return True, value

    def _proven_static_expr(
        self, node: ast.AST, locals_: dict[str, Any] | None = None
    ) -> tuple[bool, Any]:
        """Evaluate a deliberately tiny expression subset from full-domain facts."""
        locals_ = locals_ or {}
        if isinstance(node, ast.Constant):
            value = node.value.item() if isinstance(node.value, np.generic) else node.value
            return (isinstance(value, (str, bool, int, float, type(None))), value)
        if isinstance(node, ast.Name):
            if node.id in locals_ and not isinstance(locals_[node.id], _IntDomain):
                return True, locals_[node.id]
            if node.id in self.refs:
                return self._proven_static_reference_value(node.id)
            return False, None
        if (
            isinstance(node, ast.Subscript)
            and self.model_point_row is not None
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id == self.model_point_row.cell_name
            and not node.value.args and not node.value.keywords
            and isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, str)
        ):
            return self._proven_static_point_field_value(str(node.slice.value))
        if isinstance(node, ast.Subscript):
            ok, base = self._proven_static_expr(node.value, locals_)
            if not ok or not isinstance(base, (str, tuple)):
                return False, None
            if isinstance(node.slice, ast.Slice):
                parts = []
                for part in (node.slice.lower, node.slice.upper, node.slice.step):
                    if part is None:
                        parts.append(None)
                        continue
                    ok_part, value_part = self._proven_static_expr(part, locals_)
                    if not ok_part or not isinstance(value_part, int) or isinstance(value_part, bool):
                        return False, None
                    parts.append(int(value_part))
                key = slice(*parts)
            else:
                ok_key, key = self._proven_static_expr(node.slice, locals_)
                if not ok_key or not isinstance(key, (str, int)) or isinstance(key, bool):
                    return False, None
            try:
                value = base[key]
            except Exception:
                return False, None
            if isinstance(value, tuple):
                return True, value
            if isinstance(value, (str, bool, int, float, type(None))):
                return True, value
            return False, None
        if isinstance(node, ast.UnaryOp):
            ok, value = self._proven_static_expr(node.operand, locals_)
            if not ok:
                return False, None
            try:
                if isinstance(node.op, ast.Not): return True, not bool(value)
                if isinstance(node.op, ast.UAdd): return True, +value
                if isinstance(node.op, ast.USub): return True, -value
            except Exception:
                pass
            return False, None
        if isinstance(node, ast.BinOp):
            ok1, left = self._proven_static_expr(node.left, locals_)
            ok2, right = self._proven_static_expr(node.right, locals_)
            if not (ok1 and ok2):
                return False, None
            try:
                if isinstance(node.op, ast.Add): value = left + right
                elif isinstance(node.op, ast.Sub): value = left - right
                elif isinstance(node.op, ast.Mult): value = left * right
                elif isinstance(node.op, ast.Div): value = left / right
                elif isinstance(node.op, ast.FloorDiv): value = left // right
                elif isinstance(node.op, ast.Mod): value = left % right
                elif isinstance(node.op, ast.Pow): value = left ** right
                else: return False, None
                if isinstance(value, (str, bool, int, float)):
                    return True, value
            except Exception:
                pass
            return False, None
        if isinstance(node, ast.Compare) and len(node.ops) == len(node.comparators):
            ok, left = self._proven_static_expr(node.left, locals_)
            if not ok:
                return False, None
            for op, rhs_node in zip(node.ops, node.comparators):
                ok, right = self._proven_static_expr(rhs_node, locals_)
                if not ok:
                    return False, None
                try:
                    if isinstance(op, ast.Lt): verdict = left < right
                    elif isinstance(op, ast.LtE): verdict = left <= right
                    elif isinstance(op, ast.Gt): verdict = left > right
                    elif isinstance(op, ast.GtE): verdict = left >= right
                    elif isinstance(op, ast.Eq): verdict = left == right
                    elif isinstance(op, ast.NotEq): verdict = left != right
                    elif isinstance(op, ast.In): verdict = left in right
                    elif isinstance(op, ast.NotIn): verdict = left not in right
                    elif isinstance(op, (ast.Is, ast.IsNot)):
                        # Identity is only a stable compile-time relation for the
                        # singleton ``None`` object in this proof subset.  String,
                        # numeric and container identity can differ between the
                        # DataFrame/source objects used for proof and the runtime
                        # objects, so folding those would be unsound.
                        if left is not None and right is not None:
                            return False, None
                        verdict = (left is right)
                        if isinstance(op, ast.IsNot):
                            verdict = not verdict
                    else: return False, None
                except Exception:
                    return False, None
                if not verdict:
                    return True, False
                left = right
            return True, True
        if isinstance(node, ast.BoolOp):
            values: list[Any] = []
            for elt in node.values:
                ok, value = self._proven_static_expr(elt, locals_)
                if not ok:
                    return False, None
                values.append(value)
            if isinstance(node.op, ast.And):
                return True, all(bool(v) for v in values)
            if isinstance(node.op, ast.Or):
                return True, any(bool(v) for v in values)
            return False, None
        if isinstance(node, ast.IfExp):
            ok, test = self._proven_static_expr(node.test, locals_)
            if not ok:
                return False, None
            return self._proven_static_expr(node.body if bool(test) else node.orelse, locals_)
        if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
            values=[]
            for elt in node.elts:
                ok, value = self._proven_static_expr(elt, locals_)
                if not ok: return False, None
                values.append(value)
            return True, tuple(values) if isinstance(node, ast.Tuple) else values
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                name = node.func.id
                if not node.args and not node.keywords and name in self.base_funcs:
                    return self._proven_static_cell_value(name)
                if name in {"bool", "int", "float", "str", "abs", "min", "max"}:
                    vals=[]
                    for arg in node.args:
                        ok, value = self._proven_static_expr(arg, locals_)
                        if not ok: return False, None
                        vals.append(value)
                    if node.keywords: return False, None
                    try:
                        fn={"bool":bool,"int":int,"float":float,"str":str,"abs":abs,"min":min,"max":max}[name]
                        return True, fn(*vals)
                    except Exception:
                        return False, None
                if name == "__is_missing__" and len(node.args) == 1 and not node.keywords:
                    ok, value = self._proven_static_expr(node.args[0], locals_)
                    return (True, bool(pd.isna(value))) if ok else (False, None)
            if (
                isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and len(node.args) == 1 and not node.keywords
            ):
                obj = self.refs.get(node.func.value.id)
                module_name = getattr(obj, "__name__", None)
                if (
                    (module_name == "pandas" and node.func.attr in {"isna", "isnull"})
                    or (module_name == "numpy" and node.func.attr == "isnan")
                ):
                    ok, value = self._proven_static_expr(node.args[0], locals_)
                    return (True, bool(pd.isna(value))) if ok else (False, None)
        return False, None

    def _proven_coordinate_cell_constant(self, name: str) -> tuple[bool, Any]:
        """Prove a coordinate Cell constant only when every source return says so.

        This is intentionally stronger than evaluating representative coordinates.
        It is currently restricted to one coordinate parameter and no auxiliary
        parameters.  Every syntactic Return expression must independently reduce to
        the same scalar under guarded full-run static facts.
        """
        cached = self._coordinate_constant_cache.get(name)
        if cached is not None:
            return cached
        base = self.base_funcs.get(name)
        rows = [tr for tr in self.variant_trace_by_uid.values() if tr.schema.name == name]
        positions = {tr.key.time_pos for tr in rows if tr.key.time_pos is not None}
        if base is None or len(positions) != 1 or len(base.args.args) != 1:
            out=(False,None); self._coordinate_constant_cache[name]=out; return out
        returns=[node for node in ast.walk(base) if isinstance(node, ast.Return)]
        values=[]
        for ret in returns:
            if ret.value is None:
                out=(False,None); self._coordinate_constant_cache[name]=out; return out
            ok,value=self._proven_static_expr(ret.value)
            if not ok or not isinstance(value,(bool,int,float)):
                out=(False,None); self._coordinate_constant_cache[name]=out; return out
            values.append(value)
        if not values:
            out=(False,None)
        else:
            first=values[0]
            out=(all(type(v) is type(first) and v == first for v in values[1:]), first)
        self._coordinate_constant_cache[name]=out
        if out[0]:
            self._used_static_facts[("coordinate_cell",name)] = StaticScalarFact(
                "coordinate_cell", name, out[1], len(self.run_keys)
            )
        return out

    def _proven_finite_cell_domain(self, name: str, *, max_items: int = 16) -> tuple[bool, tuple[Any, ...]]:
        uid = self.variants_by_cell_aux.get((name, ()))
        if uid is None:
            return False, ()
        cached = self._finite_variant_domain_cache.get(uid)
        if cached is None:
            tr = self.variant_trace_by_uid.get(uid)
            if tr is None or tr.key.time_pos is not None:
                cached = (False, ())
            else:
                domains: list[tuple[Any, ...]] = []
                allowed = (str, bool, int, float, np.bool_, np.integer, np.floating)
                try:
                    for key in self.run_keys:
                        value = getattr(self._space_instance(key), name)()
                        if not isinstance(value, (tuple, list)) or len(value) > max_items:
                            cached = (False, ())
                            break
                        items: list[Any] = []
                        for item in value:
                            if not isinstance(item, allowed):
                                cached = (False, ())
                                break
                            if isinstance(item, np.generic):
                                item = item.item()
                            items.append(item)
                        else:
                            domains.append(tuple(items))
                            continue
                        break
                    else:
                        if domains and all(domain == domains[0] for domain in domains[1:]):
                            cached = (True, domains[0])
                        else:
                            cached = (False, ())
                except Exception:
                    cached = (False, ())
            self._finite_variant_domain_cache[uid] = cached
        ok, values = cached
        if ok:
            self._used_finite_domain_facts[("cell", name)] = FiniteDomainFact(
                "cell", name, values, len(self.run_keys)
            )
        return ok, values

    @staticmethod
    def _function_bound_names(fn: ast.FunctionDef) -> set[str]:
        names = {arg.arg for arg in (*fn.args.posonlyargs, *fn.args.args, *fn.args.kwonlyargs)}
        if fn.args.vararg is not None:
            names.add(fn.args.vararg.arg)
        if fn.args.kwarg is not None:
            names.add(fn.args.kwarg.arg)
        for node in ast.walk(fn):
            targets: list[ast.AST] = []
            if isinstance(node, (ast.Assign, ast.AnnAssign, ast.NamedExpr)):
                if isinstance(node, ast.Assign):
                    targets.extend(node.targets)
                else:
                    targets.append(node.target)
            elif isinstance(node, (ast.For, ast.comprehension)):
                targets.append(node.target)
            for target in targets:
                for child in ast.walk(target):
                    if isinstance(child, ast.Name):
                        names.add(child.id)
        return names

    def _int_domain_expr(
        self, node: ast.AST, env: dict[str, Any] | None = None, *,
        _stack: tuple[str, ...] = (),
    ) -> _IntDomain | None:
        """Conservatively prove a finite integer interval from source semantics.

        This proof may use exact frozen-RunDomain point-field bounds and may follow
        pure single-return source helpers.  It never uses representative trace
        extrema as semantic bounds.
        """
        env = env or {}
        if isinstance(node, ast.Constant) and isinstance(node.value, int) and not isinstance(node.value, bool):
            return _IntDomain(int(node.value), int(node.value))
        if isinstance(node, ast.Name):
            value = env.get(node.id)
            if isinstance(value, _IntDomain):
                return value
            if isinstance(value, int) and not isinstance(value, bool):
                return _IntDomain(int(value), int(value))
            ok, scalar = self._proven_static_expr(node, env)
            if ok and isinstance(scalar, int) and not isinstance(scalar, bool):
                return _IntDomain(int(scalar), int(scalar))
            return None
        ok, scalar = self._proven_static_expr(node, env)
        if ok and isinstance(scalar, int) and not isinstance(scalar, bool):
            return _IntDomain(int(scalar), int(scalar))
        if (
            isinstance(node, ast.Subscript)
            and self.model_point_row is not None
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id == self.model_point_row.cell_name
            and not node.value.args and not node.value.keywords
            and isinstance(node.slice, ast.Constant)
            and isinstance(node.slice.value, str)
        ):
            lo, hi = self._proven_numeric_point_field_bounds(str(node.slice.value))
            if lo is not None and hi is not None and float(lo).is_integer() and float(hi).is_integer():
                return _IntDomain(int(lo), int(hi))
            return None
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            inner = self._int_domain_expr(node.operand, env, _stack=_stack)
            if inner is None:
                return None
            return inner if isinstance(node.op, ast.UAdd) else _IntDomain(-inner.hi, -inner.lo)
        if isinstance(node, ast.BinOp):
            left = self._int_domain_expr(node.left, env, _stack=_stack)
            right = self._int_domain_expr(node.right, env, _stack=_stack)
            if left is None or right is None:
                return None
            if isinstance(node.op, ast.Add):
                return _IntDomain(left.lo + right.lo, left.hi + right.hi)
            if isinstance(node.op, ast.Sub):
                return _IntDomain(left.lo - right.hi, left.hi - right.lo)
            if isinstance(node.op, ast.Mult):
                vals = (left.lo * right.lo, left.lo * right.hi, left.hi * right.lo, left.hi * right.hi)
                return _IntDomain(min(vals), max(vals))
            if isinstance(node.op, ast.FloorDiv) and right.singleton not in (None, 0):
                d = int(right.singleton)
                vals = (left.lo // d, left.hi // d)
                return _IntDomain(min(vals), max(vals))
            if isinstance(node.op, ast.Mod) and right.singleton is not None and int(right.singleton) > 0:
                d = int(right.singleton)
                if left.singleton is not None:
                    v = int(left.singleton) % d
                    return _IntDomain(v, v)
                return _IntDomain(0, d - 1)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            name = node.func.id
            if name == "int" and len(node.args) == 1 and not node.keywords:
                return self._int_domain_expr(node.args[0], env, _stack=_stack)
            if name in {"min", "max"} and node.args and not node.keywords:
                domains = [self._int_domain_expr(arg, env, _stack=_stack) for arg in node.args]
                if all(d is not None for d in domains):
                    ds = [d for d in domains if d is not None]
                    if name == "min":
                        return _IntDomain(min(d.lo for d in ds), min(d.hi for d in ds))
                    return _IntDomain(max(d.lo for d in ds), max(d.hi for d in ds))
            if name in self.base_funcs and name not in _stack:
                bound = self._bind_source_call(name, node, env)
                if bound is not None:
                    assigned, _time_pos = bound
                    base = _strip_docstring(copy.deepcopy(self.base_funcs[name]))
                    if (
                        not base.args.posonlyargs and not base.args.kwonlyargs
                        and base.args.vararg is None and base.args.kwarg is None
                        and len(base.body) == 1 and isinstance(base.body[0], ast.Return)
                        and base.body[0].value is not None
                    ):
                        value = _Substitute(assigned).visit(copy.deepcopy(base.body[0].value))
                        value = _ConservativeFolder().visit(ast.fix_missing_locations(value))
                        if isinstance(value, ast.AST):
                            return self._int_domain_expr(value, env, _stack=_stack + (name,))
        return None

    _PRIMARY_AFFINE_COORD = "@primary_coordinate"
    _POINT_AFFINE_PREFIX = "@point:"

    def _expand_pure_single_return_call(
        self, node: ast.Call, *, _stack: tuple[str, ...] = ()
    ) -> tuple[ast.AST, str] | None:
        """Inline one pure single-return source/variant call for semantic proofs."""
        if not isinstance(node.func, ast.Name):
            return None
        name = node.func.id
        if name in _stack:
            return None
        source_name: str | None = None
        assigned: dict[str, ast.AST] | None = None
        stack_token = name
        if name in self.variant_trace_by_uid:
            tr = self.variant_trace_by_uid[name]
            source_name = tr.schema.name
            base = _strip_docstring(copy.deepcopy(self.base_funcs.get(source_name)))
            if not isinstance(base, ast.FunctionDef):
                return None
            params = [a.arg for a in base.args.args]
            assigned = {}
            if tr.key.time_pos is None:
                if node.args or node.keywords:
                    return None
                aux_iter = iter(tr.key.aux_values)
                try:
                    for param in params:
                        assigned[param] = ast.Constant(next(aux_iter))
                except StopIteration:
                    return None
            else:
                if len(node.args) != 1 or node.keywords:
                    return None
                aux_iter = iter(tr.key.aux_values)
                try:
                    for pos, param in enumerate(params):
                        assigned[param] = (
                            copy.deepcopy(node.args[0])
                            if pos == tr.key.time_pos
                            else ast.Constant(next(aux_iter))
                        )
                except StopIteration:
                    return None
        elif name in self.base_funcs:
            source_name = name
            base = _strip_docstring(copy.deepcopy(self.base_funcs[name]))
            params = [a.arg for a in base.args.args]
            defaults: dict[str, ast.AST] = {}
            if base.args.defaults:
                for param, default in zip(params[-len(base.args.defaults):], base.args.defaults):
                    defaults[param] = copy.deepcopy(default)
            assigned = {}
            if len(node.args) > len(params):
                return None
            for param, arg in zip(params, node.args):
                assigned[param] = copy.deepcopy(arg)
            for kw in node.keywords:
                if kw.arg is None or kw.arg not in params or kw.arg in assigned:
                    return None
                assigned[kw.arg] = copy.deepcopy(kw.value)
            for param in params:
                if param not in assigned:
                    if param not in defaults:
                        return None
                    assigned[param] = copy.deepcopy(defaults[param])
        else:
            return None
        if source_name is None or assigned is None:
            return None
        base = _strip_docstring(copy.deepcopy(self.base_funcs[source_name]))
        if not (
            not base.args.posonlyargs and not base.args.kwonlyargs
            and base.args.vararg is None and base.args.kwarg is None
            and len(base.body) == 1 and isinstance(base.body[0], ast.Return)
            and base.body[0].value is not None
        ):
            return None
        value = _Substitute(assigned).visit(copy.deepcopy(base.body[0].value))
        value = _ConservativeFolder().visit(ast.fix_missing_locations(value))
        return (value, stack_token) if isinstance(value, ast.AST) else None

    def _affine_int_expr(
        self, node: ast.AST, env: dict[str, Any] | None = None, *,
        _stack: tuple[str, ...] = (),
    ) -> AffineIntForm | None:
        """Normalize a deliberately small integer-affine source subset."""
        env = env or {}
        if isinstance(node, ast.Constant) and isinstance(node.value, int) and not isinstance(node.value, bool):
            return AffineIntForm.scalar(int(node.value))
        if isinstance(node, ast.Name):
            value = env.get(node.id)
            if isinstance(value, AffineIntForm):
                return value
            if isinstance(value, int) and not isinstance(value, bool):
                return AffineIntForm.scalar(int(value))
            ok, scalar = self._proven_static_expr(node, env)
            if ok and isinstance(scalar, int) and not isinstance(scalar, bool):
                return AffineIntForm.scalar(int(scalar))
            return None
        ok, scalar = self._proven_static_expr(node, env)
        if ok and isinstance(scalar, int) and not isinstance(scalar, bool):
            return AffineIntForm.scalar(int(scalar))
        if (
            isinstance(node, ast.Subscript)
            and self.model_point_row is not None
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id == self.model_point_row.cell_name
            and not node.value.args and not node.value.keywords
            and isinstance(node.slice, ast.Constant)
            and isinstance(node.slice.value, str)
        ):
            field = str(node.slice.value)
            lo, hi = self._proven_integer_point_field_bounds(field)
            if lo is None or hi is None:
                return None
            return AffineIntForm.symbol(self._POINT_AFFINE_PREFIX + field)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            inner = self._affine_int_expr(node.operand, env, _stack=_stack)
            if inner is None:
                return None
            return inner if isinstance(node.op, ast.UAdd) else inner.scale(-1)
        if isinstance(node, ast.BinOp):
            left = self._affine_int_expr(node.left, env, _stack=_stack)
            right = self._affine_int_expr(node.right, env, _stack=_stack)
            if left is None or right is None:
                return None
            if isinstance(node.op, ast.Add):
                return left.add(right)
            if isinstance(node.op, ast.Sub):
                return left.sub(right)
            if isinstance(node.op, ast.Mult):
                if not left.terms:
                    return right.scale(left.constant)
                if not right.terms:
                    return left.scale(right.constant)
                return None
            return None
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            name = node.func.id
            if name == "int" and len(node.args) == 1 and not node.keywords:
                # Preserve only already-integral affine inputs.  General truncation is
                # nonlinear and intentionally outside this proof subset.
                return self._affine_int_expr(node.args[0], env, _stack=_stack)
            expanded = self._expand_pure_single_return_call(node, _stack=_stack)
            if expanded is not None:
                value, token = expanded
                return self._affine_int_expr(value, env, _stack=_stack + (token,))
        return None

    def _affine_symbol_bounds_many(
        self, *forms: AffineIntForm | None
    ) -> dict[str, tuple[int, int]] | None:
        out: dict[str, tuple[int, int]] = {}
        for form in forms:
            if form is None:
                continue
            for symbol, _coeff in form.terms:
                if symbol == self._PRIMARY_AFFINE_COORD or symbol in out:
                    continue
                if not symbol.startswith(self._POINT_AFFINE_PREFIX):
                    return None
                field = symbol[len(self._POINT_AFFINE_PREFIX):]
                lo, hi = self._proven_integer_point_field_bounds(field)
                if lo is None or hi is None:
                    return None
                out[symbol] = (int(lo), int(hi))
        return out

    def _range_affine_constraint_from_args(
        self, args: tuple[ast.AST, ...], env: dict[str, Any] | None = None
    ) -> AffineRangeConstraint | None:
        """Freeze affine coordinate inequalities for semantic proofs only."""
        env = env or {}
        if len(args) == 1:
            start_node, stop_node, step_node = ast.Constant(0), args[0], ast.Constant(1)
        elif len(args) == 2:
            start_node, stop_node, step_node = args[0], args[1], ast.Constant(1)
        elif len(args) == 3:
            start_node, stop_node, step_node = args
        else:
            return None
        step = self._int_domain_expr(step_node, env)
        if step is None or step.singleton is None or int(step.singleton) == 0:
            return None
        start = self._affine_int_expr(start_node, env)
        stop = self._affine_int_expr(stop_node, env)
        if start is None or stop is None:
            return None
        step_value = int(step.singleton)
        if step_value > 0:
            lower = start
            upper = stop.sub(AffineIntForm.scalar(1))
        else:
            lower = stop.add(AffineIntForm.scalar(1))
            upper = start
        return AffineRangeConstraint(self._PRIMARY_AFFINE_COORD, lower=lower, upper=upper)

    def _bound_affine_under_primary_range(self, form: AffineIntForm) -> _IntDomain | None:
        constraint = self.primary_coordinate_affine_constraint
        if constraint is None:
            return None
        symbol_bounds = self._affine_symbol_bounds_many(form, constraint.lower, constraint.upper)
        if symbol_bounds is None:
            return None
        lo, hi = affine_bounds_under_range(form, constraint, symbol_bounds)
        if lo is None or hi is None or int(lo) > int(hi):
            return None
        return _IntDomain(int(lo), int(hi))

    def _correlated_int_domain_expr(
        self, node: ast.AST, *, coordinate_name: str = "t", _stack: tuple[str, ...] = ()
    ) -> _IntDomain | None:
        """Bound a small integer expression while preserving primary-range correlation."""
        env = {coordinate_name: AffineIntForm.symbol(self._PRIMARY_AFFINE_COORD)}
        affine = self._affine_int_expr(node, env, _stack=_stack)
        if affine is not None:
            bounded = self._bound_affine_under_primary_range(affine)
            if bounded is not None:
                return bounded
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            inner = self._correlated_int_domain_expr(node.operand, coordinate_name=coordinate_name, _stack=_stack)
            if inner is None:
                return None
            return inner if isinstance(node.op, ast.UAdd) else _IntDomain(-inner.hi, -inner.lo)
        if isinstance(node, ast.BinOp):
            if isinstance(node.op, ast.FloorDiv):
                right = self._int_domain_expr(node.right)
                if right is None or right.singleton is None or int(right.singleton) <= 0:
                    return None
                numerator = self._affine_int_expr(node.left, env, _stack=_stack)
                left = (
                    self._bound_affine_under_primary_range(numerator)
                    if numerator is not None else
                    self._correlated_int_domain_expr(node.left, coordinate_name=coordinate_name, _stack=_stack)
                )
                if left is None:
                    return None
                d = int(right.singleton)
                return _IntDomain(left.lo // d, left.hi // d)
            left = self._correlated_int_domain_expr(node.left, coordinate_name=coordinate_name, _stack=_stack)
            right = self._correlated_int_domain_expr(node.right, coordinate_name=coordinate_name, _stack=_stack)
            if left is None or right is None:
                return None
            if isinstance(node.op, ast.Add):
                return _IntDomain(left.lo + right.lo, left.hi + right.hi)
            if isinstance(node.op, ast.Sub):
                return _IntDomain(left.lo - right.hi, left.hi - right.lo)
            return None
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == "int" and len(node.args) == 1 and not node.keywords:
                return self._correlated_int_domain_expr(node.args[0], coordinate_name=coordinate_name, _stack=_stack)
            expanded = self._expand_pure_single_return_call(node, _stack=_stack)
            if expanded is not None:
                value, token = expanded
                return self._correlated_int_domain_expr(
                    value, coordinate_name=coordinate_name, _stack=_stack + (token,)
                )
        return None

    @staticmethod
    def _compare_domain_truth(left: _IntDomain, op: ast.cmpop, right: _IntDomain) -> bool | None:
        if isinstance(op, ast.Lt):
            if left.hi < right.lo: return True
            if left.lo >= right.hi: return False
        elif isinstance(op, ast.LtE):
            if left.hi <= right.lo: return True
            if left.lo > right.hi: return False
        elif isinstance(op, ast.Gt):
            if left.lo > right.hi: return True
            if left.hi <= right.lo: return False
        elif isinstance(op, ast.GtE):
            if left.lo >= right.hi: return True
            if left.hi < right.lo: return False
        elif isinstance(op, ast.Eq):
            if left.singleton is not None and right.singleton is not None:
                return left.singleton == right.singleton
            if left.hi < right.lo or right.hi < left.lo: return False
        elif isinstance(op, ast.NotEq):
            if left.hi < right.lo or right.hi < left.lo: return True
            if left.singleton is not None and right.singleton is not None:
                return left.singleton != right.singleton
        return None

    def _domain_truth(self, node: ast.AST, env: dict[str, Any] | None = None) -> bool | None:
        env=env or {}
        ok,value=self._proven_static_expr(node,env)
        if ok:
            return bool(value)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            val=self._domain_truth(node.operand,env)
            return None if val is None else not val
        if isinstance(node, ast.BoolOp):
            vals=[self._domain_truth(v,env) for v in node.values]
            if isinstance(node.op,ast.And):
                if any(v is False for v in vals): return False
                if all(v is True for v in vals): return True
            elif isinstance(node.op,ast.Or):
                if any(v is True for v in vals): return True
                if all(v is False for v in vals): return False
            return None
        if isinstance(node, ast.Compare) and len(node.ops)==1 and len(node.comparators)==1:
            left=self._int_domain_expr(node.left,env); right=self._int_domain_expr(node.comparators[0],env)
            if left is not None and right is not None:
                return self._compare_domain_truth(left,node.ops[0],right)
        return None

    def _refine_domain_env(self, node: ast.AST, env: dict[str, Any], truth: bool) -> dict[str, Any] | None:
        """Refine one simple comparison; unknown predicates keep the input domain."""
        out=dict(env)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op,ast.Not):
            return self._refine_domain_env(node.operand,env,not truth)
        if isinstance(node,ast.BoolOp):
            if isinstance(node.op,ast.And) and truth:
                cur=out
                for value in node.values:
                    cur=self._refine_domain_env(value,cur,True)
                    if cur is None:return None
                return cur
            if isinstance(node.op,ast.Or) and not truth:
                cur=out
                for value in node.values:
                    cur=self._refine_domain_env(value,cur,False)
                    if cur is None:return None
                return cur
            return out
        if not (isinstance(node,ast.Compare) and len(node.ops)==1 and len(node.comparators)==1):
            return out
        left,right=node.left,node.comparators[0]; op=node.ops[0]
        if isinstance(right,ast.Name) and not isinstance(left,ast.Name):
            # Reverse c OP x to x reverse(OP) c.
            rev={ast.Lt:ast.Gt(),ast.LtE:ast.GtE(),ast.Gt:ast.Lt(),ast.GtE:ast.LtE(),ast.Eq:ast.Eq(),ast.NotEq:ast.NotEq()}
            op=rev.get(type(op),op); left,right=right,left
        if not (isinstance(left,ast.Name) and isinstance(out.get(left.id),_IntDomain)):
            return out
        rhs=self._int_domain_expr(right,out)
        if rhs is None or rhs.singleton is None:
            return out
        d=out[left.id]; c=int(rhs.singleton)
        if not truth:
            inv={ast.Lt:ast.GtE(),ast.LtE:ast.Gt(),ast.Gt:ast.LtE(),ast.GtE:ast.Lt(),ast.Eq:ast.NotEq(),ast.NotEq:ast.Eq()}
            op=inv.get(type(op),op)
        if isinstance(op,ast.Lt): nd=d.intersect(hi=c-1)
        elif isinstance(op,ast.LtE): nd=d.intersect(hi=c)
        elif isinstance(op,ast.Gt): nd=d.intersect(lo=c+1)
        elif isinstance(op,ast.GtE): nd=d.intersect(lo=c)
        elif isinstance(op,ast.Eq): nd=d.intersect(lo=c,hi=c)
        elif isinstance(op,ast.NotEq):
            if d.singleton==c:return None
            # An interval cannot represent an interior hole, but excluding one
            # *boundary* value is exact.  This matters for source shapes such as
            # ``if t == 0: return ...``: the fall-through path is then provably
            # ``t >= 1`` rather than the old coarse ``t >= 0``.
            if c == d.lo:
                nd=d.intersect(lo=c+1)
            elif c == d.hi:
                nd=d.intersect(hi=c-1)
            else:
                return out
        else:return out
        if nd is None:return None
        out[left.id]=nd; return out

    def _specialize_static_facts_and_domains(
        self, fn: ast.FunctionDef, *, coordinate_env: dict[str, Any] | None = None
    ) -> ast.FunctionDef:
        """Prune control flow and expand tiny domains using full-run-key proofs.

        Scalar facts are intentionally substituted only in branch predicates.  A
        stable observed arithmetic value is *not* enough reason to turn a normal
        point input into a compile-time constant.  This keeps the native ABI honest
        while still removing source branches that cannot execute in this artifact's
        proven graph family.
        """
        frontend = self
        bound = self._function_bound_names(fn)
        coordinate_env = dict(coordinate_env or {})

        # A very small local alias form is useful for selectors written as
        # ``family = mva_family(); if family == ...``.  Only top-level, single-
        # assignment aliases are eligible; conditionally reassigned numeric locals
        # remain runtime values (the dev13 table tests enforce that distinction).
        assign_count: dict[str, int] = {}
        for node in ast.walk(fn):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        assign_count[target.id] = assign_count.get(target.id, 0) + 1
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                assign_count[node.target.id] = assign_count.get(node.target.id, 0) + 1
        local_static: dict[str, Any] = {}
        for st in fn.body:
            if not (
                isinstance(st, ast.Assign) and len(st.targets) == 1
                and isinstance(st.targets[0], ast.Name)
                and assign_count.get(st.targets[0].id) == 1
            ):
                continue
            target = st.targets[0].id
            rhs = st.value
            ok, value = self._proven_static_expr(rhs, local_static)
            if ok:
                local_static[target] = value

        class PredicateFacts(ast.NodeTransformer):
            def visit_Call(self, node: ast.Call):
                # A coordinate Cell can be substituted in a predicate only when
                # every source return is independently the same full-domain scalar.
                if isinstance(node.func,ast.Name) and node.func.id in frontend.base_funcs:
                    ok,value=frontend._proven_coordinate_cell_constant(node.func.id)
                    if ok:
                        return ast.copy_location(ast.Constant(value=value),node)
                if (
                    isinstance(node.func, ast.Name)
                    and not node.args and not node.keywords
                    and node.func.id in frontend.base_funcs
                ):
                    ok, value = frontend._proven_static_cell_value(node.func.id)
                    if ok:
                        return ast.copy_location(ast.Constant(value=value), node)
                return self.generic_visit(node)

            def visit_Name(self, node: ast.Name):
                if isinstance(node.ctx, ast.Load) and node.id in local_static:
                    return ast.copy_location(ast.Constant(value=local_static[node.id]), node)
                if isinstance(node.ctx, ast.Load) and node.id not in bound and node.id in frontend.refs:
                    ok, value = frontend._proven_static_reference_value(node.id)
                    if ok:
                        return ast.copy_location(ast.Constant(value=value), node)
                return node

        facts = PredicateFacts()

        class Specialize(ast.NodeTransformer):
            def _test(self, node: ast.AST) -> ast.AST:
                out = facts.visit(copy.deepcopy(node))
                out = _ConservativeFolder().visit(ast.fix_missing_locations(out))
                verdict=frontend._domain_truth(out,{**coordinate_env,**local_static})
                if verdict is not None:
                    out=ast.copy_location(ast.Constant(bool(verdict)),out)
                return ast.fix_missing_locations(out)

            def visit_If(self, node: ast.If):
                node = copy.deepcopy(node)
                node.test = self._test(node.test)
                # generic_visit owns statement-list flattening when a nested static
                # branch itself disappears.  Do not manually append a returned list.
                node = self.generic_visit(node)
                if isinstance(node.test, ast.Constant):
                    return node.body if bool(node.test.value) else node.orelse
                return node

            def visit_IfExp(self, node: ast.IfExp):
                node = copy.deepcopy(node)
                node.test = self._test(node.test)
                node = self.generic_visit(node)
                if isinstance(node.test, ast.Constant):
                    return node.body if bool(node.test.value) else node.orelse
                return node

            def visit_GeneratorExp(self, node: ast.GeneratorExp):
                node = copy.deepcopy(node)
                for comp in node.generators:
                    iterator = comp.iter
                    if (
                        isinstance(iterator, ast.Call)
                        and isinstance(iterator.func, ast.Name)
                        and not iterator.args and not iterator.keywords
                        and iterator.func.id in frontend.base_funcs
                    ):
                        ok, values = frontend._proven_finite_cell_domain(iterator.func.id)
                        if ok:
                            comp.iter = ast.Tuple(
                                elts=[ast.Constant(value=value) for value in values],
                                ctx=ast.Load(),
                            )
                return self.generic_visit(node)

        out = Specialize().visit(copy.deepcopy(fn))
        assert isinstance(out, ast.FunctionDef)
        out = _ConservativeFolder().visit(ast.fix_missing_locations(out))
        assert isinstance(out, ast.FunctionDef)
        out = unroll_finite_literal_generators(out)
        out = _ConservativeFolder().visit(ast.fix_missing_locations(out))
        assert isinstance(out, ast.FunctionDef)

        def strip_dead_tail(stmts: list[ast.stmt]) -> list[ast.stmt]:
            kept: list[ast.stmt] = []
            for st in stmts:
                if isinstance(st, ast.If):
                    st.body = strip_dead_tail(list(st.body))
                    st.orelse = strip_dead_tail(list(st.orelse))
                kept.append(st)
                if isinstance(st, (ast.Return, ast.Raise)):
                    break
            return kept

        out.body = strip_dead_tail(list(out.body))

        class StaticRoundPrecision(ast.NodeTransformer):
            """Specialize only the precision argument of ``round`` from guards.

            Normal arithmetic values remain runtime inputs: the dev29 contract is
            deliberately *not* changed into wholesale constant propagation.  The
            precision parameter is different because Cython needs it structurally
            static to preserve Python's decimal-rounding semantics without a dynamic
            fallback.  Full-run proof/guards are therefore consumed only at this
            call-site position.
            """

            def visit_Call(self, node: ast.Call):
                node = self.generic_visit(node)
                if not (
                    isinstance(node.func, ast.Name) and node.func.id == "round"
                    and len(node.args) == 2 and not node.keywords
                ):
                    return node
                ok, value = frontend._proven_static_expr(node.args[1], local_static)
                if not ok:
                    return node
                if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)):
                    raise FrontendError(
                        "proven-static round ndigits must be an integer"
                    )
                return ast.copy_location(
                    ast.Call(
                        func=copy.deepcopy(node.func),
                        args=[node.args[0], ast.Constant(int(value))],
                        keywords=[],
                    ),
                    node,
                )

        out = StaticRoundPrecision().visit(out)
        assert isinstance(out, ast.FunctionDef)
        out = ast.fix_missing_locations(out)
        # Static branch folding can create literal locals that were not literal in
        # source (PA's kind = "A" if static_selector() else "B").  Propagate only
        # single-assignment literal locals, never arithmetic/runtime locals.
        counts: dict[str,int]={}
        literal_locals: dict[str,Any]={}
        for node in ast.walk(out):
            if isinstance(node,ast.Name) and isinstance(node.ctx,ast.Store):
                counts[node.id]=counts.get(node.id,0)+1
        for st in out.body:
            if (
                isinstance(st,ast.Assign) and len(st.targets)==1 and isinstance(st.targets[0],ast.Name)
                and counts.get(st.targets[0].id)==1 and isinstance(st.value,ast.Constant)
            ):
                literal_locals[st.targets[0].id]=st.value.value
        if literal_locals:
            out=_Substitute({k:ast.Constant(v) for k,v in literal_locals.items()}).visit(out)
            assert isinstance(out,ast.FunctionDef)
            out=ast.fix_missing_locations(out)
        if local_static:
            loads = {
                node.id for node in ast.walk(out)
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
            }
            out.body = [
                st for st in out.body
                if not (
                    isinstance(st, ast.Assign) and len(st.targets) == 1
                    and isinstance(st.targets[0], ast.Name)
                    and st.targets[0].id in local_static
                    and st.targets[0].id not in loads
                )
            ]
        return ast.fix_missing_locations(out)

    def _range_partial_bounds_from_args(
        self, args: tuple[ast.AST, ...], env: dict[str, Any] | None = None
    ) -> tuple[int | None, int | None]:
        """Return sound one-sided bounds for values yielded by ``range``.

        Unlike exact physical range resolution, this retains safe bounds when a
        start/stop varies over the frozen RunDomain.  It is used only for semantic
        domain proofs, never to choose physical scheduling geometry.
        """
        env = env or {}
        if len(args) == 1:
            start_node, stop_node, step_node = ast.Constant(0), args[0], ast.Constant(1)
        elif len(args) == 2:
            start_node, stop_node, step_node = args[0], args[1], ast.Constant(1)
        elif len(args) == 3:
            start_node, stop_node, step_node = args
        else:
            return None, None
        start = self._int_domain_expr(start_node, env)
        stop = self._int_domain_expr(stop_node, env)
        step = self._int_domain_expr(step_node, env)
        if step is None or step.singleton is None or int(step.singleton) == 0:
            return None, None
        step_value = int(step.singleton)
        if step_value > 0:
            lo = None if start is None else int(start.lo)
            hi = None if stop is None else int(stop.hi) - 1
            return lo, hi
        lo = None if stop is None else int(stop.lo) + 1
        hi = None if start is None else int(start.hi)
        return lo, hi

    def _range_domain_from_args(
        self, args: tuple[ast.AST, ...], env: dict[str, Any] | None = None
    ) -> tuple[_IntDomain, int] | None:
        """Resolve a Python ``range`` to one exact finite integer interval."""
        env=env or {}
        vals=[]
        for arg in args:
            dom=self._int_domain_expr(arg,env)
            if dom is None or dom.singleton is None:
                return None
            vals.append(int(dom.singleton))
        if len(vals)==1:
            start,stop,step=0,vals[0],1
        elif len(vals)==2:
            start,stop,step=vals[0],vals[1],1
        elif len(vals)==3:
            start,stop,step=vals
        else:
            return None
        if step==0:
            return None
        seq=range(start,stop,step)
        if len(seq)==0:
            return None
        first=seq[0]; last=seq[-1]
        return _IntDomain(min(first,last),max(first,last)), int(step)

    def _coordinate_time_position(self, name: str) -> int | None:
        rows=[tr for tr in self.variant_trace_by_uid.values() if tr.schema.name==name and tr.key.time_pos is not None]
        positions={tr.key.time_pos for tr in rows}
        return next(iter(positions)) if len(positions)==1 else None

    def _bind_source_call(
        self, name: str, call: ast.Call, env: dict[str, Any]
    ) -> tuple[dict[str, ast.AST], int | None] | None:
        base=self.base_funcs.get(name)
        if base is None:
            return None
        params=[a.arg for a in base.args.args]
        defaults={}
        if base.args.defaults:
            for p,d in zip(params[-len(base.args.defaults):],base.args.defaults): defaults[p]=d
        assigned={p:a for p,a in zip(params,call.args)}
        for kw in call.keywords:
            if kw.arg is None or kw.arg in assigned:
                return None
            assigned[kw.arg]=kw.value
        for p in params:
            if p not in assigned:
                if p not in defaults:return None
                assigned[p]=defaults[p]
        return assigned,self._coordinate_time_position(name)

    @staticmethod
    def _merge_domain_states(states: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not states:
            return []
        if len(states)==1:
            return states
        keys=set.intersection(*(set(st) for st in states)) if states else set()
        merged: dict[str,Any]={}
        for key in keys:
            vals=[st[key] for st in states]
            if all(isinstance(v,_IntDomain) for v in vals):
                dom=vals[0]
                for value in vals[1:]:dom=dom.union(value)
                merged[key]=dom
            else:
                first=vals[0]
                try:same=all(type(v) is type(first) and v==first for v in vals[1:])
                except Exception:same=False
                if same:merged[key]=first
        return [merged]

    def _derive_coordinate_domains(self) -> dict[str, _IntDomain]:
        """Propagate finite source-proven coordinate intervals from output demand.

        Two root shapes are admitted:

        * a normalized reduction, whose exact ``range`` remains the physical root;
        * a fixed OutputInvocation, whose literal/static arguments seed demand into
          scheduled coordinate families called by the output formula.

        The latter is essential for finite reverse recurrences such as ``f(0)`` with
        source-guarded ``f(t + 1)``.  No observed trace extrema are consumed: trace
        metadata identifies coordinate/auxiliary roles only; bounds come from the
        declared OutputInvocation, source control flow, run-domain validated static
        facts and exact integer algebra.
        """
        output_matches=[
            uid for uid,tr in self.variant_trace_by_uid.items()
            if tr.schema.name==self.output
            and tr.key.time_pos is None
            and tuple(tr.key.aux_values)==tuple(self.output_invocation.argument_values)
            and tr.schema.name in self.base_funcs
        ]
        if len(output_matches)!=1:
            return {}
        output_uid=output_matches[0]
        output_fn=_strip_docstring(copy.deepcopy(self.base_funcs[self.output]))
        output_fn=self._specialize_static_facts_and_domains(output_fn)
        reduction=self._normalize_reduction(output_fn)
        root_domain: _IntDomain | None = None
        fixed_output_env: dict[str, Any] | None = None
        if reduction is not None:
            self.primary_coordinate_affine_constraint = self._range_affine_constraint_from_args(
                reduction.range_args
            )
            self.primary_coordinate_bounds = self._range_partial_bounds_from_args(reduction.range_args)
            root=self._range_domain_from_args(reduction.range_args)
            if root is None:
                return {}
            root_domain,_root_step=root
            # The root reduction range is an exact physical-loop domain even when
            # the wider inter-Cell fixed point later exceeds its proof budget.
            self.primary_coordinate_domain = root_domain
            self.primary_coordinate_bounds = (int(root_domain.lo), int(root_domain.hi))
        else:
            params=[a.arg for a in output_fn.args.args]
            values=tuple(self.output_invocation.argument_values)
            if len(params)!=len(values):
                return {}
            fixed_output_env={}
            for name,value in zip(params,values):
                if isinstance(value, np.generic):
                    value=value.item()
                if isinstance(value, bool):
                    fixed_output_env[name]=value
                elif isinstance(value, int):
                    fixed_output_env[name]=_IntDomain(int(value),int(value))
                elif isinstance(value, (float,str,type(None))):
                    fixed_output_env[name]=value
                else:
                    return {}

        domains: dict[str,_IntDomain]={}
        pending: list[str]=[]

        def add_domain(uid: str, dom: _IntDomain):
            old=domains.get(uid)
            new=dom if old is None else old.union(dom)
            if old is None or new!=old:
                domains[uid]=new
                if uid not in pending:pending.append(uid)

        def record_call(call: ast.Call, env: dict[str,Any]):
            if not (isinstance(call.func,ast.Name) and call.func.id in self.base_funcs):
                return
            name=call.func.id
            bound=self._bind_source_call(name,call,env)
            if bound is None:return
            assigned,tpos=bound
            if tpos is None:return
            params=[a.arg for a in self.base_funcs[name].args.args]
            aux=[]
            for j,p in enumerate(params):
                if j==tpos:continue
                ok,value=self._proven_static_expr(assigned[p],env)
                if not ok:return
                aux.append(value)
            uid=self.variants_by_cell_aux.get((name,tuple(aux)))
            if uid is None:return
            dom=self._int_domain_expr(assigned[params[tpos]],env)
            if dom is not None:add_domain(uid,dom)

        def scan_expr(node: ast.AST | None, env: dict[str,Any]):
            if node is None:return
            if isinstance(node,ast.IfExp):
                scan_expr(node.test,env)
                verdict=self._domain_truth(node.test,env)
                if verdict is True:
                    scan_expr(node.body,self._refine_domain_env(node.test,env,True) or env)
                elif verdict is False:
                    scan_expr(node.orelse,self._refine_domain_env(node.test,env,False) or env)
                else:
                    a=self._refine_domain_env(node.test,env,True)
                    b=self._refine_domain_env(node.test,env,False)
                    if a is not None:scan_expr(node.body,a)
                    if b is not None:scan_expr(node.orelse,b)
                return
            if isinstance(node,ast.Call):
                for arg in node.args:scan_expr(arg,env)
                for kw in node.keywords:scan_expr(kw.value,env)
                record_call(node,env)
                return
            for child in ast.iter_child_nodes(node):
                scan_expr(child,env)

        def scan_block(stmts: list[ast.stmt], initial: dict[str,Any]) -> list[dict[str,Any]]:
            states=[dict(initial)]
            for st in stmts:
                next_states=[]
                for env in states:
                    if isinstance(st,ast.Return):
                        scan_expr(st.value,env); continue
                    if isinstance(st,ast.Raise):
                        scan_expr(st.exc,env); continue
                    if isinstance(st,ast.Assign) and len(st.targets)==1 and isinstance(st.targets[0],ast.Name):
                        scan_expr(st.value,env)
                        nxt=dict(env); name=st.targets[0].id
                        ok,value=self._proven_static_expr(st.value,env)
                        if ok:nxt[name]=value
                        else:
                            dom=self._int_domain_expr(st.value,env)
                            if dom is not None:nxt[name]=dom
                            else:nxt.pop(name,None)
                        next_states.append(nxt); continue
                    if isinstance(st,ast.If):
                        scan_expr(st.test,env)
                        verdict=self._domain_truth(st.test,env)
                        branches=[]
                        if verdict is not False:
                            tenv=self._refine_domain_env(st.test,env,True)
                            if tenv is not None:branches.extend(scan_block(list(st.body),tenv))
                        if verdict is not True:
                            fenv=self._refine_domain_env(st.test,env,False)
                            if fenv is not None:
                                branches.extend(scan_block(list(st.orelse),fenv) if st.orelse else [fenv])
                        next_states.extend(branches); continue
                    if isinstance(st,ast.Expr):
                        scan_expr(st.value,env); next_states.append(env); continue
                    if isinstance(st,ast.AugAssign):
                        scan_expr(st.value,env); scan_expr(st.target,env)
                        nxt=dict(env)
                        if isinstance(st.target,ast.Name):nxt.pop(st.target.id,None)
                        next_states.append(nxt); continue
                    # Local imperative constructs are outside this proof foundation;
                    # inspect their expressions conservatively but do not infer bounds.
                    for child in ast.iter_child_nodes(st):scan_expr(child,env)
                    next_states.append(env)
                states=self._merge_domain_states(next_states)
                if not states:break
            return states

        if reduction is not None:
            assert root_domain is not None
            root_env={reduction.loop_var:root_domain}
            for filt in reduction.filters:scan_expr(filt,root_env)
            scan_expr(reduction.body_expr,root_env)
        else:
            assert fixed_output_env is not None
            scan_block(list(output_fn.body), fixed_output_env)

        iterations=0
        while pending and iterations<4096:
            iterations+=1
            uid=pending.pop(0); tr=self.variant_trace_by_uid[uid]; dom=domains[uid]
            base=copy.deepcopy(self.base_funcs.get(tr.schema.name))
            if base is None:continue
            params=[a.arg for a in base.args.args]; tpos=tr.key.time_pos
            if tpos is None:continue
            env: dict[str,Any]={params[tpos]:dom}
            aux_iter=iter(tr.key.aux_values)
            for j,p in enumerate(params):
                if j!=tpos:env[p]=next(aux_iter)
            scan_block(list(_strip_docstring(base).body),env)

        if pending:
            # A partial fixed point is an under-approximation and therefore must
            # never authorize branch deletion.  If a pathological source graph
            # does not converge within the bounded proof budget, discard the
            # entire coordinate-domain proof rather than using narrower domains.
            self.coordinate_domain_notes = [
                "source-proven coordinate-domain analysis abandoned: fixed-point budget exceeded"
            ]
            return {}

        self.coordinate_domain_notes=[
            f"source-proven coordinate domain {self.variant_trace_by_uid[uid].schema.fullname}: [{dom.lo}, {dom.hi}]"
            for uid,dom in sorted(domains.items())
        ]
        return domains

    def _derive_specialized_coordinate_domains(
        self,
        specialized: dict[str, tuple[Any, ast.FunctionDef, str | None, str | None]],
        output_uid: str,
    ) -> dict[str, _IntDomain]:
        """Prove coordinate intervals on the specialized demand graph.

        The older source-wide prepass runs before demand specialization and is
        intentionally conservative.  In particular it cannot always retain the
        path precision created later by literal auxiliary substitution,
        source-backed scheduled variants and dead-tail removal.  Lookup-domain
        safety needs the *callee call domain*, not merely the physical loop range.

        This pass therefore runs after all demanded source variants have been
        specialized but before table lowering.  Calls already name canonical UIDs,
        so no representative observed coordinate values are needed.  Source
        control flow and exact finite ``range`` semantics are the only reachability
        evidence.  If the finite-domain fixed point does not converge within the
        proof budget, the entire result is discarded rather than using an unsafe
        under-approximation.
        """
        row = specialized.get(output_uid)
        if row is None:
            return {}
        _tr, output_fn, _forced_role, _time_param_source = row
        reduction = self._normalize_reduction(copy.deepcopy(output_fn))
        if reduction is None:
            # Fixed OutputInvocation roots have no physical reduction range, but
            # the earlier source-demand fixed point can still prove exact finite
            # call domains for scheduled coordinate families.  Reuse only facts
            # for UIDs that survived demand specialization; this remains source /
            # invocation evidence and never imports representative trace extrema.
            return {
                uid: dom for uid, dom in self.coordinate_domains.items()
                if uid in specialized
            }
        root = self._range_domain_from_args(reduction.range_args)
        if root is None:
            # Source specialization has already canonicalized zero-argument Cells
            # in the range bounds (for example a zero-argument projection-length Cell) to UID calls.  The
            # earlier source-wide prepass resolved the original range before that
            # rewrite and retains the exact physical interval here.  Reusing that
            # exact root interval is safe; it is not representative trace data.
            if self.primary_coordinate_domain is None:
                return {}
            root_domain = self.primary_coordinate_domain
        else:
            root_domain, _root_step = root

        domains: dict[str, _IntDomain] = {}
        pending: list[str] = []

        def add_domain(uid: str, dom: _IntDomain) -> None:
            old = domains.get(uid)
            new = dom if old is None else old.union(dom)
            if old is None or new != old:
                domains[uid] = new
                if uid not in pending:
                    pending.append(uid)

        def record_call(call: ast.Call, env: dict[str, Any]) -> None:
            if not (
                isinstance(call.func, ast.Name)
                and call.func.id in specialized
                and call.func.id in self.variant_trace_by_uid
            ):
                return
            uid = call.func.id
            tr = self.variant_trace_by_uid[uid]
            if tr.key.time_pos is None:
                return
            # Canonical scheduled coordinate calls have one coordinate argument.
            # Fixed-coordinate synthetic scalars have none and need no call domain.
            if len(call.args) != 1 or call.keywords:
                return
            dom = self._int_domain_expr(call.args[0], env)
            if dom is not None:
                add_domain(uid, dom)

        def scan_expr(node: ast.AST | None, env: dict[str, Any]) -> None:
            if node is None:
                return
            if isinstance(node, ast.IfExp):
                scan_expr(node.test, env)
                verdict = self._domain_truth(node.test, env)
                if verdict is True:
                    scan_expr(node.body, self._refine_domain_env(node.test, env, True) or env)
                elif verdict is False:
                    scan_expr(node.orelse, self._refine_domain_env(node.test, env, False) or env)
                else:
                    tenv = self._refine_domain_env(node.test, env, True)
                    fenv = self._refine_domain_env(node.test, env, False)
                    if tenv is not None:
                        scan_expr(node.body, tenv)
                    if fenv is not None:
                        scan_expr(node.orelse, fenv)
                return
            if isinstance(node, ast.Call):
                for arg in node.args:
                    scan_expr(arg, env)
                for kw in node.keywords:
                    scan_expr(kw.value, env)
                record_call(node, env)
                return
            for child in ast.iter_child_nodes(node):
                scan_expr(child, env)

        def scan_block(stmts: list[ast.stmt], initial: dict[str, Any]) -> list[dict[str, Any]]:
            states = [dict(initial)]
            for st in stmts:
                next_states: list[dict[str, Any]] = []
                for env in states:
                    if isinstance(st, ast.Return):
                        scan_expr(st.value, env)
                        continue
                    if isinstance(st, ast.Raise):
                        scan_expr(st.exc, env)
                        continue
                    if (
                        isinstance(st, ast.Assign) and len(st.targets) == 1
                        and isinstance(st.targets[0], ast.Name)
                    ):
                        scan_expr(st.value, env)
                        nxt = dict(env)
                        name = st.targets[0].id
                        ok, value = self._proven_static_expr(st.value, env)
                        if ok:
                            nxt[name] = value
                        else:
                            dom = self._int_domain_expr(st.value, env)
                            if dom is not None:
                                nxt[name] = dom
                            else:
                                nxt.pop(name, None)
                        next_states.append(nxt)
                        continue
                    if isinstance(st, ast.AnnAssign) and isinstance(st.target, ast.Name):
                        scan_expr(st.value, env)
                        nxt = dict(env)
                        if st.value is None:
                            nxt.pop(st.target.id, None)
                        else:
                            dom = self._int_domain_expr(st.value, env)
                            if dom is not None:
                                nxt[st.target.id] = dom
                            else:
                                nxt.pop(st.target.id, None)
                        next_states.append(nxt)
                        continue
                    if isinstance(st, ast.If):
                        scan_expr(st.test, env)
                        verdict = self._domain_truth(st.test, env)
                        branches: list[dict[str, Any]] = []
                        if verdict is not False:
                            tenv = self._refine_domain_env(st.test, env, True)
                            if tenv is not None:
                                branches.extend(scan_block(list(st.body), tenv))
                        if verdict is not True:
                            fenv = self._refine_domain_env(st.test, env, False)
                            if fenv is not None:
                                branches.extend(
                                    scan_block(list(st.orelse), fenv) if st.orelse else [fenv]
                                )
                        next_states.extend(branches)
                        continue
                    if isinstance(st, ast.Expr):
                        scan_expr(st.value, env)
                        next_states.append(env)
                        continue
                    if isinstance(st, ast.AugAssign):
                        scan_expr(st.value, env)
                        scan_expr(st.target, env)
                        nxt = dict(env)
                        if isinstance(st.target, ast.Name):
                            nxt.pop(st.target.id, None)
                        next_states.append(nxt)
                        continue
                    # Imperative/local loop constructs are outside this interval
                    # proof.  Inspect calls conservatively but retain no new local
                    # bounds from them.
                    for child in ast.iter_child_nodes(st):
                        scan_expr(child, env)
                    next_states.append(env)
                states = self._merge_domain_states(next_states)
                if not states:
                    break
            return states

        root_env = {reduction.loop_var: root_domain}
        for filt in reduction.filters:
            scan_expr(filt, root_env)
        scan_expr(reduction.body_expr, root_env)

        iterations = 0
        while pending and iterations < 8192:
            iterations += 1
            uid = pending.pop(0)
            row = specialized.get(uid)
            if row is None:
                continue
            tr, fn, _forced_role, _time_param_source = row
            if tr.key.time_pos is None or not fn.args.args:
                continue
            scan_block(list(fn.body), {fn.args.args[0].arg: domains[uid]})

        if pending:
            return {}
        return domains

    def _derive_coordinate_recurrence_facts(
        self, domains: dict[str, _IntDomain]
    ) -> tuple[CoordinateRecurrenceDomainFact, ...]:
        """Freeze exact active/boundary domains for guarded unit recurrences.

        This pass runs only after the source-demand fixed point converges.  It
        rescans each demanded coordinate formula with its final domain and records
        the subdomain on which an exact self edge is reachable.  Consequently a
        fixed invocation such as ``f(0)`` with ``if t > n: return seed`` and
        ``f(t + 1)`` becomes demand ``[0,n+1]``, active ``[0,n]`` and boundary
        ``{n+1}`` without consulting observed trace coordinates.

        G2a intentionally freezes only exact unit self recurrences.  Wider/mixed
        offsets remain represented by ordinary canonical transition evidence and
        receive no boundary-domain fact from this foundation.
        """
        facts: list[CoordinateRecurrenceDomainFact] = []

        for uid, demand in sorted(domains.items()):
            tr = self.variant_trace_by_uid.get(uid)
            if tr is None or tr.key.time_pos is None:
                continue
            base = self.base_funcs.get(tr.schema.name)
            if base is None:
                continue
            params = [a.arg for a in base.args.args]
            tpos = tr.key.time_pos
            if tpos >= len(params):
                continue
            tparam = params[tpos]
            active_rows: list[tuple[int, _IntDomain]] = []

            def record_self_call(call: ast.Call, env: dict[str, Any]) -> None:
                if not (
                    isinstance(call.func, ast.Name)
                    and call.func.id == tr.schema.name
                ):
                    return
                bound = self._bind_source_call(tr.schema.name, call, env)
                if bound is None:
                    return
                assigned, call_tpos = bound
                if call_tpos != tpos:
                    return
                expr = assigned[params[tpos]]
                off = self._source_coordinate_relative_offset(expr, tparam)
                caller = env.get(tparam)
                if off is None or not isinstance(caller, _IntDomain):
                    return
                active_rows.append((int(off), caller))

            def scan_expr(node: ast.AST | None, env: dict[str, Any]) -> None:
                if node is None:
                    return
                if isinstance(node, ast.IfExp):
                    scan_expr(node.test, env)
                    verdict = self._domain_truth(node.test, env)
                    if verdict is True:
                        tenv = self._refine_domain_env(node.test, env, True) or env
                        scan_expr(node.body, tenv)
                    elif verdict is False:
                        fenv = self._refine_domain_env(node.test, env, False) or env
                        scan_expr(node.orelse, fenv)
                    else:
                        tenv = self._refine_domain_env(node.test, env, True)
                        fenv = self._refine_domain_env(node.test, env, False)
                        if tenv is not None:
                            scan_expr(node.body, tenv)
                        if fenv is not None:
                            scan_expr(node.orelse, fenv)
                    return
                if isinstance(node, ast.Call):
                    record_self_call(node, env)
                for child in ast.iter_child_nodes(node):
                    scan_expr(child, env)

            def scan_block(stmts: list[ast.stmt], initial: dict[str, Any]) -> list[dict[str, Any]]:
                states = [dict(initial)]
                for st in stmts:
                    next_states: list[dict[str, Any]] = []
                    for env in states:
                        if isinstance(st, ast.Return):
                            scan_expr(st.value, env)
                            continue
                        if isinstance(st, ast.Raise):
                            scan_expr(st.exc, env)
                            continue
                        if (
                            isinstance(st, ast.Assign)
                            and len(st.targets) == 1
                            and isinstance(st.targets[0], ast.Name)
                        ):
                            scan_expr(st.value, env)
                            nxt = dict(env)
                            name = st.targets[0].id
                            ok, value = self._proven_static_expr(st.value, env)
                            if ok:
                                nxt[name] = value
                            else:
                                local_domain = self._int_domain_expr(st.value, env)
                                if local_domain is not None:
                                    nxt[name] = local_domain
                                else:
                                    nxt.pop(name, None)
                            next_states.append(nxt)
                            continue
                        if isinstance(st, ast.If):
                            scan_expr(st.test, env)
                            verdict = self._domain_truth(st.test, env)
                            if verdict is not False:
                                tenv = self._refine_domain_env(st.test, env, True)
                                if tenv is not None:
                                    next_states.extend(scan_block(list(st.body), tenv))
                            if verdict is not True:
                                fenv = self._refine_domain_env(st.test, env, False)
                                if fenv is not None:
                                    next_states.extend(
                                        scan_block(list(st.orelse), fenv) if st.orelse else [fenv]
                                    )
                            continue
                        if isinstance(st, ast.Expr):
                            scan_expr(st.value, env)
                            next_states.append(env)
                            continue
                        for child in ast.iter_child_nodes(st):
                            scan_expr(child, env)
                        next_states.append(env)
                    states = self._merge_domain_states(next_states)
                    if not states:
                        break
                return states

            env: dict[str, Any] = {tparam: demand}
            aux_iter = iter(tr.key.aux_values)
            for index, name in enumerate(params):
                if index != tpos:
                    env[name] = next(aux_iter)
            scan_block(list(_strip_docstring(copy.deepcopy(base)).body), env)

            nonzero = [(off, dom) for off, dom in active_rows if off != 0]
            offsets = tuple(sorted({off for off, _ in nonzero}))
            if len(offsets) != 1 or abs(offsets[0]) != 1:
                continue
            offset = int(offsets[0])
            active: _IntDomain | None = None
            for row_off, row_domain in nonzero:
                if row_off != offset:
                    continue
                active = row_domain if active is None else active.union(row_domain)
            if active is None:
                continue

            boundary: tuple[int, ...] = ()
            scan_requirement = "descending" if offset > 0 else "ascending"
            if (
                offset == 1
                and int(demand.lo) == int(active.lo)
                and int(demand.hi) == int(active.hi) + 1
            ):
                boundary = (int(demand.hi),)
            elif (
                offset == -1
                and int(demand.hi) == int(active.hi)
                and int(demand.lo) == int(active.lo) - 1
            ):
                boundary = (int(demand.lo),)
            else:
                continue

            facts.append(CoordinateRecurrenceDomainFact(
                source_uid=str(uid),
                source_name=str(tr.schema.name),
                coordinate_parameter=str(tparam),
                demand_lo=int(demand.lo),
                demand_hi=int(demand.hi),
                active_lo=int(active.lo),
                active_hi=int(active.hi),
                recurrence_offsets=(offset,),
                boundary_coordinates=boundary,
                scan_requirement=scan_requirement,
                output_invocation_uid=str(self.output_invocation.uid),
            ))

        return tuple(facts)

    def _normalize_coordinate_expression(
        self, node: ast.AST, *, bound_names: set[str] | None = None
    ) -> ast.AST:
        """Substitute only already-proven static facts inside a coordinate expression."""
        frontend = self
        bound = set(bound_names or ())

        class CoordinateFacts(ast.NodeTransformer):
            def visit_Call(self, call: ast.Call):
                if (
                    isinstance(call.func, ast.Name) and not call.args and not call.keywords
                    and call.func.id in frontend.base_funcs and call.func.id not in bound
                ):
                    ok, value = frontend._proven_static_cell_value(call.func.id)
                    if ok:
                        return ast.copy_location(ast.Constant(value=value), call)
                return self.generic_visit(call)

            def visit_Name(self, name: ast.Name):
                if (
                    isinstance(name.ctx, ast.Load) and name.id not in bound
                    and name.id in frontend.refs
                ):
                    ok, value = frontend._proven_static_reference_value(name.id)
                    if ok:
                        return ast.copy_location(ast.Constant(value=value), name)
                return name

        out = CoordinateFacts().visit(copy.deepcopy(node))
        out = _CoordinateConstantFolder().visit(ast.fix_missing_locations(out))
        out = _ConservativeFolder().visit(ast.fix_missing_locations(out))
        if isinstance(out, list):
            raise FrontendError("coordinate constant folding unexpectedly produced statements")
        return ast.fix_missing_locations(out)

    def _fold_fixed_local_constants(self, fn: ast.FunctionDef) -> ast.FunctionDef:
        """Propagate literal locals after a coordinate parameter has been fixed.

        Only assignments that reduce to literal constants are propagated.  Dynamic
        locals and non-constant control flow remain untouched.
        """
        env: dict[str, ast.AST] = {}

        def assigned_names(node: ast.AST) -> set[str]:
            out: set[str] = set()
            for child in ast.walk(node):
                targets: list[ast.AST] = []
                if isinstance(child, ast.Assign):
                    targets.extend(child.targets)
                elif isinstance(child, ast.AnnAssign):
                    targets.append(child.target)
                elif isinstance(child, ast.AugAssign):
                    targets.append(child.target)
                for target in targets:
                    for part in ast.walk(target):
                        if isinstance(part, ast.Name):
                            out.add(part.id)
            return out

        def process(stmts: list[ast.stmt], current: dict[str, ast.AST]) -> list[ast.stmt]:
            out: list[ast.stmt] = []
            for original in stmts:
                st = _Substitute(current).visit(copy.deepcopy(original))
                st = _CoordinateConstantFolder().visit(ast.fix_missing_locations(st))
                st = _ConservativeFolder().visit(ast.fix_missing_locations(st))
                if isinstance(st, list):
                    out.extend(process(list(st), current))
                    if out and isinstance(out[-1], (ast.Return, ast.Raise)):
                        break
                    continue
                if isinstance(st, ast.Assign) and len(st.targets) == 1 and isinstance(st.targets[0], ast.Name):
                    target = st.targets[0].id
                    if isinstance(st.value, ast.Constant):
                        current[target] = copy.deepcopy(st.value)
                    else:
                        current.pop(target, None)
                elif isinstance(st, ast.AnnAssign) and isinstance(st.target, ast.Name):
                    target = st.target.id
                    if isinstance(st.value, ast.Constant):
                        current[target] = copy.deepcopy(st.value)
                    else:
                        current.pop(target, None)
                elif isinstance(st, ast.If):
                    for target in assigned_names(st):
                        current.pop(target, None)
                out.append(st)
                if isinstance(st, (ast.Return, ast.Raise)):
                    break
            return out

        out = copy.deepcopy(fn)
        out.body = process(list(out.body), env)
        return ast.fix_missing_locations(out)

    def _source_has_future_coordinate_dependency(self, base_uid: str) -> bool:
        cached = self._future_coordinate_source_cache.get(base_uid)
        if cached is not None:
            return cached
        tr = self.variant_trace_by_uid.get(base_uid)
        if tr is None or tr.key.time_pos is None:
            self._future_coordinate_source_cache[base_uid] = False
            return False
        fn = self.base_funcs.get(tr.schema.name)
        if fn is None:
            self._future_coordinate_source_cache[base_uid] = False
            return False
        current_t = tr.schema.parameters[tr.key.time_pos]

        for call in (node for node in ast.walk(fn) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)):
            callee = call.func.id
            candidates = [
                row for row in self.variant_trace_by_uid.values()
                if row.schema.name == callee and row.key.time_pos is not None
            ]
            if not candidates:
                continue
            positions = {row.key.time_pos for row in candidates}
            if len(positions) != 1:
                continue
            pos = next(iter(positions))
            callee_params = list(candidates[0].schema.parameters)
            arg = call.args[pos] if pos < len(call.args) else None
            if arg is None and pos < len(callee_params):
                pname = callee_params[pos]
                arg = next((kw.value for kw in call.keywords if kw.arg == pname), None)
            if arg is not None:
                off = self._source_coordinate_relative_offset(arg, current_t)
                if off is not None and off > 0:
                    self._future_coordinate_source_cache[base_uid] = True
                    return True
        self._future_coordinate_source_cache[base_uid] = False
        return False

    @staticmethod
    def _source_coordinate_relative_offset(expr: ast.AST, variable: str) -> int | None:
        if isinstance(expr, ast.Name) and expr.id == variable:
            return 0
        if (
            isinstance(expr, ast.BinOp)
            and isinstance(expr.left, ast.Name)
            and expr.left.id == variable
            and isinstance(expr.right, ast.Constant)
            and isinstance(expr.right.value, int)
            and not isinstance(expr.right.value, bool)
        ):
            if isinstance(expr.op, ast.Add):
                return int(expr.right.value)
            if isinstance(expr.op, ast.Sub):
                return -int(expr.right.value)
        return None

    def _request_fixed_coordinate(self, base_uid: str, coordinate: int) -> str:
        tr = self.variant_trace_by_uid.get(base_uid)
        if tr is None or tr.key.time_pos is None:
            raise FrontendError(f"fixed-coordinate specialization requires a coordinate variant, got {base_uid}")
        if self._source_has_future_coordinate_dependency(base_uid):
            raise FrontendError(
                f"future dependency in coordinate family {tr.schema.name} requires fallback"
            )
        if isinstance(coordinate, bool) or not isinstance(coordinate, int):
            raise FrontendError("fixed-coordinate specialization requires an integer coordinate")
        key = (base_uid, int(coordinate))
        existing = self._fixed_coordinate_uid_by_key.get(key)
        if existing is not None:
            return existing
        if len(self._fixed_coordinate_uid_by_key) >= self._fixed_coordinate_limit:
            raise FrontendError(
                f"fixed-coordinate specialization exceeds the generic cap of {self._fixed_coordinate_limit} variants"
            )
        digest = hashlib.sha1(f"{base_uid}|{int(coordinate)}".encode("utf-8")).hexdigest()[:12]
        synthetic_uid = f"vfix_{digest}"
        self._fixed_coordinate_uid_by_key[key] = synthetic_uid
        self._fixed_coordinate_requests[synthetic_uid] = key
        self._used_fixed_coordinate_facts[synthetic_uid] = FixedCoordinateFact(
            source_uid=base_uid, source_name=tr.schema.name,
            coordinate=int(coordinate), synthetic_uid=synthetic_uid,
        )
        return synthetic_uid

    def _preflight_observed_dependencies(self) -> None:
        observed = set(self.schema_by_name)
        for source_name in sorted(self.compiled_source_names):
            fn = self.base_funcs[source_name]
            for node in ast.walk(fn):
                dep = None
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    dep = node.func.id
                elif isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name):
                    dep = node.value.id
                if (
                    dep is not None
                    and dep in self.base_funcs
                    and dep not in self.fallback_cells
                    and dep not in observed
                ):
                    raise FrontendError(
                        f"Cells {dep} was not observed in the representative trace; "
                        "fallback or broader representative sampling is required"
                    )

    @staticmethod
    def _is_modelx_cells_object(value: Any) -> bool:
        """Return whether ``value`` is a concrete modelx Cells object.

        Context-accessor normalization is intentionally limited to modelx Cells.
        In particular, an arbitrary Python attribute that merely happens to be
        callable must never become a preparation-time execution escape hatch.
        """
        cls = getattr(value, "__class__", None)
        return bool(
            cls is not None
            and getattr(cls, "__name__", "") == "Cells"
            and str(getattr(cls, "__module__", "")).startswith("modelx.")
        )

    @staticmethod
    def _is_modelx_space_object(value: Any) -> bool:
        cls = getattr(value, "__class__", None)
        return bool(
            cls is not None
            and getattr(cls, "__name__", "") in {"UserSpace", "ItemSpace"}
            and str(getattr(cls, "__module__", "")).startswith("modelx.")
        )

    @staticmethod
    def _is_modelx_itemspace_object(value: Any) -> bool:
        cls = getattr(value, "__class__", None)
        return bool(
            cls is not None
            and getattr(cls, "__name__", "") == "ItemSpace"
            and str(getattr(cls, "__module__", "")).startswith("modelx.")
        )

    def _context_parameterized_space_for_key(
        self, ref_name: str, key: Any | None = None
    ) -> Any:
        root = self._context_root_for_key(ref_name, key)
        if not self._is_modelx_space_object(root):
            raise FrontendError(f"model-bound context root {ref_name!r} is not a modelx Space")
        params = tuple(getattr(root, "parameters", ()) or ())
        if not params:
            raise FrontendError(f"model-bound context Space {ref_name!r} is not parameterized")
        return root

    def _context_selected_itemspace(
        self, ref_name: str, selectors: Sequence[Any], key: Any | None = None
    ) -> Any:
        root = self._context_parameterized_space_for_key(ref_name, key)
        params = tuple(getattr(root, "parameters", ()) or ())
        if len(selectors) != len(params):
            raise FrontendError(
                f"model-bound context Space {ref_name!r} selection arity changed; "
                f"expected {len(params)}, got {len(selectors)}"
            )
        selector = selectors[0] if len(selectors) == 1 else tuple(selectors)
        try:
            item = root[selector]
        except Exception as exc:
            raise FrontendError(
                f"model-bound context Space {ref_name!r} could not select an ItemSpace: "
                f"{type(exc).__name__}: {exc}"
            ) from exc
        if not self._is_modelx_itemspace_object(item):
            raise FrontendError(
                f"model-bound context Space {ref_name!r} selection did not return an ItemSpace"
            )
        return item

    def _context_itemspace_cell(
        self, item: Any, ref_name: str, member_name: str
    ) -> Any:
        candidate = None
        cells = getattr(item, "cells", None)
        if cells is not None and member_name in cells:
            candidate = cells[member_name]
        if candidate is None:
            try:
                candidate = getattr(item, member_name)
            except Exception:
                candidate = None
        if not self._is_modelx_cells_object(candidate):
            raise FrontendError(
                f"selected model-bound Space member {ref_name}[...].{member_name} "
                "is not a concrete Cells object"
            )
        return candidate

    @staticmethod
    def _formula_unbound_load_names(source: str) -> set[str]:
        """Return lexical load names not bound inside one formula source.

        This is a source-structure query only.  It never executes source and is used
        solely to identify owner-parameter dependencies in a child Space Cells
        closure.
        """
        try:
            tree = ast.parse(source)
        except (SyntaxError, TypeError) as exc:
            raise FrontendError("could not parse child Space formula for hierarchy binding") from exc
        bound: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.arg):
                bound.add(node.arg)
            elif isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
                bound.add(node.id)
        return {
            node.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
        } - bound

    def _hierarchical_itemspace_parameter_binding(
        self, ref_name: str, cell_name: str
    ) -> HierarchicalItemSpaceParameterBinding | None:
        """Prove that a relative child-Space Cells closure inherits RunDomain keys.

        Admission is intentionally narrow: the referenced root must be an
        unparameterized modelx child Space under the selected parameterized Space,
        the selected-Space reference must actually be relative, and the Cells
        dependency closure must contain at least one bare load of a selected-Space
        declared parameter that is not shadowed by a child ref/Cells/local binding.
        Parameterized intermediate Spaces are rejected because they would introduce
        a second ItemSpace context not represented by the current RunDomain.
        """
        if not self.space_params or ref_name not in self.refs:
            return None
        root = self.refs[ref_name]
        if not self._is_modelx_space_object(root):
            return None
        if tuple(getattr(root, "parameters", ()) or ()):
            return None
        cells = getattr(root, "cells", None)
        if cells is None or cell_name not in cells:
            return None

        # A same-looking absolute Space reference is not an inherited ItemSpace
        # binding.  Require modelx's own relative-reference metadata when present.
        impl = getattr(self.space, "_impl", None)
        impl_refs = getattr(impl, "refs", None)
        try:
            ref_impl = impl_refs[ref_name] if impl_refs is not None else None
        except Exception:
            ref_impl = None
        if ref_impl is None or not bool(getattr(ref_impl, "is_relative", False)):
            return None

        # The child must belong to exactly this selected Space context.  Any
        # parameterized intermediate ancestor would need an additional selector and
        # is outside this foundation.
        cur = root
        found_owner = False
        while True:
            parent = getattr(cur, "parent", None)
            if parent is self.space:
                found_owner = True
                break
            if parent is None or parent is getattr(self.space, "model", None):
                break
            if tuple(getattr(parent, "parameters", ()) or ()):
                return None
            cur = parent
        if not found_owner:
            return None

        owner_params = tuple(self.space_params)
        owner_set = set(owner_params)
        inherited: set[str] = set()
        seen: set[tuple[str, str]] = set()
        dependency_fullnames: set[str] = set()
        stack: list[tuple[Any, str]] = [(root, cell_name)]

        def descendant_without_competing_parameters(space_obj: Any) -> bool:
            cur_space = space_obj
            while cur_space is not None:
                parent = getattr(cur_space, "parent", None)
                if parent is self.space:
                    return True
                if parent is None or parent is getattr(self.space, "model", None):
                    return False
                if tuple(getattr(parent, "parameters", ()) or ()):
                    return False
                cur_space = parent
            return False

        while stack:
            current_space, name = stack.pop()
            current_cells = getattr(current_space, "cells", None)
            if current_cells is None or name not in current_cells:
                return None
            current_cell = current_cells[name]
            cell_fullname = str(getattr(current_cell, "fullname", None) or name)
            node_key = (str(getattr(current_space, "fullname", None) or id(current_space)), cell_fullname)
            if node_key in seen:
                continue
            seen.add(node_key)
            dependency_fullnames.add(cell_fullname)
            formula = getattr(current_cell, "formula", None)
            source = getattr(formula, "source", None)
            if not isinstance(source, str) or not source.strip():
                return None
            loads = self._formula_unbound_load_names(source)
            current_refs_obj = getattr(current_space, "refs", {})
            current_refs = set(current_refs_obj.keys())
            current_cell_names = set(current_cells.keys())
            # Explicit child refs/Cells shadow an owner parameter of the same
            # spelling.  Only genuinely unresolved bare loads may be inherited.
            unresolved = loads - current_refs - current_cell_names
            inherited.update(unresolved & owner_set)

            for dep in loads & current_cell_names:
                stack.append((current_space, dep))

            # Relative Cells refs can bridge sibling child Spaces while preserving
            # the same owning ItemSpace.  Follow only those structurally relative
            # references whose target Space is still an unparameterized descendant
            # of the selected RunDomain Space.
            impl = getattr(current_space, "_impl", None)
            impl_refs = getattr(impl, "refs", None)
            for dep in loads & current_refs:
                try:
                    ref_value = current_refs_obj[dep]
                    ref_impl = impl_refs[dep] if impl_refs is not None else None
                except Exception:
                    continue
                if not (
                    self._is_modelx_cells_object(ref_value)
                    and ref_impl is not None
                    and bool(getattr(ref_impl, "is_relative", False))
                ):
                    continue
                target_space = getattr(ref_value, "parent", None)
                target_name = getattr(ref_value, "name", None)
                if (
                    target_space is not None
                    and isinstance(target_name, str)
                    and descendant_without_competing_parameters(target_space)
                ):
                    stack.append((target_space, target_name))

        if not inherited:
            return None
        names = tuple(name for name in owner_params if name in inherited)
        positions = tuple(owner_params.index(name) for name in names)
        if len(set(positions)) != len(positions):
            return None

        binding = HierarchicalItemSpaceParameterBinding(
            ref_name=ref_name,
            cell_name=cell_name,
            owner_space_fullname=str(
                getattr(self.space, "fullname", None) or getattr(self.space, "name", "<space>")
            ),
            child_space_fullname=str(
                getattr(root, "fullname", None) or getattr(root, "name", "<space>")
            ),
            parameter_names=names,
            parameter_positions=positions,
            dependency_cells=tuple(sorted(dependency_fullnames)),
        )
        # The compile-time RunDomain must already demonstrate exact activation of
        # every inherited parameter through the relative child Space.
        self._validate_hierarchical_itemspace_binding(binding, self.run_keys)
        return binding

    def _run_key_parameter_value(self, key: Any, position: int) -> Any:
        if position < 0 or position >= len(self.space_params):
            raise FrontendError("hierarchical ItemSpace parameter position is invalid")
        if len(self.space_params) == 1:
            value = key
        else:
            if not isinstance(key, tuple) or len(key) != len(self.space_params):
                raise FrontendError(
                    f"multi-parameter ItemSpace key must be a tuple of length {len(self.space_params)}"
                )
            value = key[position]
        if isinstance(value, np.generic):
            value = value.item()
        if isinstance(value, (tuple, list, dict, set, np.ndarray)):
            raise FrontendError(
                "composite ItemSpace parameters are outside hierarchical scalar binding"
            )
        return value

    def _validate_hierarchical_itemspace_binding(
        self, binding: HierarchicalItemSpaceParameterBinding, keys: Sequence[Any]
    ) -> None:
        if binding.owner_space_fullname != str(
            getattr(self.space, "fullname", None) or getattr(self.space, "name", "<space>")
        ):
            raise FrontendError("hierarchical ItemSpace owner changed after compilation")
        if tuple(binding.parameter_names) != tuple(
            self.space_params[pos] for pos in binding.parameter_positions
        ):
            raise FrontendError("hierarchical ItemSpace parameter schema changed after compilation")
        for key in keys:
            owner = self._space_instance(key)
            dynamic_root = self._context_root_for_key(binding.ref_name, key)
            if dynamic_root is self.refs[binding.ref_name]:
                raise FrontendError(
                    f"relative child Space {binding.ref_name!r} did not activate an ItemSpace context"
                )
            # The dynamic child may be more than one unparameterized level below the
            # owner, but its parent chain must terminate at this exact ItemSpace.
            cur = dynamic_root
            found_owner = False
            while cur is not None:
                parent = getattr(cur, "parent", None)
                if parent is owner:
                    found_owner = True
                    break
                if parent is None:
                    break
                if tuple(getattr(parent, "parameters", ()) or ()):
                    raise FrontendError(
                        "hierarchical binding encountered a competing parameterized ItemSpace context"
                    )
                cur = parent
            if not found_owner:
                raise FrontendError(
                    f"relative child Space {binding.ref_name!r} is not owned by the active RunDomain ItemSpace"
                )
            refs = getattr(dynamic_root, "refs", None)
            if refs is None:
                raise FrontendError("hierarchical child Space has no resolved reference environment")
            for name, pos in zip(binding.parameter_names, binding.parameter_positions):
                if name not in refs:
                    raise FrontendError(
                        f"hierarchical child Space did not inherit owner parameter {name!r}"
                    )
                actual = refs[name]
                if isinstance(actual, np.generic):
                    actual = actual.item()
                expected = self._run_key_parameter_value(key, pos)
                try:
                    equal = type(actual) is type(expected) and actual == expected
                except Exception:
                    equal = False
                if not bool(equal):
                    # Numeric scalar wrappers are harmless, but rich/coercive
                    # equality is deliberately not accepted.
                    if not (
                        isinstance(actual, (bool, int, float, str))
                        and isinstance(expected, (bool, int, float, str))
                        and actual == expected
                    ):
                        raise FrontendError(
                            f"hierarchical owner parameter {name!r} does not match the active RunDomain key"
                        )

    def _context_root_for_key(self, ref_name: str, key: Any | None = None) -> Any:
        """Resolve one model-bound root through the active ItemSpace context.

        Access through ``_space_instance`` is important for modelx interface
        references whose bound parameters are activated by the enclosing ItemSpace
        (for example a scenario Space selected by one Projection coordinate).
        """
        if ref_name not in self.refs:
            raise FrontendError(f"unknown model-bound context root {ref_name!r}")
        if key is None:
            return self.refs[ref_name]
        item = self._space_instance(key)
        refs = getattr(item, "refs", None)
        if refs is not None and ref_name in refs:
            return refs[ref_name]
        try:
            return getattr(item, ref_name)
        except Exception:
            return self.refs[ref_name]

    def _context_cell_for_key(
        self, ref_name: str, member_name: str, key: Any | None = None
    ) -> Any:
        """Resolve a concrete Cells member, including a Cells-valued Space alias."""
        root = self._context_root_for_key(ref_name, key)
        candidate = None
        cells = getattr(root, "cells", None)
        if cells is not None and member_name in cells:
            candidate = cells[member_name]
        if candidate is None:
            refs = getattr(root, "refs", None)
            if refs is not None and member_name in refs:
                candidate = refs[member_name]
        if candidate is None:
            try:
                candidate = getattr(root, member_name)
            except Exception:
                candidate = None
        if not self._is_modelx_cells_object(candidate):
            raise FrontendError(
                f"model-bound context member {ref_name}.{member_name} is not a concrete Cells object"
            )
        return candidate

    @staticmethod
    def _context_primitive(value: Any) -> tuple[bool, Any]:
        if isinstance(value, np.generic):
            value = value.item()
        return (
            isinstance(value, (str, bool, int, float, type(None))),
            value,
        )

    def _context_static_value(self, node: ast.AST, key: Any) -> tuple[bool, Any]:
        """Resolve a tiny immutable/static argument subset for context Cells calls.

        Values are re-resolved for every bound run key rather than baked into the
        generated formula.  This keeps modelx rebinding on the preparation side of
        the existing numeric ABI and avoids introducing runtime context objects.
        """
        if isinstance(node, ast.Constant):
            return self._context_primitive(node.value)
        if isinstance(node, ast.Name):
            if node.id in self.space_params or node.id not in self.refs:
                return False, None
            item = self._space_instance(key)
            refs = getattr(item, "refs", None)
            value = refs[node.id] if refs is not None and node.id in refs else self.refs[node.id]
            return self._context_primitive(value)
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            base_name = node.value.id
            if base_name not in self.refs:
                return False, None
            try:
                base = self._context_root_for_key(base_name, key)
                refs = getattr(base, "refs", None)
                if refs is not None and node.attr in refs:
                    value = refs[node.attr]
                else:
                    value = getattr(base, node.attr)
            except Exception:
                return False, None
            return self._context_primitive(value)
        if isinstance(node, ast.UnaryOp):
            ok, value = self._context_static_value(node.operand, key)
            if not ok:
                return False, None
            try:
                if isinstance(node.op, ast.UAdd):
                    return self._context_primitive(+value)
                if isinstance(node.op, ast.USub):
                    return self._context_primitive(-value)
                if isinstance(node.op, ast.Not):
                    return True, not bool(value)
            except Exception:
                return False, None
        if isinstance(node, ast.BinOp):
            ok_l, left = self._context_static_value(node.left, key)
            ok_r, right = self._context_static_value(node.right, key)
            if not (ok_l and ok_r):
                return False, None
            try:
                if isinstance(node.op, ast.Add): value = left + right
                elif isinstance(node.op, ast.Sub): value = left - right
                elif isinstance(node.op, ast.Mult): value = left * right
                elif isinstance(node.op, ast.Div): value = left / right
                elif isinstance(node.op, ast.FloorDiv): value = left // right
                elif isinstance(node.op, ast.Mod): value = left % right
                else: return False, None
            except Exception:
                return False, None
            return self._context_primitive(value)
        return False, None

    def _context_static_argument_is_fixed(self, node: ast.AST) -> bool:
        values: list[Any] = []
        for key in self.run_keys:
            ok, value = self._context_static_value(node, key)
            if not ok:
                return False
            values.append(value)
        if not values:
            return False
        first = values[0]
        try:
            return all(type(value) is type(first) and value == first for value in values[1:])
        except Exception:
            return False

    def _space_instance(self, key: Any):
        """Return the structural instance for one RunDomain key.

        Parameterized Spaces use normal ItemSpace indexing.  A non-parameterized
        Space is itself the sole structural instance and is represented in
        RunDomain by the singleton key ``()``.
        """
        if not self.space_params:
            if key != ():
                raise FrontendError(
                    f"non-parameterized Space expects RunDomain key (), got {key!r}"
                )
            return self.space
        return self.space[key]

    def modelx_output_value(self, key: Any) -> Any:
        item = self._space_instance(key)
        cell = getattr(item, self.output)
        return cell(*self.output_invocation.argument_values)

    def _infer_run_keys(self):
        if not self.space.parameters:
            return ((),)
        if self.space.parameters:
            row = self._detect_point_row_cell()
            if row is not None:
                frame = row.provider()
                if isinstance(frame, pd.DataFrame):
                    return tuple(frame.index)
        raise FrontendError("run_keys are required when the compiler cannot infer ItemSpace keys from a DataFrame row lookup")

    def _detect_point_row_cell(self) -> PointRowBinding | None:
        """Normalize supported model-point row access to one semantic source.

        Supported source spellings are deliberately narrow:

        ``direct_table.loc[point_id]``
        ``external_space.zero_arg_table_cell().loc[point_id]``

        Both become the same point-input ABI later.  Only preparation retains the
        provider callback; emitters receive numeric arrays plus provenance metadata.
        """
        if not self.space_params:
            return None
        positions = {name: i for i, name in enumerate(self.space_params)}

        def semantic_for(
            *, source_kind: str, source_ref: str, source_cell: str | None,
            frame: pd.DataFrame, key_name: str, key_pos: int,
        ) -> NormalizedPointRowSource:
            return NormalizedPointRowSource(
                source_kind=source_kind, source_ref=source_ref, source_cell=source_cell,
                source_shape=tuple(frame.shape), index_names=tuple(frame.index.names),
                key_parameter=key_name, key_position=int(key_pos),
            )

        for name, cell in self.space.cells.items():
            if cell.formula is None or cell.parameters:
                continue
            fn = ast.parse(cell.formula.source).body[0]
            body = [
                x for x in fn.body
                if not (
                    isinstance(x, ast.Expr) and isinstance(x.value, ast.Constant)
                    and isinstance(x.value.value, str)
                )
            ]
            if len(body) != 1 or not isinstance(body[0], ast.Return):
                continue
            r = body[0].value
            if not (
                isinstance(r, ast.Subscript)
                and isinstance(r.value, ast.Attribute)
                and r.value.attr == "loc"
                and isinstance(r.slice, ast.Name)
                and r.slice.id in positions
            ):
                continue
            key_name = r.slice.id
            key_pos = positions[key_name]
            table_expr = r.value.value

            # Existing direct DataFrame Reference form.
            if isinstance(table_expr, ast.Name):
                refname = table_expr.id
                frame = self.refs.get(refname)
                if isinstance(frame, pd.DataFrame):
                    semantic = semantic_for(
                        source_kind="direct_reference", source_ref=refname,
                        source_cell=None, frame=frame, key_name=key_name, key_pos=key_pos,
                    )
                    return PointRowBinding(
                        cell_name=name, semantic=semantic,
                        provider=lambda rn=refname, frontend=self: frontend.space.refs[rn],
                    )

            # Local zero-argument Cell returning a DataFrame.  This is the same
            # semantic point-row source as a direct/external table; the extra Cell
            # layer is preparation-only and must not survive the numeric ABI.
            if (
                isinstance(table_expr, ast.Call)
                and isinstance(table_expr.func, ast.Name)
                and not table_expr.args and not table_expr.keywords
                and table_expr.func.id in self.space.cells
            ):
                source_cell_name = table_expr.func.id
                source_cell = self.space.cells[source_cell_name]
                if not tuple(source_cell.parameters or ()):
                    try:
                        frame = source_cell()
                    except Exception:
                        frame = None
                    if isinstance(frame, pd.DataFrame):
                        semantic = semantic_for(
                            source_kind="local_cell", source_ref=self.space.name,
                            source_cell=source_cell_name, frame=frame,
                            key_name=key_name, key_pos=key_pos,
                        )
                        return PointRowBinding(
                            cell_name=name, semantic=semantic, provider=source_cell,
                        )

            # Qualified zero-argument external Cell returning a DataFrame.
            if (
                isinstance(table_expr, ast.Call)
                and isinstance(table_expr.func, ast.Attribute)
                and isinstance(table_expr.func.value, ast.Name)
                and not table_expr.args and not table_expr.keywords
            ):
                refname = table_expr.func.value.id
                cell_name = table_expr.func.attr
                obj = self.refs.get(refname)
                if obj is None or not hasattr(obj, "cells") or cell_name not in obj.cells:
                    continue
                source_cell = obj.cells[cell_name]
                if tuple(source_cell.parameters or ()):
                    continue
                try:
                    frame = source_cell()
                except Exception:
                    continue
                if not isinstance(frame, pd.DataFrame):
                    continue
                semantic = semantic_for(
                    source_kind="external_cell", source_ref=refname,
                    source_cell=cell_name, frame=frame, key_name=key_name, key_pos=key_pos,
                )
                return PointRowBinding(
                    cell_name=name, semantic=semantic, provider=source_cell,
                )
        return None

    def _is_numpy_array_call(self, node: ast.Call) -> bool:
        if not isinstance(node.func, ast.Attribute) or node.func.attr != "array" or not isinstance(node.func.value, ast.Name):
            return False
        obj = self.refs.get(node.func.value.id)
        return obj is np

    def _unwrap_generator(self, node: ast.AST) -> ast.GeneratorExp | None:
        if isinstance(node, ast.GeneratorExp):
            return node
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ("list", "tuple") and len(node.args)==1 and isinstance(node.args[0], ast.GeneratorExp):
            return node.args[0]
        return None

    def _discover_vector_helpers(self):
        result = {}
        for name, fn in self.base_funcs.items():
            body=[x for x in fn.body if not (isinstance(x,ast.Expr) and isinstance(x.value,ast.Constant) and isinstance(x.value.value,str))]
            if len(body)!=1 or not isinstance(body[0],ast.Return):
                continue
            ret=body[0].value
            if not (isinstance(ret,ast.Call) and self._is_numpy_array_call(ret) and len(ret.args)==1):
                continue
            gen=self._unwrap_generator(ret.args[0])
            if gen is None or len(gen.generators)!=1 or gen.generators[0].ifs:
                continue
            comp=gen.generators[0]
            if not isinstance(comp.target,ast.Name) or not (isinstance(comp.iter,ast.Call) and isinstance(comp.iter.func,ast.Name) and comp.iter.func.id=="range"):
                continue
            result[name]=(comp.target.id, copy.deepcopy(comp.iter), copy.deepcopy(gen.elt))
        return result

    def _inline_vector_subscripts(self, node: ast.AST, depth=0) -> ast.AST:
        if depth > 10:
            raise FrontendError("nested vector helper expansion exceeded safety depth")
        outer=self
        class Rewriter(ast.NodeTransformer):
            def visit_Subscript(self, n):
                n=self.generic_visit(n)
                if isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and not n.value.args and n.value.func.id in outer.vector_elements and not isinstance(n.slice,ast.Slice):
                    vname=n.value.func.id
                    var, rng, elt=outer.vector_elements[vname]
                    repl=_Substitute({var:copy.deepcopy(n.slice)}).visit(copy.deepcopy(elt))
                    return ast.copy_location(outer._inline_vector_subscripts(ast.fix_missing_locations(repl), depth+1),n)
                return n
        return ast.fix_missing_locations(Rewriter().visit(copy.deepcopy(node)))

    def _stable_realized_dep_names(self, uid: str) -> set[str] | None:
        """Return one direct same-Space dependency signature if every call agrees.

        The check is intentionally concrete rather than variant-aggregate: a time
        family may legitimately take different branches at different coordinates.
        Such a family is not branch-specialized.
        """
        tr = self.variant_trace_by_uid[uid]
        signatures: set[frozenset[str]] = set()
        for runtime_node, key in self.trace.node_variant.items():
            if key != tr.key:
                continue
            deps: set[str] = set()
            for pred in self.trace.graph.predecessors(runtime_node):
                pkey = self.trace.node_variant.get(pred)
                dep = self.trace.variants.get(pkey) if pkey is not None else None
                if dep is not None and dep.schema.name in self.base_funcs:
                    deps.add(dep.schema.name)
            signatures.add(frozenset(deps))
            if len(signatures) > 1:
                return None
        if len(signatures) != 1:
            return None
        return set(next(iter(signatures)))

    def _same_space_calls(self, node: ast.AST) -> set[str]:
        return {
            child.func.id
            for child in ast.walk(node)
            if isinstance(child, ast.Call)
            and isinstance(child.func, ast.Name)
            and child.func.id in self.base_funcs
        }

    def _enumerate_straight_paths(
        self, stmts: Sequence[ast.stmt]
    ) -> list[tuple[list[ast.stmt], set[str]]] | None:
        """Enumerate if/return execution paths for conservative graph pruning."""

        max_paths = 32

        def walk(rest: list[ast.stmt], prefix: list[ast.stmt]):
            if not rest:
                return [(list(prefix), set())]
            st, tail = rest[0], rest[1:]
            if isinstance(st, ast.Expr) and isinstance(st.value, ast.Constant) and isinstance(st.value.value, str):
                return walk(tail, prefix)
            if isinstance(st, (ast.For, ast.While, ast.Try, ast.With, ast.AsyncWith, ast.Match)):
                return None
            if isinstance(st, (ast.Return, ast.Raise)):
                return [(list(prefix) + [copy.deepcopy(st)], self._same_space_calls(st))]
            if isinstance(st, ast.If):
                cond = self._same_space_calls(st.test)
                out: list[tuple[list[ast.stmt], set[str]]] = []
                branches = [list(st.body), list(st.orelse)] if st.orelse else [list(st.body), []]
                for branch in branches:
                    got = walk(branch + tail, list(prefix))
                    if got is None:
                        return None
                    out.extend((seq, cond | calls) for seq, calls in got)
                    if len(out) > max_paths:
                        return None
                return out
            got = walk(tail, list(prefix) + [copy.deepcopy(st)])
            if got is None:
                return None
            own = self._same_space_calls(st)
            return [(seq, own | calls) for seq, calls in got]

        return walk(list(stmts), [])

    def _prune_to_realized_path(self, uid: str, fn: ast.FunctionDef) -> ast.FunctionDef:
        """Prune only a uniquely proven fixed-graph control-flow path.

        No traced scalar/table result is substituted.  The only specialization is
        graph topology, and only when every concrete invocation of the variant has
        the same direct dependency signature and exactly one source path matches it.
        """
        if not self.realized_graph_only:
            return fn
        observed = self._stable_realized_dep_names(uid)
        if observed is None:
            return fn
        source_calls = self._same_space_calls(fn)
        if not (source_calls - observed):
            return fn
        paths = self._enumerate_straight_paths(fn.body)
        if not paths or len(paths) <= 1:
            return fn
        matches = [seq for seq, calls in paths if calls == observed]
        if len(matches) != 1:
            return fn
        out = copy.deepcopy(fn)
        out.body = matches[0]
        return ast.fix_missing_locations(out)

    def _runtime_scalar_helper_candidates(self, name: str, *, allow_coordinate: bool = False):
        """Return observed variants eligible for upstream scalar-helper inlining.

        The original subset admits only non-coordinate helpers with numeric/bool
        runtime arguments.  ``allow_coordinate`` adds one deliberately narrow case:
        a scalar Cell whose representative trace classified one parameter as a
        coordinate, but whose body can still be fully inlined before scheduling.
        Numeric/bool non-coordinate arguments may remain runtime scalar expressions.
        Categorical non-coordinate arguments must become literals (or full-run-domain
        static proofs) at the call boundary; they do not create a new runtime
        categorical dimension.
        """
        base = self.base_funcs.get(name)
        if base is None:
            return ()
        params = [a.arg for a in base.args.args]
        if not params:
            return ()
        rows = [tr for tr in self.variant_trace_by_uid.values() if tr.schema.name == name]
        if not rows:
            return ()
        positions = {tr.key.time_pos for tr in rows}
        coordinate_classified = positions != {None}
        if coordinate_classified:
            if not allow_coordinate or None in positions or len(positions) != 1:
                return ()
        numeric = (bool, int, float, np.bool_, np.integer, np.floating)
        scalar = (str, bool, int, float, np.bool_, np.integer, np.floating)
        for tr in rows:
            if tr.dtype not in ("bool", "int64", "float64"):
                return ()
            expected_aux = len(params) - (1 if coordinate_classified else 0)
            if len(tr.key.aux_values) != expected_aux:
                return ()
            allowed = scalar if coordinate_classified else numeric
            if any(not isinstance(value, allowed) for value in tr.key.aux_values):
                return ()
        return tuple(rows)

    def _proven_static_helper_argument(self, expr: ast.AST) -> tuple[bool, Any]:
        """Resolve a helper selector to a literal only with a full-domain proof.

        Literal arguments are accepted directly.  A Cell call is accepted only if
        it resolves to a non-coordinate observed variant whose value is invariant
        over every ``run_key`` in the compiled artifact.  This is intentionally not
        a generic constant folder for arbitrary expressions.
        """
        try:
            value = ast.literal_eval(expr)
        except Exception:
            value = None
        else:
            if isinstance(value, np.generic):
                value = value.item()
            if isinstance(value, (str, bool, int, float)):
                return True, value

        if (
            isinstance(expr, ast.Call) and isinstance(expr.func, ast.Name)
            and expr.func.id in self.base_funcs
        ):
            try:
                uid, coordinate_expr = self._variant_for_call(expr.func.id, expr, {})
            except FrontendError:
                return False, None
            if coordinate_expr is not None:
                return False, None
            ok, value = self._proven_static_variant_value(uid)
            if ok:
                if isinstance(value, np.generic):
                    value = value.item()
                self._used_static_facts[("cell", ast.unparse(expr))] = StaticScalarFact(
                    "cell", ast.unparse(expr), value, len(self.run_keys)
                )
                return True, value

        if (
            isinstance(expr, ast.Call) and isinstance(expr.func, ast.Name)
            and expr.func.id in {"str", "bool", "int", "float"}
            and len(expr.args) == 1 and not expr.keywords
        ):
            ok, inner = self._proven_static_helper_argument(expr.args[0])
            if ok:
                try:
                    return True, {"str": str, "bool": bool, "int": int, "float": float}[expr.func.id](inner)
                except Exception:
                    return False, None
        return False, None

    def _sparse_observed_coordinate_helper_candidates(
        self, name: str, params: list[str], assigned: dict[str, ast.AST]
    ) -> tuple[tuple[Any, ...], int | None]:
        """Recover one primary-time helper parameter from a sparse fixed trace.

        Some pure wrappers are executed only when an event occurs, so modelx may
        observe ``helper(36, 'OPTION')`` as a fixed non-coordinate variant even
        though the source caller is the monthly family ``caller(t, bucket)`` and
        passes its primary ``t`` straight through.  Reclassifying the trace would
        be unsafe; instead this call-site-only proof permits upstream helper
        inlining when exactly one parameter is literally the canonical primary
        coordinate ``t``.  The observed values for that parameter must be integer
        coordinates.  All other categorical arguments remain subject to the same
        full-domain static proof as ordinary coordinate-classified helpers.
        """
        rows = tuple(tr for tr in self.variant_trace_by_uid.values() if tr.schema.name == name)
        if not rows or any(tr.key.time_pos is not None for tr in rows):
            return (), None
        if any(tr.dtype not in ("bool", "int64", "float64") for tr in rows):
            return (), None
        if any(len(tr.key.aux_values) != len(params) for tr in rows):
            return (), None
        candidates: list[int] = []
        for pos, param in enumerate(params):
            expr = assigned.get(param)
            if not (isinstance(expr, ast.Name) and expr.id == "t"):
                continue
            observed = [tr.key.aux_values[pos] for tr in rows]
            if observed and all(
                isinstance(value, (int, np.integer)) and not isinstance(value, (bool, np.bool_))
                for value in observed
            ):
                candidates.append(pos)
        if len(candidates) != 1:
            return (), None
        scalar = (str, bool, int, float, np.bool_, np.integer, np.floating)
        coordinate_pos = candidates[0]
        for tr in rows:
            if any(
                pos != coordinate_pos and not isinstance(value, scalar)
                for pos, value in enumerate(tr.key.aux_values)
            ):
                return (), None
        return rows, coordinate_pos

    def _runtime_scalar_helper_expr_from_block(
        self, stmts: list[ast.stmt], env: dict[str, ast.AST]
    ) -> ast.AST:
        """Convert a pure straight/conditional helper body to one expression.

        This is hygienic upstream inlining, not a second runtime calling convention.
        Assignments become lexical substitutions; conditionals become ``IfExp``.
        Loops, mutation, raises, augmented assignment and other statement effects are
        intentionally outside the first helper subset.
        """
        if not stmts:
            raise FrontendError("runtime scalar helper has a path without a return value")
        original = copy.deepcopy(stmts[0])
        rest = list(stmts[1:])
        st = _Substitute(env).visit(original)
        st = _ConservativeFolder().visit(ast.fix_missing_locations(st))
        if isinstance(st, list):
            return self._runtime_scalar_helper_expr_from_block(list(st) + rest, dict(env))
        if isinstance(st, ast.Expr) and isinstance(st.value, ast.Constant) and isinstance(st.value.value, str):
            return self._runtime_scalar_helper_expr_from_block(rest, dict(env))
        if isinstance(st, ast.Pass):
            return self._runtime_scalar_helper_expr_from_block(rest, dict(env))
        if isinstance(st, ast.Assign) and len(st.targets) == 1 and isinstance(st.targets[0], ast.Name):
            next_env = dict(env)
            next_env[st.targets[0].id] = copy.deepcopy(st.value)
            return self._runtime_scalar_helper_expr_from_block(rest, next_env)
        if isinstance(st, ast.AnnAssign) and isinstance(st.target, ast.Name) and st.value is not None:
            next_env = dict(env)
            next_env[st.target.id] = copy.deepcopy(st.value)
            return self._runtime_scalar_helper_expr_from_block(rest, next_env)
        if isinstance(st, ast.Return):
            if st.value is None:
                raise FrontendError("runtime scalar helper has a bare return")
            return ast.fix_missing_locations(copy.deepcopy(st.value))
        if isinstance(st, ast.If):
            test = copy.deepcopy(st.test)
            if isinstance(test, ast.Constant):
                branch = list(st.body if bool(test.value) else st.orelse)
                return self._runtime_scalar_helper_expr_from_block(branch + rest, dict(env))
            body = self._runtime_scalar_helper_expr_from_block(list(st.body) + rest, dict(env))
            other = self._runtime_scalar_helper_expr_from_block(list(st.orelse) + rest, dict(env))
            return ast.fix_missing_locations(ast.IfExp(test=test, body=body, orelse=other))
        raise FrontendError(
            f"runtime scalar helper statement {type(st).__name__} is outside the pure inlining subset"
        )

    def _prepare_runtime_scalar_helper_function(
        self, name: str, call: ast.Call
    ) -> tuple[ast.FunctionDef, tuple[str, ...], int, bool, bool, bool] | None:
        """Bind and normalize one pure scalar helper without erasing its locals.

        dev19-dev24 represented a helper call as one recursively substituted
        expression.  That is compact for tiny helpers, but it duplicates reused
        locals exponentially in deeper pure helper graphs (RILA's Black-Scholes
        chain is the first real-product example).  Keep this preparation step
        separate from the representation chosen by the caller: the legacy
        expression inliner can still use it, while dev25 can lower the same proven
        helper body into hygienic local statements.

        The returned FunctionDef has all call arguments bound and has already
        passed the same static-fact, table and local-syntax normalization used by
        the expression path.  It is *not* a runtime helper ABI: callers must erase
        it by inlining before executable graph scheduling.
        """
        base = copy.deepcopy(self.base_funcs[name])
        params = [a.arg for a in base.args.args]
        defaults: dict[str, ast.AST] = {}
        if base.args.defaults:
            for param, default in zip(params[-len(base.args.defaults):], base.args.defaults):
                defaults[param] = copy.deepcopy(default)
        assigned: dict[str, ast.AST] = {}
        for param, arg in zip(params, call.args):
            assigned[param] = copy.deepcopy(arg)
        for kw in call.keywords:
            if kw.arg is None or kw.arg in assigned:
                return None
            assigned[kw.arg] = copy.deepcopy(kw.value)
        for param in params:
            if param not in assigned:
                if param not in defaults:
                    return None
                assigned[param] = copy.deepcopy(defaults[param])
        if len(assigned) != len(params):
            return None

        rows = self._runtime_scalar_helper_candidates(name)
        coordinate_classified = False
        coordinate_recovered_from_callsite = False
        source_backed_unobserved = False
        coordinate_pos_override: int | None = None
        if not rows:
            rows = self._runtime_scalar_helper_candidates(name, allow_coordinate=True)
            coordinate_classified = bool(rows)
        if not rows:
            rows, coordinate_pos_override = self._sparse_observed_coordinate_helper_candidates(
                name, params, assigned
            )
            if rows:
                coordinate_classified = True
                coordinate_recovered_from_callsite = True
        if not rows:
            if not self._source_backed_unobserved_helper_ok(name):
                return None
            # No trace schema is invented.  This helper is erased by hygienic
            # source inlining before scheduling, so its call arguments remain the
            # caller's ordinary scalar/coordinate expressions and observed Cells
            # in its body remain graph boundaries.
            source_backed_unobserved = True

        if coordinate_classified:
            if coordinate_pos_override is None:
                positions = {tr.key.time_pos for tr in rows}
                if None in positions or len(positions) != 1:
                    return None
                coordinate_pos = next(iter(positions))
            else:
                coordinate_pos = coordinate_pos_override
            numeric = (bool, int, float, np.bool_, np.integer, np.floating)
            aux_by_pos: dict[int, list[Any]] = {pos: [] for pos in range(len(params)) if pos != coordinate_pos}
            for tr in rows:
                if coordinate_recovered_from_callsite:
                    for pos in aux_by_pos:
                        aux_by_pos[pos].append(tr.key.aux_values[pos])
                else:
                    aux_iter = iter(tr.key.aux_values)
                    for pos in range(len(params)):
                        if pos == coordinate_pos:
                            continue
                        aux_by_pos[pos].append(next(aux_iter))
            for pos, param in enumerate(params):
                if pos == coordinate_pos:
                    continue
                observed = aux_by_pos[pos]
                if observed and all(isinstance(value, numeric) for value in observed):
                    # Numeric/bool helper inputs are ordinary runtime scalars.  If a
                    # downstream operation needs them to be static, that operation's
                    # own proof/normalizer must establish it or fail closed.
                    continue
                ok, value = self._proven_static_helper_argument(assigned[param])
                if not ok:
                    return None
                assigned[param] = ast.Constant(value=value)

        # Bind helper arguments first.  In particular, a coordinate-classified pure
        # helper such as CI_UK_S.pivot_interp has categorical table selectors that
        # become static only at the caller.  Normalizing pandas before substitution
        # would therefore miss the preparation-time slice and reject a supported
        # mathematical lookup for purely syntactic reasons.
        base = _Substitute(assigned).visit(base)
        base = _ConservativeFolder().visit(ast.fix_missing_locations(base))
        if not isinstance(base, ast.FunctionDef):
            return None
        base = _prune_source_unreachable_tails(base)
        base = self._specialize_static_facts_and_domains(base)
        base = _ConservativeFolder().visit(ast.fix_missing_locations(base))
        if not isinstance(base, ast.FunctionDef):
            return None
        base = _prune_source_unreachable_tails(base)
        base = self._normalize_external_tables(base)
        base = self._normalize_simple_local_syntax(base)
        return (
            base, tuple(params), len(rows), coordinate_classified,
            coordinate_recovered_from_callsite, source_backed_unobserved,
        )

    def _record_runtime_scalar_helper_fact(
        self, name: str, params: tuple[str, ...], observed_variant_count: int,
        coordinate_classified: bool, coordinate_recovered_from_callsite: bool = False,
        source_backed_unobserved: bool = False,
    ) -> None:
        self._used_runtime_scalar_helper_facts[name] = RuntimeScalarHelperFact(
            source_name=name, parameters=params,
            observed_variant_count=observed_variant_count,
            coordinate_classified=coordinate_classified,
            coordinate_recovered_from_callsite=coordinate_recovered_from_callsite,
            source_backed_unobserved=source_backed_unobserved,
        )

    def _inline_runtime_scalar_helper_call(self, name: str, call: ast.Call) -> ast.AST | None:
        prepared = self._prepare_runtime_scalar_helper_function(name, call)
        if prepared is None:
            return None
        (
            base, params, observed_variant_count, coordinate_classified,
            coordinate_recovered, source_backed_unobserved,
        ) = prepared
        expr = self._runtime_scalar_helper_expr_from_block(list(base.body), {})
        self._record_runtime_scalar_helper_fact(
            name, params, observed_variant_count, coordinate_classified, coordinate_recovered,
            source_backed_unobserved,
        )
        return ast.copy_location(expr, call)

    def _source_backed_unobserved_helper_ok(self, name: str) -> bool:
        """Prove a completely unobserved Cell can disappear by source inlining.

        Observed Cells are terminal graph boundaries for this proof, including
        recursive state.  Only the closure made exclusively of *unobserved* helper
        Cells is recursively inspected, so a helper such as ``excess_factor(t)``
        may legitimately read observed recursive account state without flattening
        that state into the helper.  Any cycle among unobserved helpers, object
        boundary, or statement side effect fails closed.
        """
        if name in self._source_backed_helper_cache:
            return self._source_backed_helper_cache[name]
        if name in self.schema_by_name or name not in self.base_funcs:
            self._source_backed_helper_cache[name] = False
            return False

        numeric_dtypes = {"bool", "int64", "float64"}
        active: set[str] = set()
        local_cache: dict[str, bool] = {}

        def walk(current: str) -> bool:
            if current in local_cache:
                return local_cache[current]
            if current in active:
                return False
            if current in self.schema_by_name:
                if (
                    self.model_point_row is not None
                    and current == self.model_point_row.cell_name
                ):
                    # The model-point row is an object only at preparation time.
                    # Its field reads are normalized later into guarded numeric
                    # point inputs, so it is a safe source-helper boundary without
                    # creating an object runtime ABI.
                    return True
                rows = [tr for tr in self.variant_trace_by_uid.values() if tr.schema.name == current]
                return bool(rows) and all(tr.dtype in numeric_dtypes for tr in rows)
            fn = self.base_funcs.get(current)
            if fn is None:
                return False
            active.add(current)
            returns = [node for node in ast.walk(fn) if isinstance(node, ast.Return)]
            if not returns or any(node.value is None for node in returns):
                active.remove(current)
                local_cache[current] = False
                return False
            prohibited = (
                ast.Global, ast.Nonlocal, ast.AugAssign, ast.Delete,
                ast.For, ast.AsyncFor, ast.While, ast.Try, ast.With, ast.AsyncWith,
                ast.Match, ast.Yield, ast.YieldFrom, ast.Await,
            )
            if any(isinstance(node, prohibited) for node in ast.walk(fn)):
                active.remove(current)
                local_cache[current] = False
                return False
            for ret in returns:
                value = ret.value
                if isinstance(value, ast.Constant) and (
                    value.value is None or isinstance(value.value, (str, bytes, complex))
                ):
                    active.remove(current)
                    local_cache[current] = False
                    return False
                if isinstance(value, (ast.Tuple, ast.List, ast.Set, ast.Dict)):
                    active.remove(current)
                    local_cache[current] = False
                    return False
            for node in ast.walk(fn):
                if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)):
                    continue
                dep = node.func.id
                if dep not in self.base_funcs:
                    continue
                if not walk(dep):
                    active.remove(current)
                    local_cache[current] = False
                    return False
            active.remove(current)
            local_cache[current] = True
            return True

        result = walk(name)
        self._source_backed_helper_cache.update(local_cache)
        self._source_backed_helper_cache[name] = result
        return result

    def _source_reaches_recursive_cycle(self, name: str) -> bool:
        """Conservatively identify source closures that contain recursive state.

        This is used only to decide whether a non-affine coordinate call should be
        preserved as a scheduled Cell instead of treated as an acyclic helper.  It
        does not classify ordinary parameterized helper calls and it does not make
        any scheduling decision by itself.
        """
        if name in self._source_recursive_reach_cache:
            return self._source_recursive_reach_cache[name]

        seen: set[str] = set()
        active: set[str] = set()

        def walk(current: str) -> bool:
            if current in active:
                return True
            if current in seen:
                return False
            seen.add(current)
            active.add(current)
            fn = self.base_funcs.get(current)
            if fn is not None:
                for node in ast.walk(fn):
                    if (
                        isinstance(node, ast.Call)
                        and isinstance(node.func, ast.Name)
                        and node.func.id in self.base_funcs
                        and walk(node.func.id)
                    ):
                        active.remove(current)
                        return True
            active.remove(current)
            return False

        result = walk(name)
        self._source_recursive_reach_cache[name] = result
        return result

    def _inline_runtime_scalar_helpers_as_statements(
        self, fn: ast.FunctionDef
    ) -> tuple[ast.FunctionDef, dict[str, ast.AST]]:
        """Erase parameterized pure helpers while preserving their local temporaries.

        The old helper path substitutes every local into the returned expression.
        That is intentionally retained as a small/fallback representation, but it
        is a poor fit for formulas that reuse intermediates.  This pass performs a
        tiny A-normal/statement-level lowering instead: a helper call becomes a set
        of hygienically named assignments plus one result temporary.  Existing
        scheduled Cells remain calls and are canonicalized by ``Calls`` later.

        Only eager expression positions are hoisted.  Python short-circuit forms
        (BoolOp, chained Compare, IfExp, comprehensions/lambdas) are left intact so
        we never change which helper calls execute.  If such a position needs
        helper expansion, the legacy expression path remains the conservative
        backstop and its node budget still applies.
        """
        frontend = self
        existing = self._function_bound_names(fn)
        coordinate_aliases: dict[str, ast.AST] = {}
        counter = 0
        statement_expansion_nodes = 0

        def fresh(prefix: str) -> str:
            nonlocal counter
            while True:
                name = f"__mx_h_{prefix}_{counter}"
                counter += 1
                if name not in existing:
                    existing.add(name)
                    return name

        def count_added(nodes: list[ast.stmt], helper_name: str) -> None:
            nonlocal statement_expansion_nodes
            statement_expansion_nodes += sum(1 for st in nodes for _ in ast.walk(st))
            if statement_expansion_nodes > frontend._runtime_scalar_helper_expansion_limit:
                raise FrontendError(
                    "runtime scalar helper expansion budget exceeded "
                    f"({statement_expansion_nodes} > {frontend._runtime_scalar_helper_expansion_limit}) "
                    f"during statement lowering of {helper_name}"
                )

        def substitute_local(expr: ast.AST, env: dict[str, ast.AST]) -> ast.AST:
            out = _Substitute(env).visit(copy.deepcopy(expr))
            out = _ConservativeFolder().visit(ast.fix_missing_locations(out))
            if isinstance(out, list):
                raise FrontendError("runtime scalar helper expression folding produced statements")
            return ast.fix_missing_locations(out)

        def helper_call_kind(call: ast.Call) -> str | None:
            """Return source Cell name iff this call needs pure-helper inlining.

            Besides parameterized helpers with runtime numeric auxiliaries, dev25
            also uses the same fail-closed inliner to erase a *non-affine coordinate
            composition*.  The executable scheduler supports ``t + constant``.  If
            a pure Cell is called at some richer coordinate (RILA's
            ``index_level(term_start_month(t))``), inlining can move that coordinate
            expression into a table/scalar formula instead of pretending it is a
            new scheduled state dimension.  Recursive state fails closed because
            forcing its body would encounter the same helper on the inline stack.
            """
            if not (isinstance(call.func, ast.Name) and call.func.id in frontend.base_funcs):
                return None
            try:
                _uid, coordinate_expr = frontend._variant_for_call(call.func.id, call, {})
            except FrontendError as exc:
                if str(exc).startswith("non-time specialization argument is not a literal:"):
                    return call.func.id
                if (
                    str(exc).startswith(f"Cells {call.func.id} was not observed")
                    and frontend._source_backed_unobserved_helper_ok(call.func.id)
                ):
                    return call.func.id
                return None
            if coordinate_expr is None:
                return None

            # Recover SSA-like helper aliases only for the scheduling decision.
            # Arithmetic formula uses still read the local temporary itself.
            coordinate_expr = copy.deepcopy(coordinate_expr)
            for _ in range(len(coordinate_aliases) + 1):
                before = ast.dump(coordinate_expr, include_attributes=False)
                coordinate_expr = _Substitute(coordinate_aliases).visit(coordinate_expr)
                coordinate_expr = ast.fix_missing_locations(coordinate_expr)
                if ast.dump(coordinate_expr, include_attributes=False) == before:
                    break
            coordinate_expr = frontend._normalize_coordinate_expression(
                coordinate_expr, bound_names=existing
            )

            if (
                isinstance(coordinate_expr, ast.Constant)
                and isinstance(coordinate_expr.value, int)
                and not isinstance(coordinate_expr.value, bool)
            ):
                return None
            if isinstance(coordinate_expr, ast.Name) and coordinate_expr.id == "t":
                return None
            if (
                isinstance(coordinate_expr, ast.BinOp)
                and isinstance(coordinate_expr.left, ast.Name)
                and coordinate_expr.left.id == "t"
                and isinstance(coordinate_expr.right, ast.Constant)
                and isinstance(coordinate_expr.right.value, int)
                and not isinstance(coordinate_expr.right.value, bool)
                and isinstance(coordinate_expr.op, (ast.Add, ast.Sub))
            ):
                return None
            # A non-affine call into a Cell whose source closure reaches a cycle is
            # scheduled state. Preserve the outer semantic Cell rather than
            # partially flattening its implementation until a nested recursive
            # call eventually trips the inline stack. Pure coordinate helpers
            # continue through statement inlining.
            if frontend._source_reaches_recursive_cycle(call.func.id):
                # The dev26 scheduled-history foundation is explicitly tied to the
                # primary projection coordinate. A recursive Cell queried only by an
                # independent/local coordinate (IUL segment month ``m`` is the real
                # product example) is a genuine additional state dimension, not a
                # snapshot of the current monthly state. Keep the dev25 fail-closed
                # helper-recursion behavior for that class instead of routing it into
                # history scheduling / expensive loop recovery.
                mentions_primary_t = any(
                    isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load) and node.id == "t"
                    for node in ast.walk(coordinate_expr)
                )
                if mentions_primary_t:
                    return None
            return call.func.id

        def lift_expr(expr: ast.AST, helper_stack: tuple[str, ...]) -> tuple[list[ast.stmt], ast.AST]:
            """Hoist helper calls from eager scalar expression positions."""
            expr = copy.deepcopy(expr)

            # Preserve Python's conditional/short-circuit evaluation exactly.  The
            # existing expression inliner can still handle a small helper under one
            # of these nodes, or fail closed via its expansion budget.
            if isinstance(expr, (ast.BoolOp, ast.IfExp, ast.Lambda, ast.GeneratorExp,
                                 ast.ListComp, ast.SetComp, ast.DictComp)):
                return [], expr
            if isinstance(expr, ast.Compare) and len(expr.ops) > 1:
                return [], expr

            if isinstance(expr, ast.Call):
                pre: list[ast.stmt] = []
                new_args: list[ast.AST] = []
                for arg in expr.args:
                    p, value = lift_expr(arg, helper_stack)
                    pre.extend(p)
                    new_args.append(value)
                new_keywords: list[ast.keyword] = []
                for kw in expr.keywords:
                    p, value = lift_expr(kw.value, helper_stack)
                    pre.extend(p)
                    new_keywords.append(ast.keyword(arg=kw.arg, value=value))
                rebuilt = ast.copy_location(
                    ast.Call(func=copy.deepcopy(expr.func), args=new_args, keywords=new_keywords), expr
                )
                helper_name = helper_call_kind(rebuilt)
                if helper_name is None:
                    return pre, rebuilt
                if helper_name in helper_stack:
                    chain = " -> ".join((*helper_stack, helper_name))
                    raise FrontendError(f"runtime scalar helper recursion detected during helper/coordinate inlining: {chain}")
                prepared = frontend._prepare_runtime_scalar_helper_function(helper_name, rebuilt)
                if prepared is None:
                    # Leave it for the legacy fail-closed call rewriter.  In
                    # particular, do not reinterpret a categorical runtime axis as
                    # an ordinary numeric helper just to make the call disappear.
                    return pre, rebuilt
                (
                    helper_fn, params, observed_variant_count, coordinate_classified,
                    coordinate_recovered, source_backed_unobserved,
                ) = prepared
                result_name = fresh("result")
                try:
                    helper_stmts = lower_helper_block(
                        list(helper_fn.body), {}, result_name, (*helper_stack, helper_name)
                    )
                except FrontendError as exc:
                    # A coordinate-classified Cell that becomes recursive when we
                    # inspect its body is scheduled state, not an acyclic helper.
                    # Preserve the call so the executable scheduler can prove or
                    # reject the derived-coordinate history read.
                    if coordinate_classified and str(exc).startswith(
                        "runtime scalar helper recursion detected during helper/coordinate inlining:"
                    ):
                        return pre, rebuilt
                    raise
                count_added(helper_stmts, helper_name)
                frontend._record_runtime_scalar_helper_fact(
                    helper_name, params, observed_variant_count, coordinate_classified,
                    coordinate_recovered, source_backed_unobserved,
                )
                pre.extend(helper_stmts)
                return pre, ast.copy_location(ast.Name(result_name, ast.Load()), expr)

            # Eager expression nodes whose child evaluation order is simple and
            # relevant to the scalar subset.  Build them explicitly instead of a
            # generic ast walk so inserted statements keep Python evaluation order.
            if isinstance(expr, ast.BinOp):
                p1, left = lift_expr(expr.left, helper_stack)
                p2, right = lift_expr(expr.right, helper_stack)
                return p1 + p2, ast.copy_location(ast.BinOp(left, copy.deepcopy(expr.op), right), expr)
            if isinstance(expr, ast.UnaryOp):
                pre, operand = lift_expr(expr.operand, helper_stack)
                return pre, ast.copy_location(ast.UnaryOp(copy.deepcopy(expr.op), operand), expr)
            if isinstance(expr, ast.Compare):
                # One comparison has no chained-comparison short circuit.
                p1, left = lift_expr(expr.left, helper_stack)
                p2, right = lift_expr(expr.comparators[0], helper_stack)
                return p1 + p2, ast.copy_location(
                    ast.Compare(left, [copy.deepcopy(expr.ops[0])], [right]), expr
                )
            if isinstance(expr, ast.Attribute):
                pre, value = lift_expr(expr.value, helper_stack)
                return pre, ast.copy_location(ast.Attribute(value, expr.attr, copy.deepcopy(expr.ctx)), expr)
            if isinstance(expr, ast.Subscript):
                p1, value = lift_expr(expr.value, helper_stack)
                p2, sl = lift_expr(expr.slice, helper_stack)
                return p1 + p2, ast.copy_location(ast.Subscript(value, sl, copy.deepcopy(expr.ctx)), expr)
            if isinstance(expr, (ast.Tuple, ast.List, ast.Set)):
                pre: list[ast.stmt] = []
                elts: list[ast.AST] = []
                for elt in expr.elts:
                    p, value = lift_expr(elt, helper_stack)
                    pre.extend(p)
                    elts.append(value)
                if isinstance(expr, ast.Tuple):
                    rebuilt = ast.Tuple(elts, copy.deepcopy(expr.ctx))
                elif isinstance(expr, ast.List):
                    rebuilt = ast.List(elts, copy.deepcopy(expr.ctx))
                else:
                    rebuilt = ast.Set(elts)
                return pre, ast.copy_location(rebuilt, expr)
            if isinstance(expr, ast.Dict):
                pre: list[ast.stmt] = []
                keys: list[ast.AST | None] = []
                vals: list[ast.AST] = []
                for key, val in zip(expr.keys, expr.values):
                    if key is not None:
                        pk, key2 = lift_expr(key, helper_stack)
                        pre.extend(pk)
                    else:
                        key2 = None
                    pv, val2 = lift_expr(val, helper_stack)
                    pre.extend(pv)
                    keys.append(key2)
                    vals.append(val2)
                return pre, ast.copy_location(ast.Dict(keys, vals), expr)

            # Constants, Names and source forms without helper-bearing eager
            # children are safe to leave for the ordinary Cells/intrinsic rewriter.
            return [], expr

        def lower_helper_block(
            stmts: list[ast.stmt], env: dict[str, ast.AST], result_name: str,
            helper_stack: tuple[str, ...],
        ) -> list[ast.stmt]:
            if not stmts:
                raise FrontendError("runtime scalar helper has a path without a return value")
            st = copy.deepcopy(stmts[0])
            rest = list(stmts[1:])
            if isinstance(st, ast.Expr) and isinstance(st.value, ast.Constant) and isinstance(st.value.value, str):
                return lower_helper_block(rest, dict(env), result_name, helper_stack)
            if isinstance(st, ast.Pass):
                return lower_helper_block(rest, dict(env), result_name, helper_stack)
            if isinstance(st, ast.Assign) and len(st.targets) == 1 and isinstance(st.targets[0], ast.Name):
                rhs = substitute_local(st.value, env)
                pre, rhs = lift_expr(rhs, helper_stack)
                local_name = fresh(f"local_{st.targets[0].id}")
                assign = ast.copy_location(
                    ast.Assign([ast.Name(local_name, ast.Store())], rhs), st
                )
                # Helper locals are SSA-like (every lowering path gets a fresh
                # name).  Keep their defining expressions separately so the graph
                # call rewriter can recover a coordinate expression such as ``t``
                # from ``m = t`` without substituting arithmetic locals everywhere.
                coordinate_aliases[local_name] = copy.deepcopy(rhs)
                next_env = dict(env)
                next_env[st.targets[0].id] = ast.Name(local_name, ast.Load())
                return pre + [assign] + lower_helper_block(rest, next_env, result_name, helper_stack)
            if isinstance(st, ast.AnnAssign) and isinstance(st.target, ast.Name) and st.value is not None:
                rhs = substitute_local(st.value, env)
                pre, rhs = lift_expr(rhs, helper_stack)
                local_name = fresh(f"local_{st.target.id}")
                assign = ast.copy_location(
                    ast.Assign([ast.Name(local_name, ast.Store())], rhs), st
                )
                coordinate_aliases[local_name] = copy.deepcopy(rhs)
                next_env = dict(env)
                next_env[st.target.id] = ast.Name(local_name, ast.Load())
                return pre + [assign] + lower_helper_block(rest, next_env, result_name, helper_stack)
            if isinstance(st, ast.Return):
                if st.value is None:
                    raise FrontendError("runtime scalar helper has a bare return")
                value = substitute_local(st.value, env)
                pre, value = lift_expr(value, helper_stack)
                out = ast.copy_location(
                    ast.Assign([ast.Name(result_name, ast.Store())], value), st
                )
                return pre + [out]
            if isinstance(st, ast.Raise):
                # Preserve terminal helper guards until the established canonical
                # guard-normalization pass.  Local substitutions are applied here
                # so a helper such as ``msg = \"bad\"; raise ValueError(msg)`` can
                # still become the supported literal guard form downstream.
                #
                # Deliberately do not append ``rest``: raise is terminal control
                # flow.  Exception type/message validation and guard-code ownership
                # remain exclusively in normalize_formula_guards().
                exc = None if st.exc is None else substitute_local(st.exc, env)
                cause = None if st.cause is None else substitute_local(st.cause, env)
                return [
                    ast.copy_location(
                        ast.Raise(exc=copy.deepcopy(exc), cause=copy.deepcopy(cause)),
                        st,
                    )
                ]
            if isinstance(st, ast.If):
                test = substitute_local(st.test, env)
                try:
                    constant_test = ast.literal_eval(test)
                except Exception:
                    constant_test = None
                    is_constant = False
                else:
                    is_constant = True
                if is_constant:
                    branch = list(st.body if bool(constant_test) else st.orelse)
                    return lower_helper_block(branch + rest, dict(env), result_name, helper_stack)
                pre, test = lift_expr(test, helper_stack)
                body = lower_helper_block(list(st.body) + rest, dict(env), result_name, helper_stack)
                other = lower_helper_block(list(st.orelse) + rest, dict(env), result_name, helper_stack)
                cond = ast.copy_location(ast.If(test=test, body=body, orelse=other), st)
                return pre + [cond]
            raise FrontendError(
                f"runtime scalar helper statement {type(st).__name__} is outside the pure statement inlining subset"
            )

        def transform_block(stmts: list[ast.stmt]) -> list[ast.stmt]:
            out: list[ast.stmt] = []
            for st in stmts:
                st = copy.deepcopy(st)
                if isinstance(st, ast.Assign):
                    pre, value = lift_expr(st.value, ())
                    st.value = value
                    out.extend(pre)
                    out.append(st)
                elif isinstance(st, ast.AnnAssign) and st.value is not None:
                    pre, value = lift_expr(st.value, ())
                    st.value = value
                    out.extend(pre)
                    out.append(st)
                elif isinstance(st, ast.Return) and st.value is not None:
                    pre, value = lift_expr(st.value, ())
                    st.value = value
                    out.extend(pre)
                    out.append(st)
                elif isinstance(st, ast.If):
                    pre, test = lift_expr(st.test, ())
                    st.test = test
                    st.body = transform_block(list(st.body))
                    st.orelse = transform_block(list(st.orelse))
                    out.extend(pre)
                    out.append(st)
                else:
                    out.append(st)
            return out

        out = copy.deepcopy(fn)
        out.body = transform_block(list(out.body))
        return ast.fix_missing_locations(out), coordinate_aliases

    def _request_source_backed_scheduled_variant(
        self,
        name: str,
        *,
        params: list[str],
        assigned: dict[str, ast.AST],
        observed_time_pos: int | None = None,
    ) -> tuple[str, ast.AST | None] | None:
        """Create one demanded coordinate variant from source, never from values.

        This is deliberately *not* helper inlining.  The returned variant remains a
        normal scheduled graph operation and may participate in lagged recursion.
        The first subset accepts exactly one primary-coordinate argument and only
        literal/full-domain-static auxiliary arguments.  Source lowering, graph
        cycle checks, history/ring proofs and backend safety remain authoritative
        downstream.
        """
        if (
            name not in self.base_funcs
            or name not in self.compiled_source_names
            or name in self.fallback_cells
            or name in self.vector_elements
            or (self.model_point_row is not None and name == self.model_point_row.cell_name)
        ):
            return None
        fn = self.base_funcs[name]
        if (
            fn.args.posonlyargs or fn.args.kwonlyargs or fn.args.vararg is not None
            or fn.args.kwarg is not None or len(fn.args.args) != len(params)
        ):
            return None
        # Side-effectful Python control flow is not admitted merely because source
        # exists.  Ordinary scalar If/Return/Assign and guard raises continue to be
        # validated later by the normal formula safety pass.
        forbidden = (
            ast.Global, ast.Nonlocal, ast.Delete, ast.Yield, ast.YieldFrom, ast.Await,
            ast.With, ast.AsyncWith, ast.Try, ast.AsyncFor, ast.AsyncFunctionDef,
            ast.ClassDef, ast.Import, ast.ImportFrom,
        )
        if any(isinstance(node, forbidden) for node in ast.walk(fn)):
            return None

        if observed_time_pos is not None:
            time_pos = int(observed_time_pos)
            if not (0 <= time_pos < len(params)):
                return None
        else:
            dynamic_positions: list[int] = []
            for pos, param in enumerate(params):
                ok, _value = self._proven_static_helper_argument(assigned[param])
                if not ok:
                    dynamic_positions.append(pos)
            if len(dynamic_positions) != 1:
                return None
            time_pos = dynamic_positions[0]

        time_param = params[time_pos]
        time_expr = copy.deepcopy(assigned[time_param])
        # First proof subset: the demanded coordinate must be expressed directly
        # from the caller's primary ``t``.  More elaborate coordinate-helper
        # algebra belongs to the existing coordinate-relation proof layer rather
        # than being guessed here.
        if not any(
            isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load) and node.id == "t"
            for node in ast.walk(time_expr)
        ):
            return None

        aux_values: list[Any] = []
        for pos, param in enumerate(params):
            if pos == time_pos:
                continue
            ok, value = self._proven_static_helper_argument(assigned[param])
            if not ok:
                return None
            if isinstance(value, np.generic):
                value = value.item()
            if not isinstance(value, (str, bool, int, float)):
                return None
            aux_values.append(value)
        aux = tuple(aux_values)
        token = (name, aux)
        existing = self._source_backed_scheduled_uid_by_key.get(token)
        if existing is not None:
            return existing, time_expr
        observed_uid = self.variants_by_cell_aux.get(token)
        if observed_uid is not None:
            return observed_uid, time_expr

        try:
            cell = self.space.cells[name]
            source = cell.formula.source
            fullname = getattr(cell, "fullname", None) or name
        except Exception:
            return None
        schema = CellSchema(
            fullname=str(fullname), name=name, parameters=tuple(params), source=str(source)
        )
        key = VariantKey(schema.uid, time_pos, aux)
        # The first scheduled-source subset is numeric state.  Dtype is intentionally
        # conservative: bool/int source-backed state should get an explicit source
        # dtype proof in a later extension rather than relying on value sampling.
        tr = VariantTrace(key=key, schema=schema, dtype="float64")
        uid = tr.uid
        if uid in self.variant_trace_by_uid:
            return uid, time_expr
        self.schema_by_name.setdefault(name, schema)
        self.variant_trace_by_uid[uid] = tr
        self.variants_by_cell_aux[token] = uid
        self._source_backed_scheduled_uid_by_key[token] = uid
        if self.primary_coordinate_domain is not None:
            self.coordinate_domains[uid] = self.primary_coordinate_domain
        fact = SourceBackedScheduledFact(
            source_name=name,
            synthetic_uid=uid,
            parameters=tuple(params),
            time_param=time_param,
            aux_values=aux,
            dtype="float64",
            observed=False,
        )
        self._used_source_backed_scheduled_facts[uid] = fact
        return uid, time_expr

    def _variant_for_call(self, name: str, call: ast.Call, caller_mapping: dict[str, ast.AST]) -> tuple[str, ast.AST | None]:
        if name not in self.base_funcs:
            raise FrontendError(f"unknown Cells call {name}")
        base=self.base_funcs[name]
        params=[a.arg for a in base.args.args]
        defaults={}
        if base.args.defaults:
            for p,d in zip(params[-len(base.args.defaults):],base.args.defaults): defaults[p]=d
        assigned: dict[str,ast.AST]={}
        for p,a in zip(params,call.args): assigned[p]=a
        for kw in call.keywords:
            if kw.arg is None:
                raise FrontendError("**kwargs Cells calls are not natively specialized")
            if kw.arg in assigned:
                raise FrontendError(f"duplicate argument {kw.arg!r} in call to {name}")
            assigned[kw.arg]=kw.value
        for p in params:
            if p not in assigned:
                if p in defaults: assigned[p]=defaults[p]
                else: raise FrontendError(f"missing argument {p!r} in call to {name}")
        assigned={p:_Substitute(caller_mapping).visit(copy.deepcopy(v)) for p,v in assigned.items()}

        schema=self.schema_by_name.get(name)
        if schema is None:
            # Acyclic source-backed helpers retain the upstream inlining path.  A
            # recursive/uninlineable demanded Cell may instead become a scheduled
            # source-backed coordinate variant if it satisfies the narrow proof.
            if self._source_backed_unobserved_helper_ok(name):
                raise FrontendError(f"Cells {name} was not observed in the representative trace")
            scheduled = self._request_source_backed_scheduled_variant(
                name, params=params, assigned=assigned
            )
            if scheduled is not None:
                return scheduled
            raise FrontendError(f"Cells {name} was not observed in the representative trace")

        # Schema time position comes from trace, never from parameter spelling.
        time_pos=None
        aux=()
        candidates=[tr for tr in self.variant_trace_by_uid.values() if tr.schema.name==name and tr.key.time_pos is not None]
        if candidates:
            positions={tr.key.time_pos for tr in candidates}
            if len(positions)!=1: raise FrontendError(f"ambiguous time parameter for {name}")
            time_pos=next(iter(positions))
            auxvals=[]
            for j,p in enumerate(params):
                if j==time_pos: continue
                auxvals.append(_literal(assigned[p]))
            aux=tuple(auxvals)
            time_expr=assigned[params[time_pos]]
        else:
            # Non-time parameters are specialized from representative literal calls.
            aux=tuple(_literal(assigned[p]) for p in params)
            time_expr=None
        uid=self.variants_by_cell_aux.get((name,aux))
        if uid is None:
            if not self._source_backed_unobserved_helper_ok(name):
                scheduled = self._request_source_backed_scheduled_variant(
                    name, params=params, assigned=assigned, observed_time_pos=time_pos
                )
                if scheduled is not None:
                    return scheduled
            raise FrontendError(f"call variant {name}{aux!r} was not observed in sample trace; fallback required")
        return uid,time_expr

    def _reference_metadata_scalar_ok(self, name: str) -> bool:
        """Admit a narrow finite loop over immutable reference metadata.

        This is not runtime ``For`` lowering.  The source Cell must be zero-arg,
        point-independent, non-recursive, and every loop must iterate directly over
        ``<DataFrame-or-Series-reference>.index``.  Assignments are local names only;
        calls into other model Cells or effectful Python statements are rejected.
        """
        base=self.base_funcs.get(name)
        if base is None:
            return False
        if base.args.posonlyargs or base.args.args or base.args.kwonlyargs or base.args.vararg or base.args.kwarg:
            return False
        loops=[node for node in ast.walk(base) if isinstance(node,ast.For)]
        if not loops:
            return False
        for loop in loops:
            if not (
                isinstance(loop.target,ast.Name)
                and isinstance(loop.iter,ast.Attribute) and loop.iter.attr == "index"
                and isinstance(loop.iter.value,ast.Name)
                and isinstance(self.refs.get(loop.iter.value.id),(pd.DataFrame,pd.Series))
            ):
                return False
        forbidden=(
            ast.AsyncFor,ast.While,ast.With,ast.AsyncWith,ast.Try,ast.Raise,ast.Delete,
            ast.AugAssign,ast.NamedExpr,ast.Yield,ast.YieldFrom,ast.Await,ast.Global,ast.Nonlocal,
        )
        if any(isinstance(node,forbidden) for node in ast.walk(base)):
            return False
        for node in ast.walk(base):
            if isinstance(node,(ast.Assign,ast.AnnAssign)):
                targets=node.targets if isinstance(node,ast.Assign) else [node.target]
                if any(not isinstance(target,ast.Name) for target in targets):
                    return False
            if isinstance(node,ast.Call) and isinstance(node.func,ast.Name):
                if node.func.id in self.base_funcs or node.func.id in self.fallback_input_by_name:
                    return False
                if node.func.id not in {
                    "abs","all","any","bool","float","int","len","max","min","range","round","sum"
                }:
                    return False
            if isinstance(node,ast.Name) and isinstance(node.ctx,ast.Load):
                if node.id in self.space_params:
                    return False
                if self.model_point_row is not None and node.id == self.model_point_row.cell_name:
                    return False
        return not self._source_reaches_recursive_cycle(name)

    def _materialize_static_value_operators(
        self, uid: str, fn: ast.FunctionDef
    ) -> ast.FunctionDef:
        """Materialize safe immutable static index/slice/cast expressions.

        This pass is intentionally narrower than generic constant folding.  It
        targets expressions whose non-numeric/indexing shape would otherwise leak
        into numeric backends, and admits them only when ``_proven_static_expr``
        can evaluate the exact source expression from complete-run-domain facts.
        """
        frontend = self
        def current_static_facts() -> dict[str, StaticScalarFact]:
            return {
                fact.source_name: fact
                for fact in frontend._used_static_facts.values()
            }

        def dependencies(node: ast.AST) -> tuple[tuple[str, Any], ...]:
            facts = current_static_facts()
            names = sorted({
                child.func.id
                for child in ast.walk(node)
                if isinstance(child, ast.Call) and isinstance(child.func, ast.Name)
                and child.func.id in facts
            })
            return tuple((name, facts[name].value) for name in names)

        def dtype_of(value: Any) -> str:
            if isinstance(value, bool):
                return "bool"
            if isinstance(value, int):
                return "int64"
            if isinstance(value, float):
                return "float64"
            if isinstance(value, str):
                return "string"
            return type(value).__name__

        class Materialize(ast.NodeTransformer):
            def _replace(self, node: ast.AST):
                ok, value = frontend._proven_static_expr(node)
                if not ok or not isinstance(value, (str, bool, int, float)):
                    return None
                deps = dependencies(node)
                if not deps:
                    return None
                facts = current_static_facts()
                frontend._normalized_operators[uid] = NormalizedOperator(
                    uid=uid,
                    kind="static_value",
                    result_dtype=dtype_of(value),
                    result_shape="scalar",
                    static_inputs=deps,
                    provenance=tuple(
                        f"full_run_static:{name}:{facts[name].proof_domain_size}"
                        for name, _ in deps
                    ),
                    state_semantic="state_free",
                    python_supported=True,
                    cython_supported=True,
                )
                return ast.copy_location(ast.Constant(value=value), node)

            def visit_Call(self, node: ast.Call):
                # Casts around a proven static index/slice are materialized as one
                # typed operator, avoiding string/object syntax in numeric IR.
                if (
                    isinstance(node.func, ast.Name)
                    and node.func.id in {"bool", "int", "float", "str"}
                    and any(isinstance(child, ast.Subscript) for child in ast.walk(node))
                ):
                    replacement = self._replace(node)
                    if replacement is not None:
                        return replacement
                return self.generic_visit(node)

            def visit_Subscript(self, node: ast.Subscript):
                replacement = self._replace(node)
                if replacement is not None:
                    return replacement
                return self.generic_visit(node)

        out = Materialize().visit(copy.deepcopy(fn))
        if not isinstance(out, ast.FunctionDef):
            raise FrontendError(f"static operator materialization removed formula {fn.name}")
        return ast.fix_missing_locations(out)

    def _specialize_function(
        self, uid: str, *, fixed_time: int | None = None, synthetic_uid: str | None = None
    ) -> ast.FunctionDef | None:
        tr=self.variant_trace_by_uid[uid]
        name=tr.schema.name
        if name not in self.base_funcs:
            return None
        fn=copy.deepcopy(self.base_funcs[name])
        # Finite reference-only metadata loops are preparation inputs, not runtime
        # control flow.  Lower them before statement helper processing so an
        # otherwise unsupported ``For`` never enters canonical execution.
        if tr.key.time_pos is None and not tr.key.aux_values and self._reference_metadata_scalar_ok(name):
            key=self.registry.reference_metadata_scalar(name)
            spec=self.registry.specs[key]
            self._normalized_operators[uid]=NormalizedOperator(
                uid=uid,kind="reference_metadata_scalar",
                result_dtype=spec.dtype,result_shape="scalar",
                static_inputs=(("input_key",key),("source_cell",name)),
                provenance=(
                    "finite_reference_index_loop","point_independent_run_domain",
                    "numeric_global_input",
                ),
                state_semantic="state_free",python_supported=True,cython_supported=True,
            )
            return ast.fix_missing_locations(ast.FunctionDef(
                name=synthetic_uid or uid,
                args=ast.arguments(posonlyargs=[],args=[],vararg=None,kwonlyargs=[],kw_defaults=[],kwarg=None,defaults=[]),
                body=[ast.Return(ast.Call(ast.Name("global_input",ast.Load()),[ast.Constant(key)],[]))],
                decorator_list=[],returns=None,type_comment=None,
            ))
        source_params=[a.arg for a in fn.args.args]
        coord_env={}
        if tr.key.time_pos is not None:
            source_param=source_params[tr.key.time_pos]
            if fixed_time is not None:
                coord_env[source_param]=_IntDomain(int(fixed_time),int(fixed_time))
            elif uid in self.coordinate_domains:
                coord_env[source_param]=self.coordinate_domains[uid]
        fn=self._specialize_static_facts_and_domains(fn,coordinate_env=coord_env)
        fn=self._materialize_static_value_operators(uid, fn)
        fn=self._prune_to_realized_path(uid, fn)
        params=[a.arg for a in fn.args.args]
        tpos=tr.key.time_pos
        mapping={}
        aux_iter=iter(tr.key.aux_values)
        for j,p in enumerate(params):
            if tpos is not None and j==tpos:
                mapping[p] = ast.Constant(int(fixed_time)) if fixed_time is not None else ast.Name("t",ast.Load())
            else:
                mapping[p]=ast.Constant(next(aux_iter))
        fn=_Substitute(mapping).visit(fn)
        if fixed_time is not None:
            fn=_CoordinateConstantFolder().visit(fn)
        fn=_ConservativeFolder().visit(fn)
        if isinstance(fn,list):
            raise FrontendError(f"constant folding unexpectedly replaced function {name}")
        fn=ast.fix_missing_locations(fn)
        fn=_prune_source_unreachable_tails(fn)
        if fixed_time is not None:
            fn=self._fold_fixed_local_constants(fn)
            fn=self._specialize_static_facts_and_domains(fn)
            fn=self._fold_fixed_local_constants(fn)
            fn=_prune_source_unreachable_tails(fn)
        fn.name=synthetic_uid or uid
        fn.args=ast.arguments(
            posonlyargs=[],
            args=[ast.arg("t")] if (tpos is not None and fixed_time is None) else [],
            vararg=None,kwonlyargs=[],kw_defaults=[],kwarg=None,defaults=[]
        )
        fn=_strip_docstring(fn)
        # Preserve pure-helper locals before the legacy expression inliner gets a
        # chance to substitute them repeatedly.  Ordinary scheduled Cells remain
        # source-name calls here and are canonicalized by Calls below.
        fn, helper_coordinate_aliases = self._inline_runtime_scalar_helpers_as_statements(fn)
        bound_names=self._function_bound_names(fn)

        frontend=self
        class Calls(ast.NodeTransformer):
            def __init__(self):
                super().__init__()
                self.helper_expansion_nodes = 0

            def visit_Call(self,n):
                # Do not generic_visit first: Cells argument expressions must be rewritten under caller mapping exactly once.
                if isinstance(n.func,ast.Name) and n.func.id in frontend.fallback_input_by_name:
                    if n.args or n.keywords:
                        raise FrontendError(f"regional fallback Cell {n.func.id!r} must be called without arguments")
                    key=frontend.fallback_input_by_name[n.func.id]
                    return ast.copy_location(
                        ast.Call(ast.Name("point_input",ast.Load()),[ast.Constant(key)],[]), n
                    )
                if isinstance(n.func,ast.Name) and (n.func.id in frontend.vector_elements or (frontend.model_point_row and n.func.id == frontend.model_point_row.cell_name)):
                    return self.generic_visit(n)
                if isinstance(n.func,ast.Name) and n.func.id in frontend.base_funcs:
                    if n.func.id in frontend._runtime_scalar_helper_inline_stack:
                        chain = " -> ".join(frontend._runtime_scalar_helper_inline_stack + [n.func.id])
                        raise FrontendError(f"runtime scalar helper recursion detected: {chain}")
                    try:
                        cuid,texpr=frontend._variant_for_call(n.func.id,n,{})
                    except FrontendError as exc:
                        source_backed = (
                            str(exc).startswith(f"Cells {n.func.id} was not observed")
                            and frontend._source_backed_unobserved_helper_ok(n.func.id)
                        )
                        if str(exc).startswith("non-time specialization argument is not a literal:") or source_backed:
                            frontend._runtime_scalar_helper_inline_stack.append(n.func.id)
                            try:
                                inlined = frontend._inline_runtime_scalar_helper_call(n.func.id, n)
                                if inlined is not None:
                                    self.helper_expansion_nodes += sum(1 for _ in ast.walk(inlined))
                                    if self.helper_expansion_nodes > frontend._runtime_scalar_helper_expansion_limit:
                                        raise FrontendError(
                                            "runtime scalar helper expansion budget exceeded "
                                            f"({self.helper_expansion_nodes} > {frontend._runtime_scalar_helper_expansion_limit}) "
                                            f"while inlining {n.func.id}"
                                        )
                                    return self.visit(inlined)
                            finally:
                                popped = frontend._runtime_scalar_helper_inline_stack.pop()
                                assert popped == n.func.id
                        raise
                    if texpr is None:
                        return ast.copy_location(ast.Call(ast.Name(cuid,ast.Load()),[],[]),n)
                    # Statement-level helper lowering preserves arithmetic locals,
                    # but graph scheduling still needs the defining expression of a
                    # local used as a Cell coordinate.  Fresh helper locals are
                    # single-assignment, so substituting only here is hygienic and
                    # does not reintroduce expression duplication in the formula.
                    for _ in range(len(helper_coordinate_aliases) + 1):
                        before = ast.dump(texpr, include_attributes=False)
                        texpr = _Substitute(helper_coordinate_aliases).visit(copy.deepcopy(texpr))
                        texpr = ast.fix_missing_locations(texpr)
                        if ast.dump(texpr, include_attributes=False) == before:
                            break
                    texpr = frontend._normalize_coordinate_expression(
                        texpr, bound_names=bound_names
                    )
                    if (
                        isinstance(texpr, ast.Constant)
                        and isinstance(texpr.value, int)
                        and not isinstance(texpr.value, bool)
                    ):
                        # A constant call into a future-recursive coordinate family
                        # must remain parameterized.  Expanding it into a synthetic
                        # fixed scalar would recursively request t, t+1, t+2, ...
                        # and therefore hides the recurrence from the canonical
                        # scheduler.  Ordinary acyclic/fixed-coordinate families
                        # keep the historical specialization path.
                        if frontend._source_has_future_coordinate_dependency(cuid):
                            return ast.copy_location(
                                ast.Call(
                                    ast.Name(cuid, ast.Load()),
                                    [ast.Constant(int(texpr.value))],
                                    [],
                                ),
                                n,
                            )
                        fixed_uid = frontend._request_fixed_coordinate(cuid, int(texpr.value))
                        return ast.copy_location(ast.Call(ast.Name(fixed_uid,ast.Load()),[],[]),n)
                    return ast.copy_location(
                        ast.Call(ast.Name(cuid,ast.Load()),[self.visit(texpr)],[]), n
                    )
                return self.generic_visit(n)
            def visit_Subscript(self,n):
                # modelx Cells subscript call syntax: f[t] / f[t, aux]
                if isinstance(n.value,ast.Name) and n.value.id in frontend.base_funcs:
                    sl=n.slice
                    args=list(sl.elts) if isinstance(sl,ast.Tuple) else [sl]
                    call=ast.Call(ast.Name(n.value.id,ast.Load()),args,[])
                    return self.visit_Call(call)
                return self.generic_visit(n)
        fn=Calls().visit(fn)
        fn=ast.fix_missing_locations(fn)
        fn=self._inline_fixed_time_calls(fn)
        fn=self._inline_vector_subscripts(fn)
        return ast.fix_missing_locations(fn)

    def _inline_fixed_time_calls(self, fn: ast.FunctionDef) -> ast.FunctionDef:
        frontend=self
        class Inliner(ast.NodeTransformer):
            depth=0
            def visit_Call(self,n):
                n=self.generic_visit(n)
                if self.depth>10 or not (isinstance(n.func,ast.Name) and n.func.id in frontend.variant_trace_by_uid and len(n.args)==1):
                    return n
                arg=n.args[0]
                if not isinstance(arg,ast.Constant) or not isinstance(arg.value,int):
                    return n
                callee=frontend._specialize_function(n.func.id)
                if callee is None or not callee.args.args:
                    return n
                callee=_Substitute({"t":ast.Constant(int(arg.value))}).visit(callee)
                callee=_ConservativeFolder().visit(callee)
                if isinstance(callee,list): return n
                callee=_strip_docstring(callee)
                body=callee.body
                if len(body)==1 and isinstance(body[0],ast.Return):
                    self.depth+=1
                    val=self.visit(copy.deepcopy(body[0].value))
                    self.depth-=1
                    return ast.copy_location(val,n)
                return n
        return ast.fix_missing_locations(Inliner().visit(fn))

    def _normalize_scalar_intrinsics(self, fn: ast.FunctionDef) -> ast.FunctionDef:
        """Lower a tiny backend-neutral scalar-intrinsic subset.

        pandas/numpy missing-value spellings are source conveniences.  Only a
        numeric scalar predicate survives as ``__is_missing__(x)``; emitters map
        that semantic operation to their native floating-point implementation.
        """
        frontend = self

        class Normalize(ast.NodeTransformer):
            def visit_Attribute(self, node: ast.Attribute):
                node = self.generic_visit(node)
                if not isinstance(node.value, ast.Name) or node.attr != "inf":
                    return node
                obj = frontend.refs.get(node.value.id)
                module_name = getattr(obj, "__name__", None)
                if module_name in ("math", "numpy"):
                    # Keep infinity as a backend-neutral numeric AST constant.
                    # Emitters choose their native spelling (math.inf / INFINITY).
                    return ast.copy_location(ast.Constant(value=float("inf")), node)
                return node

            def visit_Call(self, node: ast.Call):
                node = self.generic_visit(node)
                if not (
                    isinstance(node.func, ast.Attribute)
                    and isinstance(node.func.value, ast.Name)
                    and len(node.args) == 1 and not node.keywords
                ):
                    return node
                receiver = node.func.value.id
                obj = frontend.refs.get(receiver)
                module_name = getattr(obj, "__name__", None)
                if module_name == "pandas" and node.func.attr in {"isna", "isnull"}:
                    return ast.copy_location(
                        ast.Call(ast.Name("__is_missing__", ast.Load()), [node.args[0]], []), node
                    )
                if module_name == "numpy" and node.func.attr == "isnan":
                    return ast.copy_location(
                        ast.Call(ast.Name("__is_missing__", ast.Load()), [node.args[0]], []), node
                    )
                if module_name in ("math", "numpy") and node.func.attr == "isinf":
                    return ast.copy_location(
                        ast.Call(ast.Name("__is_inf__", ast.Load()), [node.args[0]], []), node
                    )
                if module_name == "math" and node.func.attr == "erf":
                    return ast.copy_location(
                        ast.Call(ast.Name("__erf__", ast.Load()), [node.args[0]], []), node
                    )
                return node

        out = Normalize().visit(copy.deepcopy(fn))
        assert isinstance(out, ast.FunctionDef)
        return ast.fix_missing_locations(out)

    def _normalize_simple_local_syntax(self, fn: ast.FunctionDef) -> ast.FunctionDef:
        """Lower small Python-local conveniences to the verified scalar subset.

        This pass changes syntax, not model semantics:
        * fixed-arity tuple/list unpacking uses temporaries so all RHS expressions
          are evaluated left-to-right before any target is assigned;
        * numeric local AugAssign becomes an ordinary assignment;
        * a local list used only as a min/max accumulator via ``append`` is
          scalarized to repeated min/max updates.
        """
        existing = self._function_bound_names(fn)
        counter = 0

        def fresh(prefix: str) -> str:
            nonlocal counter
            while True:
                name = f"__mx_{prefix}_{counter}"
                counter += 1
                if name not in existing:
                    existing.add(name)
                    return name

        class Basic(ast.NodeTransformer):
            def visit_Assign(self, node: ast.Assign):
                node = self.generic_visit(node)
                if not (
                    len(node.targets) == 1
                    and isinstance(node.targets[0], (ast.Tuple, ast.List))
                    and isinstance(node.value, (ast.Tuple, ast.List))
                    and len(node.targets[0].elts) == len(node.value.elts)
                    and len(node.targets[0].elts) >= 1
                    and all(isinstance(x, ast.Name) for x in node.targets[0].elts)
                    and all(not isinstance(x, ast.Starred) for x in node.targets[0].elts)
                ):
                    return node
                temps = [fresh("unpack") for _ in node.value.elts]
                out: list[ast.stmt] = []
                for tmp, value in zip(temps, node.value.elts):
                    out.append(ast.copy_location(
                        ast.Assign([ast.Name(tmp, ast.Store())], value), node
                    ))
                for target, tmp in zip(node.targets[0].elts, temps):
                    out.append(ast.copy_location(
                        ast.Assign([ast.Name(target.id, ast.Store())], ast.Name(tmp, ast.Load())), node
                    ))
                return out

            def visit_AugAssign(self, node: ast.AugAssign):
                node = self.generic_visit(node)
                if not isinstance(node.target, ast.Name):
                    return node
                return ast.copy_location(
                    ast.Assign(
                        [ast.Name(node.target.id, ast.Store())],
                        ast.BinOp(ast.Name(node.target.id, ast.Load()), node.op, node.value),
                    ),
                    node,
                )

        out = Basic().visit(copy.deepcopy(fn))
        assert isinstance(out, ast.FunctionDef)
        out = ast.fix_missing_locations(out)

        # Identify list locals whose *only* reads are append operations and one
        # consistent min/max aggregate.  Anything else remains untouched/fail-closed.
        candidates: dict[str, str] = {}
        for st in out.body:
            if not (
                isinstance(st, ast.Assign) and len(st.targets) == 1
                and isinstance(st.targets[0], ast.Name)
                and isinstance(st.value, ast.List) and len(st.value.elts) == 1
            ):
                continue
            name = st.targets[0].id
            total_loads = sum(
                1 for n in ast.walk(out)
                if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load) and n.id == name
            )
            append_loads = 0
            aggregates: list[str] = []
            for n in ast.walk(out):
                if (
                    isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                    and isinstance(n.func.value, ast.Name) and n.func.value.id == name
                    and n.func.attr == "append" and len(n.args) == 1 and not n.keywords
                ):
                    append_loads += 1
                if (
                    isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                    and n.func.id in {"min", "max"} and len(n.args) == 1
                    and isinstance(n.args[0], ast.Name) and n.args[0].id == name
                ):
                    aggregates.append(n.func.id)
            if aggregates and len(set(aggregates)) == 1 and total_loads == append_loads + len(aggregates):
                candidates[name] = aggregates[0]

        if not candidates:
            return out

        class Accumulator(ast.NodeTransformer):
            def visit_Assign(self, node: ast.Assign):
                node = self.generic_visit(node)
                if (
                    len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
                    and node.targets[0].id in candidates
                    and isinstance(node.value, ast.List) and len(node.value.elts) == 1
                ):
                    node.value = node.value.elts[0]
                return node

            def visit_Expr(self, node: ast.Expr):
                node = self.generic_visit(node)
                call = node.value
                if (
                    isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
                    and isinstance(call.func.value, ast.Name)
                    and call.func.value.id in candidates and call.func.attr == "append"
                    and len(call.args) == 1 and not call.keywords
                ):
                    name = call.func.value.id
                    return ast.copy_location(
                        ast.Assign(
                            [ast.Name(name, ast.Store())],
                            ast.Call(
                                ast.Name(candidates[name], ast.Load()),
                                [ast.Name(name, ast.Load()), call.args[0]], [],
                            ),
                        ),
                        node,
                    )
                return node

            def visit_Call(self, node: ast.Call):
                node = self.generic_visit(node)
                if (
                    isinstance(node.func, ast.Name) and node.func.id in {"min", "max"}
                    and len(node.args) == 1 and isinstance(node.args[0], ast.Name)
                    and node.args[0].id in candidates and candidates[node.args[0].id] == node.func.id
                ):
                    return ast.copy_location(ast.Name(node.args[0].id, ast.Load()), node)
                return node

        out = Accumulator().visit(out)
        assert isinstance(out, ast.FunctionDef)
        return ast.fix_missing_locations(out)

    def _normalize_external_tables(
        self, fn: ast.FunctionDef, *, operator_uid: str | None = None
    ) -> ast.FunctionDef:
        """Lower supported external DataFrame semantics before either backend sees them.

        Exact numeric ``.loc`` lookups may combine compile-time-fixed, finite
        categorical and regular numeric runtime selectors.  Multi-dimensional
        runtime keys are normalized to dense or sparse numeric inputs; pandas
        objects and label semantics never survive into the optimized program.
        """
        frontend = self
        registry = self.registry

        @dataclass(frozen=True)
        class TableSource:
            ref_name: str
            cell_name: str
            cell: Any
            sample: pd.DataFrame

        @dataclass(frozen=True)
        class RowSource:
            table: TableSource
            row_expr: ast.AST

        @dataclass(frozen=True)
        class SeriesSource:
            """A numeric 1-D Series proven from a static MultiIndex prefix.

            The object itself is preparation-only.  Consumers are rewritten to the
            existing normalized numeric ``axis1d`` input, so neither pandas nor a
            Python Series reaches optimized Python/Cython.
            """

            table: TableSource
            fixed_levels: tuple[tuple[int, Any], ...]
            dynamic_level: int
            column: Any

        @dataclass(frozen=True)
        class FiniteEnumValue:
            """Numeric code expression plus the exact finite source label domain.

            This is deliberately an upstream/frontend proof object.  The canonical
            executable graph sees only the integer ``code_expr``; string labels are
            retained solely while normalizing source control flow/table dispatch.
            """

            labels: tuple[str, ...]
            code_expr: ast.AST = field(compare=False, repr=False)
            source_name: str | None = None

        @dataclass(frozen=True)
        class FiniteDispatch:
            fixed_levels: tuple[tuple[int, Any], ...]
            enum_level: int
            enum_value: FiniteEnumValue = field(compare=False, repr=False)
            numeric_level: int
            numeric_expr: ast.AST = field(compare=False, repr=False)

        class Normalize(ast.NodeTransformer):
            def __init__(self):
                self.table_aliases: dict[str, TableSource] = {}
                self.row_aliases: dict[str, RowSource] = {}
                self.series_aliases: dict[str, SeriesSource] = {}
                # Direct DataFrame-reference column views, e.g. ``s = table[col]``.
                # These are preparation-only symbolic Series objects.  Supported
                # consumers (index min/max and exact row lookup) are rewritten
                # before the ordinary expression lowerer sees the incomplete
                # one-index DataFrame operation.
                self.direct_dataframe_series_aliases: dict[str, tuple[str, ast.AST]] = {}
                self.finite_enum_aliases: dict[str, FiniteEnumValue] = {}
                self.value_aliases: dict[str, ast.AST] = {}
                self.external_cache: dict[tuple[str, str], TableSource | None] = {}
                self.series_helper_cache: dict[str, SeriesSource | None] = {}
                self.finite_enum_cache: dict[str, FiniteEnumValue | None] = {}
                self.store_counts: dict[str, int] = {}
                self.membership_guarded_rows: list[tuple[str, str]] = []
                self.active_membership_guarded_rows: list[tuple[str, str]] = []
                for child in ast.walk(fn):
                    if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Store):
                        self.store_counts[child.id] = self.store_counts.get(child.id, 0) + 1
                # Preserve a tiny but important source contract: a direct
                # ``if key not in table.index: return default`` makes a following
                # lookup total over enum labels absent from the table.  We record
                # only the local aliases here; table/row identity is checked after
                # aliases have been proven by this same normalizer.
                for index, st in enumerate(fn.body):
                    if not (
                        isinstance(st, ast.If) and not st.orelse and len(st.body) == 1
                        and isinstance(st.body[0], ast.Return) and st.body[0].value is not None
                        and isinstance(st.body[0].value, ast.Constant)
                        and isinstance(st.body[0].value.value, (int, float, np.integer, np.floating))
                        and not isinstance(st.body[0].value.value, (bool, np.bool_))
                        and isinstance(st.test, ast.Compare) and len(st.test.ops) == 1
                        and isinstance(st.test.ops[0], ast.NotIn)
                        and len(st.test.comparators) == 1
                        and isinstance(st.test.left, ast.Name)
                        and isinstance(st.test.comparators[0], ast.Attribute)
                        and st.test.comparators[0].attr == "index"
                        and isinstance(st.test.comparators[0].value, ast.Name)
                    ):
                        continue
                    key_name = st.test.left.id
                    # A membership-return check is a lookup guard only when it
                    # precedes every source ``.loc[key]`` access.  Merely finding a
                    # matching ``if`` somewhere in the function would be a rather
                    # inventive interpretation of Python control flow.
                    unsafe_prior_lookup = any(
                        isinstance(child, ast.Subscript)
                        and isinstance(child.value, ast.Attribute)
                        and child.value.attr == "loc"
                        and any(
                            isinstance(name, ast.Name) and isinstance(name.ctx, ast.Load)
                            and name.id == key_name
                            for name in ast.walk(child.slice)
                        )
                        for prior in fn.body[:index]
                        for child in ast.walk(prior)
                    )
                    if unsafe_prior_lookup:
                        continue
                    self.membership_guarded_rows.append(
                        (key_name, st.test.comparators[0].value.id)
                    )

            @staticmethod
            def _same_expr(left: ast.AST, right: ast.AST) -> bool:
                return ast.dump(left, include_attributes=False) == ast.dump(right, include_attributes=False)

            def _numeric_bounds(
                self, node: ast.AST, *, _stack: tuple[str, ...] = ()
            ) -> tuple[float | None, float | None]:
                """Return sound numeric lower/upper bounds for a tiny pure subset.

                The analysis exists to prove lookup-domain preconditions, not to fold
                arbitrary formulas.  Unknown pieces remain unbounded.  Calls into source
                Cells are followed only when their body is a single pure ``return``
                expression; recursion and statementful helpers fail closed.  This lets
                formulas such as ``policy_year(t) = max(0, t // 12) + 1`` prove a
                lower bound of one without learning anything about the concrete value of
                ``t`` or relying on representative-trace coverage.
                """
                node = self._expand_alias(node)
                ok_static, static_value = frontend._proven_static_expr(node)
                if (
                    ok_static
                    and isinstance(static_value, (int, float, np.integer, np.floating))
                    and not isinstance(static_value, (bool, np.bool_))
                    and np.isfinite(float(static_value))
                ):
                    value = float(static_value)
                    return value, value
                if isinstance(node, ast.Name) and node.id == "t":
                    dom = (
                        frontend.specialized_coordinate_domains.get(fn.name)
                        or frontend.coordinate_domains.get(fn.name)
                        or frontend.primary_coordinate_domain
                    )
                    if dom is not None:
                        return float(dom.lo), float(dom.hi)
                    lo, hi = frontend.primary_coordinate_bounds
                    return (None if lo is None else float(lo), None if hi is None else float(hi))
                if (
                    isinstance(node, ast.Subscript)
                    and frontend.model_point_row is not None
                    and isinstance(node.value, ast.Call)
                    and isinstance(node.value.func, ast.Name)
                    and node.value.func.id == frontend.model_point_row.cell_name
                    and not node.value.args and not node.value.keywords
                    and isinstance(node.slice, ast.Constant)
                    and isinstance(node.slice.value, str)
                ):
                    return frontend._proven_numeric_point_field_bounds(str(node.slice.value))
                if isinstance(node, ast.Constant):
                    value = node.value
                    if isinstance(value, (int, float, np.integer, np.floating)) and not isinstance(
                        value, (bool, np.bool_)
                    ):
                        value = float(value)
                        if np.isfinite(value):
                            return value, value
                    return None, None
                if isinstance(node, ast.UnaryOp):
                    lo, hi = self._numeric_bounds(node.operand, _stack=_stack)
                    if isinstance(node.op, ast.UAdd):
                        return lo, hi
                    if isinstance(node.op, ast.USub):
                        return (None if hi is None else -hi, None if lo is None else -lo)
                    return None, None
                if isinstance(node, ast.BinOp):
                    llo, lhi = self._numeric_bounds(node.left, _stack=_stack)
                    rlo, rhi = self._numeric_bounds(node.right, _stack=_stack)
                    if isinstance(node.op, ast.Add):
                        return (
                            None if llo is None or rlo is None else llo + rlo,
                            None if lhi is None or rhi is None else lhi + rhi,
                        )
                    if isinstance(node.op, ast.Sub):
                        return (
                            None if llo is None or rhi is None else llo - rhi,
                            None if lhi is None or rlo is None else lhi - rlo,
                        )
                    if isinstance(node.op, ast.Mult) and None not in (llo, lhi, rlo, rhi):
                        vals = (llo * rlo, llo * rhi, lhi * rlo, lhi * rhi)
                        return min(vals), max(vals)
                    if isinstance(node.op, ast.FloorDiv) and rlo == rhi and rlo is not None and rlo > 0:
                        return (
                            None if llo is None else float(np.floor(llo / rlo)),
                            None if lhi is None else float(np.floor(lhi / rlo)),
                        )
                    return None, None
                if isinstance(node, ast.IfExp):
                    blo, bhi = self._numeric_bounds(node.body, _stack=_stack)
                    olo, ohi = self._numeric_bounds(node.orelse, _stack=_stack)
                    return (
                        None if blo is None or olo is None else min(blo, olo),
                        None if bhi is None or ohi is None else max(bhi, ohi),
                    )
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    name = node.func.id
                    if name in {"int", "float"} and len(node.args) == 1 and not node.keywords:
                        return self._numeric_bounds(node.args[0], _stack=_stack)
                    if name in {"max", "min"} and node.args and not node.keywords:
                        bounds = [self._numeric_bounds(arg, _stack=_stack) for arg in node.args]
                        los = [lo for lo, _ in bounds if lo is not None]
                        his = [hi for _, hi in bounds if hi is not None]
                        if name == "max":
                            # max(x, c) is >= c even when x is otherwise unbounded.
                            lo = max(los) if los else None
                            hi = max(his) if len(his) == len(bounds) else None
                        else:
                            lo = min(los) if len(los) == len(bounds) else None
                            # min(x, c) is <= c even when x is otherwise unbounded.
                            hi = min(his) if his else None
                        return lo, hi
                    if name == "abs" and len(node.args) == 1 and not node.keywords:
                        lo, hi = self._numeric_bounds(node.args[0], _stack=_stack)
                        upper = None
                        if lo is not None and hi is not None:
                            upper = max(abs(lo), abs(hi))
                        return 0.0, upper
                    source_name = None
                    assigned: dict[str, ast.AST] | None = None
                    stack_token = name
                    if name in frontend.variant_trace_by_uid and name not in _stack:
                        tr = frontend.variant_trace_by_uid[name]
                        source_name = tr.schema.name
                        base = _strip_docstring(copy.deepcopy(frontend.base_funcs.get(source_name)))
                        params = [a.arg for a in base.args.args] if isinstance(base, ast.FunctionDef) else []
                        assigned = {}
                        if tr.key.time_pos is None:
                            if node.args or node.keywords:
                                assigned = None
                            else:
                                aux_iter = iter(tr.key.aux_values)
                                for param in params:
                                    assigned[param] = ast.Constant(next(aux_iter))
                        else:
                            if len(node.args) != 1 or node.keywords:
                                assigned = None
                            else:
                                aux_iter = iter(tr.key.aux_values)
                                for pos, param in enumerate(params):
                                    if pos == tr.key.time_pos:
                                        assigned[param] = copy.deepcopy(node.args[0])
                                    else:
                                        assigned[param] = ast.Constant(next(aux_iter))
                    elif name in frontend.base_funcs and name not in _stack:
                        source_name = name
                        base = _strip_docstring(copy.deepcopy(frontend.base_funcs[name]))
                        params = [a.arg for a in base.args.args]
                        defaults: dict[str, ast.AST] = {}
                        if base.args.defaults:
                            for param, default in zip(params[-len(base.args.defaults):], base.args.defaults):
                                defaults[param] = copy.deepcopy(default)
                        assigned = {}
                        if len(node.args) <= len(params):
                            for param, arg in zip(params, node.args):
                                assigned[param] = copy.deepcopy(arg)
                            for kw in node.keywords:
                                if kw.arg is None or kw.arg not in params or kw.arg in assigned:
                                    assigned = None
                                    break
                                assigned[kw.arg] = copy.deepcopy(kw.value)
                            if assigned is not None:
                                for param in params:
                                    if param not in assigned:
                                        if param not in defaults:
                                            assigned = None
                                            break
                                        assigned[param] = copy.deepcopy(defaults[param])
                        else:
                            assigned = None
                    if source_name is not None and assigned is not None:
                        base = _strip_docstring(copy.deepcopy(frontend.base_funcs[source_name]))
                        if (
                            not base.args.posonlyargs and not base.args.kwonlyargs
                            and base.args.vararg is None and base.args.kwarg is None
                            and len(base.body) == 1 and isinstance(base.body[0], ast.Return)
                            and base.body[0].value is not None
                        ):
                            value = _Substitute(assigned).visit(copy.deepcopy(base.body[0].value))
                            value = _ConservativeFolder().visit(ast.fix_missing_locations(value))
                            if isinstance(value, ast.AST):
                                return self._numeric_bounds(value, _stack=_stack + (stack_token,))
                return None, None

            def _rewrite_interp_lookup_function(self, fn: ast.FunctionDef) -> ast.FunctionDef:
                """Recognize a bounded pivot interpolation idiom as InterpLookup1D.

                This is intentionally a mathematical recognizer, not general pandas
                lowering.  It accepts a static DataFrame prefix slice, a sorted
                numeric pivot axis, nearest-end-segment extrapolation, and either
                linear or multiplicative log-linear interpolation between adjacent
                pivots.  Any structural deviation fails closed.
                """
                work = _strip_docstring(copy.deepcopy(fn))
                body = list(work.body)
                if len(body) != 6:
                    return fn

                # sub = table.loc[static_prefix]
                sub_st = body[0]
                if not (
                    isinstance(sub_st, ast.Assign) and len(sub_st.targets) == 1
                    and isinstance(sub_st.targets[0], ast.Name)
                ):
                    return fn
                sub_name = sub_st.targets[0].id
                row = self._row_proxy(sub_st.value)
                if row is None:
                    return fn
                ok_row, row_key = self._static_value(row.row_expr)
                if not ok_row:
                    return fn

                # ages = sorted(int(a) for a in sub.index)
                ages_st = body[1]
                if not (
                    isinstance(ages_st, ast.Assign) and len(ages_st.targets) == 1
                    and isinstance(ages_st.targets[0], ast.Name)
                    and isinstance(ages_st.value, ast.Call)
                    and isinstance(ages_st.value.func, ast.Name) and ages_st.value.func.id == "sorted"
                    and len(ages_st.value.args) == 1 and not ages_st.value.keywords
                    and isinstance(ages_st.value.args[0], ast.GeneratorExp)
                ):
                    return fn
                ages_name = ages_st.targets[0].id
                gen = ages_st.value.args[0]
                if len(gen.generators) != 1:
                    return fn
                comp = gen.generators[0]
                if not (
                    isinstance(comp.target, ast.Name) and not comp.ifs and not comp.is_async
                    and isinstance(comp.iter, ast.Attribute) and comp.iter.attr == "index"
                    and isinstance(comp.iter.value, ast.Name) and comp.iter.value.id == sub_name
                    and isinstance(gen.elt, ast.Call) and isinstance(gen.elt.func, ast.Name)
                    and gen.elt.func.id in {"int", "float"} and len(gen.elt.args) == 1
                    and not gen.elt.keywords and isinstance(gen.elt.args[0], ast.Name)
                    and gen.elt.args[0].id == comp.target.id
                ):
                    return fn

                bracket = body[2]
                if not (
                    isinstance(bracket, ast.If) and len(bracket.body) == 1
                    and len(bracket.orelse) == 1 and isinstance(bracket.orelse[0], ast.If)
                ):
                    return fn
                outer = bracket
                inner = bracket.orelse[0]

                def axis_sub(expr: ast.AST, index: int) -> bool:
                    if not (
                        isinstance(expr, ast.Subscript) and isinstance(expr.value, ast.Name)
                        and expr.value.id == ages_name
                    ):
                        return False
                    try:
                        return int(ast.literal_eval(expr.slice)) == index
                    except Exception:
                        return False

                if not (
                    isinstance(outer.test, ast.Compare) and len(outer.test.ops) == 1
                    and isinstance(outer.test.ops[0], ast.LtE) and len(outer.test.comparators) == 1
                    and axis_sub(outer.test.comparators[0], 0)
                ):
                    return fn
                query = copy.deepcopy(outer.test.left)
                if not (
                    isinstance(inner.test, ast.Compare) and len(inner.test.ops) == 1
                    and isinstance(inner.test.ops[0], ast.GtE) and len(inner.test.comparators) == 1
                    and self._same_expr(inner.test.left, query) and axis_sub(inner.test.comparators[0], -1)
                    and len(inner.body) == 1 and len(inner.orelse) == 2
                ):
                    return fn

                def pair_assign(st: ast.stmt, left_idx: int, right_idx: int):
                    if not (
                        isinstance(st, ast.Assign) and len(st.targets) == 1
                        and isinstance(st.targets[0], (ast.Tuple, ast.List))
                        and len(st.targets[0].elts) == 2
                        and all(isinstance(x, ast.Name) for x in st.targets[0].elts)
                        and isinstance(st.value, (ast.Tuple, ast.List)) and len(st.value.elts) == 2
                        and axis_sub(st.value.elts[0], left_idx) and axis_sub(st.value.elts[1], right_idx)
                    ):
                        return None
                    return st.targets[0].elts[0].id, st.targets[0].elts[1].id

                first_pair = pair_assign(outer.body[0], 0, 1)
                last_pair = pair_assign(inner.body[0], -2, -1)
                if first_pair is None or last_pair != first_pair:
                    return fn
                lo_name, hi_name = first_pair

                def interior_pick(st: ast.stmt, func_name: str, op_type, target_name: str) -> bool:
                    if not (
                        isinstance(st, ast.Assign) and len(st.targets) == 1
                        and isinstance(st.targets[0], ast.Name) and st.targets[0].id == target_name
                        and isinstance(st.value, ast.Call) and isinstance(st.value.func, ast.Name)
                        and st.value.func.id == func_name and len(st.value.args) == 1 and not st.value.keywords
                        and isinstance(st.value.args[0], ast.GeneratorExp)
                    ):
                        return False
                    g = st.value.args[0]
                    if len(g.generators) != 1:
                        return False
                    c = g.generators[0]
                    if not (
                        isinstance(c.target, ast.Name) and isinstance(c.iter, ast.Name)
                        and c.iter.id == ages_name and len(c.ifs) == 1 and not c.is_async
                        and isinstance(g.elt, ast.Name) and g.elt.id == c.target.id
                    ):
                        return False
                    cond = c.ifs[0]
                    return (
                        isinstance(cond, ast.Compare) and len(cond.ops) == 1
                        and isinstance(cond.ops[0], op_type) and len(cond.comparators) == 1
                        and isinstance(cond.left, ast.Name) and cond.left.id == c.target.id
                        and self._same_expr(cond.comparators[0], query)
                    )

                if not interior_pick(inner.orelse[0], "max", ast.LtE, lo_name):
                    return fn
                if not interior_pick(inner.orelse[1], "min", ast.Gt, hi_name):
                    return fn

                def value_assign(st: ast.stmt, index_name: str):
                    if not (
                        isinstance(st, ast.Assign) and len(st.targets) == 1
                        and isinstance(st.targets[0], ast.Name)
                    ):
                        return None
                    expr = st.value
                    if (
                        isinstance(expr, ast.Call) and isinstance(expr.func, ast.Name)
                        and expr.func.id == "float" and len(expr.args) == 1 and not expr.keywords
                    ):
                        expr = expr.args[0]
                    if not (
                        isinstance(expr, ast.Subscript) and isinstance(expr.value, ast.Attribute)
                        and expr.value.attr == "loc" and isinstance(expr.value.value, ast.Name)
                        and expr.value.value.id == sub_name and isinstance(expr.slice, ast.Tuple)
                        and len(expr.slice.elts) == 2 and isinstance(expr.slice.elts[0], ast.Name)
                        and expr.slice.elts[0].id == index_name
                    ):
                        return None
                    ok, column = self._static_value(expr.slice.elts[1])
                    if not ok or column not in row.table.sample.columns:
                        return None
                    return st.targets[0].id, column

                lo_value = value_assign(body[3], lo_name)
                hi_value = value_assign(body[4], hi_name)
                if lo_value is None or hi_value is None or lo_value[1] != hi_value[1]:
                    return fn
                r_lo_name, column = lo_value
                r_hi_name, _ = hi_value
                ret = body[5]
                if not isinstance(ret, ast.Return) or ret.value is None:
                    return fn

                frac = ast.BinOp(
                    left=ast.BinOp(copy.deepcopy(query), ast.Sub(), ast.Name(lo_name, ast.Load())),
                    op=ast.Div(),
                    right=ast.BinOp(ast.Name(hi_name, ast.Load()), ast.Sub(), ast.Name(lo_name, ast.Load())),
                )

                log_expr = ast.BinOp(
                    left=ast.Name(r_lo_name, ast.Load()), op=ast.Mult(),
                    right=ast.BinOp(
                        left=ast.BinOp(ast.Name(r_hi_name, ast.Load()), ast.Div(), ast.Name(r_lo_name, ast.Load())),
                        op=ast.Pow(), right=frac,
                    ),
                )
                linear_expr = ast.BinOp(
                    left=ast.Name(r_lo_name, ast.Load()), op=ast.Add(),
                    right=ast.BinOp(
                        left=ast.BinOp(ast.Name(r_hi_name, ast.Load()), ast.Sub(), ast.Name(r_lo_name, ast.Load())),
                        op=ast.Mult(), right=frac,
                    ),
                )
                if self._same_expr(ret.value, log_expr):
                    mode = "log_linear"
                    mode_code = 1
                elif self._same_expr(ret.value, linear_expr):
                    mode = "linear"
                    mode_code = 0
                else:
                    return fn

                axis_key, value_key = registry.external_dataframe_interp_lookup(
                    row.table.ref_name, row.table.cell_name, row.table.cell,
                    row_key=row_key, column=column, interpolation=mode,
                    extrapolation="endpoint_segment",
                )
                call = ast.Call(
                    func=ast.Name("__interp_lookup_1d__", ast.Load()),
                    args=[ast.Constant(axis_key), ast.Constant(value_key), query, ast.Constant(mode_code)],
                    keywords=[],
                )
                out = copy.deepcopy(fn)
                out.body = [ast.copy_location(ast.Return(call), ret)]
                return ast.fix_missing_locations(out)

            def _rewrite_step_lookup_function(self, fn: ast.FunctionDef) -> ast.FunctionDef:
                """Recognize explicit last-anchor-<=x idioms as StepLookup1D.

                Supported tails are deliberately mathematical rather than pandas-general:

                * explicit numeric default below the first anchor;
                * hold-first below the first anchor via ``max(keys) if keys else min(index)``;
                * no fallback only when the query syntax itself proves a lower bound at
                  or above the first anchor (for example ``max(t, 0)`` with axis min 0).
                """
                body = list(fn.body)

                def finite_row_dispatch(row: RowSource):
                    """Prove one finite categorical prefix for a residual step axis.

                    A partial MultiIndex row view is eligible when it fixes every
                    leading level except the final residual numeric step axis, and
                    exactly one of those prefix selectors is a structurally proven
                    finite categorical value.  The other prefix levels, if any, must
                    be compile-time static.  Runtime dispatch is numeric code only;
                    each branch reuses the existing static StepLookup1D ABI.
                    """
                    table = row.table
                    if not isinstance(table.sample.index, pd.MultiIndex):
                        return None
                    nlevels = int(table.sample.index.nlevels)
                    prefix = self._expand_alias(copy.deepcopy(row.row_expr))
                    parts = list(prefix.elts) if isinstance(prefix, ast.Tuple) else [prefix]
                    if nlevels < 2 or len(parts) != nlevels - 1:
                        return None
                    fixed: dict[int, Any] = {}
                    dynamic: list[tuple[int, FiniteEnumValue]] = []
                    for level, expr in enumerate(parts):
                        ok, value = self._static_value(expr)
                        if ok:
                            fixed[level] = value
                            continue
                        enum_value = self._finite_enum(expr)
                        if enum_value is None:
                            return None
                        dynamic.append((level, enum_value))
                    if len(dynamic) != 1:
                        return None
                    level, enum_value = dynamic[0]
                    return tuple(sorted(fixed.items())), int(level), enum_value

                def step_parts(st: ast.stmt):
                    if not (
                        isinstance(st, ast.Assign) and len(st.targets) == 1
                        and isinstance(st.targets[0], ast.Name)
                    ):
                        return None
                    row = self._row_proxy(st.value)
                    if row is not None:
                        ok_row, row_key = self._static_value(row.row_expr)
                        if ok_row:
                            return st.targets[0].id, row.table, row_key, False, None
                        dispatch = finite_row_dispatch(row)
                        if dispatch is None:
                            return None
                        return st.targets[0].id, row.table, None, False, dispatch
                    table = self._table(st.value)
                    if table is not None and not isinstance(table.sample.index, pd.MultiIndex):
                        return st.targets[0].id, table, None, True, None
                    return None

                def key_list(st: ast.stmt, sub_name: str):
                    if not (
                        isinstance(st, ast.Assign) and len(st.targets) == 1
                        and isinstance(st.targets[0], ast.Name)
                        and isinstance(st.value, ast.ListComp)
                        and len(st.value.generators) == 1
                    ):
                        return None
                    comp = st.value.generators[0]
                    if not (
                        isinstance(comp.target, ast.Name)
                        and isinstance(comp.iter, ast.Attribute) and comp.iter.attr == "index"
                        and isinstance(comp.iter.value, ast.Name) and comp.iter.value.id == sub_name
                        and len(comp.ifs) == 1 and not comp.is_async
                        and isinstance(st.value.elt, ast.Name) and st.value.elt.id == comp.target.id
                    ):
                        return None
                    cond = comp.ifs[0]
                    if not (
                        isinstance(cond, ast.Compare) and len(cond.ops) == 1
                        and isinstance(cond.ops[0], ast.LtE) and len(cond.comparators) == 1
                        and isinstance(cond.left, ast.Name) and cond.left.id == comp.target.id
                    ):
                        return None
                    return st.targets[0].id, copy.deepcopy(cond.comparators[0])

                def lookup_return(st: ast.stmt, sub_name: str, table: TableSource, index_expr_pred):
                    if not isinstance(st, ast.Return) or st.value is None:
                        return None
                    expr = st.value
                    if (
                        isinstance(expr, ast.Call) and isinstance(expr.func, ast.Name)
                        and expr.func.id == "float" and len(expr.args) == 1 and not expr.keywords
                    ):
                        expr = expr.args[0]
                    if not (
                        isinstance(expr, ast.Subscript)
                        and isinstance(expr.value, ast.Attribute) and expr.value.attr == "loc"
                        and isinstance(expr.value.value, ast.Name) and expr.value.value.id == sub_name
                    ):
                        return None
                    slice_node = expr.slice
                    if not (isinstance(slice_node, ast.Tuple) and len(slice_node.elts) == 2):
                        return None
                    row_expr, col_expr = slice_node.elts
                    if not index_expr_pred(row_expr):
                        return None
                    try:
                        column = self._column_value(col_expr, table)
                    except FrontendError:
                        return None
                    return column

                def dispatch_row_keys(table: TableSource, dispatch):
                    fixed_items, enum_level, enum_value = dispatch
                    fixed = dict(fixed_items)
                    nlevels = int(table.sample.index.nlevels)
                    keys: list[tuple[int, str, Any]] = []
                    for code, label in enumerate(enum_value.labels):
                        values: list[Any] = []
                        for level in range(nlevels - 1):
                            if level == enum_level:
                                values.append(label)
                            elif level in fixed:
                                values.append(fixed[level])
                            else:  # pragma: no cover - guarded by finite_row_dispatch
                                raise FrontendError(
                                    "finite step-dispatch prefix has an unproved row level"
                                )
                        row_key = values[0] if len(values) == 1 else tuple(values)
                        try:
                            sub = table.sample.loc[row_key]
                        except Exception as exc:
                            raise FrontendError(
                                f"finite categorical step selector label {label!r} has no row slice in "
                                f"{table.ref_name}.{table.cell_name}"
                            ) from exc
                        if not isinstance(sub, (pd.DataFrame, pd.Series)):
                            raise FrontendError(
                                "finite categorical step selector did not leave a residual row axis"
                            )
                        keys.append((code, label, row_key))
                    if not keys:
                        raise FrontendError("finite categorical step selector has an empty domain")
                    return keys

                def step_call(table, row_key, whole_table, column, query, below_first, default_value):
                    axis_key, value_key = registry.external_dataframe_step_lookup(
                        table.ref_name, table.cell_name, table.cell,
                        row_key=row_key, column=column, below_first=below_first,
                        default_value=default_value, whole_table=whole_table,
                    )
                    return ast.Call(
                        func=ast.Name("__step_lookup_1d__", ast.Load()),
                        args=[
                            ast.Constant(axis_key), ast.Constant(value_key), copy.deepcopy(query),
                            ast.Constant(0.0 if default_value is None else float(default_value)),
                            ast.Constant(1 if below_first == "first" else 0),
                        ], keywords=[],
                    )

                def emit(
                    prefix, origin, table, row_key, whole_table, column, query,
                    below_first, default_value, dispatch=None,
                ):
                    if dispatch is None:
                        call = step_call(
                            table, row_key, whole_table, column, query,
                            below_first, default_value,
                        )
                    else:
                        rows = dispatch_row_keys(table, dispatch)
                        enum_value = dispatch[2]
                        enum_expr = self.visit(copy.deepcopy(enum_value.code_expr))
                        branch_calls = [
                            step_call(
                                table, branch_row_key, False, column, query,
                                below_first, default_value,
                            )
                            for _code, _label, branch_row_key in rows
                        ]
                        # The finite-enum proof plus its input-domain guard makes the
                        # code exhaustive.  Use the final proven label as the terminal
                        # branch and test every preceding code explicitly.
                        call = branch_calls[-1]
                        for (code, _label, _row_key), branch in reversed(
                            list(zip(rows[:-1], branch_calls[:-1]))
                        ):
                            call = ast.IfExp(
                                test=ast.Compare(
                                    copy.deepcopy(enum_expr), [ast.Eq()], [ast.Constant(code)]
                                ),
                                body=branch,
                                orelse=call,
                            )
                    out = copy.deepcopy(fn)
                    out.body = copy.deepcopy(prefix) + [ast.copy_location(ast.Return(call), origin)]
                    return ast.fix_missing_locations(out)

                for i, st in enumerate(body):
                    parts = step_parts(st)
                    if parts is None or i + 2 >= len(body):
                        continue
                    sub_name, table, row_key, whole_table, dispatch = parts
                    kl = key_list(body[i + 1], sub_name)
                    if kl is None:
                        continue
                    keys_name, query = kl

                    # Explicit constant default then max(keys).
                    if i + 3 < len(body):
                        default_st = body[i + 2]
                        if (
                            isinstance(default_st, ast.If)
                            and isinstance(default_st.test, ast.UnaryOp)
                            and isinstance(default_st.test.op, ast.Not)
                            and isinstance(default_st.test.operand, ast.Name)
                            and default_st.test.operand.id == keys_name
                            and len(default_st.body) == 1 and isinstance(default_st.body[0], ast.Return)
                            and not default_st.orelse
                        ):
                            ok_default, default_value = self._static_value(default_st.body[0].value)
                            if (
                                ok_default and not isinstance(default_value, bool)
                                and isinstance(default_value, (int, float, np.integer, np.floating))
                            ):
                                def is_max_keys(x):
                                    return (
                                        isinstance(x, ast.Call) and isinstance(x.func, ast.Name)
                                        and x.func.id == "max" and len(x.args) == 1 and not x.keywords
                                        and isinstance(x.args[0], ast.Name) and x.args[0].id == keys_name
                                    )
                                column = lookup_return(body[i + 3], sub_name, table, is_max_keys)
                                if column is not None and i + 4 == len(body):
                                    return emit(
                                        body[:i], body[i + 3], table, row_key, whole_table, column, query,
                                        "default", float(default_value), dispatch=dispatch,
                                    )

                    # key = max(keys) if keys else min(sub.index); return sub.loc[key, col]
                    key_st = body[i + 2]
                    if (
                        isinstance(key_st, ast.Assign) and len(key_st.targets) == 1
                        and isinstance(key_st.targets[0], ast.Name)
                        and isinstance(key_st.value, ast.IfExp)
                        and isinstance(key_st.value.test, ast.Name)
                        and key_st.value.test.id == keys_name
                    ):
                        selected_name = key_st.targets[0].id
                        yes, no = key_st.value.body, key_st.value.orelse
                        yes_ok = (
                            isinstance(yes, ast.Call) and isinstance(yes.func, ast.Name)
                            and yes.func.id == "max" and len(yes.args) == 1 and not yes.keywords
                            and isinstance(yes.args[0], ast.Name) and yes.args[0].id == keys_name
                        )
                        no_ok = (
                            isinstance(no, ast.Call) and isinstance(no.func, ast.Name)
                            and no.func.id == "min" and len(no.args) == 1 and not no.keywords
                            and isinstance(no.args[0], ast.Attribute) and no.args[0].attr == "index"
                            and isinstance(no.args[0].value, ast.Name) and no.args[0].value.id == sub_name
                        )
                        if yes_ok and no_ok and i + 3 < len(body):
                            column = lookup_return(
                                body[i + 3], sub_name, table,
                                lambda x: isinstance(x, ast.Name) and x.id == selected_name,
                            )
                            if column is not None and i + 4 == len(body):
                                return emit(
                                    body[:i], body[i + 3], table, row_key, whole_table, column, query,
                                    "first", None, dispatch=dispatch,
                                )

                    # Bare max(keys) is safe only if the query itself proves a lower bound.
                    def is_max_keys(x):
                        return (
                            isinstance(x, ast.Call) and isinstance(x.func, ast.Name)
                            and x.func.id == "max" and len(x.args) == 1 and not x.keywords
                            and isinstance(x.args[0], ast.Name) and x.args[0].id == keys_name
                        )
                    column = lookup_return(body[i + 2], sub_name, table, is_max_keys)
                    if column is not None and i + 3 == len(body):
                        row_slices: list[tuple[Any, pd.DataFrame | pd.Series]] = []
                        try:
                            if dispatch is None:
                                sub = table.sample if whole_table else table.sample.loc[row_key]
                                row_slices.append((row_key, sub))
                            else:
                                for _code, _label, branch_row_key in dispatch_row_keys(table, dispatch):
                                    row_slices.append((branch_row_key, table.sample.loc[branch_row_key]))
                            axis_mins = [float(min(sub.index)) for _rk, sub in row_slices]
                            axis_min = max(axis_mins)
                        except Exception:
                            continue
                        lower_bound, _upper_bound = self._numeric_bounds(query)
                        if lower_bound is not None and lower_bound >= axis_min:
                            tr = frontend.variant_trace_by_uid.get(fn.name)
                            source_name = tr.schema.name if tr is not None else fn.name
                            for branch_row_key, sub in row_slices:
                                branch_axis_min = float(min(sub.index))
                                fact_key = (
                                    fn.name,
                                    ast.dump(query, include_attributes=False),
                                    branch_axis_min,
                                    table.ref_name,
                                    table.cell_name,
                                    repr(branch_row_key),
                                    repr(column),
                                )
                                frontend._used_step_lookup_domain_facts[fact_key] = StepLookupDomainFact(
                                    source_uid=fn.name,
                                    source_name=source_name,
                                    query_expr=ast.unparse(query),
                                    axis_min=branch_axis_min,
                                    proven_lower_bound=float(lower_bound),
                                    proven_upper_bound=(
                                        None if _upper_bound is None else float(_upper_bound)
                                    ),
                                )
                            return emit(
                                body[:i], body[i + 2], table, row_key, whole_table, column, query,
                                "first", None, dispatch=dispatch,
                            )
                return fn

            def _rewrite_interval_lookup_function(self, fn: ast.FunctionDef) -> ast.FunctionDef:
                """Recognize the narrow ``iterrows`` interval-table idiom.

                Supported semantic: source-order ``lower < query <= upper`` tests
                with ``iloc[-1][value]`` fallback.  This is intentionally not a
                general DataFrame-loop lowering pass.
                """
                body = list(fn.body)

                def unwrap_float(expr: ast.AST) -> ast.AST:
                    if (
                        isinstance(expr, ast.Call) and isinstance(expr.func, ast.Name)
                        and expr.func.id == "float" and len(expr.args) == 1 and not expr.keywords
                    ):
                        return expr.args[0]
                    return expr

                def row_col(expr: ast.AST, row_name: str):
                    expr = unwrap_float(expr)
                    if not (
                        isinstance(expr, ast.Subscript) and isinstance(expr.value, ast.Name)
                        and expr.value.id == row_name
                    ):
                        return None
                    ok, value = self._static_value(expr.slice)
                    return value if ok else None

                def fallback_parts(st: ast.stmt):
                    if not isinstance(st, ast.Return) or st.value is None:
                        return None
                    expr = unwrap_float(st.value)
                    if not isinstance(expr, ast.Subscript):
                        return None
                    ok_col, value_col = self._static_value(expr.slice)
                    if not ok_col:
                        return None
                    iloc = expr.value
                    if not (
                        isinstance(iloc, ast.Subscript) and isinstance(iloc.value, ast.Attribute)
                        and iloc.value.attr == "iloc"
                    ):
                        return None
                    idx = iloc.slice
                    is_minus_one = (
                        isinstance(idx, ast.Constant) and idx.value == -1
                    ) or (
                        isinstance(idx, ast.UnaryOp) and isinstance(idx.op, ast.USub)
                        and isinstance(idx.operand, ast.Constant) and idx.operand.value == 1
                    )
                    if not is_minus_one:
                        return None
                    table = self._table(iloc.value.value)
                    if table is None:
                        return None
                    return table, value_col

                for i, st in enumerate(body):
                    if not isinstance(st, ast.For) or i + 1 != len(body) - 1:
                        continue
                    if not (
                        isinstance(st.target, (ast.Tuple, ast.List)) and len(st.target.elts) == 2
                        and isinstance(st.target.elts[1], ast.Name)
                        and isinstance(st.iter, ast.Call) and not st.iter.args and not st.iter.keywords
                        and isinstance(st.iter.func, ast.Attribute) and st.iter.func.attr == "iterrows"
                    ):
                        continue
                    row_name = st.target.elts[1].id
                    table = self._table(st.iter.func.value)
                    if table is None or len(st.body) != 1 or st.orelse:
                        continue
                    branch = st.body[0]
                    if not (
                        isinstance(branch, ast.If) and len(branch.body) == 1
                        and isinstance(branch.body[0], ast.Return) and branch.body[0].value is not None
                        and not branch.orelse
                    ):
                        continue
                    cond = branch.test
                    if not (
                        isinstance(cond, ast.Compare) and len(cond.ops) == 2 and len(cond.comparators) == 2
                        and isinstance(cond.ops[0], ast.Lt) and isinstance(cond.ops[1], ast.LtE)
                    ):
                        continue
                    lower_col = row_col(cond.left, row_name)
                    upper_col = row_col(cond.comparators[1], row_name)
                    value_col = row_col(branch.body[0].value, row_name)
                    if lower_col is None or upper_col is None or value_col is None:
                        continue
                    query = copy.deepcopy(cond.comparators[0])
                    fallback = fallback_parts(body[i + 1])
                    if fallback is None:
                        continue
                    fallback_table, fallback_col = fallback
                    if (
                        fallback_table.ref_name != table.ref_name
                        or fallback_table.cell_name != table.cell_name
                        or fallback_col != value_col
                    ):
                        continue
                    for col in (lower_col, upper_col, value_col):
                        if col not in table.sample.columns:
                            continue
                    lo_key, hi_key, value_key = registry.external_dataframe_interval_lookup(
                        table.ref_name, table.cell_name, table.cell,
                        lower_column=lower_col, upper_column=upper_col, value_column=value_col,
                        closure="(lo,hi]", fallback="last",
                    )
                    call = ast.Call(
                        func=ast.Name("__interval_lookup_1d__", ast.Load()),
                        args=[ast.Constant(lo_key), ast.Constant(hi_key), ast.Constant(value_key), query],
                        keywords=[],
                    )
                    out = copy.deepcopy(fn)
                    out.body = copy.deepcopy(body[:i]) + [ast.copy_location(ast.Return(call), st)]
                    return ast.fix_missing_locations(out)
                return fn

            def _external_table(self, node: ast.AST) -> TableSource | None:
                if not (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and isinstance(node.func.value, ast.Name)
                    and not node.args and not node.keywords
                ):
                    return None
                rn = node.func.value.id
                cn = node.func.attr
                cache_key = (rn, cn)
                if cache_key in self.external_cache:
                    return self.external_cache[cache_key]
                obj = frontend.refs.get(rn)
                if obj is None or not hasattr(obj, "cells") or cn not in obj.cells:
                    self.external_cache[cache_key] = None
                    return None
                cell = obj.cells[cn]
                try:
                    value = cell()
                except Exception:
                    self.external_cache[cache_key] = None
                    return None
                if not isinstance(value, pd.DataFrame):
                    self.external_cache[cache_key] = None
                    return None
                src = TableSource(rn, cn, cell, value)
                self.external_cache[cache_key] = src
                return src

            def _table(self, node: ast.AST) -> TableSource | None:
                if isinstance(node, ast.Name) and node.id in self.table_aliases:
                    return self.table_aliases[node.id]
                return self._external_table(node)

            def _series_from_expr(self, node: ast.AST) -> SeriesSource | None:
                """Recognize ``table.loc[static_prefix][numeric_column]`` exactly.

                pandas partial MultiIndex semantics select leading index levels.  The
                first version therefore requires *all but the final* index level to
                be compile-time proven static.  That leaves one numeric row axis and
                avoids pretending arbitrary pandas slicing is native semantics.
                """
                if not (
                    isinstance(node, ast.Subscript)
                    and isinstance(node.value, ast.Subscript)
                    and isinstance(node.value.value, ast.Attribute)
                    and node.value.value.attr == "loc"
                ):
                    return None
                table = self._table(node.value.value.value)
                if table is None or not isinstance(table.sample.index, pd.MultiIndex):
                    return None
                nlevels = int(table.sample.index.nlevels)
                prefix_node = self._expand_alias(node.value.slice)
                if isinstance(prefix_node, ast.Tuple):
                    prefix_parts = list(prefix_node.elts)
                else:
                    prefix_parts = [prefix_node]
                if len(prefix_parts) != nlevels - 1 or nlevels < 2:
                    return None
                fixed: list[tuple[int, Any]] = []
                for level, expr in enumerate(prefix_parts):
                    ok, value = self._static_value(expr)
                    if not ok:
                        return None
                    fixed.append((level, value))
                ok, column = self._static_value(node.slice)
                if not ok or column not in table.sample.columns:
                    return None
                source = SeriesSource(
                    table=table,
                    fixed_levels=tuple(fixed),
                    dynamic_level=nlevels - 1,
                    column=column,
                )
                # Force preparation-time validation now: unique/regular numeric axis,
                # numeric values and a non-empty static-prefix slice are all required.
                registry.external_dataframe_axis(
                    table.ref_name, table.cell_name, table.cell,
                    fixed_levels=dict(source.fixed_levels),
                    dynamic_level=source.dynamic_level,
                    column=source.column,
                )
                return source

            def _series(self, node: ast.AST) -> SeriesSource | None:
                if isinstance(node, ast.Name) and node.id in self.series_aliases:
                    return self.series_aliases[node.id]
                direct = self._series_from_expr(node)
                if direct is not None:
                    return direct
                if not (
                    isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and not node.args and not node.keywords
                ):
                    return None
                call_name = node.func.id
                if call_name in self.series_helper_cache:
                    return self.series_helper_cache[call_name]
                source_name: str | None = None
                if call_name in frontend.variant_trace_by_uid:
                    tr = frontend.variant_trace_by_uid[call_name]
                    if tr.key.time_pos is None and not tr.key.aux_values and tr.dtype == "object":
                        source_name = tr.schema.name
                elif call_name in frontend.base_funcs:
                    source_name = call_name
                base = frontend.base_funcs.get(source_name) if source_name is not None else None
                if base is None or base.args.args or base.args.posonlyargs or base.args.kwonlyargs:
                    self.series_helper_cache[call_name] = None
                    return None
                body = _strip_docstring(copy.deepcopy(base)).body
                if len(body) != 1 or not isinstance(body[0], ast.Return) or body[0].value is None:
                    self.series_helper_cache[call_name] = None
                    return None
                out = self._series_from_expr(body[0].value)
                self.series_helper_cache[call_name] = out
                return out

            def _point_field_finite_enum(
                self, source_name: str, node: ast.Call
            ) -> FiniteEnumValue | None:
                """Return the numeric enum ABI for a proven point-field selector.

                Guard-bearing selectors reuse ``ValidatedEnumCell`` evidence
                discovered earlier by the frontend; this table-normalization pass
                does not rediscover or reinterpret their validation control flow.
                Unguarded direct ``return model_point()["field"]`` selectors are
                admitted from the exact frozen RunDomain as before.
                """
                if frontend.model_point_row is None:
                    return None

                field: str | None = None
                labels: tuple[str, ...] | None = None
                validated = frontend.validated_enum_cells.get(source_name)
                if validated is not None:
                    if node.args or node.keywords:
                        return None
                    field = validated.field
                    labels = tuple(validated.allowed_values)
                else:
                    original = frontend.base_funcs.get(source_name)
                    if original is None:
                        return None
                    direct = _strip_docstring(copy.deepcopy(original))
                    positional = [*direct.args.posonlyargs, *direct.args.args]
                    if len(positional) != len(node.args) or node.keywords:
                        return None
                    mapping: dict[str, ast.AST] = {}
                    for param, arg in zip(positional, node.args):
                        ok, value = self._static_value(arg)
                        if not ok:
                            return None
                        mapping[param.arg] = ast.Constant(value)
                    if mapping:
                        direct = _Substitute(mapping).visit(direct)
                        direct = _ConservativeFolder().visit(direct)
                        if not isinstance(direct, ast.FunctionDef):
                            return None
                        direct = _prune_source_unreachable_tails(direct)
                    if not (
                        not direct.args.kwonlyargs and direct.args.vararg is None
                        and direct.args.kwarg is None and len(direct.body) == 1
                        and isinstance(direct.body[0], ast.Return)
                        and isinstance(direct.body[0].value, ast.Subscript)
                        and isinstance(direct.body[0].value.value, ast.Call)
                        and isinstance(direct.body[0].value.value.func, ast.Name)
                        and direct.body[0].value.value.func.id == frontend.model_point_row.cell_name
                        and not direct.body[0].value.value.args
                        and not direct.body[0].value.value.keywords
                        and isinstance(direct.body[0].value.slice, ast.Constant)
                        and isinstance(direct.body[0].value.slice.value, str)
                    ):
                        return None
                    field = str(direct.body[0].value.slice.value)

                try:
                    frame = frontend.model_point_row.provider()
                    values = frame[field].tolist()
                except Exception:
                    return None
                if not values:
                    return None

                if labels is None:
                    if not all(
                        isinstance(value, str) or bool(pd.isna(value)) for value in values
                    ):
                        return None
                    labels = tuple(dict.fromkeys(
                        value for value in values if isinstance(value, str)
                    ))
                    if not labels or len(labels) > 16:
                        return None
                else:
                    # A guard-bearing selector promises this exact source domain;
                    # every value in the frozen RunDomain must satisfy it now.
                    if not all(
                        isinstance(value, str) and value in labels for value in values
                    ):
                        return None

                key = registry.point_field(
                    frontend.model_point_row, field, enum_labels=labels
                )
                point_code = ast.Call(
                    ast.Name("point_input", ast.Load()), [ast.Constant(key)], []
                )
                has_other = any(not isinstance(value, str) for value in values)
                code_expr = (
                    ast.Call(
                        ast.Name("__exact_axis_code__", ast.Load()),
                        [point_code, ast.Constant(0), ast.Constant(1), ast.Constant(len(labels))], [],
                    )
                    if has_other else point_code
                )
                return FiniteEnumValue(
                    labels=labels, code_expr=code_expr, source_name=source_name,
                )

            def _encode_nested_enum_comparisons(self, expr: ast.AST) -> ast.AST:
                """Replace proven categorical string comparisons by integer-code tests.

                This is used only while proving another finite categorical helper.
                Unsupported object/string dependencies remain in the tree and are
                rejected by the caller, so composition is fail-closed.
                """
                outer = self

                class Encode(ast.NodeTransformer):
                    def visit_Compare(self, node: ast.Compare):
                        if (
                            len(node.ops) == 1 and isinstance(node.ops[0], (ast.Eq, ast.NotEq))
                            and len(node.comparators) == 1
                        ):
                            pairs = (
                                (node.left, node.comparators[0], False),
                                (node.comparators[0], node.left, True),
                            )
                            for enum_node, label_node, reversed_order in pairs:
                                enum_value = outer._finite_enum(enum_node)
                                if enum_value is None or not (
                                    isinstance(label_node, ast.Constant)
                                    and isinstance(label_node.value, str)
                                ):
                                    continue
                                code = outer._enum_label_code(enum_value, label_node.value)
                                if code is None:
                                    value = isinstance(node.ops[0], ast.NotEq)
                                    return ast.copy_location(ast.Constant(value), node)
                                left = copy.deepcopy(enum_value.code_expr)
                                right = ast.Constant(code)
                                if reversed_order:
                                    left, right = right, left
                                return ast.copy_location(
                                    ast.Compare(left, [copy.deepcopy(node.ops[0])], [right]), node
                                )
                        return self.generic_visit(node)

                return ast.fix_missing_locations(Encode().visit(copy.deepcopy(expr)))

            @staticmethod
            def _finite_string_value_labels(expr: ast.AST) -> tuple[str, ...] | None:
                """Return the finite string value domain of a pure conditional expression."""
                if isinstance(expr, ast.Constant) and isinstance(expr.value, str):
                    return (str(expr.value),)
                if isinstance(expr, ast.IfExp):
                    left = Normalize._finite_string_value_labels(expr.body)
                    right = Normalize._finite_string_value_labels(expr.orelse)
                    if left is None or right is None:
                        return None
                    return tuple(dict.fromkeys((*left, *right)))
                return None

            @staticmethod
            def _encode_finite_string_values(
                expr: ast.AST, codes: Mapping[str, int]
            ) -> ast.AST | None:
                """Encode only the value leaves of a proven finite string expression."""
                if isinstance(expr, ast.Constant) and isinstance(expr.value, str):
                    if expr.value not in codes:
                        return None
                    return ast.copy_location(ast.Constant(int(codes[expr.value])), expr)
                if isinstance(expr, ast.IfExp):
                    body = Normalize._encode_finite_string_values(expr.body, codes)
                    orelse = Normalize._encode_finite_string_values(expr.orelse, codes)
                    if body is None or orelse is None:
                        return None
                    return ast.copy_location(
                        ast.IfExp(test=copy.deepcopy(expr.test), body=body, orelse=orelse), expr
                    )
                return None

            def _finite_enum(self, node: ast.AST) -> FiniteEnumValue | None:
                """Prove one object Cell call is a pure finite string selector.

                The source Cell is specialized through the ordinary frontend first,
                so full-domain static branches have already disappeared and nested
                numeric helpers are already canonical UID calls.  We then require
                every reachable return to be a literal string and encode those
                labels as small integer codes.  No object/string value survives into
                canonical execution.
                """
                if isinstance(node, ast.Name) and node.id in self.finite_enum_aliases:
                    return self.finite_enum_aliases[node.id]
                expanded_node = self._expand_alias(copy.deepcopy(node))
                if isinstance(expanded_node, ast.IfExp):
                    # A local/source expression such as
                    # ``"a" if numeric_predicate else "b"`` is already a
                    # complete finite value-domain proof.  Encode only the
                    # string leaves here; the ordinary visitor remains
                    # responsible for lowering the numeric predicate itself.
                    encoded_condition = self._encode_nested_enum_comparisons(expanded_node)
                    labels = self._finite_string_value_labels(encoded_condition)
                    if labels and len(labels) <= 16:
                        codes = {label: i for i, label in enumerate(labels)}
                        encoded = self._encode_finite_string_values(encoded_condition, codes)
                        if encoded is not None:
                            encoded = ast.fix_missing_locations(encoded)
                            if not any(
                                isinstance(child, ast.Call)
                                and isinstance(child.func, ast.Name)
                                and child.func.id in frontend.variant_trace_by_uid
                                and frontend.variant_trace_by_uid[child.func.id].dtype == "object"
                                for child in ast.walk(encoded)
                            ):
                                return FiniteEnumValue(
                                    labels=labels,
                                    code_expr=encoded,
                                    source_name="<finite_expression>",
                                )
                if not (
                    isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and not node.keywords
                ):
                    return None
                token = ast.dump(node, include_attributes=False)
                if token in self.finite_enum_cache:
                    return self.finite_enum_cache[token]

                call_name = node.func.id
                tr = frontend.variant_trace_by_uid.get(call_name)
                source_name = tr.schema.name if tr is not None else (
                    call_name if call_name in frontend.base_funcs else None
                )
                if source_name is None:
                    self.finite_enum_cache[token] = None
                    return None
                if tr is not None and (
                    tr.dtype != "object" or frontend._source_reaches_recursive_cycle(source_name)
                ):
                    self.finite_enum_cache[token] = None
                    return None

                point_enum = self._point_field_finite_enum(source_name, node)
                if point_enum is not None:
                    self.finite_enum_cache[token] = point_enum
                    return point_enum

                if tr is None:
                    self.finite_enum_cache[token] = None
                    return None
                prepared = frontend._specialize_function(node.func.id)
                if prepared is None or prepared.args.vararg is not None or prepared.args.kwarg is not None:
                    self.finite_enum_cache[token] = None
                    return None
                params = [arg.arg for arg in prepared.args.args]
                if len(params) != len(node.args):
                    self.finite_enum_cache[token] = None
                    return None
                try:
                    expr = frontend._runtime_scalar_helper_expr_from_block(list(prepared.body), {})
                except FrontendError:
                    self.finite_enum_cache[token] = None
                    return None
                if params:
                    expr = _Substitute({
                        param: copy.deepcopy(arg) for param, arg in zip(params, node.args)
                    }).visit(expr)
                    expr = ast.fix_missing_locations(expr)
                expr = self._encode_nested_enum_comparisons(expr)
                labels = self._finite_string_value_labels(expr)
                if not labels or len(labels) > 16:
                    self.finite_enum_cache[token] = None
                    return None
                codes = {label: i for i, label in enumerate(labels)}
                encoded = self._encode_finite_string_values(expr, codes)
                if encoded is None:
                    self.finite_enum_cache[token] = None
                    return None
                encoded = ast.fix_missing_locations(encoded)
                if any(
                    isinstance(child, ast.Call) and isinstance(child.func, ast.Name)
                    and child.func.id in frontend.variant_trace_by_uid
                    and frontend.variant_trace_by_uid[child.func.id].dtype == "object"
                    for child in ast.walk(encoded)
                ):
                    # A condition that still depends on an object-valued Cell has
                    # not actually been converted into a numeric finite selector.
                    self.finite_enum_cache[token] = None
                    return None
                out = FiniteEnumValue(
                    labels=labels, code_expr=encoded, source_name=tr.schema.name
                )
                self.finite_enum_cache[token] = out
                return out

            @staticmethod
            def _enum_label_code(value: FiniteEnumValue, label: str) -> int | None:
                try:
                    return value.labels.index(label)
                except ValueError:
                    return None

            def _finite_dispatch(
                self, table: TableSource, row: ast.AST
            ) -> FiniteDispatch | None:
                if not isinstance(table.sample.index, pd.MultiIndex):
                    return None
                parts = self._row_parts(row, table)
                fixed: dict[int, Any] = {}
                enum_rows: list[tuple[int, FiniteEnumValue]] = []
                numeric_rows: list[tuple[int, ast.AST]] = []
                for level, expr in enumerate(parts):
                    ok, value = self._static_value(expr)
                    if ok:
                        fixed[level] = value
                        continue
                    enum_value = self._finite_enum(expr)
                    if enum_value is not None:
                        enum_rows.append((level, enum_value))
                    else:
                        numeric_rows.append((level, self._expand_alias(expr)))
                if len(enum_rows) != 1 or len(numeric_rows) != 1:
                    return None
                enum_level, enum_value = enum_rows[0]
                numeric_level, numeric_expr = numeric_rows[0]
                return FiniteDispatch(
                    fixed_levels=tuple(sorted(fixed.items())),
                    enum_level=int(enum_level), enum_value=enum_value,
                    numeric_level=int(numeric_level), numeric_expr=copy.deepcopy(numeric_expr),
                )

            def _dispatch_numeric_labels(
                self, table: TableSource, dispatch: FiniteDispatch, label: str
            ) -> tuple[Any, ...]:
                fixed = dict(dispatch.fixed_levels)
                fixed[dispatch.enum_level] = label
                labels: list[Any] = []
                for row in table.sample.index:
                    parts = row if isinstance(row, tuple) else (row,)
                    if all(parts[level] == value for level, value in fixed.items()):
                        labels.append(parts[dispatch.numeric_level])
                return tuple(labels)

            @staticmethod
            def _finite_numeric_exact_labels(
                labels: Sequence[Any], *, cap: int = 128
            ) -> tuple[tuple[Any, ...], tuple[int, ...]]:
                """Normalize a bounded finite integer label set without assuming spacing."""
                if not labels or len(labels) > int(cap):
                    raise FrontendError(
                        "finite irregular exact axis is empty or exceeds the bounded native dispatch cap"
                    )
                pairs: list[tuple[int, Any]] = []
                for label in labels:
                    raw = label
                    if isinstance(raw, str):
                        try:
                            raw = int(raw)
                        except Exception as exc:
                            raise FrontendError(
                                f"non-integral finite exact table label {label!r}"
                            ) from exc
                    if not isinstance(raw, (int, np.integer)) or isinstance(raw, (bool, np.bool_)):
                        raise FrontendError(
                            f"non-integral finite exact table label {label!r}"
                        )
                    pairs.append((int(raw), label))
                pairs.sort(key=lambda item: item[0])
                numeric = tuple(value for value, _source in pairs)
                if len(set(numeric)) != len(numeric):
                    raise FrontendError("finite exact table labels are not numerically unique")
                return tuple(source for _value, source in pairs), numeric

            def _finite_numeric_exact_code(
                self, expr: ast.AST, labels: Sequence[Any]
            ) -> tuple[tuple[Any, ...], ast.AST]:
                source_labels, numeric = self._finite_numeric_exact_labels(labels)
                x = self.visit(copy.deepcopy(expr))
                result: ast.AST = ast.Constant(-1)
                for code, value in reversed(tuple(enumerate(numeric))):
                    result = ast.IfExp(
                        test=ast.Compare(
                            copy.deepcopy(x), [ast.Eq()], [ast.Constant(int(value))]
                        ),
                        body=ast.Constant(int(code)),
                        orelse=result,
                    )
                return source_labels, ast.fix_missing_locations(result)

            def _numeric_membership_test(self, expr: ast.AST, labels: Sequence[Any]) -> ast.AST:
                try:
                    numeric, start, step = _safe_numeric_axis(labels)
                except FrontendError:
                    _source_labels, numeric = self._finite_numeric_exact_labels(labels)
                    x = self.visit(copy.deepcopy(expr))
                    tests = [
                        ast.Compare(
                            copy.deepcopy(x), [ast.Eq()], [ast.Constant(int(value))]
                        )
                        for value in numeric
                    ]
                    if len(tests) == 1:
                        return tests[0]
                    return ast.BoolOp(ast.Or(), tests)
                lo, hi = min(numeric), max(numeric)
                x = self.visit(copy.deepcopy(expr))
                tests: list[ast.AST] = [
                    ast.Compare(copy.deepcopy(x), [ast.GtE()], [ast.Constant(lo)]),
                    ast.Compare(copy.deepcopy(x), [ast.LtE()], [ast.Constant(hi)]),
                ]
                if step != 1:
                    tests.append(ast.Compare(
                        ast.BinOp(
                            ast.BinOp(copy.deepcopy(x), ast.Sub(), ast.Constant(start)),
                            ast.Mod(), ast.Constant(step),
                        ),
                        [ast.Eq()], [ast.Constant(0)],
                    ))
                return ast.BoolOp(ast.And(), tests)

            def _row_is_membership_guarded(
                self, table: TableSource, row: ast.AST
            ) -> bool:
                try:
                    actual = self._row_parts(row, table)
                except FrontendError:
                    return False
                actual_sig = tuple(ast.dump(part, include_attributes=False) for part in actual)
                for key_name, table_name in (
                    *self.membership_guarded_rows,
                    *self.active_membership_guarded_rows,
                ):
                    candidate = self.table_aliases.get(table_name)
                    if candidate is None or (
                        candidate.ref_name != table.ref_name or candidate.cell_name != table.cell_name
                    ):
                        continue
                    if key_name not in self.value_aliases:
                        continue
                    try:
                        expected = self._row_parts(ast.Name(key_name, ast.Load()), table)
                    except FrontendError:
                        continue
                    expected_sig = tuple(ast.dump(part, include_attributes=False) for part in expected)
                    if expected_sig == actual_sig:
                        return True
                return False

            @staticmethod
            def _inline_membership_guard(
                test: ast.AST,
            ) -> tuple[str, str, bool] | None:
                """Recognize one local ``key in table.index`` branch contract.

                The returned boolean tells whether the true branch is guarded.
                Guard scope is applied only while visiting that branch.
                """
                if not (
                    isinstance(test, ast.Compare)
                    and len(test.ops) == 1
                    and isinstance(test.ops[0], (ast.In, ast.NotIn))
                    and len(test.comparators) == 1
                    and isinstance(test.left, ast.Name)
                    and isinstance(test.comparators[0], ast.Attribute)
                    and test.comparators[0].attr == "index"
                    and isinstance(test.comparators[0].value, ast.Name)
                ):
                    return None
                return (
                    test.left.id,
                    test.comparators[0].value.id,
                    isinstance(test.ops[0], ast.In),
                )

            def _series_axis(self, source: SeriesSource) -> tuple[str, int, int, tuple[float, ...]]:
                key, start, step = registry.external_dataframe_axis(
                    source.table.ref_name, source.table.cell_name, source.table.cell,
                    fixed_levels=dict(source.fixed_levels),
                    dynamic_level=source.dynamic_level,
                    column=source.column,
                )
                sem = registry.specs[key].normalized_table
                assert sem is not None
                labels = tuple(float(x) for x in sem.dynamic_labels)
                return key, start, step, labels

            def _expand_alias(self, node: ast.AST, depth: int = 0) -> ast.AST:
                if depth > 8:
                    return node
                if isinstance(node, ast.Name) and node.id in self.value_aliases:
                    return self._expand_alias(copy.deepcopy(self.value_aliases[node.id]), depth + 1)
                return node

            def _static_value(self, node: ast.AST) -> tuple[bool, Any]:
                node = self._expand_alias(node)
                if isinstance(node, ast.Constant):
                    return True, node.value
                if isinstance(node, ast.Tuple):
                    values = []
                    for item in node.elts:
                        ok, value = self._static_value(item)
                        if not ok:
                            return False, None
                        values.append(value)
                    return True, tuple(values)
                if isinstance(node, ast.UnaryOp):
                    ok, value = self._static_value(node.operand)
                    if not ok:
                        return False, None
                    try:
                        if isinstance(node.op, ast.USub): return True, -value
                        if isinstance(node.op, ast.UAdd): return True, +value
                        if isinstance(node.op, ast.Not): return True, not value
                    except Exception:
                        return False, None
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if not node.args and not node.keywords:
                        if node.func.id in frontend.variant_trace_by_uid:
                            return frontend._proven_static_variant_value(node.func.id)
                        if node.func.id in frontend.base_funcs:
                            ok, value = frontend._proven_static_cell_value(node.func.id)
                            if ok:
                                return True, value
                    if node.func.id in {"int", "float", "str", "bool"} and len(node.args) == 1 and not node.keywords:
                        ok, value = self._static_value(node.args[0])
                        if not ok:
                            return False, None
                        try:
                            return True, {"int": int, "float": float, "str": str, "bool": bool}[node.func.id](value)
                        except Exception:
                            return False, None
                return False, None

            def _row_parts(self, row: ast.AST, table: TableSource) -> list[ast.AST]:
                row = self._expand_alias(row)
                nlevels = int(table.sample.index.nlevels) if isinstance(table.sample.index, pd.MultiIndex) else 1
                if nlevels == 1:
                    return [row]
                if isinstance(row, ast.Tuple) and len(row.elts) == nlevels:
                    return [self._expand_alias(x) for x in row.elts]
                raise FrontendError(
                    f"external table {table.ref_name}.{table.cell_name} requires a {nlevels}-part row key"
                )

            def _column_value(self, node: ast.AST, table: TableSource) -> Any:
                ok, value = self._static_value(node)
                if not ok:
                    raise FrontendError(
                        f"external table {table.ref_name}.{table.cell_name} requires a compile-time column label"
                    )
                if value not in table.sample.columns:
                    raise FrontendError(
                        f"external table {table.ref_name}.{table.cell_name} has no column {value!r}"
                    )
                return value

            def _record_exact_table_operator(
                self,
                *,
                table: TableSource,
                column: Any,
                value_key: str,
                sparse_key: str | None,
                layout: str,
                axes: Sequence[NormalizedTableAxis],
                dynamic_exprs: Sequence[ast.AST],
                fixed_levels: Mapping[int, Any],
                provenance_tag: str = "external_dataframe_exact_lookup",
            ) -> None:
                if operator_uid is None:
                    return
                binding = (
                    ("source_ref", table.ref_name),
                    ("source_cell", table.cell_name),
                    ("column", repr(column)),
                    ("layout", layout),
                    ("value_input_key", value_key),
                    ("sparse_key_input", sparse_key),
                    ("fixed_levels", tuple(sorted((int(k), repr(v)) for k, v in fixed_levels.items()))),
                    ("axes", tuple(
                        (
                            axis.level, axis.index_name, axis.selector_kind,
                            tuple(axis.labels), axis.axis_start, axis.axis_step,
                            axis.axis_input_key,
                        )
                        for axis in axes
                    )),
                )
                prior = frontend._normalized_operators.get(operator_uid)
                prior_bindings: tuple[tuple[str, Any], ...] = ()
                prior_dynamic: tuple[str, ...] = ()
                prior_provenance: tuple[str, ...] = ()
                if prior is not None and prior.kind == "table_lookup":
                    prior_bindings = prior.static_inputs
                    prior_dynamic = prior.dynamic_inputs
                    prior_provenance = prior.provenance
                lookup_no = sum(1 for name, _ in prior_bindings if name.startswith("lookup_"))
                frontend._normalized_operators[operator_uid] = NormalizedOperator(
                    uid=operator_uid,
                    kind="table_lookup",
                    result_dtype="float64",
                    result_shape="scalar",
                    static_inputs=prior_bindings + ((f"lookup_{lookup_no}", binding),),
                    dynamic_inputs=prior_dynamic + tuple(ast.unparse(x) for x in dynamic_exprs),
                    provenance=tuple(dict.fromkeys((*prior_provenance,
                        provenance_tag,
                        "numeric_selector_encoding",
                        layout,
                        "runtime_domain_guard",
                    ))),
                    state_semantic="state_free",
                    python_supported=True,
                    cython_supported=True,
                )

            def _exact_nd_lookup(
                self,
                table: TableSource,
                parts: Sequence[ast.AST],
                fixed: Mapping[int, Any],
                dynamic: Sequence[tuple[int, ast.AST]],
                column: Any,
                origin: ast.AST,
                membership_guarded: bool = False,
            ) -> ast.AST:
                axes: list[NormalizedTableAxis] = []
                selector_codes: list[ast.AST] = []
                selector_sources: list[ast.AST] = []
                fixed_dict = dict(fixed)
                nlevels = int(table.sample.index.nlevels) if isinstance(table.sample.index, pd.MultiIndex) else 1
                index_names = tuple(table.sample.index.names) if isinstance(table.sample.index, pd.MultiIndex) else (table.sample.index.name,)

                for level, raw_expr in dynamic:
                    expr = self._expand_alias(copy.deepcopy(raw_expr))
                    selector_sources.append(copy.deepcopy(expr))
                    enum_value = self._finite_enum(expr)
                    if enum_value is not None:
                        axes.append(NormalizedTableAxis(
                            level=int(level), index_name=index_names[level],
                            selector_kind="finite_categorical",
                            labels=tuple(enum_value.labels),
                        ))
                        selector_codes.append(self.visit(copy.deepcopy(enum_value.code_expr)))
                        continue

                    labels: list[Any] = []
                    for row_label in table.sample.index:
                        row_parts = row_label if isinstance(row_label, tuple) else (row_label,)
                        if all(row_parts[k] == value for k, value in fixed_dict.items()):
                            labels.append(row_parts[level])
                    unique_labels = tuple(sorted(set(labels)))
                    try:
                        numeric_labels, start, step = _safe_numeric_axis(unique_labels)
                    except FrontendError as exc:
                        if not membership_guarded:
                            raise FrontendError(
                                f"external table {table.ref_name}.{table.cell_name} dynamic level "
                                f"{level} selector {ast.unparse(expr)!r} is neither a proven finite "
                                f"categorical selector nor a regular numeric exact axis: {exc}"
                            ) from exc
                        source_labels, code_expr = self._finite_numeric_exact_code(
                            expr, unique_labels
                        )
                        axes.append(NormalizedTableAxis(
                            level=int(level), index_name=index_names[level],
                            selector_kind="finite_numeric_exact",
                            labels=source_labels,
                        ))
                        selector_codes.append(code_expr)
                        continue
                    # Preserve the source labels used to slice/materialize the
                    # pandas table while deriving numeric runtime codes from their
                    # integral interpretation.  This matters for legitimate axes
                    # such as columns ``"0".."5"`` whose runtime selector is an
                    # integer but whose source labels are strings.
                    numeric_to_source = sorted(
                        zip(numeric_labels, unique_labels), key=lambda item: item[0]
                    )
                    source_labels = tuple(label for _numeric, label in numeric_to_source)
                    visited = self.visit(copy.deepcopy(expr))
                    selector_codes.append(ast.Call(
                        ast.Name("__exact_axis_code__", ast.Load()),
                        [
                            visited,
                            ast.Constant(int(start)), ast.Constant(int(step)),
                            ast.Constant(len(source_labels)),
                        ], [],
                    ))
                    axes.append(NormalizedTableAxis(
                        level=int(level), index_name=index_names[level],
                        selector_kind="numeric_exact", labels=source_labels,
                        axis_start=int(start), axis_step=int(step),
                    ))

                value_key, sparse_key, layout = registry.external_dataframe_exact_nd(
                    table.ref_name, table.cell_name, table.cell,
                    fixed_levels=fixed_dict, dynamic_axes=tuple(axes), column=column,
                )
                self._record_exact_table_operator(
                    table=table, column=column, value_key=value_key,
                    sparse_key=sparse_key, layout=layout, axes=axes,
                    dynamic_exprs=selector_sources,
                    fixed_levels=fixed_dict,
                )
                if layout == "dense_cartesian":
                    return ast.copy_location(
                        ast.Call(
                            ast.Name("table_input", ast.Load()),
                            [ast.Constant(value_key), *selector_codes], [],
                        ),
                        origin,
                    )
                assert sparse_key is not None
                return ast.copy_location(
                    ast.Call(
                        ast.Name("__sparse_table_lookup__", ast.Load()),
                        [ast.Constant(sparse_key), ast.Constant(value_key), *selector_codes], [],
                    ),
                    origin,
                )

            def _lookup(self, table: TableSource, row: ast.AST, column_node: ast.AST, origin: ast.AST) -> ast.AST:
                ok_column, _static_column = self._static_value(column_node)
                if not ok_column:
                    column_enum = self._finite_enum(column_node)
                    if column_enum is not None:
                        labels = tuple(column_enum.labels)
                        if not labels or any(label not in table.sample.columns for label in labels):
                            raise FrontendError(
                                f"external table {table.ref_name}.{table.cell_name} finite column selector "
                                "exceeds the frozen column domain"
                            )
                        kinds = tuple(np.asarray(table.sample[label]).dtype.kind for label in labels)
                        if any(kind not in "iubfc" for kind in kinds):
                            raise FrontendError(
                                f"external table {table.ref_name}.{table.cell_name} finite column selector "
                                "includes a non-numeric column"
                            )

                        selector = self.visit(copy.deepcopy(column_enum.code_expr))
                        branches = [
                            self._lookup(
                                table, copy.deepcopy(row), ast.Constant(label), origin
                            )
                            for label in labels
                        ]
                        result = branches[-1]
                        for code, branch in reversed(tuple(enumerate(branches[:-1]))):
                            result = ast.IfExp(
                                test=ast.Compare(
                                    copy.deepcopy(selector), [ast.Eq()], [ast.Constant(code)]
                                ),
                                body=branch,
                                orelse=result,
                            )
                        if operator_uid is not None:
                            prior = frontend._normalized_operators.get(operator_uid)
                            if prior is not None and prior.kind == "table_lookup":
                                frontend._normalized_operators[operator_uid] = NormalizedOperator(
                                    uid=prior.uid,
                                    kind=prior.kind,
                                    result_dtype=prior.result_dtype,
                                    result_shape=prior.result_shape,
                                    static_inputs=prior.static_inputs + ((
                                        "finite_column_labels", tuple(map(repr, labels))
                                    ),),
                                    dynamic_inputs=prior.dynamic_inputs + (
                                        ast.unparse(self._expand_alias(copy.deepcopy(column_node))),
                                    ),
                                    provenance=tuple(dict.fromkeys((
                                        *prior.provenance,
                                        "finite_categorical_column_dispatch",
                                    ))),
                                    state_semantic=prior.state_semantic,
                                    python_supported=prior.python_supported,
                                    cython_supported=prior.cython_supported,
                                )
                        return ast.copy_location(ast.fix_missing_locations(result), origin)
                column = self._column_value(column_node, table)
                parts = self._row_parts(row, table)
                fixed: dict[int, Any] = {}
                dynamic: list[tuple[int, ast.AST]] = []
                for level, expr in enumerate(parts):
                    ok, value = self._static_value(expr)
                    if ok:
                        fixed[level] = value
                    else:
                        dynamic.append((level, self._expand_alias(expr)))
                if not dynamic:
                    row_key: Any
                    values = tuple(fixed[i] for i in range(len(parts)))
                    row_key = values[0] if len(values) == 1 else values
                    key = registry.external_dataframe_scalar(
                        table.ref_name, table.cell_name, table.cell, row_key, column
                    )
                    return ast.copy_location(
                        ast.Call(ast.Name("global_input", ast.Load()), [ast.Constant(key)], []), origin
                    )
                if len(dynamic) >= 2:
                    return self._exact_nd_lookup(
                        table, parts, fixed, dynamic, column, origin,
                        membership_guarded=self._row_is_membership_guarded(table, row),
                    )
                if len(dynamic) != 1:
                    dispatch = self._finite_dispatch(table, row)
                    if dispatch is None:
                        raise FrontendError(
                            f"external table {table.ref_name}.{table.cell_name} lookup has {len(dynamic)} dynamic row levels; "
                            "current optimized table subset supports at most one numeric level unless one other level "
                            "is a structurally proven finite categorical selector"
                        )
                    guarded = self._row_is_membership_guarded(table, row)
                    enum_expr = self.visit(copy.deepcopy(dispatch.enum_value.code_expr))
                    numeric_bounds = self._numeric_bounds(dispatch.numeric_expr)
                    result: ast.AST | None = None
                    col_kind = np.asarray(table.sample[column]).dtype.kind
                    fallback: ast.AST = ast.Constant(0 if col_kind in "iub" else 0.0)
                    result = fallback
                    for code, label in reversed(tuple(enumerate(dispatch.enum_value.labels))):
                        labels = self._dispatch_numeric_labels(table, dispatch, label)
                        if not labels:
                            if not guarded:
                                raise FrontendError(
                                    f"finite categorical selector label {label!r} has no rows in "
                                    f"{table.ref_name}.{table.cell_name} and the source lookup is not protected by "
                                    "a direct membership-return guard"
                                )
                            continue
                        numeric, axis_start, axis_step = _safe_numeric_axis(labels)
                        lo, hi = min(numeric), max(numeric)
                        qlo, qhi = numeric_bounds
                        if not guarded and (
                            qlo is None or qhi is None or qlo < lo or qhi > hi
                            or (axis_step != 1 and not (
                                qlo == qhi and (qlo - axis_start) % axis_step == 0
                            ))
                        ):
                            raise FrontendError(
                                "finite categorical table lookup requires either source-proven in-domain numeric "
                                f"bounds or a direct membership-return guard; label={label!r}, "
                                f"proven={qlo!r},{qhi!r}, axis={lo!r},{hi!r}"
                            )
                        fixed_levels = dict(dispatch.fixed_levels)
                        fixed_levels[dispatch.enum_level] = label
                        key, start, step = registry.external_dataframe_axis(
                            table.ref_name, table.cell_name, table.cell,
                            fixed_levels=fixed_levels,
                            dynamic_level=dispatch.numeric_level, column=column,
                        )
                        # ``external_dataframe_axis`` is the authoritative source of
                        # executable axis semantics.  The local validation above uses
                        # the same labels only to decide whether an unguarded lookup is
                        # total over the proven query domain.
                        assert int(start) == int(axis_start) and int(step) == int(axis_step)
                        mapped = _axis_index_expr(
                            self.visit(copy.deepcopy(dispatch.numeric_expr)), start, step
                        )
                        value = ast.Call(
                            ast.Name("array_input", ast.Load()), [ast.Constant(key), mapped], []
                        )
                        test = ast.Compare(
                            copy.deepcopy(enum_expr), [ast.Eq()], [ast.Constant(code)]
                        )
                        result = ast.IfExp(test=test, body=value, orelse=result)
                    return ast.copy_location(ast.fix_missing_locations(result), origin)
                level, expr = dynamic[0]
                key, start, step = registry.external_dataframe_axis(
                    table.ref_name, table.cell_name, table.cell,
                    fixed_levels=fixed, dynamic_level=level, column=column,
                )
                mapped = _axis_index_expr(self.visit(copy.deepcopy(expr)), start, step)
                return ast.copy_location(
                    ast.Call(ast.Name("array_input", ast.Load()), [ast.Constant(key), mapped], []), origin
                )

            def _loc_parts(self, node: ast.AST) -> tuple[TableSource, ast.AST] | None:
                if not (
                    isinstance(node, ast.Subscript)
                    and isinstance(node.value, ast.Attribute)
                    and node.value.attr == "loc"
                ):
                    return None
                table = self._table(node.value.value)
                if table is None:
                    return None
                return table, node.slice

            def _is_scalar_loc(self, table: TableSource, slice_node: ast.AST) -> tuple[ast.AST, ast.AST] | None:
                if not isinstance(slice_node, ast.Tuple) or len(slice_node.elts) != 2:
                    return None
                first, second = slice_node.elts
                if isinstance(first, ast.Tuple):
                    return first, second
                expanded = self._expand_alias(first)
                if isinstance(expanded, ast.Tuple):
                    ok, col = self._static_value(second)
                    if ok and col in table.sample.columns:
                        return expanded, second
                nlevels = int(table.sample.index.nlevels) if isinstance(table.sample.index, pd.MultiIndex) else 1
                if nlevels == 1:
                    return first, second
                ok, col = self._static_value(second)
                if ok and col in table.sample.columns:
                    return first, second
                return None

            def _row_proxy(self, node: ast.AST) -> RowSource | None:
                loc = self._loc_parts(node)
                if loc is None:
                    return None
                table, slice_node = loc
                if self._is_scalar_loc(table, slice_node) is not None:
                    return None
                return RowSource(table, self._expand_alias(slice_node))

            def _row_view_axis_extreme_lookup(
                self, row: RowSource, *, extreme: str, origin: ast.AST
            ) -> ast.AST | None:
                table = row.table
                if not isinstance(table.sample.index, pd.MultiIndex):
                    return None
                nlevels = int(table.sample.index.nlevels)
                prefix = self._expand_alias(copy.deepcopy(row.row_expr))
                prefix_parts = list(prefix.elts) if isinstance(prefix, ast.Tuple) else [prefix]
                # Pandas partial MultiIndex row selection fixes leading levels.
                # This normalized subset requires exactly one residual level.
                if len(prefix_parts) != nlevels - 1:
                    return None
                residual_level = len(prefix_parts)
                index_names = tuple(table.sample.index.names)

                fixed: dict[int, Any] = {}
                dynamic: list[tuple[int, ast.AST]] = []
                for level, expr in enumerate(prefix_parts):
                    ok, value = self._static_value(expr)
                    if ok:
                        fixed[level] = value
                    else:
                        dynamic.append((level, self._expand_alias(copy.deepcopy(expr))))

                axes: list[NormalizedTableAxis] = []
                selector_codes: list[ast.AST] = []
                selector_sources: list[ast.AST] = []
                for level, raw_expr in dynamic:
                    expr = self._expand_alias(copy.deepcopy(raw_expr))
                    selector_sources.append(copy.deepcopy(expr))
                    enum_value = self._finite_enum(expr)
                    if enum_value is not None:
                        axes.append(NormalizedTableAxis(
                            level=int(level), index_name=index_names[level],
                            selector_kind="finite_categorical",
                            labels=tuple(enum_value.labels),
                        ))
                        selector_codes.append(self.visit(copy.deepcopy(enum_value.code_expr)))
                        continue

                    labels: list[Any] = []
                    for row_label in table.sample.index:
                        parts = row_label if isinstance(row_label, tuple) else (row_label,)
                        if all(parts[k] == value for k, value in fixed.items()):
                            labels.append(parts[level])
                    unique_labels = tuple(sorted(set(labels)))
                    try:
                        numeric_labels, start, step = _safe_numeric_axis(unique_labels)
                    except FrontendError as exc:
                        raise FrontendError(
                            f"external table {table.ref_name}.{table.cell_name} row-view prefix level "
                            f"{level} selector {ast.unparse(expr)!r} is neither a proven finite "
                            f"categorical selector nor a regular numeric exact axis: {exc}"
                        ) from exc
                    numeric_to_source = sorted(
                        zip(numeric_labels, unique_labels), key=lambda item: item[0]
                    )
                    source_labels = tuple(label for _numeric, label in numeric_to_source)
                    visited = self.visit(copy.deepcopy(expr))
                    selector_codes.append(ast.Call(
                        ast.Name("__exact_axis_code__", ast.Load()),
                        [
                            visited,
                            ast.Constant(int(start)), ast.Constant(int(step)),
                            ast.Constant(len(source_labels)),
                        ], [],
                    ))
                    axes.append(NormalizedTableAxis(
                        level=int(level), index_name=index_names[level],
                        selector_kind="numeric_exact", labels=source_labels,
                        axis_start=int(start), axis_step=int(step),
                    ))

                value_key, sparse_key, layout = registry.external_dataframe_row_axis_extreme(
                    table.ref_name, table.cell_name, table.cell,
                    fixed_levels=fixed, dynamic_axes=tuple(axes),
                    residual_level=residual_level, extreme=extreme,
                )
                self._record_exact_table_operator(
                    table=table,
                    column=(f"__index_{extreme}__", residual_level),
                    value_key=value_key,
                    sparse_key=sparse_key,
                    layout=layout,
                    axes=axes,
                    dynamic_exprs=selector_sources,
                    fixed_levels=fixed,
                    provenance_tag="external_row_view_axis_metadata",
                )
                if not axes:
                    # All prefix levels are static, so the prepared metadata input
                    # is a scalar singleton domain.
                    return ast.copy_location(
                        ast.Call(ast.Name("global_input", ast.Load()), [ast.Constant(value_key)], []),
                        origin,
                    )
                if layout == "dense_cartesian":
                    return ast.copy_location(
                        ast.Call(
                            ast.Name("table_input", ast.Load()),
                            [ast.Constant(value_key), *selector_codes], [],
                        ),
                        origin,
                    )
                assert sparse_key is not None
                return ast.copy_location(
                    ast.Call(
                        ast.Name("__sparse_table_lookup__", ast.Load()),
                        [ast.Constant(sparse_key), ast.Constant(value_key), *selector_codes], [],
                    ),
                    origin,
                )

            def _table_index_extreme(self, node: ast.AST) -> ast.AST | None:
                if not (
                    isinstance(node, ast.Call) and not node.args and not node.keywords
                    and isinstance(node.func, ast.Attribute) and node.func.attr in {"min", "max"}
                    and isinstance(node.func.value, ast.Attribute) and node.func.value.attr == "index"
                ):
                    return None
                base = node.func.value.value
                if isinstance(base, ast.Name) and base.id in self.series_aliases:
                    _, _, _, labels = self._series_axis(self.series_aliases[base.id])
                    if not labels:
                        return None
                    extreme = min(labels) if node.func.attr == "min" else max(labels)
                    if float(extreme).is_integer():
                        extreme = int(extreme)
                    return ast.copy_location(ast.Constant(extreme), node)
                if isinstance(base, ast.Name) and base.id in self.row_aliases:
                    row = self.row_aliases[base.id]
                    ok, row_key = self._static_value(row.row_expr)
                    if not ok:
                        return self._row_view_axis_extreme_lookup(
                            row, extreme=node.func.attr, origin=node
                        )
                    try:
                        sub = row.table.sample.loc[row_key]
                    except Exception as exc:
                        raise FrontendError(
                            f"external table row slice {row.table.ref_name}.{row.table.cell_name}[{row_key!r}] failed"
                        ) from exc
                    if isinstance(sub, pd.Series):
                        # A Series row has column labels rather than a numeric row axis.
                        return None
                    if not isinstance(sub, pd.DataFrame) or isinstance(sub.index, pd.MultiIndex):
                        return None
                    labels, _, _ = _safe_numeric_axis(sub.index)
                    extreme = min(labels) if node.func.attr == "min" else max(labels)
                    return ast.copy_location(ast.Constant(extreme), node)
                table = self._table(base)
                if table is None:
                    return None
                if isinstance(table.sample.index, pd.MultiIndex):
                    raise FrontendError(
                        f"external table {table.ref_name}.{table.cell_name}.index.{node.func.attr}() on MultiIndex is outside the normalized subset"
                    )
                labels, _, _ = _safe_numeric_axis(table.sample.index)
                extreme = min(labels) if node.func.attr == "min" else max(labels)
                return ast.copy_location(ast.Constant(extreme), node)

            def _multiindex_level_extreme(self, node: ast.AST) -> ast.AST | None:
                """Resolve a pure min/max projection of one MultiIndex level.

                This is preparation-time metadata normalization, not a general
                generator-expression evaluator.  The accepted source shape is
                deliberately exact::

                    max(level_name for level_a, level_name in table.index)

                (and the analogous ``min`` form).  The generator must have one
                unfiltered synchronous iterator over the immutable prepared table
                index, and the yielded expression must be exactly one tuple-bound
                index component.  Anything more dynamic remains ordinary Python
                source and therefore fails closed later in table normalization.
                """
                if not (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id in {"min", "max"}
                    and len(node.args) == 1
                    and not node.keywords
                    and isinstance(node.args[0], ast.GeneratorExp)
                ):
                    return None
                gen = node.args[0]
                if len(gen.generators) != 1:
                    return None
                comp = gen.generators[0]
                if comp.ifs or comp.is_async:
                    return None
                if not (
                    isinstance(comp.iter, ast.Attribute)
                    and comp.iter.attr == "index"
                ):
                    return None
                table = self._table(comp.iter.value)
                if table is None or not isinstance(table.sample.index, pd.MultiIndex):
                    return None
                if not isinstance(comp.target, (ast.Tuple, ast.List)):
                    return None
                targets = list(comp.target.elts)
                nlevels = int(table.sample.index.nlevels)
                if len(targets) != nlevels or not all(isinstance(x, ast.Name) for x in targets):
                    return None
                names = [x.id for x in targets]
                if len(set(names)) != len(names):
                    return None
                if not isinstance(gen.elt, ast.Name) or gen.elt.id not in names:
                    return None
                level = names.index(gen.elt.id)
                values = list(table.sample.index.get_level_values(level))
                if not values:
                    raise FrontendError(
                        f"external table {table.ref_name}.{table.cell_name} has an empty index level"
                    )
                normalized: list[int | float] = []
                for value in values:
                    if (
                        not isinstance(value, (int, float, np.integer, np.floating))
                        or isinstance(value, (bool, np.bool_))
                        or not np.isfinite(float(value))
                    ):
                        raise FrontendError(
                            f"external table {table.ref_name}.{table.cell_name} index level {level} "
                            "is not finite numeric and cannot be aggregated during preparation"
                        )
                    normalized.append(value.item() if isinstance(value, np.generic) else value)
                extreme = min(normalized) if node.func.id == "min" else max(normalized)
                return ast.copy_location(ast.Constant(extreme), node)

            def _membership(self, left: ast.AST, comparator: ast.AST, origin: ast.AST) -> ast.AST | None:
                if not (isinstance(comparator, ast.Attribute) and comparator.attr == "index"):
                    return None
                table = self._table(comparator.value)
                if table is None:
                    return None
                if isinstance(table.sample.index, pd.MultiIndex):
                    parts = self._row_parts(left, table)
                    fixed = {}
                    dynamic = []
                    for level, expr in enumerate(parts):
                        ok, value = self._static_value(expr)
                        if ok: fixed[level] = value
                        else: dynamic.append((level, self._expand_alias(expr)))
                    if len(dynamic) != 1:
                        dispatch = self._finite_dispatch(table, left)
                        if dispatch is None:
                            raise FrontendError(
                                "normalized table membership requires exactly one dynamic numeric row level, "
                                "or one such level plus one structurally proven finite categorical selector"
                            )
                        enum_expr = self.visit(copy.deepcopy(dispatch.enum_value.code_expr))
                        branches: list[ast.AST] = []
                        for code, label in enumerate(dispatch.enum_value.labels):
                            labels = self._dispatch_numeric_labels(table, dispatch, label)
                            if not labels:
                                continue
                            numeric_test = self._numeric_membership_test(
                                dispatch.numeric_expr, labels
                            )
                            branches.append(ast.BoolOp(ast.And(), [
                                ast.Compare(
                                    copy.deepcopy(enum_expr), [ast.Eq()], [ast.Constant(code)]
                                ),
                                numeric_test,
                            ]))
                        if not branches:
                            return ast.copy_location(ast.Constant(False), origin)
                        replacement = branches[0] if len(branches) == 1 else ast.BoolOp(ast.Or(), branches)
                        return ast.copy_location(ast.fix_missing_locations(replacement), origin)
                    dyn_level, dyn_expr = dynamic[0]
                    labels = []
                    for label in table.sample.index:
                        vals = label if isinstance(label, tuple) else (label,)
                        if all(vals[k] == v for k, v in fixed.items()):
                            labels.append(vals[dyn_level])
                else:
                    dyn_expr = self._expand_alias(left)
                    labels = list(table.sample.index)
                return ast.copy_location(
                    ast.fix_missing_locations(
                        self._numeric_membership_test(dyn_expr, labels)
                    ),
                    origin,
                )

            def _direct_dataframe_column(self, node: ast.AST):
                if not (
                    isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name)
                    and node.value.id in frontend.refs
                ):
                    return None
                frame = frontend.refs[node.value.id]
                if not isinstance(frame, pd.DataFrame) or isinstance(node.slice, ast.Tuple):
                    return None
                return node.value.id, copy.deepcopy(node.slice)

            def _direct_series_index_extreme(self, node: ast.Call) -> ast.AST | None:
                if not (
                    isinstance(node.func, ast.Name) and node.func.id in {"min", "max"}
                    and len(node.args) == 1 and not node.keywords
                    and isinstance(node.args[0], ast.Attribute)
                    and node.args[0].attr == "index"
                    and isinstance(node.args[0].value, ast.Name)
                    and node.args[0].value.id in self.direct_dataframe_series_aliases
                ):
                    return None
                alias = node.args[0].value.id
                ref_name, _column = self.direct_dataframe_series_aliases[alias]
                frame = frontend.refs[ref_name]
                labels, _, _ = _safe_numeric_axis(frame.index)
                if not labels:
                    raise FrontendError(f"DataFrame Reference {ref_name} has an empty index")
                value = min(labels) if node.func.id == "min" else max(labels)
                return ast.copy_location(ast.Constant(int(value)), node)

            def visit_Assign(self, node: ast.Assign):
                if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                    name = node.targets[0].id
                    direct_series = self._direct_dataframe_column(node.value)
                    if direct_series is not None:
                        self.direct_dataframe_series_aliases[name] = direct_series
                        return None
                    table = self._table(node.value)
                    if table is not None:
                        self.table_aliases[name] = table
                        return None
                    series = self._series(node.value)
                    if series is not None:
                        self.series_aliases[name] = series
                        return None
                    row = self._row_proxy(node.value)
                    if row is not None:
                        self.row_aliases[name] = row
                        return None
                    enum_value = self._finite_enum(node.value)
                    if enum_value is not None:
                        # Keep the local in emitted numeric code, but replace the
                        # object/string Cell call with its proven integer code.
                        code_expr = self.visit(copy.deepcopy(enum_value.code_expr))
                        self.finite_enum_aliases[name] = FiniteEnumValue(
                            labels=enum_value.labels,
                            code_expr=ast.Name(name, ast.Load()),
                            source_name=enum_value.source_name,
                        )
                        return ast.copy_location(
                            ast.Assign(targets=copy.deepcopy(node.targets), value=code_expr), node
                        )
                out = self.generic_visit(node)
                if (
                    isinstance(out, ast.Assign) and len(out.targets) == 1
                    and isinstance(out.targets[0], ast.Name)
                    and self.store_counts.get(out.targets[0].id) == 1
                ):
                    # Single-store locals are safe proof aliases.  They are never
                    # substituted into emitted code by this pass; they exist only so
                    # range checks can see through patterns such as
                    # ``y = min(policy_year(t), int(scale.index.max()))``.
                    self.value_aliases[out.targets[0].id] = copy.deepcopy(out.value)
                return out

            def visit_Call(self, node: ast.Call):
                replacement = self._direct_series_index_extreme(node)
                if replacement is not None:
                    return replacement
                replacement = self._multiindex_level_extreme(node)
                if replacement is not None:
                    return replacement
                replacement = self._table_index_extreme(node)
                if replacement is not None:
                    return replacement
                return self.generic_visit(node)

            def visit_Compare(self, node: ast.Compare):
                if (
                    len(node.ops) == 1 and isinstance(node.ops[0], (ast.Eq, ast.NotEq))
                    and len(node.comparators) == 1
                ):
                    pairs = (
                        (node.left, node.comparators[0], False),
                        (node.comparators[0], node.left, True),
                    )
                    for enum_node, label_node, reversed_order in pairs:
                        enum_value = self._finite_enum(enum_node)
                        if enum_value is None or not (
                            isinstance(label_node, ast.Constant) and isinstance(label_node.value, str)
                        ):
                            continue
                        code = self._enum_label_code(enum_value, label_node.value)
                        if code is None:
                            value = isinstance(node.ops[0], ast.NotEq)
                            return ast.copy_location(ast.Constant(value), node)
                        left = self.visit(copy.deepcopy(enum_value.code_expr))
                        right = ast.Constant(code)
                        if reversed_order:
                            left, right = right, left
                        return ast.copy_location(
                            ast.Compare(left, [copy.deepcopy(node.ops[0])], [right]), node
                        )
                if len(node.ops) == 1 and isinstance(node.ops[0], (ast.In, ast.NotIn)) and len(node.comparators) == 1:
                    replacement = self._membership(node.left, node.comparators[0], node)
                    if replacement is not None:
                        if isinstance(node.ops[0], ast.NotIn):
                            replacement = ast.UnaryOp(ast.Not(), replacement)
                        return ast.copy_location(replacement, node)
                return self.generic_visit(node)

            def visit_IfExp(self, node: ast.IfExp):
                guard = self._inline_membership_guard(node.test)
                if guard is None:
                    return self.generic_visit(node)
                key_name, table_name, guarded_on_true = guard
                test = self.visit(copy.deepcopy(node.test))

                def visit_guarded(expr: ast.AST) -> ast.AST:
                    self.active_membership_guarded_rows.append((key_name, table_name))
                    try:
                        return self.visit(copy.deepcopy(expr))
                    finally:
                        self.active_membership_guarded_rows.pop()

                if guarded_on_true:
                    body = visit_guarded(node.body)
                    orelse = self.visit(copy.deepcopy(node.orelse))
                else:
                    body = self.visit(copy.deepcopy(node.body))
                    orelse = visit_guarded(node.orelse)
                return ast.copy_location(
                    ast.fix_missing_locations(
                        ast.IfExp(test=test, body=body, orelse=orelse)
                    ),
                    node,
                )

            def visit_Subscript(self, node: ast.Subscript):
                if (
                    isinstance(node.value, ast.Name)
                    and node.value.id in self.direct_dataframe_series_aliases
                ):
                    ref_name, column = self.direct_dataframe_series_aliases[node.value.id]
                    replacement = ast.Subscript(
                        value=ast.Subscript(
                            value=ast.Name(ref_name, ast.Load()),
                            slice=copy.deepcopy(column), ctx=ast.Load(),
                        ),
                        slice=self.visit(copy.deepcopy(node.slice)), ctx=ast.Load(),
                    )
                    return ast.copy_location(ast.fix_missing_locations(replacement), node)
                if isinstance(node.value, ast.Name) and node.value.id in self.series_aliases:
                    source = self.series_aliases[node.value.id]
                    key, start, step, labels = self._series_axis(source)
                    query = self._expand_alias(copy.deepcopy(node.slice))
                    lo, hi = self._numeric_bounds(query)
                    axis_lo, axis_hi = min(labels), max(labels)
                    if lo is None or hi is None or lo < axis_lo or hi > axis_hi:
                        correlated = frontend._correlated_int_domain_expr(
                            query, coordinate_name="t"
                        )
                        if correlated is not None:
                            corr_lo, corr_hi = float(correlated.lo), float(correlated.hi)
                            if corr_lo >= axis_lo and corr_hi <= axis_hi:
                                lo, hi = corr_lo, corr_hi
                    if lo is None or hi is None or lo < axis_lo or hi > axis_hi:
                        raise FrontendError(
                            "static-prefix Series lookup requires a source-proven in-domain "
                            f"numeric query {ast.unparse(query)!r}; "
                            f"proven bounds={lo!r},{hi!r}, axis={axis_lo!r},{axis_hi!r}"
                        )
                    mapped = _axis_index_expr(self.visit(copy.deepcopy(query)), start, step)
                    return ast.copy_location(
                        ast.Call(ast.Name("array_input", ast.Load()), [ast.Constant(key), mapped], []),
                        node,
                    )
                # Scalar lookup through a previously normalized row slice, e.g.
                # ``grid = table.loc[static_key]`` then ``grid.loc[x, column]``.
                if (
                    isinstance(node.value, ast.Attribute) and node.value.attr == "loc"
                    and isinstance(node.value.value, ast.Name)
                    and node.value.value.id in self.row_aliases
                    and isinstance(node.slice, ast.Tuple) and len(node.slice.elts) == 2
                ):
                    row = self.row_aliases[node.value.value.id]
                    nlevels = int(row.table.sample.index.nlevels) if isinstance(row.table.sample.index, pd.MultiIndex) else 1
                    prefix = self._expand_alias(copy.deepcopy(row.row_expr))
                    prefix_parts = list(prefix.elts) if isinstance(prefix, ast.Tuple) else [prefix]
                    # A local ``tbl = frame.loc[static_prefix]`` is merely a
                    # preparation-time view when that prefix fixes all but one row
                    # level.  Reconstitute the full row key and reuse the ordinary
                    # normalized lookup path instead of giving the local DataFrame
                    # view runtime semantics.
                    if len(prefix_parts) == nlevels - 1:
                        full_row = ast.Tuple(
                            elts=[*prefix_parts, copy.deepcopy(node.slice.elts[0])],
                            ctx=ast.Load(),
                        )
                        return self._lookup(row.table, full_row, node.slice.elts[1], node)
                loc = self._loc_parts(node)
                if loc is not None:
                    table, slice_node = loc
                    scalar = self._is_scalar_loc(table, slice_node)
                    if scalar is not None:
                        return self._lookup(table, scalar[0], scalar[1], node)
                if isinstance(node.value, ast.Name) and node.value.id in self.row_aliases:
                    row = self.row_aliases[node.value.id]
                    return self._lookup(row.table, row.row_expr, node.slice, node)
                return self.generic_visit(node)

        normalizer = Normalize()
        prepared_fn = normalizer._rewrite_interp_lookup_function(copy.deepcopy(fn))
        prepared_fn = normalizer._rewrite_step_lookup_function(prepared_fn)
        prepared_fn = normalizer._rewrite_interval_lookup_function(prepared_fn)
        out = normalizer.visit(prepared_fn)
        if out is None or not isinstance(out, ast.FunctionDef):
            raise FrontendError(f"external table normalization removed formula {fn.name}")
        out = ast.fix_missing_locations(out)

        removed = (
            set(normalizer.table_aliases) | set(normalizer.row_aliases)
            | set(normalizer.series_aliases)
        )
        residual = {
            node.id for node in ast.walk(out)
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load) and node.id in removed
        }
        if residual:
            raise FrontendError(
                f"{fn.name}: external DataFrame operation is outside the optimized table subset: "
                + ", ".join(sorted(residual))
            )

        loads = {
            node.id for node in ast.walk(out)
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
        }
        cleaned: list[ast.stmt] = []
        for st in out.body:
            if (
                isinstance(st, ast.Assign) and len(st.targets) == 1
                and isinstance(st.targets[0], ast.Name)
                and st.targets[0].id in normalizer.value_aliases
                and st.targets[0].id not in loads
            ):
                continue
            cleaned.append(st)
        out.body = cleaned

        # A helper may have been table-normalized before it was inlined into this
        # canonical formula.  In that case the final pass sees only ``table_input``
        # or ``__sparse_table_lookup__`` and would otherwise lose the per-formula
        # NormalizedOperator permission record.  Recover that record strictly from
        # the already-frozen numeric InputSpec semantics; no pandas operation is
        # reinterpreted here.
        if operator_uid is not None:
            prior = self._normalized_operators.get(operator_uid)
            existing_value_keys: set[str] = set()
            if prior is not None and prior.kind == "table_lookup":
                for name, payload in prior.static_inputs:
                    if not name.startswith("lookup_"):
                        continue
                    try:
                        existing_value_keys.add(str(dict(payload)["value_input_key"]))
                    except Exception:
                        pass
            for call in (
                node for node in ast.walk(out)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            ):
                value_key = None
                selector_args: list[ast.AST] = []
                if (
                    call.func.id == "table_input" and len(call.args) >= 1
                    and isinstance(call.args[0], ast.Constant)
                    and isinstance(call.args[0].value, str)
                ):
                    value_key = str(call.args[0].value)
                    selector_args = list(call.args[1:])
                elif (
                    call.func.id == "__sparse_table_lookup__" and len(call.args) >= 2
                    and isinstance(call.args[1], ast.Constant)
                    and isinstance(call.args[1].value, str)
                ):
                    value_key = str(call.args[1].value)
                    selector_args = list(call.args[2:])
                if value_key is None or value_key in existing_value_keys:
                    continue
                spec = registry.specs.get(value_key)
                sem = None if spec is None else spec.normalized_table
                if sem is None or sem.result_kind != "exact_nd":
                    continue
                binding = (
                    ("source_ref", sem.source_ref),
                    ("source_cell", sem.source_cell),
                    ("column", repr(sem.selected_column)),
                    ("layout", sem.layout),
                    ("value_input_key", value_key),
                    ("sparse_key_input", sem.sparse_key_input),
                    ("fixed_levels", tuple((int(k), repr(v)) for k, v in sem.fixed_row_labels)),
                    ("axes", tuple(
                        (
                            axis.level, axis.index_name, axis.selector_kind,
                            tuple(axis.labels), axis.axis_start, axis.axis_step,
                            axis.axis_input_key,
                        )
                        for axis in sem.dynamic_axes
                    )),
                )
                prior = self._normalized_operators.get(operator_uid)
                prior_bindings = prior.static_inputs if prior is not None and prior.kind == "table_lookup" else ()
                prior_dynamic = prior.dynamic_inputs if prior is not None and prior.kind == "table_lookup" else ()
                prior_provenance = prior.provenance if prior is not None and prior.kind == "table_lookup" else ()
                lookup_no = sum(1 for name, _ in prior_bindings if name.startswith("lookup_"))
                self._normalized_operators[operator_uid] = NormalizedOperator(
                    uid=operator_uid,
                    kind="table_lookup",
                    result_dtype=spec.dtype,
                    result_shape="scalar",
                    static_inputs=prior_bindings + ((f"lookup_{lookup_no}", binding),),
                    dynamic_inputs=prior_dynamic + tuple(ast.unparse(x) for x in selector_args),
                    provenance=tuple(dict.fromkeys((
                        *prior_provenance,
                        "normalized_table_input_recovered",
                        "numeric_selector_encoding",
                        sem.layout,
                        "runtime_domain_guard",
                    ))),
                    state_semantic="state_free",
                    python_supported=True,
                    cython_supported=True,
                )
                existing_value_keys.add(value_key)
        return ast.fix_missing_locations(out)

    def _normalize_reduction(self, fn: ast.FunctionDef) -> ReductionSpec | None:
        body=[x for x in fn.body if not (isinstance(x,ast.Expr) and isinstance(x.value,ast.Constant) and isinstance(x.value.value,str))]
        # Explicit accumulator loop, semantics preserved including initial value and range args.
        if len(body)==3 and isinstance(body[0],ast.Assign) and len(body[0].targets)==1 and isinstance(body[0].targets[0],ast.Name) and isinstance(body[1],ast.For) and isinstance(body[2],ast.Return):
            acc=body[0].targets[0].id; loop=body[1]; ret=body[2]
            if isinstance(ret.value,ast.Name) and ret.value.id==acc and isinstance(loop.target,ast.Name) and isinstance(loop.iter,ast.Call) and isinstance(loop.iter.func,ast.Name) and loop.iter.func.id=="range" and len(loop.body)==1 and isinstance(loop.body[0],ast.AugAssign) and isinstance(loop.body[0].target,ast.Name) and loop.body[0].target.id==acc and isinstance(loop.body[0].op,ast.Add):
                return ReductionSpec(copy.deepcopy(body[0].value),acc,loop.target.id,tuple(copy.deepcopy(loop.iter.args)),copy.deepcopy(loop.body[0].value),())

        if len(body)!=1 or not isinstance(body[0],ast.Return): return None
        ret=body[0].value
        if not (isinstance(ret,ast.Call) and isinstance(ret.func,ast.Name) and ret.func.id=="sum" and len(ret.args)==1 and not ret.keywords): return None
        arg=self._inline_vector_subscripts(ret.args[0])
        # sum(EXPR for x in range(...) if ...)
        gen=self._unwrap_generator(arg)
        if gen is not None:
            if len(gen.generators)!=1: return None
            c=gen.generators[0]
            if not (isinstance(c.target,ast.Name) and isinstance(c.iter,ast.Call) and isinstance(c.iter.func,ast.Name) and c.iter.func.id=="range"):
                return None
            return ReductionSpec(ast.Constant(0.0),"_acc",c.target.id,tuple(copy.deepcopy(c.iter.args)),copy.deepcopy(gen.elt),tuple(copy.deepcopy(c.ifs)))

        # Proven aligned vector product: sum(list(EXPR for x in range(...)) * VECTOR[:stop])
        if isinstance(arg,ast.BinOp) and isinstance(arg.op,ast.Mult):
            for gside,vside in ((arg.left,arg.right),(arg.right,arg.left)):
                gen=self._unwrap_generator(gside)
                if gen is None or len(gen.generators)!=1: continue
                c=gen.generators[0]
                if not (isinstance(c.target,ast.Name) and isinstance(c.iter,ast.Call) and isinstance(c.iter.func,ast.Name) and c.iter.func.id=="range"):
                    continue
                if not (isinstance(vside,ast.Subscript) and isinstance(vside.slice,ast.Slice)):
                    continue
                sl=vside.slice
                # Only transform when the slice is exactly the same 0:stop:1 domain as range(stop).
                if len(c.iter.args)!=1 or sl.lower is not None or sl.step is not None or sl.upper is None:
                    continue
                if ast.dump(c.iter.args[0],include_attributes=False)!=ast.dump(sl.upper,include_attributes=False):
                    continue
                vector_value=vside.value
                if not (isinstance(vector_value,ast.Call) and isinstance(vector_value.func,ast.Name) and not vector_value.args and vector_value.func.id in self.vector_elements):
                    continue
                var,_,elt=self.vector_elements[vector_value.func.id]
                elem=_Substitute({var:ast.Name(c.target.id,ast.Load())}).visit(copy.deepcopy(elt))
                elem=self._inline_vector_subscripts(elem)
                bodyexpr=ast.BinOp(copy.deepcopy(gen.elt),ast.Mult(),elem)
                return ReductionSpec(ast.Constant(0.0),"_acc",c.target.id,tuple(copy.deepcopy(c.iter.args)),ast.fix_missing_locations(bodyexpr),tuple(copy.deepcopy(c.ifs)))
        return None

    def _expr_lowerer(self, operator_uid: str | None = None):
        frontend=self
        registry=self.registry
        point_row=self.model_point_row
        point_key_input=[None]
        class Lower(ast.NodeTransformer):
            def __init__(self):
                super().__init__()
                self._single_assign_names: set[str] = set()
                self._space_alias_roots: dict[str, str] = {}
                self._space_bindings: dict[str, tuple[str, tuple[ast.AST, ...]]] = {}
                self._numeric_bindings: dict[str, ast.AST] = {}
                self._space_assignment_names: set[str] = set()

            @staticmethod
            def _subscript_elements(node: ast.Subscript) -> tuple[ast.AST, ...]:
                return tuple(node.slice.elts) if isinstance(node.slice, ast.Tuple) else (node.slice,)

            def prepare_function(self, fn: ast.FunctionDef) -> None:
                """Pre-prove nonescaping local binders for parameterized modelx Spaces."""
                assign_count: dict[str, int] = {}
                assignments: dict[str, ast.Assign] = {}
                parents: dict[int, ast.AST] = {}

                def target_names(target: ast.AST) -> tuple[str, ...]:
                    if isinstance(target, ast.Name):
                        return (target.id,)
                    if isinstance(target, (ast.Tuple, ast.List)):
                        out: list[str] = []
                        for elt in target.elts:
                            out.extend(target_names(elt))
                        return tuple(out)
                    return ()

                for parent in ast.walk(fn):
                    for child in ast.iter_child_nodes(parent):
                        parents[id(child)] = parent
                    if isinstance(parent, ast.Assign):
                        for target in parent.targets:
                            for name in target_names(target):
                                assign_count[name] = assign_count.get(name, 0) + 1
                        if len(parent.targets) == 1 and isinstance(parent.targets[0], ast.Name):
                            assignments[parent.targets[0].id] = parent
                    elif isinstance(parent, ast.AnnAssign):
                        for name in target_names(parent.target):
                            assign_count[name] = assign_count.get(name, 0) + 1
                self._single_assign_names = {name for name, count in assign_count.items() if count == 1}

                for name in sorted(self._single_assign_names):
                    st = assignments.get(name)
                    if st is None or not (
                        isinstance(st.value, ast.Subscript)
                        and isinstance(st.value.value, ast.Name)
                    ):
                        continue
                    root_name = st.value.value.id
                    if root_name not in frontend.refs:
                        continue
                    try:
                        probe_key = frontend.run_keys[0] if frontend.run_keys else None
                        frontend._context_parameterized_space_for_key(root_name, probe_key)
                    except FrontendError:
                        continue

                    loads = [
                        node for node in ast.walk(fn)
                        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load) and node.id == name
                    ]
                    if not loads:
                        continue
                    admitted = True
                    for load in loads:
                        attr = parents.get(id(load))
                        call = parents.get(id(attr)) if isinstance(attr, ast.Attribute) else None
                        if not (
                            isinstance(attr, ast.Attribute)
                            and attr.value is load
                            and isinstance(call, ast.Call)
                            and call.func is attr
                        ):
                            admitted = False
                            break
                    if admitted:
                        self._space_alias_roots[name] = root_name

            def _expand_numeric_expr(self, node: ast.AST, seen: frozenset[str] = frozenset()) -> ast.AST:
                outer = self
                class Expand(ast.NodeTransformer):
                    def visit_Name(self, name: ast.Name):
                        if (
                            isinstance(name.ctx, ast.Load)
                            and name.id in outer._numeric_bindings
                            and name.id not in seen
                        ):
                            return outer._expand_numeric_expr(
                                copy.deepcopy(outer._numeric_bindings[name.id]), seen | {name.id}
                            )
                        return copy.deepcopy(name)
                return ast.fix_missing_locations(Expand().visit(copy.deepcopy(node)))

            def cleanup_function(self, fn: ast.FunctionDef) -> ast.FunctionDef:
                """Erase compile-time-only Space binders only after all alias loads vanish."""
                loads = {
                    node.id for node in ast.walk(fn)
                    if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
                }
                removable = self._space_assignment_names - loads
                if not removable:
                    return fn

                def clean(stmts: list[ast.stmt]) -> list[ast.stmt]:
                    out: list[ast.stmt] = []
                    for st in stmts:
                        if (
                            isinstance(st, ast.Assign) and len(st.targets) == 1
                            and isinstance(st.targets[0], ast.Name)
                            and st.targets[0].id in removable
                        ):
                            continue
                        if isinstance(st, ast.If):
                            st = copy.deepcopy(st)
                            st.body = clean(list(st.body))
                            st.orelse = clean(list(st.orelse))
                        out.append(st)
                    return out

                fn = copy.deepcopy(fn)
                fn.body = clean(list(fn.body))
                return ast.fix_missing_locations(fn)

            def visit_Name(self,n):
                if isinstance(n.ctx,ast.Load):
                    if n.id in frontend.space_params:
                        pos=frontend.space_params.index(n.id)
                        key=registry.point_coordinate(pos)
                        return ast.copy_location(
                            ast.Call(ast.Name("point_input",ast.Load()),[ast.Constant(key)],[]),n
                        )
                    if n.id in frontend.refs:
                        v=frontend.refs[n.id]
                        if isinstance(v,(int,float,np.integer,np.floating,bool,np.bool_)):
                            key=registry.scalar_ref(n.id,v)
                            return ast.copy_location(ast.Call(ast.Name("global_input",ast.Load()),[ast.Constant(key)],[]),n)
                return n

            def visit_Attribute(self, n):
                if (
                    isinstance(n.ctx, ast.Load)
                    and isinstance(n.value, ast.Name)
                    and n.value.id in frontend.refs
                ):
                    try:
                        key = registry.context_static_attribute(n.value.id, n.attr)
                    except FrontendError:
                        pass
                    else:
                        return ast.copy_location(
                            ast.Call(ast.Name("global_input", ast.Load()), [ast.Constant(key)], []), n
                        )
                return self.generic_visit(n)

            def visit_Assign(self, n):
                n = self.generic_visit(n)
                if len(n.targets) != 1:
                    return n
                target_node = n.targets[0]
                if isinstance(target_node, (ast.Tuple, ast.List)) and isinstance(n.value, (ast.Tuple, ast.List)):
                    def bind_pattern(target: ast.AST, value: ast.AST) -> None:
                        if isinstance(target, ast.Name):
                            if target.id in self._single_assign_names:
                                self._numeric_bindings[target.id] = copy.deepcopy(value)
                            return
                        if (
                            isinstance(target, (ast.Tuple, ast.List))
                            and isinstance(value, (ast.Tuple, ast.List))
                            and len(target.elts) == len(value.elts)
                        ):
                            for left, right in zip(target.elts, value.elts):
                                bind_pattern(left, right)
                    bind_pattern(target_node, n.value)
                    return n
                if not isinstance(target_node, ast.Name):
                    return n
                target = target_node.id
                if target not in self._single_assign_names:
                    return n
                if (
                    target in self._space_alias_roots
                    and isinstance(n.value, ast.Subscript)
                    and isinstance(n.value.value, ast.Name)
                    and n.value.value.id == self._space_alias_roots[target]
                ):
                    selectors = tuple(
                        self._expand_numeric_expr(part)
                        for part in self._subscript_elements(n.value)
                    )
                    self._space_bindings[target] = (n.value.value.id, selectors)
                    self._space_assignment_names.add(target)
                    return n
                self._numeric_bindings[target] = copy.deepcopy(n.value)
                return n

            def _external(self,call):
                if not (isinstance(call.func,ast.Attribute) and isinstance(call.func.value,ast.Name) and not call.args and not call.keywords): return None
                rn=call.func.value.id
                obj=frontend.refs.get(rn)
                if obj is None or not hasattr(obj,"cells") or call.func.attr not in obj.cells: return None
                return rn,call.func.attr,obj.cells[call.func.attr]

            def _context_accessor(self, call):
                """Return a concrete modelx Cells-backed attribute call if provable.

                This deliberately accepts only direct ``root.member(...)`` calls where
                ``root`` is a frozen model reference.  Local rich-object methods remain
                a separate operator problem unless another typed lowering proves them.
                """
                if not (
                    isinstance(call, ast.Call)
                    and isinstance(call.func, ast.Attribute)
                    and isinstance(call.func.value, ast.Name)
                    and not call.keywords
                ):
                    return None
                rn = call.func.value.id
                if rn not in frontend.refs:
                    return None
                try:
                    frontend._context_cell_for_key(rn, call.func.attr, None)
                except FrontendError:
                    return None
                return rn, call.func.attr

            def _coordinate_name_and_domain(self):
                if operator_uid is None:
                    return None
                tr = frontend.variant_trace_by_uid.get(operator_uid)
                if tr is None or tr.key.time_pos is None:
                    return None
                pos = int(tr.key.time_pos)
                if pos < 0 or pos >= len(tr.schema.parameters):
                    return None
                domain = (
                    frontend.specialized_coordinate_domains.get(operator_uid)
                    or frontend.coordinate_domains.get(operator_uid)
                )
                if domain is None:
                    return None
                return tr.schema.parameters[pos], domain

            def _selected_space_method_call(
                self, call: ast.Call
            ) -> tuple[str, tuple[ast.AST, ...], str, tuple[ast.AST, ...]] | None:
                """Describe one proven selected-Space Cells call without selecting it at runtime.

                V02386/V02387 originally admitted only the local-alias surface::

                    obj = root[selectors]
                    obj.member(args)

                V02389 admits the semantically identical direct receiver surface::

                    root[selectors].member(args)

                Both shapes return the same root/selectors/member/arguments descriptor
                and therefore share InputRegistry proof, memoization, materialization,
                rebinding and domain guards.  This is intentionally not a generic
                attribute/subscript interpreter.
                """
                if not (
                    isinstance(call.func, ast.Attribute)
                    and not call.keywords
                ):
                    return None

                def lowered(node: ast.AST) -> ast.AST:
                    # Direct receivers are seen before ``generic_visit`` would lower
                    # their selector/argument children (for example an owning Space
                    # parameter such as ``ScenID``).  Lower just those bounded numeric
                    # expressions, then expand single-assignment numeric aliases.
                    visited = self.visit(copy.deepcopy(node))
                    if visited is None or isinstance(visited, list):
                        return copy.deepcopy(node)
                    return self._expand_numeric_expr(visited)

                receiver = call.func.value
                if isinstance(receiver, ast.Name) and receiver.id in self._space_bindings:
                    root_name, selectors = self._space_bindings[receiver.id]
                    return (
                        root_name,
                        tuple(lowered(selector) for selector in selectors),
                        call.func.attr,
                        tuple(lowered(arg) for arg in call.args),
                    )

                if (
                    isinstance(receiver, ast.Subscript)
                    and isinstance(receiver.value, ast.Name)
                    and receiver.value.id in frontend.refs
                ):
                    root_name = receiver.value.id
                    # Structural precheck only.  Full selector arity, ItemSpace and
                    # concrete Cells-member proof remains owned by InputRegistry.
                    try:
                        probe_key = frontend.run_keys[0] if frontend.run_keys else None
                        frontend._context_parameterized_space_for_key(root_name, probe_key)
                    except FrontendError:
                        return None
                    selectors = tuple(
                        lowered(part) for part in self._subscript_elements(receiver)
                    )
                    return (
                        root_name,
                        selectors,
                        call.func.attr,
                        tuple(lowered(arg) for arg in call.args),
                    )
                return None

            def _bounded_context_argument(
                self, node: ast.AST, coordinate_name: str | None = None
            ) -> ast.AST:
                """Lower one context-accessor argument into the bounded numeric ABI subset.

                Ordinary nested input/context reads are lowered first.  If that is
                still not representable, V02390 may hygienically substitute exactly
                one existing pure single-return source/variant helper and retry.
                The substituted result must itself reduce completely to the bounded
                ABI-expression subset; arbitrary helper execution never becomes part
                of preparation or generated runtime.
                """
                def lowered(expr: ast.AST) -> ast.AST:
                    visited = self.visit(copy.deepcopy(expr))
                    if visited is None or isinstance(visited, list):
                        return copy.deepcopy(expr)
                    return self._expand_numeric_expr(visited)

                direct = lowered(node)
                if registry.bound_numeric_expr_supported(direct, coordinate_name):
                    return direct

                if isinstance(direct, ast.Call) and isinstance(direct.func, ast.Name):
                    expanded = frontend._expand_pure_single_return_call(direct)
                    if expanded is not None:
                        expr, _helper_token = expanded
                        candidate = lowered(expr)
                        if registry.bound_numeric_expr_supported(candidate, coordinate_name):
                            return candidate
                return direct

            def visit_Call(self,n):
                selected = self._selected_space_method_call(n)
                if selected is not None:
                    root_name, selectors, member_name, args = selected
                    try:
                        key = registry.parameterized_space_method_point(
                            root_name, selectors, member_name, args
                        )
                    except FrontendError:
                        pass
                    else:
                        return ast.copy_location(
                            ast.Call(ast.Name("point_input", ast.Load()), [ast.Constant(key)], []), n
                        )

                    # V02387: the same selected-ItemSpace/Cells proof may be
                    # materialized over exactly one source-proven coordinate axis.
                    # The point-only path above remains first so point scalars do not
                    # silently become two-dimensional tables.
                    coord = self._coordinate_name_and_domain()
                    if coord is not None and operator_uid is not None:
                        coordinate_name, domain = coord
                        if (
                            all(
                                registry.bound_numeric_expr_supported(arg, coordinate_name)
                                for arg in args
                            )
                            and any(
                                registry.bound_numeric_expr_uses_coordinate(arg, coordinate_name)
                                for arg in args
                            )
                        ):
                            try:
                                table_key, ordinal_key = (
                                    registry.parameterized_space_method_coordinate(
                                        root_name,
                                        selectors,
                                        member_name,
                                        args,
                                        coordinate_name,
                                        int(domain.lo),
                                        int(domain.hi),
                                        operator_uid,
                                        1,
                                    )
                                )
                            except FrontendError:
                                pass
                            else:
                                column = _axis_index_expr(
                                    ast.Name(coordinate_name, ast.Load()), int(domain.lo), 1
                                )
                                return ast.copy_location(
                                    ast.Call(
                                        ast.Name("table_input", ast.Load()),
                                        [
                                            ast.Constant(table_key),
                                            ast.Call(
                                                ast.Name("point_input", ast.Load()),
                                                [ast.Constant(ordinal_key)],
                                                [],
                                            ),
                                            column,
                                        ],
                                        [],
                                    ),
                                    n,
                                )

                ext=self._external(n)
                if ext:
                    rn,cn,cell=ext
                    key=registry.external_scalar(rn,cn,cell)
                    intrinsic = "point_input" if registry.specs[key].scope == "point" else "global_input"
                    return ast.copy_location(
                        ast.Call(ast.Name(intrinsic,ast.Load()),[ast.Constant(key)],[]),n
                    )

                ctx = self._context_accessor(n)
                if ctx:
                    rn, cn = ctx
                    coord = self._coordinate_name_and_domain()
                    if coord is not None and operator_uid is not None:
                        coordinate_name, domain = coord
                        coordinate_args = tuple(
                            self._bounded_context_argument(arg, coordinate_name) for arg in n.args
                        )
                        if (
                            coordinate_args
                            and all(
                                registry.bound_numeric_expr_supported(arg, coordinate_name)
                                for arg in coordinate_args
                            )
                            and any(
                                registry.bound_numeric_expr_uses_coordinate(arg, coordinate_name)
                                for arg in coordinate_args
                            )
                        ):
                            try:
                                table_key, ordinal_key = registry.context_coordinate_accessor(
                                    rn, cn, coordinate_args, coordinate_name,
                                    int(domain.lo), int(domain.hi), operator_uid, 1,
                                )
                            except FrontendError:
                                pass
                            else:
                                column = _axis_index_expr(
                                    ast.Name(coordinate_name, ast.Load()), int(domain.lo), 1
                                )
                                return ast.copy_location(
                                    ast.Call(
                                        ast.Name("table_input", ast.Load()),
                                        [
                                            ast.Constant(table_key),
                                            ast.Call(
                                                ast.Name("point_input", ast.Load()),
                                                [ast.Constant(ordinal_key)], [],
                                            ),
                                            column,
                                        ],
                                        [],
                                    ),
                                    n,
                                )

                    point_args = tuple(
                        self._bounded_context_argument(arg, None) for arg in n.args
                    )
                    if all(registry.bound_numeric_expr_supported(arg) for arg in point_args):
                        try:
                            key = registry.context_scalar_accessor(rn, cn, point_args)
                        except FrontendError:
                            pass
                        else:
                            intrinsic = (
                                "global_input"
                                if registry.specs[key].scope == "global"
                                else "point_input"
                            )
                            return ast.copy_location(
                                ast.Call(ast.Name(intrinsic, ast.Load()), [ast.Constant(key)], []),
                                n,
                            )
                return self.generic_visit(n)

            def _point_enum_selector(self, node: ast.AST):
                """Return (labels, numeric-code-expr) for a direct point-row string Cell.

                This is deliberately the same structural proof used by normalized
                external-table dispatch: the source helper must consist solely of
                ``return model_point()["field"]`` and the exact frozen point-row
                domain must contain a small finite set of strings.
                """
                if not (
                    isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and not node.args and not node.keywords and frontend.model_point_row is not None
                ):
                    return None
                call_name = node.func.id
                tr = frontend.variant_trace_by_uid.get(call_name)
                source_name = tr.schema.name if tr is not None else (
                    call_name if call_name in frontend.base_funcs else None
                )
                if source_name is None:
                    return None
                original = frontend.base_funcs.get(source_name)
                if original is None:
                    return None
                direct = _strip_docstring(copy.deepcopy(original))
                if not (
                    isinstance(direct, ast.FunctionDef)
                    and not direct.args.posonlyargs and not direct.args.args
                    and not direct.args.kwonlyargs and direct.args.vararg is None
                    and direct.args.kwarg is None and len(direct.body) == 1
                    and isinstance(direct.body[0], ast.Return)
                    and isinstance(direct.body[0].value, ast.Subscript)
                    and isinstance(direct.body[0].value.value, ast.Call)
                    and isinstance(direct.body[0].value.value.func, ast.Name)
                    and direct.body[0].value.value.func.id == frontend.model_point_row.cell_name
                    and not direct.body[0].value.value.args
                    and not direct.body[0].value.value.keywords
                    and isinstance(direct.body[0].value.slice, ast.Constant)
                    and isinstance(direct.body[0].value.slice.value, str)
                ):
                    return None
                field = str(direct.body[0].value.slice.value)
                frame = frontend.model_point_row.provider()
                if not isinstance(frame, pd.DataFrame) or field not in frame.columns:
                    return None
                values = frame[field].tolist()
                if not values or not all(
                    isinstance(value, str) or bool(pd.isna(value)) for value in values
                ):
                    return None
                labels = tuple(dict.fromkeys(value for value in values if isinstance(value, str)))
                if not labels or len(labels) > 16:
                    return None
                key = registry.point_field(frontend.model_point_row, field, enum_labels=labels)
                point_code = ast.Call(
                    ast.Name("point_input", ast.Load()), [ast.Constant(key)], []
                )
                has_other = any(not isinstance(value, str) for value in values)
                if has_other:
                    point_code = ast.Call(
                        ast.Name("__exact_axis_code__", ast.Load()),
                        [point_code, ast.Constant(0), ast.Constant(1), ast.Constant(len(labels))], [],
                    )
                return labels, point_code

            def _exact_dataframe_axis(self, expr: ast.AST, labels: tuple[Any, ...], level: int):
                ok, value = frontend._proven_static_expr(expr)
                if ok:
                    if value not in labels:
                        raise FrontendError(
                            f"DataFrame exact lookup axis {level} has no label {value!r}"
                        )
                    return None, ast.Constant(0), {level: value}

                enum = self._point_enum_selector(expr)
                if enum is not None:
                    enum_labels, code = enum
                    if any(label not in labels for label in enum_labels):
                        raise FrontendError(
                            f"DataFrame exact lookup categorical axis {level} exceeds frozen label domain"
                        )
                    axis = NormalizedTableAxis(
                        level=level, index_name=None if level == 0 else "__columns__",
                        selector_kind="finite_categorical", labels=tuple(enum_labels),
                    )
                    return axis, code, {}

                try:
                    numeric, start, step = _safe_numeric_axis(labels)
                except FrontendError as exc:
                    raise FrontendError(
                        f"DataFrame exact lookup dynamic axis {level} is neither a finite "
                        f"categorical point selector nor a regular numeric axis: {exc}"
                    ) from exc
                numeric_to_source = sorted(zip(numeric, labels), key=lambda item: item[0])
                source_labels = tuple(label for _numeric, label in numeric_to_source)
                visited = self.visit(copy.deepcopy(expr))
                axis = NormalizedTableAxis(
                    level=level, index_name=None if level == 0 else "__columns__",
                    selector_kind="numeric_exact", labels=source_labels,
                    axis_start=int(start), axis_step=int(step),
                )
                code = ast.Call(
                    ast.Name("__exact_axis_code__", ast.Load()),
                    [visited, ast.Constant(int(start)), ast.Constant(int(step)), ast.Constant(len(source_labels))], []
                )
                return axis, code, {}

            def visit_Subscript(self,n):
                # A zero-argument local Cell returning a dense numeric two-level
                # Series is an explicit state-free indexed input.  The object never
                # crosses the numeric backend boundary.
                if (
                    isinstance(n.value, ast.Call)
                    and isinstance(n.value.func, ast.Name)
                    and not n.value.args and not n.value.keywords
                    and n.value.func.id in frontend.variant_trace_by_uid
                    and isinstance(n.slice, ast.Tuple) and len(n.slice.elts) == 2
                ):
                    trace = frontend.variant_trace_by_uid[n.value.func.id]
                    if trace.dtype == "object" and not trace.schema.parameters:
                        cell_name = trace.schema.name
                        cell = frontend.space.cells.get(cell_name)
                        if cell is not None:
                            try:
                                key = registry.local_cell_multiindex_series(cell_name, cell)
                            except FrontendError:
                                pass
                            else:
                                r0, rs, c0, cs = frontend.multiindex_axes[key]
                                row_expr = _axis_index_expr(self.visit(copy.deepcopy(n.slice.elts[0])), r0, rs)
                                col_expr = _axis_index_expr(self.visit(copy.deepcopy(n.slice.elts[1])), c0, cs)
                                if operator_uid is not None:
                                    frontend._normalized_operators[operator_uid] = NormalizedOperator(
                                        uid=operator_uid,
                                        kind="indexed_input",
                                        result_dtype="float64",
                                        result_shape="scalar",
                                        static_inputs=(("input_key", key), ("source_cell", cell_name)),
                                        dynamic_inputs=(ast.unparse(n.slice.elts[0]), ast.unparse(n.slice.elts[1])),
                                        provenance=(
                                            "local_zero_arg_object_cell",
                                            "dense_numeric_two_level_multiindex",
                                            "runtime_domain_guard",
                                        ),
                                        state_semantic="state_free",
                                        python_supported=True,
                                        cython_supported=True,
                                    )
                                return ast.copy_location(
                                    ast.Call(ast.Name("table_input",ast.Load()),[ast.Constant(key),row_expr,col_expr],[]),n
                                )

                # DataFrame point-row Cells followed by a column selection.  The
                # call may already have been rewritten to its canonical variant UID;
                # match by trace schema as well as source Cell spelling.
                point_row_call = False
                if point_row and isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Name) and not n.value.args and not n.value.keywords:
                    called = n.value.func.id
                    if called == point_row.cell_name:
                        point_row_call = True
                    else:
                        trace = frontend.variant_trace_by_uid.get(called)
                        point_row_call = bool(trace is not None and trace.schema.name == point_row.cell_name)
                if point_row_call:
                    ok, field = frontend._proven_static_expr(n.slice)
                    if ok and isinstance(field, str):
                        key=registry.point_field(point_row,field)
                        return ast.copy_location(ast.Call(ast.Name("point_input",ast.Load()),[ast.Constant(key)],[]),n)

                if isinstance(n.value,ast.Call):
                    ext=self._external(n.value)
                    if ext:
                        rn,cn,cell=ext
                        if isinstance(n.slice,ast.Name) and n.slice.id in frontend.space_params:
                            pos = frontend.space_params.index(n.slice.id)
                            key=registry.external_array(rn,cn,cell,pos)
                            return ast.copy_location(ast.Call(ast.Name("point_input",ast.Load()),[ast.Constant(key)],[]),n)
                        key=registry.external_array(rn,cn,cell,None)
                        if isinstance(n.slice,ast.Tuple) and len(n.slice.elts)==2:
                            return ast.copy_location(ast.Call(ast.Name("table_input",ast.Load()),[ast.Constant(key),self.visit(n.slice.elts[0]),self.visit(n.slice.elts[1])],[]),n)
                        return ast.copy_location(ast.Call(ast.Name("array_input",ast.Load()),[ast.Constant(key),self.visit(n.slice)],[]),n)

                    # General model-bound Cells accessors that escaped the historical
                    # zero-argument ``obj.cells`` path.  The bounded first shape is a
                    # numeric vector selected by one exact ItemSpace coordinate; this
                    # covers Cells aliases and finite/static call arguments without
                    # introducing a runtime context proxy.
                    ctx = self._context_accessor(n.value)
                    if (
                        ctx is not None
                        and isinstance(n.slice, ast.Name)
                        and n.slice.id in frontend.space_params
                    ):
                        rn, cn = ctx
                        pos = frontend.space_params.index(n.slice.id)
                        try:
                            key = registry.context_point_accessor(
                                rn, cn, n.value.args, pos
                            )
                        except FrontendError:
                            pass
                        else:
                            return ast.copy_location(
                                ast.Call(
                                    ast.Name("point_input", ast.Load()),
                                    [ast.Constant(key)], [],
                                ),
                                n,
                            )

                # Exact DataFrame column-then-row: ref[col][row].  Handle the
                # outer shape before recursively visiting the inner subscript; the
                # latter is intentionally not a complete scalar lookup by itself.
                if isinstance(n.value,ast.Subscript) and isinstance(n.value.value,ast.Name):
                    rn=n.value.value.id; v=frontend.refs.get(rn)
                    if isinstance(v,pd.DataFrame):
                        col=n.value.slice
                        if isinstance(col,ast.Call) and isinstance(col.func,ast.Name) and col.func.id=="str" and len(col.args)==1 and not col.keywords:
                            col=col.args[0]
                        # Preserve the established affine lowering when both source
                        # axes are numeric (including numeric-string labels).  The
                        # richer exact N-D path is reserved for genuinely labelled
                        # categorical axes, avoiding needless source-shape churn in
                        # existing native controls.
                        try:
                            key,rm,cm=registry.global_dataframe(rn,v)
                        except FrontendError:
                            row_labels=tuple(v.index.tolist()); col_labels=tuple(v.columns.tolist())
                            row_axis,row_code,row_fixed=self._exact_dataframe_axis(n.slice,row_labels,0)
                            col_axis,col_code,col_fixed=self._exact_dataframe_axis(col,col_labels,1)
                            axes=tuple(x for x in (row_axis,col_axis) if x is not None)
                            fixed={**row_fixed,**col_fixed}
                            key=registry.global_dataframe_exact_nd(
                                rn,v,fixed_axes=fixed,dynamic_axes=axes,
                            )
                            return ast.copy_location(
                                ast.Call(ast.Name("table_input",ast.Load()),[ast.Constant(key),row_code,col_code],[]),n
                            )
                        else:
                            return ast.copy_location(
                                ast.Call(
                                    ast.Name("table_input",ast.Load()),
                                    [ast.Constant(key),rm(self.visit(n.slice)),cm(self.visit(col))],[],
                                ),n
                            )

                # Direct Series/DataFrame reference indexing.
                if isinstance(n.value,ast.Name) and n.value.id in frontend.refs:
                    rn=n.value.id; v=frontend.refs[rn]
                    if isinstance(v,pd.Series):
                        if isinstance(v.index,pd.MultiIndex):
                            if not (isinstance(n.slice,ast.Tuple) and len(n.slice.elts)==2):
                                raise FrontendError(f"MultiIndex Reference {rn} requires a two-element key")
                            key,_=registry.global_multiindex_series(rn,v)
                            r0,rs,c0,cs=frontend.multiindex_axes[key]
                            r=_axis_index_expr(self.visit(n.slice.elts[0]),r0,rs); c=_axis_index_expr(self.visit(n.slice.elts[1]),c0,cs)
                            return ast.copy_location(ast.Call(ast.Name("table_input",ast.Load()),[ast.Constant(key),r,c],[]),n)
                        key,mapidx=registry.global_series(rn,v)
                        return ast.copy_location(ast.Call(ast.Name("array_input",ast.Load()),[ast.Constant(key),mapidx(self.visit(n.slice))],[]),n)
                    if isinstance(v,pd.DataFrame):
                        if not (isinstance(n.slice,ast.Tuple) and len(n.slice.elts)==2):
                            raise FrontendError(f"DataFrame Reference {rn} direct indexing requires two indices")
                        key,rm,cm=registry.global_dataframe(rn,v)
                        return ast.copy_location(ast.Call(ast.Name("table_input",ast.Load()),[ast.Constant(key),rm(self.visit(n.slice.elts[0])),cm(self.visit(n.slice.elts[1]))],[]),n)

                return self.generic_visit(n)
        return Lower()

    def _build_canonical(self) -> CanonicalModel:
        canonical: dict[str,CanonicalVariant]={}
        diagnostics=list(self.trace.diagnostics)
        diagnostics.extend(d for d in self.ir.diagnostics if d not in diagnostics)
        diagnostics.extend(d for d in self.coordinate_domain_notes if d not in diagnostics)
        # Explicit regional fallback boundaries are identities supplied by the
        # caller, not semantic names.  They are marshaled as one scalar per model
        # point and may later be overridden by a callback/orchestrator.
        for name in sorted(self.fallback_cells):
            traces=[tr for tr in self.selected_trace_variants.values() if tr.schema.name == name]
            if len(traces) != 1:
                raise FrontendError(
                    f"regional fallback Cell {name!r} must resolve to one observed zero-argument variant"
                )
            self.fallback_input_by_name[name] = self.registry.regional_fallback_point(name, traces[0].dtype)

        # v0.6 executable roles are derived from trace-coordinate evidence and the
        # statically normalized formula itself.  Legacy planner kind/stage values
        # remain only as compatibility/audit metadata.
        coordinate_uids = {
            tr.uid for tr in self.variant_trace_by_uid.values()
            if tr.key.time_pos is not None
        }
        next_guard_code = 1

        def lower_into_canonical(
            uid: str, tr, fn: ast.FunctionDef, *, forced_role: str | None = None,
            time_param_source: str | None = None,
        ) -> None:
            nonlocal next_guard_code
            lower = self._expr_lowerer(uid)
            fn = self._normalize_external_tables(fn, operator_uid=uid)
            lower.prepare_function(fn)
            guards: tuple[GuardSpec, ...] = ()

            if forced_role is not None:
                role = forced_role
            elif tr.schema.name in self.vector_elements and tr.dtype == "object":
                role = "vector"
            elif tr.key.time_pos is not None:
                role = "coordinate"
            else:
                role = "scalar"

            reduction = None
            if role == "scalar":
                reduction = self._normalize_reduction(fn)
                if reduction is not None:
                    role = "reduction"

            if tr.dtype == "object" and role not in ("vector",):
                if forced_role is not None:
                    raise FrontendError(
                        f"fixed/native scalar specialization of object Cell {tr.schema.name!r} is unsupported"
                    )
                # Ordinary object helper Cells are consumed by input/table lowering
                # and do not enter the numeric kernel, matching the dev15 path.
                return

            if role == "reduction":
                reduction = ReductionSpec(
                    lower.visit(copy.deepcopy(reduction.init)), reduction.target, reduction.loop_var,
                    tuple(lower.visit(copy.deepcopy(a)) for a in reduction.range_args),
                    lower.visit(copy.deepcopy(reduction.body_expr)),
                    tuple(lower.visit(copy.deepcopy(f)) for f in reduction.filters),
                )
                ast.fix_missing_locations(reduction.body_expr)
            elif role != "vector":
                fn.body = [lower.visit(copy.deepcopy(x)) for x in fn.body]
                fn = ast.fix_missing_locations(fn)
                fn = lower.cleanup_function(fn)
                fn = self._normalize_scalar_intrinsics(fn)
                fn = self._normalize_simple_local_syntax(fn)
                try:
                    fn, guards, next_guard_code = normalize_formula_guards(
                        fn, uid=uid, next_code=next_guard_code
                    )
                    validate_formula_control_flow(fn)
                except (SemanticSafetyError, ProgramSemanticError) as exc:
                    raise FrontendError(str(exc)) from exc

            canonical[uid] = CanonicalVariant(
                uid=uid, source_name=tr.schema.name, source_fullname=tr.schema.fullname,
                dtype=tr.dtype if tr.dtype in ("int64", "bool") else "float64",
                role=role, function=fn, reduction=reduction,
                time_param_source=time_param_source,
                # Output arguments are invocation geometry, not helper-variant
                # axes.  _specialize_function already bound them into the root
                # formula, so the canonical root is a zero-argument scalar/reduction.
                aux_values=(() if uid == output_uid else tr.key.aux_values),
                guards=guards,
            )

        # Source specialization is demand-driven from the scalar output.  Earlier
        # releases specialized every observed trace variant and pruned reachability
        # afterwards.  Once parameterized pure helpers are erased by inlining, that
        # eagerly constructs large populations of helper variants that no generated
        # program can call (RILA observes many Black-Scholes argument combinations).
        # Specializing only dependencies discovered from already-specialized source
        # ASTs is semantically equivalent to the old pre-reachability filter, while
        # preserving the important phase-order rule: static topology proofs run before
        # an unsupported dead helper body is ever handed to table/backend lowering.
        output_matches = [
            uid for uid, tr in self.variant_trace_by_uid.items()
            if tr.schema.name == self.output
            and tr.key.time_pos is None
            and tuple(tr.key.aux_values)==tuple(self.output_invocation.argument_values)
            and tr.schema.name in self.base_funcs
            and tr.schema.name not in self.fallback_cells
            and tr.schema.name in self.compiled_source_names
        ]
        if len(output_matches) != 1:
            raise FrontendError(
                f"could not uniquely identify scalar output Cell {self.output!r} before lowering"
            )
        output_uid = output_matches[0]

        specialized: dict[str, tuple[Any, ast.FunctionDef, str | None, str | None]] = {}
        pending: list[str] = [output_uid]
        queued: set[str] = {output_uid}

        def enqueue_dependencies(fn: ast.FunctionDef) -> None:
            # _specialize_function has already canonicalized ordinary Cells calls to
            # observed variant UIDs and has registered any synthetic fixed-coordinate
            # calls.  Pure scalar helpers disappeared into local statements, so their
            # standalone observed variants are deliberately absent from this queue.
            for child in ast.walk(fn):
                if not (isinstance(child, ast.Call) and isinstance(child.func, ast.Name)):
                    continue
                dep = child.func.id
                if dep in self.variant_trace_by_uid and dep not in queued:
                    tr = self.variant_trace_by_uid[dep]
                    if (
                        tr.schema.name in self.base_funcs
                        and tr.schema.name not in self.fallback_cells
                        and tr.schema.name in self.compiled_source_names
                    ):
                        queued.add(dep)
                        pending.append(dep)
                elif dep in self._fixed_coordinate_requests and dep not in queued:
                    queued.add(dep)
                    pending.append(dep)

        while pending:
            uid = pending.pop()
            if uid in specialized:
                continue
            if uid in self._fixed_coordinate_requests:
                base_uid, coordinate = self._fixed_coordinate_requests[uid]
                tr = self.variant_trace_by_uid[base_uid]
                fn = self._specialize_function(
                    base_uid, fixed_time=int(coordinate), synthetic_uid=uid
                )
                if fn is None:
                    raise FrontendError(
                        f"could not specialize fixed-coordinate variant {tr.schema.name}({coordinate})"
                    )
                specialized[uid] = (tr, fn, "scalar", None)
            else:
                tr = self.variant_trace_by_uid[uid]
                fn = self._specialize_function(uid)
                if fn is None:
                    continue
                specialized[uid] = (
                    tr, fn, None,
                    tr.schema.parameters[tr.key.time_pos] if tr.key.time_pos is not None else None,
                )
            enqueue_dependencies(fn)

            # A reachable specialization can discover fixed-coordinate calls while
            # processing nested expressions.  Enqueue any such calls even if a later
            # local rewrite happened to remove their syntactic call site; retaining an
            # extra proven scalar specialization is conservative and bounded.
            for synthetic_uid in self._fixed_coordinate_requests:
                if synthetic_uid not in queued:
                    queued.add(synthetic_uid)
                    pending.append(synthetic_uid)

        # Table/domain lowering happens only after the complete demanded source
        # graph has been specialized.  Derive one second, more precise coordinate
        # fixed point here so lookup preconditions see caller-refined domains rather
        # than only the physical root range.  This proof is source/control-flow
        # based and never consumes representative observed coordinate values.
        self.specialized_coordinate_domains = self._derive_specialized_coordinate_domains(
            specialized, output_uid
        )
        for uid, dom in sorted(self.specialized_coordinate_domains.items()):
            tr = self.variant_trace_by_uid.get(uid)
            if tr is None:
                continue
            note = (
                f"source-proven specialized call domain {tr.schema.fullname}"
                f"{tr.key.aux_values!r}: [{dom.lo}, {dom.hi}]"
            )
            if note not in diagnostics:
                diagnostics.append(note)

        # Keep canonical/input registration order stable with the historical eager
        # frontend.  Demand-driven specialization changes discovery order (DFS from
        # the output), but generated ABI names such as p_1/a1_5 should not churn just
        # because unreachable helpers stopped being compiled.  Normal observed
        # variants therefore lower in trace order; synthetic fixed-coordinate
        # variants follow their request order, matching the old two-phase loop.
        lower_order = [uid for uid in self.variant_trace_by_uid if uid in specialized]
        lower_order.extend(
            uid for uid in self._fixed_coordinate_requests
            if uid in specialized and uid not in self.variant_trace_by_uid
        )
        for uid in lower_order:
            tr, fn, forced_role, time_param_source = specialized[uid]
            lower_into_canonical(
                uid, tr, fn, forced_role=forced_role, time_param_source=time_param_source
            )

        if (
            output_uid not in canonical
            or canonical[output_uid].role not in ("scalar", "reduction")
            or canonical[output_uid].aux_values
        ):
            raise FrontendError(f"output Cell {self.output!r} did not lower as a scalar/reduction")

        # Lowering itself can erase additional dependencies (for example normalized
        # table/helper syntax), so retain the existing post-lowering reachability pass
        # as a second conservative cleanup.
        known=set(canonical)
        deps: dict[str,set[str]] = {uid:set() for uid in canonical}
        for uid,cv in canonical.items():
            nodes=[]
            if cv.function is not None:
                nodes.extend(cv.function.body)
            if cv.reduction is not None:
                nodes.extend([cv.reduction.init, cv.reduction.body_expr, *cv.reduction.filters, *cv.reduction.range_args])
            for node in nodes:
                for child in ast.walk(node):
                    if isinstance(child,ast.Call) and isinstance(child.func,ast.Name) and child.func.id in known:
                        deps[uid].add(child.func.id)
        reachable=set()
        stack=[output_uid]
        while stack:
            uid=stack.pop()
            if uid in reachable:
                continue
            reachable.add(uid)
            stack.extend(deps.get(uid,()))
        canonical={uid:cv for uid,cv in canonical.items() if uid in reachable}

        # Static formula lowering has inspected every included numeric formula.
        # Strengthen observed loop evidence before freezing the canonical proof
        # boundary so the observational semantic bridge sees the same proof scope
        # as the legacy executable scheduler.
        if any(v.role == "coordinate" for v in canonical.values()):
            self.ir.authorize_loop_generalization(
                "exact coordinate-domain AST + fail-closed formula lowering validated by frontend"
            )

        coordinate_proof_domains = {
            uid: (int(dom.lo), int(dom.hi))
            for uid, dom in self.specialized_coordinate_domains.items()
            if uid in canonical
        }

        def proof_static_scalar_resolver(uid: str) -> int | None:
            cv = canonical.get(uid)
            if cv is None or cv.role != "scalar" or cv.aux_values:
                return None
            ok, value = self._proven_static_expr(
                ast.Call(func=ast.Name(id=cv.source_name, ctx=ast.Load()), args=[], keywords=[])
            )
            if ok and isinstance(value, int) and not isinstance(value, bool):
                return int(value)
            return None

        # Freeze the exact V02346 two-gate PureMap proof at the pre-scheduler
        # boundary.  The legacy scheduler reuses the same proof implementation, so
        # the new observational graph cannot silently broaden PureMap admission.
        snapshot_pure_maps = prove_executable_pure_maps(
            canonical,
            source_pure_map_names=self.source_pure_map_names,
            static_scalar_resolver=proof_static_scalar_resolver,
        )

        # Preserve all evidence needed by the pre-scheduler semantic graph.  Source
        # semantics remain provenance only; exact canonical UIDs remain identities.
        # Recovered loop evidence supplied lazily by NativeBatch is materialized by
        # capture_canonical_proof_snapshot() for audit tooling, not eagerly on the
        # production compile path.
        scheduler_evidence_status = (
            "complete_with_recovered_evidence" if self.recovered_loop_evidence is not None
            else "recovered_evidence_deferred" if self.recovered_loop_evidence_provider is not None
            else "complete_without_recovered_evidence"
        )
        self._canonical_proof_snapshot = CanonicalProofSnapshot(
            output_uid=output_uid,
            run_key_count=len(self.run_keys),
            variants=dict(canonical),
            formula_hash=str(self.ir.formula_hash),
            structural_hash=str(self.ir.structural_hash),
            coordinate_domains=tuple(sorted(
                (uid, int(dom.lo), int(dom.hi))
                for uid, dom in self.specialized_coordinate_domains.items()
                if uid in canonical
            )),
            static_facts=tuple(sorted(
                self._used_static_facts.values(), key=lambda x: (x.source_kind, x.source_name)
            )),
            validated_static_facts=tuple(sorted(
                self._used_validated_static_facts.values(), key=lambda x: x.source_name
            )),
            finite_domain_facts=tuple(sorted(
                self._used_finite_domain_facts.values(), key=lambda x: (x.source_kind, x.source_name)
            )),
            fixed_coordinate_facts=tuple(sorted(
                (fact for fact in self._used_fixed_coordinate_facts.values()
                 if fact.synthetic_uid in canonical),
                key=lambda x: x.synthetic_uid,
            )),
            coordinate_recurrence_facts=tuple(
                fact for fact in self.coordinate_recurrence_facts
                if fact.source_uid in canonical
            ),
            runtime_scalar_helper_facts=tuple(sorted(
                self._used_runtime_scalar_helper_facts.values(), key=lambda x: x.source_name
            )),
            source_backed_scheduled_facts=tuple(sorted(
                self._used_source_backed_scheduled_facts.values(),
                key=lambda x: (x.source_name, x.synthetic_uid),
            )),
            step_lookup_domain_facts=tuple(sorted(
                self._used_step_lookup_domain_facts.values(),
                key=lambda x: (x.source_name, x.source_uid, x.query_expr, x.axis_min),
            )),
            normalized_operators=tuple(sorted(self._normalized_operators.values(), key=lambda x: x.uid)),
            source_value_semantics=tuple(
                self.source_value_semantics[name] for name in sorted(self.source_value_semantics)
            ),
            pure_map_specs=tuple(snapshot_pure_maps[uid] for uid in sorted(snapshot_pure_maps)),
            loop_topology_facts=freeze_graph_ir_loop_topology(self.ir),
            recovered_loop_topology_facts=freeze_recovered_loop_topology(self.recovered_loop_evidence),
            scheduler_evidence_status=scheduler_evidence_status,
        )

        canonical_semantic_graph = None
        canonical_schedule_analysis = None
        canonical_execution_schedule = None
        stage_execution_plan = None
        stage_storage_plan = None
        if self.canonical_schedule_authority_enabled:
            # V02349 authority seam: construct schedule meaning before the legacy
            # executable builder.  Ineligibility is a typed contract result; an
            # analyzer exception is not silently converted into legacy authority.
            canonical_semantic_graph = build_canonical_semantic_graph(self._canonical_proof_snapshot)
            canonical_schedule_analysis = analyze_canonical_component_schedule(canonical_semantic_graph)
            canonical_execution_schedule = build_canonical_execution_schedule(
                canonical_schedule_analysis
            )
            # V02350A observational execution-plan seam.  This total canonical
            # stage/lifetime plan never changes production lowering in this
            # iteration; it records unsupported shapes as capability blockers.
            stage_execution_plan = build_stage_execution_plan(
                canonical_semantic_graph, canonical_schedule_analysis
            )
            stage_storage_plan = build_stage_storage_plan(
                canonical_semantic_graph, stage_execution_plan,
                analysis=canonical_schedule_analysis, variants=canonical,
            )
            diagnostics.append(
                "canonical stage execution plan built: "
                f"{stage_execution_plan.uid}; backend_eligible={stage_execution_plan.backend_eligible}"
            )
            diagnostics.append(
                "canonical stage storage plan built: "
                f"{stage_storage_plan.uid}; geometry_proven={stage_storage_plan.geometry_proven}"
            )
            if canonical_execution_schedule.eligible:
                diagnostics.append(
                    "canonical schedule authority eligible: "
                    f"{canonical_execution_schedule.uid}"
                )
            else:
                diagnostics.append(
                    "canonical schedule authority ineligible: "
                    + "; ".join(canonical_execution_schedule.capability_blockers)
                )

        executable = None
        domain_graph_shadow = None
        if self.legacy_comparison_enabled:
            try:
                executable = build_executable_graph(
                    self.ir, canonical, output_uid,
                    coordinate_domains=coordinate_proof_domains,
                    proof_static_scalar_resolver=proof_static_scalar_resolver,
                    source_pure_map_names=self.source_pure_map_names,
                    recovered_loop_evidence=self.recovered_loop_evidence,
                    recovered_loop_evidence_provider=self.recovered_loop_evidence_provider,
                    canonical_execution_schedule=canonical_execution_schedule,
                )
            except TemplateError as exc:
                raise FrontendError(f"legacy comparison executable lowering failed: {exc}") from exc
            # Comparison-only shadow retained for mature oracle tooling.  Canonical
            # Stage scheduling/storage never consumes this object.
            domain_graph_shadow = build_shadow_domain_graph(executable, canonical)
            if self._canonical_proof_snapshot is not None:
                self._canonical_proof_snapshot = (
                    self._canonical_proof_snapshot.with_executable_schedule()
                )
            diagnostics.append("legacy comparison executable built")
        else:
            diagnostics.append("legacy comparison executable skipped; canonical Stage pipeline owns production execution")

        return CanonicalModel(
            model=self.model, space=self.space, output_name=self.output, output_uid=output_uid,
            output_invocation=self.output_invocation,
            run_domain=self.run_domain,
            result_domain=self.result_domain,
            sample_keys=self.sample_keys, run_keys=self.run_keys, trace=self.trace,
            variants=canonical, inputs=self.registry.specs, executable=executable,
            domain_graph_shadow=domain_graph_shadow,
            canonical_semantic_graph=canonical_semantic_graph,
            canonical_schedule_analysis=canonical_schedule_analysis,
            canonical_execution_schedule=canonical_execution_schedule,
            stage_execution_plan=stage_execution_plan,
            stage_storage_plan=stage_storage_plan,
            normalized_operators=tuple(sorted(self._normalized_operators.values(), key=lambda x: x.uid)),
            diagnostics=diagnostics,
            static_facts=tuple(sorted(self._used_static_facts.values(), key=lambda x: (x.source_kind, x.source_name))),
            validated_static_facts=tuple(sorted(self._used_validated_static_facts.values(), key=lambda x: x.source_name)),
            finite_domain_facts=tuple(sorted(self._used_finite_domain_facts.values(), key=lambda x: (x.source_kind, x.source_name))),
            fixed_coordinate_facts=tuple(
                sorted(
                    (fact for fact in self._used_fixed_coordinate_facts.values() if fact.synthetic_uid in canonical),
                    key=lambda x: x.synthetic_uid,
                )
            ),
            coordinate_recurrence_facts=tuple(
                fact for fact in self.coordinate_recurrence_facts
                if fact.source_uid in canonical
            ),
            runtime_scalar_helper_facts=tuple(
                sorted(self._used_runtime_scalar_helper_facts.values(), key=lambda x: x.source_name)
            ),
            source_backed_scheduled_facts=tuple(
                sorted(
                    self._used_source_backed_scheduled_facts.values(),
                    key=lambda x: (x.source_name, x.synthetic_uid),
                )
            ),
            step_lookup_domain_facts=tuple(
                sorted(
                    self._used_step_lookup_domain_facts.values(),
                    key=lambda x: (x.source_name, x.source_uid, x.query_expr, x.axis_min),
                )
            ),
        )


def capture_canonical_proof_snapshot(*args, **kwargs) -> CanonicalProofSnapshot:
    """Run the normal frontend and retain its pre-scheduler proof snapshot.

    Audit capture additionally materializes a deferred recovered-loop provider when
    one was supplied.  This keeps the *production* compile path lazy while making
    the returned evidence object self-contained enough for the observational
    canonical scheduler.  Provider failure is recorded as incomplete evidence; it
    never turns an otherwise valid canonical graph into an exception.
    """

    compiler = GraphModelCompiler.__new__(GraphModelCompiler)
    failure: FrontendError | None = None
    try:
        GraphModelCompiler.__init__(compiler, *args, **kwargs)
    except FrontendError as exc:
        failure = exc
    snapshot = getattr(compiler, "_canonical_proof_snapshot", None)
    if snapshot is None:
        if failure is not None:
            raise failure
        raise FrontendError("frontend completed without a canonical proof snapshot")

    provider = getattr(compiler, "recovered_loop_evidence_provider", None)
    existing = getattr(compiler, "recovered_loop_evidence", None)
    if existing is not None:
        snapshot = snapshot.with_recovered_loop_evidence(existing)
    elif provider is not None:
        try:
            snapshot = snapshot.with_recovered_loop_evidence(provider())
        except Exception as exc:
            snapshot = snapshot._copy(
                scheduler_evidence_status=f"recovered_evidence_failed:{type(exc).__name__}"
            )

    if failure is not None:
        snapshot = snapshot.with_failure(str(failure))
    return snapshot

