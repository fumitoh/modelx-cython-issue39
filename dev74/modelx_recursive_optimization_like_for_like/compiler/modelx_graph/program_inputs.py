from __future__ import annotations

"""Backend-neutral input semantics shared by optimized Python and Cython.

The compiler may obtain inputs from modelx/pandas during preparation, but emitters
must see only normalized numeric inputs plus semantic metadata describing how the
input was derived.  This keeps pandas/table interpretation upstream of both
runtime backends.
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class NormalizedTableAxis:
    """One exact runtime selector axis of a normalized table lookup."""

    level: int
    index_name: str | None
    selector_kind: str  # finite_categorical | numeric_exact | finite_numeric_exact
    labels: tuple[Any, ...]
    axis_start: float | int | None = None
    axis_step: float | int | None = None
    axis_input_key: str | None = None

    def manifest(self) -> dict[str, Any]:
        return {
            "level": int(self.level),
            "index_name": self.index_name,
            "selector_kind": self.selector_kind,
            "labels": [repr(x) for x in self.labels],
            "axis_start": self.axis_start,
            "axis_step": self.axis_step,
            "axis_input_key": self.axis_input_key,
        }


@dataclass(frozen=True)
class NormalizedTableInput:
    """Semantic record for one numeric input normalized from a pandas table.

    ``result_kind`` is either ``"scalar"`` or ``"axis1d"``.  Concrete values are
    still supplied through the ordinary numeric input ABI; this object records the
    table-domain proof that produced that ABI and is therefore backend-neutral.
    """

    source_ref: str
    source_cell: str
    source_shape: tuple[int, int]
    index_names: tuple[str | None, ...]
    selected_column: Any
    fixed_row_labels: tuple[tuple[int, Any], ...]
    dynamic_level: int | None
    dynamic_labels: tuple[Any, ...]
    axis_start: int | None
    axis_step: int | None
    result_kind: str
    layout: str = "legacy"
    dynamic_axes: tuple[NormalizedTableAxis, ...] = ()
    sparse_key_input: str | None = None
    metadata_kind: str | None = None
    metadata_level: int | None = None

    def manifest(self) -> dict[str, Any]:
        return {
            "source_ref": self.source_ref,
            "source_cell": self.source_cell,
            "source_shape": list(self.source_shape),
            "index_names": list(self.index_names),
            "selected_column": repr(self.selected_column),
            "fixed_row_labels": [
                {"level": int(level), "label": repr(label)}
                for level, label in self.fixed_row_labels
            ],
            "dynamic_level": self.dynamic_level,
            "dynamic_labels": [repr(x) for x in self.dynamic_labels],
            "axis_start": self.axis_start,
            "axis_step": self.axis_step,
            "result_kind": self.result_kind,
            "layout": self.layout,
            "dynamic_axes": [x.manifest() for x in self.dynamic_axes],
            "sparse_key_input": self.sparse_key_input,
            "metadata_kind": self.metadata_kind,
            "metadata_level": self.metadata_level,
        }


@dataclass(frozen=True)
class NormalizedLookup1D:
    """Backend-neutral provenance for one normalized mathematical 1-D lookup.

    ``kind`` is currently ``"step"``, ``"interval"`` or ``"interp"``.  Preparation may use
    pandas/modelx to discover and validate the source table, but runtime backends
    consume only the normalized numeric arrays described here.
    """

    kind: str
    source_ref: str
    source_cell: str
    source_shape: tuple[int, int]
    row_selector: Any = None
    selected_column: Any = None
    axis_labels: tuple[float, ...] = ()
    below_first: str | None = None
    default_value: float | None = None
    lower_column: Any = None
    upper_column: Any = None
    lower_labels: tuple[float, ...] = ()
    upper_labels: tuple[float, ...] = ()
    closure: str | None = None
    fallback: str | None = None
    interpolation: str | None = None
    extrapolation: str | None = None

    def manifest(self) -> dict[str, Any]:
        out = {
            "kind": self.kind,
            "source_ref": self.source_ref,
            "source_cell": self.source_cell,
            "source_shape": list(self.source_shape),
            "selected_column": repr(self.selected_column),
        }
        if self.kind == "step":
            out.update({
                "row_selector": repr(self.row_selector),
                "axis_labels": list(self.axis_labels),
                "below_first": self.below_first,
                "default_value": self.default_value,
            })
        elif self.kind == "interval":
            out.update({
                "lower_column": repr(self.lower_column),
                "upper_column": repr(self.upper_column),
                "lower_labels": list(self.lower_labels),
                "upper_labels": list(self.upper_labels),
                "closure": self.closure,
                "fallback": self.fallback,
            })
        elif self.kind == "interp":
            out.update({
                "row_selector": repr(self.row_selector),
                "axis_labels": list(self.axis_labels),
                "interpolation": self.interpolation,
                "extrapolation": self.extrapolation,
            })
        return out


@dataclass(frozen=True)
class NormalizedPointRowSource:
    """Backend-neutral provenance for one ItemSpace-keyed model-point table.

    Preparation may discover the table either as a direct DataFrame Reference or
    through a zero-argument external Cell returning a DataFrame.  Runtime emitters
    see neither pandas nor modelx; they receive ordinary point-scoped numeric
    arrays.  This record exists only to make the normalization/proof auditable.
    """

    source_kind: str  # direct_reference | external_cell
    source_ref: str
    source_cell: str | None
    source_shape: tuple[int, int]
    index_names: tuple[str | None, ...]
    key_parameter: str
    key_position: int

    def manifest(self) -> dict[str, Any]:
        return {
            "source_kind": self.source_kind,
            "source_ref": self.source_ref,
            "source_cell": self.source_cell,
            "source_shape": list(self.source_shape),
            "index_names": list(self.index_names),
            "key_parameter": self.key_parameter,
            "key_position": int(self.key_position),
        }


@dataclass(frozen=True)
class OptimizedInputSpec:
    key: str
    dtype: str
    ndim: int
    scope: str
    description: str
    expected_shape: tuple[int, ...] | None = None
    domain_token: str | None = None
    normalized_table: NormalizedTableInput | None = None
    point_row_source: NormalizedPointRowSource | None = None
    point_field: Any | None = None
    normalized_lookup_1d: NormalizedLookup1D | None = None
    lookup_1d_role: str | None = None
    enum_labels: tuple[str, ...] | None = None

    def manifest(self) -> dict[str, Any]:
        out = {
            "dtype": self.dtype,
            "ndim": int(self.ndim),
            "scope": self.scope,
            "description": self.description,
            "expected_shape": None if self.expected_shape is None else list(self.expected_shape),
            "domain_token": self.domain_token,
        }
        if self.normalized_table is not None:
            out["normalized_table"] = self.normalized_table.manifest()
        if self.point_row_source is not None:
            out["point_row_source"] = self.point_row_source.manifest()
            out["point_field"] = repr(self.point_field)
        if self.normalized_lookup_1d is not None:
            out["normalized_lookup_1d"] = self.normalized_lookup_1d.manifest()
            out["lookup_1d_role"] = self.lookup_1d_role
        if self.enum_labels is not None:
            out["enum_labels"] = list(self.enum_labels)
        return out
