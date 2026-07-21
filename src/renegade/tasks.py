"""Immutable deterministic representations and inspection for ARC task data.

This module deliberately inspects each supplied grid independently.  It does
not compare grids or derive transformations, correspondences, or solutions.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Mapping

from .core import EventKind, ExecutionEvent
from .foundation import StableIdentifier
from .pipeline import PerceptPipelineResult, inspect_grid, normalize_grid


class TaskKind(str, Enum):
    """Structural source format label; it carries no task semantics."""

    ARC = "arc"


class GridRole(str, Enum):
    """The structural position of a grid in a task."""

    TRAINING_INPUT = "training_input"
    TRAINING_OUTPUT = "training_output"
    TEST_INPUT = "test_input"
    EXPECTED_OUTPUT = "expected_output"


@dataclass(frozen=True)
class TaskGrid:
    """One raw task grid and, after inspection, its independent pipeline result."""

    identity: StableIdentifier
    role: GridRole
    raw_grid: tuple[tuple[Any, ...], ...]
    pipeline_result: PerceptPipelineResult | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.identity, StableIdentifier):
            raise TypeError("identity must be a StableIdentifier")
        if not isinstance(self.role, GridRole):
            raise TypeError("role must be a GridRole")
        object.__setattr__(self, "raw_grid", normalize_grid(self.raw_grid))
        if self.pipeline_result is not None and not isinstance(self.pipeline_result, PerceptPipelineResult):
            raise TypeError("pipeline_result must be a PerceptPipelineResult or None")
        if self.pipeline_result is not None and self.pipeline_result.grid != self.raw_grid:
            raise ValueError("pipeline_result grid must equal raw_grid")


@dataclass(frozen=True)
class TrainingPair:
    """An ordered input/output pair without any inferred connection between them."""

    input_grid: TaskGrid
    output_grid: TaskGrid

    def __post_init__(self) -> None:
        if self.input_grid.role is not GridRole.TRAINING_INPUT:
            raise ValueError("training pair input_grid must have TRAINING_INPUT role")
        if self.output_grid.role is not GridRole.TRAINING_OUTPUT:
            raise ValueError("training pair output_grid must have TRAINING_OUTPUT role")


@dataclass(frozen=True)
class Task:
    """A complete ordered ARC task with structural provenance and metadata."""

    identifier: str
    provenance: str
    training_pairs: tuple[TrainingPair, ...]
    test_inputs: tuple[TaskGrid, ...]
    expected_outputs: tuple[TaskGrid | None, ...] = ()
    metadata: tuple[tuple[str, Any], ...] = ()
    kind: TaskKind = TaskKind.ARC
    trace: tuple[ExecutionEvent, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.identifier, str) or not self.identifier:
            raise ValueError("identifier must be a non-empty string")
        if not isinstance(self.provenance, str) or not self.provenance:
            raise ValueError("provenance must be a non-empty string")
        if not isinstance(self.kind, TaskKind):
            raise TypeError("kind must be a TaskKind")
        if not self.training_pairs:
            raise ValueError("task must contain at least one training pair")
        if not self.test_inputs:
            raise ValueError("task must contain at least one test input")
        if any(grid.role is not GridRole.TEST_INPUT for grid in self.test_inputs):
            raise ValueError("test_inputs must have TEST_INPUT role")
        outputs = self.expected_outputs or (None,) * len(self.test_inputs)
        if len(outputs) != len(self.test_inputs):
            raise ValueError("expected_outputs must align with test_inputs")
        if any(grid is not None and grid.role is not GridRole.EXPECTED_OUTPUT for grid in outputs):
            raise ValueError("expected outputs must have EXPECTED_OUTPUT role")
        object.__setattr__(self, "expected_outputs", tuple(outputs))
        object.__setattr__(self, "metadata", tuple(self.metadata))

    @property
    def test_input(self) -> TaskGrid:
        """The sole test input, for callers handling canonical single-test tasks."""
        if len(self.test_inputs) != 1:
            raise ValueError("task has multiple test inputs")
        return self.test_inputs[0]

    @property
    def expected_output(self) -> TaskGrid | None:
        """The sole optional expected output, for canonical single-test tasks."""
        if len(self.expected_outputs) != 1:
            raise ValueError("task has multiple test inputs")
        return self.expected_outputs[0]


def _grid(identifier: str, role: GridRole, index: int, value: Any) -> TaskGrid:
    return TaskGrid(StableIdentifier("task-grid", f"{identifier}-{role.value}-{index}", 1), role, normalize_grid(value))


def load_task(data: Mapping[str, Any], identifier: str, provenance: str = "ARC JSON") -> Task:
    """Parse canonical ARC JSON data with explicit, deterministic validation."""
    if not isinstance(data, Mapping):
        raise TypeError("task data must be an object")
    if set(data) - {"train", "test"}:
        raise ValueError("task data contains unsupported fields")
    for field in ("train", "test"):
        if field not in data:
            raise ValueError(f"task data is missing required field: {field}")
        if not isinstance(data[field], list) or not data[field]:
            raise ValueError(f"task data field {field} must be a non-empty array")
    pairs: list[TrainingPair] = []
    for index, item in enumerate(data["train"], 1):
        if not isinstance(item, Mapping): raise TypeError(f"train[{index - 1}] must be an object")
        if set(item) != {"input", "output"}: raise ValueError(f"train[{index - 1}] must contain exactly input and output")
        pairs.append(TrainingPair(_grid(identifier, GridRole.TRAINING_INPUT, index, item["input"]), _grid(identifier, GridRole.TRAINING_OUTPUT, index, item["output"])))
    inputs: list[TaskGrid] = []; outputs: list[TaskGrid | None] = []
    for index, item in enumerate(data["test"], 1):
        if not isinstance(item, Mapping): raise TypeError(f"test[{index - 1}] must be an object")
        if "input" not in item or set(item) - {"input", "output"}: raise ValueError(f"test[{index - 1}] must contain input and optional output")
        inputs.append(_grid(identifier, GridRole.TEST_INPUT, index, item["input"]))
        outputs.append(_grid(identifier, GridRole.EXPECTED_OUTPUT, index, item["output"]) if "output" in item else None)
    return Task(identifier, provenance, tuple(pairs), tuple(inputs), tuple(outputs))


def _inspect_grid(grid: TaskGrid) -> TaskGrid:
    return replace(grid, pipeline_result=inspect_grid(grid.raw_grid, grid.identity.local_name))


def inspect_task(task: Task) -> Task:
    """Independently inspect every task grid in deterministic structural order."""
    if not isinstance(task, Task):
        raise TypeError("task must be a Task")
    trace: list[ExecutionEvent] = []
    def event(kind: EventKind, message: str, **details: Any) -> None:
        trace.append(ExecutionEvent(len(trace) + 1, kind, message, tuple(details.items())))
    event(EventKind.TASK_CREATED, f"Created task {task.identifier}.", task_identifier=task.identifier)
    def run(grid: TaskGrid) -> TaskGrid:
        event(EventKind.TASK_GRID_STARTED, f"Started task grid {grid.identity}.", grid_identity=str(grid.identity), grid_role=grid.role.value)
        inspected = _inspect_grid(grid)
        event(EventKind.TASK_GRID_COMPLETED, f"Completed task grid {grid.identity}.", grid_identity=str(grid.identity), grid_role=grid.role.value)
        return inspected
    pairs = tuple(TrainingPair(run(pair.input_grid), run(pair.output_grid)) for pair in task.training_pairs)
    inputs = tuple(run(grid) for grid in task.test_inputs)
    outputs = tuple(run(grid) if grid is not None else None for grid in task.expected_outputs)
    event(EventKind.TASK_COMPLETED, f"Completed task {task.identifier}.", task_identifier=task.identifier)
    return replace(task, training_pairs=pairs, test_inputs=inputs, expected_outputs=outputs, trace=tuple(trace))
