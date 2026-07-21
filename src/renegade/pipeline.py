"""Explicit deterministic orchestration for supported rectangular grids."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .core import EventKind, Workspace
from .foundation import StableIdentifier
from .measurements import measure_bounds, measure_dimensions, measure_observation_count
from .observations import Observation, ObservationFrame, ObservationKind, _normalize_value
from .percepts import Percept, form_connected_regions, form_frame_percept

def normalize_grid(value: Any) -> tuple[tuple[Any, ...], ...]:
    if not isinstance(value, (list, tuple)) or not value: raise ValueError("grid must be a non-empty array of rows")
    if not all(isinstance(row, (list, tuple)) and row for row in value): raise ValueError("grid rows must be non-empty arrays")
    if len({len(row) for row in value}) != 1: raise ValueError("grid rows must have equal length")
    normalized = tuple(tuple(_normalize_value(cell) for cell in row) for row in value)
    return normalized

@dataclass(frozen=True)
class PerceptPipelineResult:
    grid: tuple[tuple[Any, ...], ...]
    frame: ObservationFrame
    observations: tuple[Observation, ...]
    measurements: tuple[Any, ...]
    frame_percept: Percept
    region_percepts: tuple[Percept, ...]
    trace: tuple[Any, ...]

def inspect_grid(value: Any, name: str = "grid") -> PerceptPipelineResult:
    """Record, measure, and structurally form one supplied rectangular grid."""
    grid = normalize_grid(value)
    if not isinstance(name, str) or not name: raise ValueError("name must be a non-empty string")
    observations = tuple(Observation(( (row, column), cell), StableIdentifier("observation", f"{name}-cell-{row}-{column}", 1), ObservationKind.STRUCTURED, "percept pipeline") for row, values in enumerate(grid) for column, cell in enumerate(values))
    frame = ObservationFrame(StableIdentifier("frame", name, 1), observations, "percept pipeline")
    workspace = Workspace(observation=observations[0], frame=frame)
    workspace.record(EventKind.OBSERVATION_FRAME_RECEIVED, f"Received observation frame {frame.identity}.", frame_identity=str(frame.identity), observation_count=len(observations))
    for observation in observations:
        workspace.observations.register(observation); workspace.record(EventKind.OBSERVATION_REGISTERED, f"Registered observation {observation.identity}.", observation_identity=str(observation.identity), observation_kind=observation.kind.value)
    measurements = []
    for capability in (measure_dimensions, measure_bounds, measure_observation_count):
        workspace.record(EventKind.CAPABILITY_RETRIEVED, f"Requested capability {capability.__name__}.", capability_name=capability.__name__)
        workspace.record(EventKind.CAPABILITY_STARTED, f"Started capability {capability.__name__}.", capability_name=capability.__name__)
        measurement = capability(frame); measurements.append(measurement)
        workspace.record(EventKind.MEASUREMENT_CREATED, f"Created measurement {measurement.identity}.", measurement_identity=str(measurement.identity), measurement_kind=measurement.kind.value)
        workspace.measurements.register(measurement); workspace.record(EventKind.MEASUREMENT_RECORDED, f"Recorded measurement {measurement.identity}.", measurement_identity=str(measurement.identity))
        workspace.record(EventKind.EXECUTION_SUCCEEDED, f"Capability {capability.__name__} completed.", capability_name=capability.__name__)
    references = tuple(item.identity for item in measurements)
    for capability, produced in ((form_frame_percept, (form_frame_percept(frame, references),)), (form_connected_regions, tuple(form_connected_regions(frame, references)))):
        workspace.record(EventKind.CAPABILITY_RETRIEVED, f"Requested capability {capability.__name__}.", capability_name=capability.__name__)
        workspace.record(EventKind.CAPABILITY_STARTED, f"Started capability {capability.__name__}.", capability_name=capability.__name__)
        for percept in produced:
            workspace.record(EventKind.PERCEPT_CREATED, f"Created percept {percept.identity}.", percept_identity=str(percept.identity), percept_kind=percept.kind.value)
            workspace.percepts.register(percept); workspace.record(EventKind.PERCEPT_RECORDED, f"Recorded percept {percept.identity}.", percept_identity=str(percept.identity))
        workspace.record(EventKind.EXECUTION_SUCCEEDED, f"Capability {capability.__name__} completed.", capability_name=capability.__name__)
    all_percepts = workspace.percepts.all()
    return PerceptPipelineResult(grid, frame, workspace.observations.all(), workspace.measurements.all(), all_percepts[0], all_percepts[1:], tuple(workspace.trace))
