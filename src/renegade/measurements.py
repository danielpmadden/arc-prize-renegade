"""Deterministic, provenance-preserving computed properties.

Measurements report reproducible properties of supplied observations.  They do
not assign semantic meaning, classify inputs, or establish truth.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .foundation import EvidenceReference, StableIdentifier
from .observations import FrozenValueMapping, Observation, ObservationFrame, ObservationValue, _normalize_value, _references


class MeasurementKind(str, Enum):
    """A small vocabulary for property categories, not categories of things."""

    DIMENSION = "dimension"
    COUNT = "count"
    POSITION = "position"
    BOUND = "bound"
    DISTANCE = "distance"
    HISTOGRAM = "histogram"
    ATTRIBUTE = "attribute"
    STRUCTURE = "structure"


MeasurementValue = ObservationValue


@dataclass(frozen=True, eq=False)
class Measurement:
    """One immutable computed property with explicit production provenance."""

    identity: StableIdentifier
    kind: MeasurementKind
    value: MeasurementValue
    observation_references: tuple[StableIdentifier, ...]
    producing_capability: str
    evidence: tuple[EvidenceReference, ...] = ()
    concept_references: tuple[StableIdentifier, ...] = ()
    description: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.identity, StableIdentifier):
            raise TypeError("measurement identity must be a StableIdentifier")
        if not isinstance(self.kind, MeasurementKind):
            raise TypeError("measurement kind must be a MeasurementKind")
        _references(self.observation_references, "observation_references")
        if not self.observation_references:
            raise ValueError("measurement requires at least one observation reference")
        if not isinstance(self.producing_capability, str) or not self.producing_capability:
            raise ValueError("producing_capability must be a non-empty string")
        if not isinstance(self.evidence, tuple) or not all(
            isinstance(reference, EvidenceReference) for reference in self.evidence
        ):
            raise TypeError("measurement evidence must be a tuple of EvidenceReference values")
        _references(self.concept_references, "concept_references")
        if self.description is not None and not isinstance(self.description, str):
            raise TypeError("measurement description must be a string or None")
        object.__setattr__(self, "value", _normalize_value(self.value))

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Measurement) and self.identity == other.identity

    def __hash__(self) -> int:
        return hash(self.identity)


@dataclass(frozen=True)
class MeasurementSet:
    """An ordered grouping with common production context and no semantic claim."""

    identity: StableIdentifier
    measurements: tuple[Measurement, ...]
    source_observations: tuple[StableIdentifier, ...]
    producing_capability: str
    evidence: tuple[EvidenceReference, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.identity, StableIdentifier):
            raise TypeError("measurement set identity must be a StableIdentifier")
        if not isinstance(self.measurements, tuple) or not self.measurements:
            raise ValueError("measurement set measurements must be a non-empty tuple")
        if not all(isinstance(item, Measurement) for item in self.measurements):
            raise TypeError("measurement set measurements must contain Measurement values")
        identities = tuple(item.identity for item in self.measurements)
        if len(set(identities)) != len(identities):
            raise ValueError("measurement set must not contain duplicate measurement identities")
        _references(self.source_observations, "source_observations")
        if not self.source_observations:
            raise ValueError("measurement set requires at least one source observation")
        if not isinstance(self.producing_capability, str) or not self.producing_capability:
            raise ValueError("producing_capability must be a non-empty string")
        if not isinstance(self.evidence, tuple) or not all(
            isinstance(reference, EvidenceReference) for reference in self.evidence
        ):
            raise TypeError("measurement set evidence must be a tuple of EvidenceReference values")

    def __iter__(self) -> Iterator[Measurement]:
        return iter(self.measurements)


@dataclass
class MeasurementRegistry:
    """Exact, insertion-ordered measurement lookup with no ranking or inference."""

    _measurements: dict[StableIdentifier, Measurement] = field(default_factory=dict)

    def register(self, measurement: Measurement) -> Measurement:
        if not isinstance(measurement, Measurement):
            raise TypeError("measurement must be a Measurement")
        if measurement.identity in self._measurements:
            raise ValueError(f"measurement already registered: {measurement.identity}")
        self._measurements[measurement.identity] = measurement
        return measurement

    def get(self, identity: StableIdentifier) -> Measurement:
        if not isinstance(identity, StableIdentifier):
            raise TypeError("measurement identity must be a StableIdentifier")
        return self._measurements[identity]

    def all(self) -> tuple[Measurement, ...]:
        return tuple(self._measurements.values())

    def by_kind(self, kind: MeasurementKind) -> tuple[Measurement, ...]:
        if not isinstance(kind, MeasurementKind):
            raise TypeError("measurement kind must be a MeasurementKind")
        return tuple(item for item in self._measurements.values() if item.kind is kind)

    def by_capability(self, capability: str) -> tuple[Measurement, ...]:
        if not isinstance(capability, str) or not capability:
            raise ValueError("capability must be a non-empty string")
        return tuple(item for item in self._measurements.values() if item.producing_capability == capability)

    def by_observation(self, identity: StableIdentifier) -> tuple[Measurement, ...]:
        if not isinstance(identity, StableIdentifier):
            raise TypeError("observation identity must be a StableIdentifier")
        return tuple(item for item in self._measurements.values() if identity in item.observation_references)


def _grid(observation: Observation) -> tuple[int, int]:
    """Return supplied tuple-grid dimensions, rejecting non-rectangular input."""
    value = observation.value
    if not isinstance(value, tuple) or not value or not all(isinstance(row, tuple) for row in value):
        raise TypeError("grid measurement requires a non-empty tuple of tuple rows")
    width = len(value[0])
    if any(len(row) != width for row in value):
        raise ValueError("grid measurement requires rows with equal length")
    return len(value), width


def _measurement_identity(kind: str, observation: Observation) -> StableIdentifier:
    return StableIdentifier("measurement", f"{kind}-{observation.identity.local_name}", observation.identity.revision)


def measure_dimensions(frame: ObservationFrame) -> Measurement:
    """Measure the height and width of the frame's first supplied tuple grid."""
    if not isinstance(frame, ObservationFrame):
        raise TypeError("measure_dimensions requires an ObservationFrame")
    observation = frame.observations[0]
    height, width = _grid(observation)
    return Measurement(_measurement_identity("dimensions", observation), MeasurementKind.DIMENSION,
                       {"height": height, "width": width}, (observation.identity,), "measure_dimensions")


def measure_bounds(frame: ObservationFrame) -> Measurement:
    """Measure inclusive coordinate bounds of the frame's first supplied tuple grid."""
    if not isinstance(frame, ObservationFrame):
        raise TypeError("measure_bounds requires an ObservationFrame")
    observation = frame.observations[0]
    height, width = _grid(observation)
    return Measurement(_measurement_identity("bounds", observation), MeasurementKind.BOUND,
                       {"column_max": width - 1, "column_min": 0, "row_max": height - 1, "row_min": 0},
                       (observation.identity,), "measure_bounds")


def measure_observation_count(frame: ObservationFrame) -> Measurement:
    """Measure the number of observations supplied in one frame."""
    if not isinstance(frame, ObservationFrame):
        raise TypeError("measure_observation_count requires an ObservationFrame")
    return Measurement(StableIdentifier("measurement", f"observation-count-{frame.identity.local_name}", frame.identity.revision),
                       MeasurementKind.COUNT, len(frame.observations),
                       tuple(item.identity for item in frame), "measure_observation_count")
