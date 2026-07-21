"""Deterministic structural percept formation without semantic interpretation."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from enum import Enum

from .foundation import EvidenceReference, StableIdentifier
from .observations import Observation, ObservationFrame, _references


class PerceptKind(str, Enum):
    """Structural formation categories, never semantic classifications."""

    FRAME = "frame"
    REGION = "region"


@dataclass(frozen=True, eq=False)
class Percept:
    """An immutable, identity-based organization of recorded structure."""

    identity: StableIdentifier
    kind: PerceptKind
    producing_capability: str
    observation_references: tuple[StableIdentifier, ...]
    measurement_references: tuple[StableIdentifier, ...] = ()
    evidence: tuple[EvidenceReference, ...] = ()
    parent_frame: StableIdentifier | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.identity, StableIdentifier):
            raise TypeError("percept identity must be a StableIdentifier")
        if not isinstance(self.kind, PerceptKind):
            raise TypeError("percept kind must be a PerceptKind")
        if not isinstance(self.producing_capability, str) or not self.producing_capability:
            raise ValueError("producing_capability must be a non-empty string")
        _references(self.observation_references, "observation_references")
        if not self.observation_references:
            raise ValueError("percept requires at least one observation reference")
        _references(self.measurement_references, "measurement_references")
        if not isinstance(self.evidence, tuple) or not all(isinstance(item, EvidenceReference) for item in self.evidence):
            raise TypeError("percept evidence must be a tuple of EvidenceReference values")
        if self.parent_frame is not None and not isinstance(self.parent_frame, StableIdentifier):
            raise TypeError("parent_frame must be a StableIdentifier or None")

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Percept) and self.identity == other.identity

    def __hash__(self) -> int:
        return hash(self.identity)


@dataclass(frozen=True)
class PerceptSet:
    """A non-empty ordered grouping with no implicit relationships."""

    identity: StableIdentifier
    percepts: tuple[Percept, ...]
    producing_capability: str

    def __post_init__(self) -> None:
        if not isinstance(self.identity, StableIdentifier):
            raise TypeError("percept set identity must be a StableIdentifier")
        if not isinstance(self.percepts, tuple) or not self.percepts:
            raise ValueError("percept set percepts must be a non-empty tuple")
        if not all(isinstance(item, Percept) for item in self.percepts):
            raise TypeError("percept set percepts must contain Percept values")
        if len({item.identity for item in self.percepts}) != len(self.percepts):
            raise ValueError("percept set must not contain duplicate percept identities")
        if not isinstance(self.producing_capability, str) or not self.producing_capability:
            raise ValueError("producing_capability must be a non-empty string")

    def __iter__(self) -> Iterator[Percept]:
        return iter(self.percepts)


@dataclass
class PerceptRegistry:
    """Exact insertion-ordered percept registry with structural filters only."""

    _percepts: dict[StableIdentifier, Percept] = field(default_factory=dict)

    def register(self, percept: Percept) -> Percept:
        if not isinstance(percept, Percept):
            raise TypeError("percept must be a Percept")
        if percept.identity in self._percepts:
            raise ValueError(f"percept already registered: {percept.identity}")
        self._percepts[percept.identity] = percept
        return percept

    def get(self, identity: StableIdentifier) -> Percept:
        if not isinstance(identity, StableIdentifier):
            raise TypeError("percept identity must be a StableIdentifier")
        return self._percepts[identity]

    def all(self) -> tuple[Percept, ...]: return tuple(self._percepts.values())
    def by_kind(self, kind: PerceptKind) -> tuple[Percept, ...]:
        if not isinstance(kind, PerceptKind): raise TypeError("percept kind must be a PerceptKind")
        return tuple(item for item in self._percepts.values() if item.kind is kind)
    def by_capability(self, capability: str) -> tuple[Percept, ...]:
        if not isinstance(capability, str) or not capability: raise ValueError("capability must be a non-empty string")
        return tuple(item for item in self._percepts.values() if item.producing_capability == capability)
    def by_observation(self, identity: StableIdentifier) -> tuple[Percept, ...]:
        if not isinstance(identity, StableIdentifier): raise TypeError("observation identity must be a StableIdentifier")
        return tuple(item for item in self._percepts.values() if identity in item.observation_references)
    def by_parent_frame(self, identity: StableIdentifier) -> tuple[Percept, ...]:
        if not isinstance(identity, StableIdentifier): raise TypeError("frame identity must be a StableIdentifier")
        return tuple(item for item in self._percepts.values() if item.parent_frame == identity)


def form_frame_percept(frame: ObservationFrame, measurement_references: tuple[StableIdentifier, ...] = ()) -> Percept:
    """Form one whole-frame structural unit from all supplied observations."""
    if not isinstance(frame, ObservationFrame): raise TypeError("form_frame_percept requires an ObservationFrame")
    return Percept(StableIdentifier("percept", f"frame-{frame.identity.local_name}", frame.identity.revision), PerceptKind.FRAME,
        "form_frame_percept", tuple(item.identity for item in frame), measurement_references, frame.evidence, frame.identity)


def form_connected_regions(frame: ObservationFrame, measurement_references: tuple[StableIdentifier, ...] = ()) -> PerceptSet:
    """Form same-value orthogonal regions by row-major scan and U/R/D/L traversal."""
    if not isinstance(frame, ObservationFrame): raise TypeError("form_connected_regions requires an ObservationFrame")
    cells: dict[tuple[int, int], Observation] = {}
    for item in frame:
        if not (isinstance(item.value, tuple) and len(item.value) == 2 and isinstance(item.value[0], tuple) and len(item.value[0]) == 2):
            raise TypeError("connected-region formation requires coordinate cell observations")
        coordinate, _ = item.value
        if not all(isinstance(value, int) and not isinstance(value, bool) and value >= 0 for value in coordinate):
            raise TypeError("cell coordinates must be non-negative integer pairs")
        cells[coordinate] = item
    if not cells: raise ValueError("connected-region formation requires cells")
    height, width = max(row for row, _ in cells) + 1, max(column for _, column in cells) + 1
    if len(cells) != height * width: raise ValueError("cell observations must form a complete rectangle")
    assigned: set[tuple[int, int]] = set(); regions: list[Percept] = []
    for row in range(height):
        for column in range(width):
            start = (row, column)
            if start in assigned: continue
            value = cells[start].value[1]; assigned.add(start); queue = [start]; ordered: list[tuple[int, int]] = []
            while queue:
                coordinate = queue.pop(0); ordered.append(coordinate)
                for neighbor in ((coordinate[0] - 1, coordinate[1]), (coordinate[0], coordinate[1] + 1), (coordinate[0] + 1, coordinate[1]), (coordinate[0], coordinate[1] - 1)):
                    if neighbor in cells and neighbor not in assigned and cells[neighbor].value[1] == value:
                        assigned.add(neighbor); queue.append(neighbor)
            regions.append(Percept(StableIdentifier("percept", f"region-{frame.identity.local_name}-{len(regions) + 1}", frame.identity.revision), PerceptKind.REGION,
                "form_connected_regions", tuple(cells[coordinate].identity for coordinate in ordered), measurement_references, frame.evidence, frame.identity))
    return PerceptSet(StableIdentifier("percept-set", f"regions-{frame.identity.local_name}", frame.identity.revision), tuple(regions), "form_connected_regions")
