"""Deterministic recording values for supplied information, not interpretation."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass, field
from enum import Enum
import math
from typing import Any

from .foundation import EvidenceReference, StableIdentifier


class ObservationKind(str, Enum):
    """How information was recorded, without describing what it means."""

    RAW = "raw"
    STRUCTURED = "structured"
    FEATURE = "feature"
    EVENT = "event"
    STATE = "state"


@dataclass(frozen=True)
class FrozenValueMapping(Mapping[str, "ObservationValue"]):
    """A compact, immutable mapping accepted as an observation value."""

    entries: tuple[tuple[str, "ObservationValue"], ...]

    def __post_init__(self) -> None:
        if tuple(sorted(self.entries, key=lambda entry: entry[0])) != self.entries:
            raise ValueError("frozen mapping entries must be ordered by key")
        if len({key for key, _ in self.entries}) != len(self.entries):
            raise ValueError("frozen mapping keys must be unique")

    def __getitem__(self, key: str) -> "ObservationValue":
        for candidate, value in self.entries:
            if candidate == key:
                return value
        raise KeyError(key)

    def __iter__(self) -> Iterator[str]:
        return (key for key, _ in self.entries)

    def __len__(self) -> int:
        return len(self.entries)


ObservationValue = None | bool | int | float | str | bytes | tuple[Any, ...] | FrozenValueMapping


def _normalize_value(value: Any) -> ObservationValue:
    if value is None or isinstance(value, (bool, int, str, bytes)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("observation floats must be finite")
        return value
    if isinstance(value, tuple):
        return tuple(_normalize_value(item) for item in value)
    if isinstance(value, Mapping):
        entries: list[tuple[str, ObservationValue]] = []
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError("observation mapping keys must be strings")
            entries.append((key, _normalize_value(item)))
        return FrozenValueMapping(tuple(sorted(entries, key=lambda entry: entry[0])))
    raise TypeError("observation value must be an immutable supported value")


def _references(value: tuple[StableIdentifier, ...], label: str) -> None:
    if not isinstance(value, tuple) or not all(isinstance(item, StableIdentifier) for item in value):
        raise TypeError(f"{label} must be a tuple of StableIdentifier values")
    if len(set(value)) != len(value):
        raise ValueError(f"{label} must not contain duplicates")


@dataclass(frozen=True, eq=False)
class Observation:
    """Immutable supplied information; its identity, not payload, determines equality.

    ``name`` is a compatibility label for the Pass 1 API.  New callers provide
    ``identity`` directly.  A legacy name deterministically maps to
    ``observation:<name>:1`` and never uses time or randomness.
    """

    value: ObservationValue
    identity: StableIdentifier | None = None
    kind: ObservationKind = ObservationKind.RAW
    source: str = "supplied"
    evidence: tuple[EvidenceReference, ...] = ()
    concept_references: tuple[StableIdentifier, ...] = ()
    description: str | None = None
    name: str | None = None

    def __post_init__(self) -> None:
        identity = self.identity
        if identity is None:
            if not isinstance(self.name, str) or not self.name:
                raise ValueError("observation identity is required when name is not supplied")
            identity = StableIdentifier("observation", self.name, 1)
            object.__setattr__(self, "identity", identity)
        if not isinstance(identity, StableIdentifier):
            raise TypeError("observation identity must be a StableIdentifier")
        if not isinstance(self.kind, ObservationKind):
            raise TypeError("observation kind must be an ObservationKind")
        if not isinstance(self.source, str) or not self.source:
            raise ValueError("observation source must be a non-empty string")
        if self.description is not None and not isinstance(self.description, str):
            raise TypeError("observation description must be a string or None")
        if self.name is not None and (not isinstance(self.name, str) or not self.name):
            raise ValueError("observation name must be a non-empty string or None")
        if not isinstance(self.evidence, tuple) or not all(
            isinstance(reference, EvidenceReference) for reference in self.evidence
        ):
            raise TypeError("observation evidence must be a tuple of EvidenceReference values")
        _references(self.concept_references, "concept_references")
        object.__setattr__(self, "value", _normalize_value(self.value))

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Observation) and self.identity == other.identity

    def __hash__(self) -> int:
        return hash(self.identity)


@dataclass(frozen=True)
class ObservationFrame:
    """An ordered grouping that asserts only joint recording, not a relationship."""

    identity: StableIdentifier
    observations: tuple[Observation, ...]
    source: str | None = None
    evidence: tuple[EvidenceReference, ...] = ()
    concept_references: tuple[StableIdentifier, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.identity, StableIdentifier):
            raise TypeError("frame identity must be a StableIdentifier")
        if not isinstance(self.observations, tuple) or not self.observations:
            raise ValueError("frame observations must be a non-empty tuple")
        if not all(isinstance(item, Observation) for item in self.observations):
            raise TypeError("frame observations must contain Observation values")
        identities = tuple(item.identity for item in self.observations)
        if len(set(identities)) != len(identities):
            raise ValueError("frame must not contain duplicate observation identities")
        if self.source is not None and (not isinstance(self.source, str) or not self.source):
            raise ValueError("frame source must be a non-empty string or None")
        if not isinstance(self.evidence, tuple) or not all(
            isinstance(reference, EvidenceReference) for reference in self.evidence
        ):
            raise TypeError("frame evidence must be a tuple of EvidenceReference values")
        _references(self.concept_references, "concept_references")

    def __iter__(self) -> Iterator[Observation]:
        return iter(self.observations)


@dataclass
class ObservationRegistry:
    """Small ordered exact-identity registry with no similarity behavior."""

    _observations: dict[StableIdentifier, Observation] = field(default_factory=dict)

    def register(self, observation: Observation) -> Observation:
        if not isinstance(observation, Observation):
            raise TypeError("observation must be an Observation")
        if observation.identity in self._observations:
            raise ValueError(f"observation already registered: {observation.identity}")
        self._observations[observation.identity] = observation
        return observation

    def get(self, identity: StableIdentifier) -> Observation:
        if not isinstance(identity, StableIdentifier):
            raise TypeError("observation identity must be a StableIdentifier")
        return self._observations[identity]

    def all(self) -> tuple[Observation, ...]:
        return tuple(self._observations.values())

    def by_kind(self, kind: ObservationKind) -> tuple[Observation, ...]:
        if not isinstance(kind, ObservationKind):
            raise TypeError("observation kind must be an ObservationKind")
        return tuple(item for item in self._observations.values() if item.kind is kind)

    def by_concept(self, identity: StableIdentifier) -> tuple[Observation, ...]:
        if not isinstance(identity, StableIdentifier):
            raise TypeError("concept identity must be a StableIdentifier")
        return tuple(item for item in self._observations.values() if identity in item.concept_references)
