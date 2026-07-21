"""Deterministic summaries for inspecting an already-completed grid pipeline."""

from __future__ import annotations

from dataclasses import dataclass

from .pipeline import PerceptPipelineResult


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
