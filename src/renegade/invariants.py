"""Deterministic compressed regularities over explicit relationship records.

Invariants group repeated structural facts. They neither inspect observations nor
assign concepts, interpretations, or causes.
"""
from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from enum import Enum

from .foundation import EvidenceReference, StableIdentifier
from .observations import _references
from .relationships import RelationshipKind, StructuralRelationship


class InvariantKind(str, Enum):
    SAME_VALUE_GROUP = "same_value_group"
    SAME_SHAPE_GROUP = "same_shape_group"
    SAME_CELL_COUNT_GROUP = "same_cell_count_group"
    SAME_BOUNDS_GROUP = "same_bounds_group"
    TRANSLATION_FAMILY = "translation_family"


@dataclass(frozen=True, eq=False)
class Invariant:
    """An immutable identity-based compression of explicit relationships."""
    identity: StableIdentifier
    kind: InvariantKind
    member_percepts: tuple[StableIdentifier, ...]
    relationship_references: tuple[StableIdentifier, ...]
    producing_capability: str
    parent_frame: StableIdentifier | None
    evidence: tuple[EvidenceReference, ...] = ()
    derivation: tuple[tuple[str, int], ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.identity, StableIdentifier): raise TypeError("invariant identity must be a StableIdentifier")
        if not isinstance(self.kind, InvariantKind): raise TypeError("kind must be an InvariantKind")
        _references(self.member_percepts, "member_percepts")
        if len(self.member_percepts) < 2: raise ValueError("invariant requires at least two member percepts")
        _references(self.relationship_references, "relationship_references")
        if not self.relationship_references: raise ValueError("invariant requires relationship references")
        if not isinstance(self.producing_capability, str) or not self.producing_capability: raise ValueError("producing_capability must be a non-empty string")
        if self.parent_frame is not None and not isinstance(self.parent_frame, StableIdentifier): raise TypeError("parent_frame must be a StableIdentifier or None")
        if not isinstance(self.evidence, tuple) or not all(isinstance(x, EvidenceReference) for x in self.evidence): raise TypeError("evidence must be a tuple of EvidenceReference values")
        if not isinstance(self.derivation, tuple) or not all(isinstance(k, str) and isinstance(v, int) and not isinstance(v, bool) for k, v in self.derivation): raise TypeError("derivation must be a tuple of string, integer pairs")

    def __eq__(self, other: object) -> bool: return isinstance(other, Invariant) and self.identity == other.identity
    def __hash__(self) -> int: return hash(self.identity)
    def canonical_key(self): return (self.kind, self.member_percepts, self.parent_frame, self.derivation)


@dataclass(frozen=True)
class InvariantSet:
    identity: StableIdentifier; invariants: tuple[Invariant, ...]; producing_capability: str
    def __post_init__(self) -> None:
        if not isinstance(self.identity, StableIdentifier): raise TypeError("invariant set identity must be a StableIdentifier")
        if not isinstance(self.invariants, tuple) or not self.invariants: raise ValueError("invariant set invariants must be a non-empty tuple")
        if not all(isinstance(x, Invariant) for x in self.invariants): raise TypeError("invariant set must contain Invariant values")
        if len({x.identity for x in self.invariants}) != len(self.invariants) or len({x.canonical_key() for x in self.invariants}) != len(self.invariants): raise ValueError("invariant set must not contain duplicates")
    def __iter__(self) -> Iterator[Invariant]: return iter(self.invariants)


