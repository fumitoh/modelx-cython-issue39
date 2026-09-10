"""Native-friendly lookup semantics for modelx Cell formulas.

This module is intentionally standard-library-only.  It gives ordinary Python
models explicit scalar lookup operations that are cheap after preparation and,
more importantly, have simple semantics a native compiler can recognize and
lower without carrying pandas objects into the hot path.

Preparation happens outside hot Cells.  Hot Cells call exactN/step1/
grouped_stepN/column_value with primitive scalar keys.
"""
from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass
from typing import Generic, Iterable, Sequence, TypeVar, Hashable, Any

V = TypeVar("V")
K = TypeVar("K", bound=Hashable)


@dataclass(frozen=True, slots=True)
class ExactTable(Generic[V]):
    values: dict[Any, V]


@dataclass(frozen=True, slots=True)
class StepTable(Generic[V]):
    keys: tuple[float | int, ...]
    values: tuple[V, ...]
    below: str = "error"  # error | clamp


@dataclass(frozen=True, slots=True)
class GroupedStepTable(Generic[V]):
    groups: dict[Any, StepTable[V]]


def _unique_dict(rows: Iterable[tuple[Any, V]]) -> dict[Any, V]:
    out: dict[Any, V] = {}
    for key, value in rows:
        if key in out:
            raise ValueError(f"duplicate lookup key: {key!r}")
        out[key] = value
    return out


def build_exact1(rows: Iterable[tuple[Any, V]]) -> ExactTable[V]:
    return ExactTable(_unique_dict(rows))


def build_exact2(rows: Iterable[tuple[Any, Any, V]]) -> ExactTable[V]:
    return ExactTable(_unique_dict(((a, b), v) for a, b, v in rows))


def build_exact3(rows: Iterable[tuple[Any, Any, Any, V]]) -> ExactTable[V]:
    return ExactTable(_unique_dict(((a, b, c), v) for a, b, c, v in rows))


def build_exact4(rows: Iterable[tuple[Any, Any, Any, Any, V]]) -> ExactTable[V]:
    return ExactTable(_unique_dict(((a, b, c, d), v) for a, b, c, d, v in rows))


def exact1(table: ExactTable[V], k1: Any) -> V:
    return table.values[k1]


def exact2(table: ExactTable[V], k1: Any, k2: Any) -> V:
    return table.values[(k1, k2)]


def exact3(table: ExactTable[V], k1: Any, k2: Any, k3: Any) -> V:
    return table.values[(k1, k2, k3)]


def exact4(table: ExactTable[V], k1: Any, k2: Any, k3: Any, k4: Any) -> V:
    return table.values[(k1, k2, k3, k4)]


def build_step1(rows: Iterable[tuple[float | int, V]], *, below: str = "error") -> StepTable[V]:
    if below not in {"error", "clamp"}:
        raise ValueError("below must be 'error' or 'clamp'")
    ordered = sorted(rows, key=lambda kv: kv[0])
    if not ordered:
        raise ValueError("step table must not be empty")
    keys: list[float | int] = []
    vals: list[V] = []
    for key, value in ordered:
        if keys and key == keys[-1]:
            raise ValueError(f"duplicate step key: {key!r}")
        keys.append(key); vals.append(value)
    return StepTable(tuple(keys), tuple(vals), below)


def step1(table: StepTable[V], x: float | int) -> V:
    pos = bisect_right(table.keys, x) - 1
    if pos < 0:
        if table.below == "clamp":
            pos = 0
        else:
            raise KeyError(x)
    return table.values[pos]


def build_grouped_step1(
    rows: Iterable[tuple[Any, float | int, V]], *, below: str = "error"
) -> GroupedStepTable[V]:
    tmp: dict[Any, list[tuple[float | int, V]]] = {}
    for g1, axis, value in rows:
        tmp.setdefault(g1, []).append((axis, value))
    return GroupedStepTable({g: build_step1(items, below=below) for g, items in tmp.items()})


def build_grouped_step2(
    rows: Iterable[tuple[Any, Any, float | int, V]], *, below: str = "error"
) -> GroupedStepTable[V]:
    tmp: dict[tuple[Any, Any], list[tuple[float | int, V]]] = {}
    for g1, g2, axis, value in rows:
        tmp.setdefault((g1, g2), []).append((axis, value))
    return GroupedStepTable({g: build_step1(items, below=below) for g, items in tmp.items()})


def grouped_step1(table: GroupedStepTable[V], g1: Any, x: float | int) -> V:
    return step1(table.groups[g1], x)


def grouped_step2(table: GroupedStepTable[V], g1: Any, g2: Any, x: float | int) -> V:
    return step1(table.groups[(g1, g2)], x)


def column_value(values: Sequence[V], point_index: int) -> V:
    """Read one prepared model-point column by integer row index."""
    return values[point_index]
