"""Deterministic, inspectable primitives for the first Renegade reasoning cycle.

This module deliberately implements only observation, capability retrieval, execution,
trace recording, and memory recording. It does not validate or promote capabilities.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Any, Callable, TypeAlias

from .foundation import (
    EvidenceReference,
    LifecycleState,
    LifecycleTransition,
    LineageEdge,
    StableIdentifier,
    decide_transition,
)


Details: TypeAlias = tuple[tuple[str, Any], ...]
CapabilityFunction: TypeAlias = Callable[[Any], Any]


class EventKind(str, Enum):
    """Stable names for events emitted during one reasoning attempt."""

    OBSERVATION_RECORDED = "observation.recorded"
    CAPABILITY_RETRIEVED = "capability.retrieved"
    CAPABILITY_MISSING = "capability.missing"
    CAPABILITY_INELIGIBLE = "capability.ineligible"
    EXECUTION_SUCCEEDED = "execution.succeeded"
    EXECUTION_FAILED = "execution.failed"
    MEMORY_RECORDED = "memory.recorded"


class Outcome(str, Enum):
    """The inspectable result of a reasoning attempt."""

    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass(frozen=True)
class Observation:
    """A named value presented as evidence to the system."""

    name: str
    value: Any

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("observation name must be a non-empty string")


@dataclass(frozen=True)
class Capability:
    """A deterministic operation with explicit identity, status, and provenance."""

    name: str
    description: str
    function: CapabilityFunction
    identity: StableIdentifier
    version: str = "0.1.0"
    location: str = "capability"
    source: str = "foundational primitive"
    creation_reason: str = "Provide a deterministic reusable operation."
    lifecycle_state: LifecycleState = LifecycleState.PROTOTYPE
    lineage: tuple[LineageEdge, ...] = ()
    lifecycle_history: tuple[LifecycleTransition, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("capability name must be a non-empty string")
        if not isinstance(self.description, str) or not self.description:
            raise ValueError("capability description must be a non-empty string")
        if not callable(self.function):
            raise TypeError("capability function must be callable")
        if self.identity.category != "capability":
            raise ValueError("capability identity must use the capability category")
        if any(edge.source != self.identity for edge in self.lineage):
            raise ValueError("capability lineage edges must originate from its identity")

    def transition_to(
        self,
        requested_state: LifecycleState,
        reason: str,
        evidence: tuple[EvidenceReference, ...],
    ) -> Capability:
        """Return a successor capability after one explicit, valid transition."""
        transition = decide_transition(
            self.lifecycle_state, requested_state, reason, evidence
        )
        return replace(
            self,
            lifecycle_state=requested_state,
            lifecycle_history=(*self.lifecycle_history, transition),
        )

    def execute(self, value: Any) -> Any:
        """Execute the capability; callers record any resulting failure explicitly."""
        return self.function(value)


@dataclass(frozen=True)
class ExecutionEvent:
    """An immutable, ordered explanation of a reasoning-cycle event."""

    sequence: int
    kind: EventKind
    message: str
    details: Details = ()


@dataclass(frozen=True)
class MemoryEvent:
    """A durable record that links an execution outcome to its provenance."""

    sequence: int
    capability_name: str
    capability_version: str
    observation_name: str
    outcome: Outcome


@dataclass
class Memory:
    """Capability registry and append-only execution records."""

    capabilities: dict[str, Capability] = field(default_factory=dict)
    history: list[MemoryEvent] = field(default_factory=list)

    def remember_capability(self, capability: Capability) -> None:
        """Register a capability by its stable name."""
        self.capabilities[capability.name] = capability

    def record_execution(
        self, capability: Capability, observation: Observation, outcome: Outcome
    ) -> MemoryEvent:
        """Append a provenance-preserving record of an execution attempt."""
        event = MemoryEvent(
            sequence=len(self.history) + 1,
            capability_name=capability.name,
            capability_version=capability.version,
            observation_name=observation.name,
            outcome=outcome,
        )
        self.history.append(event)
        return event


@dataclass
class Workspace:
    """The inspectable active state for one deterministic reasoning attempt."""

    observation: Observation
    result: Any | None = None
    outcome: Outcome = Outcome.PENDING
    failure_reason: str | None = None
    trace: list[ExecutionEvent] = field(default_factory=list)

    def record(self, kind: EventKind, message: str, **details: Any) -> ExecutionEvent:
        """Append an event with a deterministic, attempt-local sequence number."""
        event = ExecutionEvent(
            sequence=len(self.trace) + 1,
            kind=kind,
            message=message,
            details=tuple(details.items()),
        )
        self.trace.append(event)
        return event


class Executive:
    """Retrieve one requested capability and execute it without broad search."""

    def __init__(self, memory: Memory) -> None:
        self.memory = memory

    def solve(self, observation: Observation, capability_name: str) -> Workspace:
        """Run observation → retrieval → execution → result → trace → memory.

        Invalid request objects raise ``TypeError`` before a workspace can exist.
        Missing capabilities and capability input errors instead return a failed,
        inspectable workspace with an explanatory event trace.
        """
        if not isinstance(observation, Observation):
            raise TypeError("observation must be an Observation")
        if not isinstance(capability_name, str) or not capability_name:
            raise ValueError("capability_name must be a non-empty string")

        workspace = Workspace(observation=observation)
        workspace.record(
            EventKind.OBSERVATION_RECORDED,
            f"Observed {observation.name}.",
            observation_name=observation.name,
            value=observation.value,
        )
        capability = self.memory.capabilities.get(capability_name)
        if capability is None:
            workspace.outcome = Outcome.FAILED
            workspace.failure_reason = f"Capability not found: {capability_name}"
            workspace.record(
                EventKind.CAPABILITY_MISSING,
                workspace.failure_reason,
                capability_name=capability_name,
            )
            return workspace

        workspace.record(
            EventKind.CAPABILITY_RETRIEVED,
            f"Selected capability {capability.name}.",
            capability_identity=str(capability.identity),
            capability_name=capability.name,
            capability_version=capability.version,
            lifecycle_state=capability.lifecycle_state.value,
        )
        if capability.lifecycle_state in {
            LifecycleState.DEPRECATED,
            LifecycleState.ARCHIVED,
            LifecycleState.RETIRED,
        }:
            workspace.outcome = Outcome.FAILED
            workspace.failure_reason = (
                f"Capability {capability.name} is not executable while "
                f"{capability.lifecycle_state.value}."
            )
            workspace.record(
                EventKind.CAPABILITY_INELIGIBLE,
                workspace.failure_reason,
                capability_identity=str(capability.identity),
                lifecycle_state=capability.lifecycle_state.value,
            )
            return workspace
        try:
            workspace.result = capability.execute(observation.value)
        except (TypeError, ValueError) as error:
            workspace.outcome = Outcome.FAILED
            workspace.failure_reason = str(error)
            workspace.record(
                EventKind.EXECUTION_FAILED,
                f"Capability {capability.name} failed: {error}",
                capability_name=capability.name,
                error_type=type(error).__name__,
                failure_reason=str(error),
            )
        else:
            workspace.outcome = Outcome.SUCCEEDED
            workspace.record(
                EventKind.EXECUTION_SUCCEEDED,
                f"Capability {capability.name} produced a result.",
                capability_name=capability.name,
                result=workspace.result,
            )

        memory_event = self.memory.record_execution(capability, observation, workspace.outcome)
        workspace.record(
            EventKind.MEMORY_RECORDED,
            f"Recorded execution of {capability.name} in memory.",
            # The durable record has a memory-local sequence number.  Do not
            # expose it in the attempt trace: an equivalent request must keep
            # an equivalent explanation even after prior memory activity.
            outcome=memory_event.outcome.value,
        )
        return workspace


def double_number(value: Any) -> int:
    """Return twice an integer, rejecting non-integer input explicitly."""
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError("double_number requires an integer")
    return value * 2
