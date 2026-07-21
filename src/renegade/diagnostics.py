"""Deterministic summaries for inspecting an already-completed grid pipeline."""

from __future__ import annotations

from dataclasses import dataclass

from .pipeline import PerceptPipelineResult
from .tasks import Task, TaskGrid, TrainingPair


@dataclass(frozen=True)
class PipelineDiagnostics:
    """Counts recorded by one pipeline execution, without deriving new facts."""

    observation_count: int
    measurement_count: int
    percept_count: int
    relationship_count: int
    invariant_count: int
    archetype_count: int
    execution_event_count: int


def summarize_pipeline(result: PerceptPipelineResult) -> PipelineDiagnostics:
    """Return a deterministic count-only summary of an existing result."""
    if not isinstance(result, PerceptPipelineResult):
        raise TypeError("result must be a PerceptPipelineResult")
    return PipelineDiagnostics(
        observation_count=len(result.observations),
        measurement_count=len(result.measurements),
        percept_count=1 + len(result.region_percepts),
        relationship_count=len(result.relationships),
        invariant_count=len(result.invariants),
        archetype_count=len(result.archetypes),
        execution_event_count=len(result.trace),
    )


@dataclass(frozen=True)
class TaskGridDiagnostics(PipelineDiagnostics):
    """Count-only summary of one inspected task grid."""

    role: str


@dataclass(frozen=True)
class TrainingPairDiagnostics:
    """Independent summaries for the two grids in one training pair."""

    input_grid: TaskGridDiagnostics
    output_grid: TaskGridDiagnostics


@dataclass(frozen=True)
class TaskDiagnostics:
    """Totals from an inspected task; no cross-grid facts are derived."""

    grid_count: int
    pair_count: int
    observation_count: int
    measurement_count: int
    percept_count: int
    relationship_count: int
    invariant_count: int
    archetype_count: int
    execution_event_count: int


def summarize_task_grid(grid: TaskGrid) -> TaskGridDiagnostics:
    if not isinstance(grid, TaskGrid): raise TypeError("grid must be a TaskGrid")
    if grid.pipeline_result is None: raise ValueError("task grid has not been inspected")
    return TaskGridDiagnostics(**summarize_pipeline(grid.pipeline_result).__dict__, role=grid.role.value)


def summarize_training_pair(pair: TrainingPair) -> TrainingPairDiagnostics:
    if not isinstance(pair, TrainingPair): raise TypeError("pair must be a TrainingPair")
    return TrainingPairDiagnostics(summarize_task_grid(pair.input_grid), summarize_task_grid(pair.output_grid))


def summarize_task(task: Task) -> TaskDiagnostics:
    if not isinstance(task, Task): raise TypeError("task must be a Task")
    grids = [grid for pair in task.training_pairs for grid in (pair.input_grid, pair.output_grid)] + list(task.test_inputs) + [grid for grid in task.expected_outputs if grid is not None]
    summaries = tuple(summarize_task_grid(grid) for grid in grids)
    return TaskDiagnostics(len(grids), len(task.training_pairs), *(sum(getattr(summary, field) for summary in summaries) for field in ("observation_count", "measurement_count", "percept_count", "relationship_count", "invariant_count", "archetype_count")), len(task.trace))
