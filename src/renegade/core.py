"""Deterministic, inspectable primitives for one explicit execution attempt.

This module deliberately implements only observation, capability retrieval, execution,
trace recording, and memory recording. It does not validate or promote capabilities.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, TypeAlias

from .observations import Observation, ObservationFrame, ObservationRegistry
from .measurements import Measurement, MeasurementRegistry, MeasurementSet


Details: TypeAlias = tuple[tuple[str, Any], ...]
CapabilityFunction: TypeAlias = Callable[[Any], Any]


class EventKind(str, Enum):
    """Stable names for events emitted during one execution attempt."""

    OBSERVATION_RECORDED = "observation.recorded"
    CAPABILITY_RETRIEVED = "capability.retrieved"
    CAPABILITY_MISSING = "capability.missing"
    EXECUTION_SUCCEEDED = "execution.succeeded"
    EXECUTION_FAILED = "execution.failed"
    MEMORY_RECORDED = "memory.recorded"
    OBSERVATION_FRAME_RECEIVED = "observation.frame.received"
    OBSERVATION_REGISTERED = "observation.registered"
    MEASUREMENT_CREATED = "measurement.created"
    MEASUREMENT_RECORDED = "measurement.recorded"


class Outcome(str, Enum):
    """The inspectable result of an execution attempt."""

    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass(frozen=True)
class Capability:
    """A bounded deterministic operation with minimal identity and provenance."""

    name: str
    description: str
    function: CapabilityFunction
    version: str = "0.1.0"
    location: str = "capability"
    source: str = "foundational primitive"
    creation_reason: str = "Provide a deterministic reusable operation."

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("capability name must be a non-empty string")
        if not isinstance(self.description, str) or not self.description:
            raise ValueError("capability description must be a non-empty string")
        if not callable(self.function):
            raise TypeError("capability function must be callable")

    def execute(self, value: Any) -> Any:
        """Execute the capability; callers record any resulting failure explicitly."""
        return self.function(value)


@dataclass(frozen=True)
class ExecutionEvent:
    """An immutable, ordered explanation of an execution-attempt event."""

    sequence: int
    kind: EventKind
    message: str
    details: Details = ()


@dataclass(frozen=True)
class MemoryEvent:
    """A durable record that links a successful execution to its provenance."""

    sequence: int
    capability_name: str
    capability_version: str
    observation_name: str
    outcome: Outcome
    observation_identity: str | None = None
    frame_identity: str | None = None


@dataclass
class Memory:
    """Capability registry and append-only execution records."""

    capabilities: dict[str, Capability] = field(default_factory=dict)
    history: list[MemoryEvent] = field(default_factory=list)

    def remember_capability(self, capability: Capability) -> None:
        """Register a capability by its stable name."""
        self.capabilities[capability.name] = capability

    def record_execution(
        self,
        capability: Capability,
        observation: Observation | None,
        outcome: Outcome,
        frame: ObservationFrame | None = None,
    ) -> MemoryEvent:
        """Append a provenance-preserving record of an execution attempt."""
        event = MemoryEvent(
            sequence=len(self.history) + 1,
            capability_name=capability.name,
            capability_version=capability.version,
            observation_name=(
                observation.name or str(observation.identity) if observation else "frame"
            ),
            outcome=outcome,
            observation_identity=str(observation.identity) if observation else None,
            frame_identity=str(frame.identity) if frame else None,
        )
        self.history.append(event)
        return event


@dataclass
class Workspace:
    """The inspectable active state for one deterministic execution attempt."""

    observation: Observation | None = None
    frame: ObservationFrame | None = None
    observations: ObservationRegistry = field(default_factory=ObservationRegistry)
    measurements: MeasurementRegistry = field(default_factory=MeasurementRegistry)
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

    def solve(
        self, observation: Observation | ObservationFrame, capability_name: str
    ) -> Workspace:
        """Run observation → retrieval → execution → result → trace → memory.

        Invalid request objects raise ``TypeError`` before a workspace can exist.
        Missing capabilities and capability input errors instead return a failed,
        inspectable workspace with an explanatory event trace.
        """
        if not isinstance(observation, (Observation, ObservationFrame)):
            raise TypeError("observation must be an Observation or ObservationFrame")
        if not isinstance(capability_name, str) or not capability_name:
            raise ValueError("capability_name must be a non-empty string")

        frame = observation if isinstance(observation, ObservationFrame) else None
        primary = (
            observation if isinstance(observation, Observation) else observation.observations[0]
        )
        workspace = Workspace(observation=primary, frame=frame)
        if frame is None:
            workspace.observations.register(primary)
            workspace.record(
                EventKind.OBSERVATION_RECORDED,
                f"Observed {primary.name or primary.identity}.",
                observation_name=primary.name,
                observation_identity=str(primary.identity),
                value=primary.value,
            )
        else:
            workspace.record(
                EventKind.OBSERVATION_FRAME_RECEIVED,
                f"Received observation frame {frame.identity}.",
                frame_identity=str(frame.identity),
                observation_count=len(frame.observations),
            )
            for item in frame:
                workspace.observations.register(item)
                workspace.record(
                    EventKind.OBSERVATION_REGISTERED,
                    f"Registered observation {item.identity}.",
                    observation_identity=str(item.identity),
                    observation_kind=item.kind.value,
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
            capability_name=capability.name,
            capability_version=capability.version,
        )
        try:
            workspace.result = capability.execute(frame if frame is not None else primary.value)
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
            produced = (workspace.result.measurements if isinstance(workspace.result, MeasurementSet)
                        else (workspace.result,) if isinstance(workspace.result, Measurement) else ())
            for measurement in produced:
                workspace.record(
                    EventKind.MEASUREMENT_CREATED,
                    f"Capability {capability.name} created measurement {measurement.identity}.",
                    measurement_identity=str(measurement.identity), measurement_kind=measurement.kind.value,
                )
                workspace.measurements.register(measurement)
                workspace.record(
                    EventKind.MEASUREMENT_RECORDED,
                    f"Recorded measurement {measurement.identity} in workspace.",
                    measurement_identity=str(measurement.identity),
                )
            workspace.record(
                EventKind.EXECUTION_SUCCEEDED,
                f"Capability {capability.name} produced a result.",
                capability_name=capability.name,
                result=workspace.result,
            )

        memory_event = self.memory.record_execution(capability, primary, workspace.outcome, frame)
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
