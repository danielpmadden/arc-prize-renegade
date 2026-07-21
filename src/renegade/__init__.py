"""Intentional public API for Renegade's deterministic structural pipeline."""

from .core import (
    Capability,
    EventKind,
    ExecutionEvent,
    Executive,
    Memory,
    MemoryEvent,
    Observation,
    Outcome,
    Workspace,
    double_number,
)
from .concepts import Concept, ConceptCategory
from .foundation import EvidenceKind, EvidenceReference, StableIdentifier
from .observations import ObservationFrame, ObservationKind, ObservationRegistry
from .measurements import (
    Measurement, MeasurementKind, MeasurementRegistry, MeasurementSet,
    measure_bounds, measure_dimensions, measure_observation_count,
)
from .percepts import Percept, PerceptKind, PerceptRegistry, PerceptSet, form_connected_regions, form_frame_percept
from .pipeline import PerceptPipelineResult, inspect_grid
from .relationships import PerceptGraph, RelationshipDirection, RelationshipKind, RelationshipRegistry, RelationshipSet, StructuralRelationship, derive_alignment_relationships, derive_exact_comparison_relationships, derive_frame_relationships, derive_relationships, derive_spatial_relationships, derive_topological_relationships
from .invariants import Invariant, InvariantKind, InvariantRegistry, InvariantSet, derive_invariants, derive_same_bounds_groups, derive_same_cell_count_groups, derive_same_shape_groups, derive_same_value_groups, derive_translation_families
from .archetypes import Archetype, ArchetypeKind, ArchetypeRegistry, ArchetypeSet, derive_archetypes
from .diagnostics import PipelineDiagnostics, summarize_pipeline
from .tasks import GridRole, Task, TaskGrid, TaskKind, TrainingPair, inspect_task, load_task
from .diagnostics import TaskDiagnostics, TaskGridDiagnostics, TrainingPairDiagnostics, summarize_task, summarize_task_grid, summarize_training_pair

__all__ = [
    "Capability",
    "Concept",
    "ConceptCategory",
    "EvidenceKind",
    "EvidenceReference",
    "EventKind",
    "ExecutionEvent",
    "Executive",
    "Measurement",
    "MeasurementKind",
    "MeasurementRegistry",
    "MeasurementSet",
    "Memory",
    "MemoryEvent",
    "Observation",
    "ObservationFrame",
    "ObservationKind",
    "ObservationRegistry",
    "Outcome",
    "Workspace",
    "StableIdentifier",
    "double_number",
    "measure_bounds",
    "measure_dimensions",
    "measure_observation_count",
    "Percept", "PerceptKind", "PerceptRegistry", "PerceptSet",
    "PerceptPipelineResult", "form_connected_regions", "form_frame_percept", "inspect_grid",
    "PerceptGraph", "RelationshipDirection", "RelationshipKind", "RelationshipRegistry", "RelationshipSet", "StructuralRelationship", "derive_relationships",
    "derive_topological_relationships", "derive_spatial_relationships", "derive_alignment_relationships", "derive_exact_comparison_relationships", "derive_frame_relationships",
    "Invariant", "InvariantKind", "InvariantRegistry", "InvariantSet", "derive_invariants", "derive_same_value_groups", "derive_same_shape_groups", "derive_same_cell_count_groups", "derive_same_bounds_groups", "derive_translation_families",
    "Archetype", "ArchetypeKind", "ArchetypeRegistry", "ArchetypeSet", "derive_archetypes",
    "PipelineDiagnostics", "summarize_pipeline",
    "GridRole", "Task", "TaskGrid", "TaskKind", "TrainingPair", "inspect_task", "load_task",
    "TaskDiagnostics", "TaskGridDiagnostics", "TrainingPairDiagnostics", "summarize_task", "summarize_task_grid", "summarize_training_pair",
]
from .solver import ChangeKind, ChangeSummary, Correspondence, Operation, Program, SolverResult, Validation, apply, correspondence, execute, solve_task
__all__ += ["ChangeKind", "ChangeSummary", "Correspondence", "Operation", "Program", "SolverResult", "Validation", "apply", "correspondence", "execute", "solve_task"]
from .generator import DIFFICULTIES, GeneratedTask, canonical_hash, difficulty_spec, generate_batch, generate_task, validate_generated
__all__ += ["DIFFICULTIES", "GeneratedTask", "canonical_hash", "difficulty_spec", "generate_batch", "generate_task", "validate_generated"]
