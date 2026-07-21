"""Deterministic structural motifs derived only from structural invariants.

Archetypes name exact arrangements encoded by invariant records.  They do not
inspect observations, percepts, or relationships and carry no semantic claim.
"""
from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from enum import Enum

from .foundation import EvidenceReference, StableIdentifier
from .invariants import Invariant, InvariantKind
from .observations import _references


class ArchetypeKind(str, Enum):
    SINGLE_CELL = "single_cell"
    HORIZONTAL_LINE = "horizontal_line"
    VERTICAL_LINE = "vertical_line"
    FILLED_RECTANGLE = "filled_rectangle"
    HOLLOW_RECTANGLE = "hollow_rectangle"
    SQUARE = "square"
    LINEAR_CHAIN = "linear_chain"
    TRANSLATION_ARRAY = "translation_array"
    CHECKERBOARD = "checkerboard"


@dataclass(frozen=True, eq=False)
class Archetype:
    """An immutable, identity-based exact motif over invariant provenance."""
    identity: StableIdentifier
    kind: ArchetypeKind
    invariant_references: tuple[StableIdentifier, ...]
    producing_capability: str
    parent_frame: StableIdentifier | None
    evidence: tuple[EvidenceReference, ...] = ()
    derivation: tuple[tuple[str, int], ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.identity, StableIdentifier): raise TypeError("archetype identity must be a StableIdentifier")
        if not isinstance(self.kind, ArchetypeKind): raise TypeError("kind must be an ArchetypeKind")
        _references(self.invariant_references, "invariant_references")
        if not self.invariant_references: raise ValueError("archetype requires invariant references")
        if not isinstance(self.producing_capability, str) or not self.producing_capability: raise ValueError("producing_capability must be a non-empty string")
        if self.parent_frame is not None and not isinstance(self.parent_frame, StableIdentifier): raise TypeError("parent_frame must be a StableIdentifier or None")
        if not isinstance(self.evidence, tuple) or not all(isinstance(item, EvidenceReference) for item in self.evidence): raise TypeError("evidence must be a tuple of EvidenceReference values")
        if not isinstance(self.derivation, tuple) or not all(isinstance(key, str) and isinstance(value, int) and not isinstance(value, bool) for key, value in self.derivation): raise TypeError("derivation must be a tuple of string, integer pairs")

    def __eq__(self, other: object) -> bool: return isinstance(other, Archetype) and self.identity == other.identity
    def __hash__(self) -> int: return hash(self.identity)
    def canonical_key(self) -> tuple[object, ...]: return (self.kind, self.invariant_references, self.parent_frame, self.derivation)


@dataclass(frozen=True)
class ArchetypeSet:
    identity: StableIdentifier
    archetypes: tuple[Archetype, ...]
    producing_capability: str
    def __post_init__(self) -> None:
        if not isinstance(self.identity, StableIdentifier): raise TypeError("archetype set identity must be a StableIdentifier")
        if not isinstance(self.archetypes, tuple) or not self.archetypes: raise ValueError("archetype set archetypes must be a non-empty tuple")
        if not all(isinstance(item, Archetype) for item in self.archetypes): raise TypeError("archetype set must contain Archetype values")
        if len({item.identity for item in self.archetypes}) != len(self.archetypes) or len({item.canonical_key() for item in self.archetypes}) != len(self.archetypes): raise ValueError("archetype set must not contain duplicates")
        if not isinstance(self.producing_capability, str) or not self.producing_capability: raise ValueError("producing_capability must be a non-empty string")
    def __iter__(self) -> Iterator[Archetype]: return iter(self.archetypes)


@dataclass
class ArchetypeRegistry:
    _archetypes: dict[StableIdentifier, Archetype] = field(default_factory=dict)
    def register(self, archetype: Archetype) -> Archetype:
        if not isinstance(archetype, Archetype): raise TypeError("archetype must be an Archetype")
        if archetype.identity in self._archetypes: raise ValueError(f"archetype already registered: {archetype.identity}")
        if any(item.canonical_key() == archetype.canonical_key() for item in self._archetypes.values()): raise ValueError("duplicate canonical archetype")
        self._archetypes[archetype.identity] = archetype; return archetype
    def get(self, identity: StableIdentifier) -> Archetype:
        if not isinstance(identity, StableIdentifier): raise TypeError("archetype identity must be a StableIdentifier")
        return self._archetypes[identity]
    def all(self) -> tuple[Archetype, ...]: return tuple(self._archetypes.values())
    def by_kind(self, kind: ArchetypeKind) -> tuple[Archetype, ...]:
        if not isinstance(kind, ArchetypeKind): raise TypeError("archetype kind must be an ArchetypeKind")
        return tuple(item for item in self.all() if item.kind is kind)
    def by_invariant(self, identity: StableIdentifier) -> tuple[Archetype, ...]:
        if not isinstance(identity, StableIdentifier): raise TypeError("invariant identity must be a StableIdentifier")
        return tuple(item for item in self.all() if identity in item.invariant_references)
    def by_parent_frame(self, identity: StableIdentifier) -> tuple[Archetype, ...]:
        if not isinstance(identity, StableIdentifier): raise TypeError("frame identity must be a StableIdentifier")
        return tuple(item for item in self.all() if item.parent_frame == identity)


def _metadata(invariant: Invariant) -> dict[str, int]: return dict(invariant.derivation)
def _matches(invariant: Invariant) -> tuple[ArchetypeKind, ...]:
    """Recognize only complete, explicit invariant metadata; never infer."""
    data = _metadata(invariant); height, width = data.get("height"), data.get("width")
    results: list[ArchetypeKind] = []
    if data.get("cell_count") == 1: results.append(ArchetypeKind.SINGLE_CELL)
    if height == 1 and isinstance(width, int) and width > 1: results.append(ArchetypeKind.HORIZONTAL_LINE)
    if width == 1 and isinstance(height, int) and height > 1: results.append(ArchetypeKind.VERTICAL_LINE)
    if height is not None and width is not None and data.get("cell_count") == height * width: results.append(ArchetypeKind.FILLED_RECTANGLE)
    if height is not None and width is not None and height > 1 and width > 1 and data.get("cell_count") == 2 * height + 2 * width - 4: results.append(ArchetypeKind.HOLLOW_RECTANGLE)
    if height is not None and width == height and height > 0: results.append(ArchetypeKind.SQUARE)
    if invariant.kind is InvariantKind.TRANSLATION_FAMILY and len(invariant.member_percepts) >= 3:
        results.extend((ArchetypeKind.LINEAR_CHAIN, ArchetypeKind.TRANSLATION_ARRAY))
    if data.get("checkerboard") == 1: results.append(ArchetypeKind.CHECKERBOARD)
    return tuple(results)


def derive_archetypes(invariants: tuple[Invariant, ...], frame: StableIdentifier) -> tuple[Archetype, ...]:
    """Derive exact archetypes from ordered invariant records only."""
    if not isinstance(invariants, tuple) or not all(isinstance(item, Invariant) for item in invariants): raise TypeError("invariants must be a tuple of Invariant values")
    if not isinstance(frame, StableIdentifier): raise TypeError("frame must be a StableIdentifier")
    out: list[Archetype] = []
    for invariant in invariants:
        if invariant.parent_frame != frame: continue
        for kind in _matches(invariant):
            out.append(Archetype(StableIdentifier("archetype", f"{frame.local_name}-{len(out) + 1}", frame.revision), kind, (invariant.identity,), "derive_archetypes", frame, invariant.evidence, invariant.derivation))
    return tuple(out)
