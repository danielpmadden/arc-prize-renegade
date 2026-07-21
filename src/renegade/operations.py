"""Executable-operation inventory shared by solver-facing tooling and generation.

This declarative module records only operations implemented by ``solver.apply``.
It contains no generator provenance and validates itself against the executor contract.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Any

from .solver import SUPPORTED_OPERATION_NAMES

@dataclass(frozen=True)
class OperationSpec:
    name: str; family: str; parameter_schema: str; input_constraints: str
    output_shape: str; dimensions_preserved: bool; requires_colors: bool
    requires_regions: bool; solver_searches: bool; generator_supported: bool
    generator_reason: str

_OPERATION_SPECS = (
    OperationSpec("identity", "identity", "none", "rectangular grid", "unchanged", True, False, False, True, False, "excluded: cannot be effective"),
    OperationSpec("recolor", "color", "mapping: ordered distinct source/target color pairs", "source color present", "same shape", True, True, False, True, True, "constructive palette world"),
    OperationSpec("rotate", "geometry", "turns: 1, 2, or 3", "asymmetric rectangular grid", "90/180/270 degree rotation", False, False, False, True, True, "constructive asymmetric world"),
    OperationSpec("reflect", "geometry", "axis: horizontal or vertical", "asymmetric grid about selected axis", "same shape", True, False, False, True, True, "constructive asymmetric world"),
    OperationSpec("crop", "shape", "background: observed color", "non-background extent", "bounding rectangle", False, True, False, True, False, "excluded: safe compositions not yet constructively modelled"),
    OperationSpec("extract_object", "object", "background; unique selector", "unique selected component", "selected component bounding rectangle", False, True, True, True, False, "excluded: object curriculum not yet implemented"),
    OperationSpec("render_objects", "object", "background; predicate; canvas", "one or more selected components", "input or selected bounding canvas", False, True, True, True, False, "excluded: object curriculum not yet implemented"),
    OperationSpec("recolor_objects", "object", "background; predicate; color", "one or more selected components", "same shape", True, True, True, True, False, "excluded: object curriculum not yet implemented"),
    OperationSpec("repeat_object", "object", "background; predicate; bounded count; axis; gap", "exactly one selected component", "constructed repetition canvas", False, True, True, True, False, "excluded: object curriculum not yet implemented"),
    OperationSpec("render_related", "object", "background; unique reference; relation; canvas", "relation-selected components", "input or selected bounding canvas", False, True, True, True, False, "excluded: object curriculum not yet implemented"),
    OperationSpec("translate", "geometry", "offset: bounded (dr, dc); background", "movable non-background content", "same shape", True, True, False, True, True, "constructive padded world"),
    OperationSpec("fill", "region", "background; color='enclosing' or color", "enclosed background region", "same shape", True, True, True, True, False, "excluded: safe composition model not yet implemented"),
    OperationSpec("outline", "shape", "background", "solid interior cell", "same shape", True, True, True, True, False, "excluded: safe composition model not yet implemented"),
)

OPERATION_SPECS = {spec.name: spec for spec in _OPERATION_SPECS}
_inventory_names = frozenset(OPERATION_SPECS)
if _inventory_names != SUPPORTED_OPERATION_NAMES:
    missing = sorted(SUPPORTED_OPERATION_NAMES - _inventory_names)
    stale = sorted(_inventory_names - SUPPORTED_OPERATION_NAMES)
    raise RuntimeError(f"operation inventory/executor mismatch: missing={missing}, stale={stale}")
GENERATOR_OPERATION_NAMES = tuple(spec.name for spec in _OPERATION_SPECS if spec.generator_supported)
GENERATOR_FAMILIES = tuple(sorted({OPERATION_SPECS[name].family for name in GENERATOR_OPERATION_NAMES}))

def operation_inventory() -> list[dict[str, Any]]:
    """Stable JSON-ready operation inventory in operation-name order."""
    return [asdict(spec) for spec in _OPERATION_SPECS]