@dataclass
class InvariantRegistry:
    _invariants: dict[StableIdentifier, Invariant] = field(default_factory=dict)
    def register(self, invariant: Invariant) -> Invariant:
        if not isinstance(invariant, Invariant): raise TypeError("invariant must be an Invariant")
        if invariant.identity in self._invariants: raise ValueError(f"invariant already registered: {invariant.identity}")
        if any(x.canonical_key() == invariant.canonical_key() for x in self._invariants.values()): raise ValueError("duplicate canonical invariant")
        self._invariants[invariant.identity] = invariant; return invariant
    def get(self, identity: StableIdentifier) -> Invariant: return self._invariants[identity]
    def all(self) -> tuple[Invariant, ...]: return tuple(self._invariants.values())
    def by_kind(self, kind: InvariantKind) -> tuple[Invariant, ...]: return tuple(x for x in self.all() if x.kind is kind)
    def by_member(self, identity: StableIdentifier) -> tuple[Invariant, ...]: return tuple(x for x in self.all() if identity in x.member_percepts)
    def by_relationship(self, identity: StableIdentifier) -> tuple[Invariant, ...]: return tuple(x for x in self.all() if identity in x.relationship_references)
    def by_parent_frame(self, identity: StableIdentifier) -> tuple[Invariant, ...]: return tuple(x for x in self.all() if x.parent_frame == identity)


_GROUPS = (
    (InvariantKind.SAME_VALUE_GROUP, RelationshipKind.SAME_VALUE),
    (InvariantKind.SAME_SHAPE_GROUP, RelationshipKind.SAME_COORDINATE_SHAPE),
    (InvariantKind.SAME_CELL_COUNT_GROUP, RelationshipKind.SAME_CELL_COUNT),
    (InvariantKind.SAME_BOUNDS_GROUP, RelationshipKind.SAME_BOUNDS_SIZE),
)

def _components(relationships: tuple[StructuralRelationship, ...]):
    remaining = list(relationships); groups=[]
    while remaining:
        first=remaining.pop(0); members={first.source, first.target}; refs=[first]
        changed=True
        while changed:
            changed=False
            for item in tuple(remaining):
                if item.source in members or item.target in members:
                    members.update((item.source,item.target)); refs.append(item); remaining.remove(item); changed=True
        groups.append((tuple(sorted(members)), tuple(refs)))
    return groups

def derive_invariants(relationships: tuple[StructuralRelationship, ...], frame: StableIdentifier) -> tuple[Invariant, ...]:
    """Group existing relationships only, in kind then relationship order."""
    if not isinstance(relationships, tuple) or not all(isinstance(x, StructuralRelationship) for x in relationships): raise TypeError("relationships must be a tuple of StructuralRelationship values")
    if not isinstance(frame, StableIdentifier): raise TypeError("frame must be a StableIdentifier")
    out=[]
    for invariant_kind, relationship_kind in _GROUPS:
        for members, refs in _components(tuple(x for x in relationships if x.kind is relationship_kind)):
            out.append(Invariant(StableIdentifier("invariant", f"{frame.local_name}-{len(out)+1}", frame.revision), invariant_kind, members, tuple(x.identity for x in refs), "derive_invariants", frame, tuple(refs[0].evidence)))
    vectors=sorted({x.derivation for x in relationships if x.kind is RelationshipKind.TRANSLATED_COPY})
    for vector in vectors:
        matches=tuple(x for x in relationships if x.kind is RelationshipKind.TRANSLATED_COPY and x.derivation == vector)
        for members, refs in _components(matches):
            out.append(Invariant(StableIdentifier("invariant", f"{frame.local_name}-{len(out)+1}", frame.revision), InvariantKind.TRANSLATION_FAMILY, members, tuple(x.identity for x in refs), "derive_invariants", frame, tuple(refs[0].evidence), vector))
    return tuple(out)

def derive_same_value_groups(relationships, frame): return tuple(x for x in derive_invariants(relationships, frame) if x.kind is InvariantKind.SAME_VALUE_GROUP)
def derive_same_shape_groups(relationships, frame): return tuple(x for x in derive_invariants(relationships, frame) if x.kind is InvariantKind.SAME_SHAPE_GROUP)
def derive_same_cell_count_groups(relationships, frame): return tuple(x for x in derive_invariants(relationships, frame) if x.kind is InvariantKind.SAME_CELL_COUNT_GROUP)
def derive_same_bounds_groups(relationships, frame): return tuple(x for x in derive_invariants(relationships, frame) if x.kind is InvariantKind.SAME_BOUNDS_GROUP)
def derive_translation_families(relationships, frame): return tuple(x for x in derive_invariants(relationships, frame) if x.kind is InvariantKind.TRANSLATION_FAMILY)
