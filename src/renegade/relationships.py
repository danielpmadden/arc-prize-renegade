"""Exact, bounded structural relationships between already formed percepts.

This module records geometry only.  It neither assigns concepts nor interprets
the structural facts it derives.
"""
from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass, field
from enum import Enum

from .foundation import EvidenceReference, StableIdentifier
from .observations import Observation, _references
from .percepts import Percept, PerceptKind, PerceptRegistry


class RelationshipDirection(str, Enum):
    SYMMETRIC = "symmetric"
    DIRECTED = "directed"


class RelationshipKind(str, Enum):
    ORTHOGONALLY_ADJACENT = "orthogonally_adjacent"; DIAGONALLY_ADJACENT = "diagonally_adjacent"
    DISJOINT = "disjoint"; OVERLAPS = "overlaps"
    LEFT_OF = "left_of"; RIGHT_OF = "right_of"; ABOVE = "above"; BELOW = "below"
    SAME_ROW_SPAN = "same_row_span"; SAME_COLUMN_SPAN = "same_column_span"
    ROW_ALIGNED = "row_aligned"; COLUMN_ALIGNED = "column_aligned"
    SAME_VALUE = "same_value"; SAME_CELL_COUNT = "same_cell_count"; SAME_BOUNDS_SIZE = "same_bounds_size"
    SAME_COORDINATE_SHAPE = "same_coordinate_shape"; TRANSLATED_COPY = "translated_copy"
    TOUCHES_TOP_BOUNDARY = "touches_top_boundary"; TOUCHES_BOTTOM_BOUNDARY = "touches_bottom_boundary"
    TOUCHES_LEFT_BOUNDARY = "touches_left_boundary"; TOUCHES_RIGHT_BOUNDARY = "touches_right_boundary"
    TOUCHES_ANY_BOUNDARY = "touches_any_boundary"; TOUCHES_ALL_BOUNDARIES = "touches_all_boundaries"
    COORDINATE_SUBSET_OF = "coordinate_subset_of"; BOUNDS_WITHIN = "bounds_within"


_SYMMETRIC = frozenset({
    RelationshipKind.ORTHOGONALLY_ADJACENT, RelationshipKind.DIAGONALLY_ADJACENT,
    RelationshipKind.DISJOINT, RelationshipKind.OVERLAPS, RelationshipKind.SAME_ROW_SPAN,
    RelationshipKind.SAME_COLUMN_SPAN, RelationshipKind.ROW_ALIGNED,
    RelationshipKind.COLUMN_ALIGNED, RelationshipKind.SAME_VALUE, RelationshipKind.SAME_CELL_COUNT,
    RelationshipKind.SAME_BOUNDS_SIZE, RelationshipKind.SAME_COORDINATE_SHAPE,
    RelationshipKind.TRANSLATED_COPY,
})


@dataclass(frozen=True, eq=False)
class StructuralRelationship:
    """An identity-based, immutable, explicitly derived structural fact."""
    identity: StableIdentifier
    kind: RelationshipKind
    source: StableIdentifier
    target: StableIdentifier
    producing_capability: str
    parent_frame: StableIdentifier | None
    supporting_observations: tuple[StableIdentifier, ...] = ()
    supporting_measurements: tuple[StableIdentifier, ...] = ()
    evidence: tuple[EvidenceReference, ...] = ()
    derivation: tuple[tuple[str, int], ...] = ()

    def __post_init__(self) -> None:
        if not all(isinstance(x, StableIdentifier) for x in (self.identity, self.source, self.target)):
            raise TypeError("relationship identities must be StableIdentifier values")
        if not isinstance(self.kind, RelationshipKind): raise TypeError("kind must be a RelationshipKind")
        if self.source == self.target: raise ValueError("relationships cannot refer to themselves")
        if not isinstance(self.producing_capability, str) or not self.producing_capability: raise ValueError("producing_capability must be a non-empty string")
        if self.parent_frame is not None and not isinstance(self.parent_frame, StableIdentifier): raise TypeError("parent_frame must be a StableIdentifier or None")
        _references(self.supporting_observations, "supporting_observations"); _references(self.supporting_measurements, "supporting_measurements")
        if not isinstance(self.evidence, tuple) or not all(isinstance(x, EvidenceReference) for x in self.evidence): raise TypeError("evidence must be a tuple of EvidenceReference values")
        if not isinstance(self.derivation, tuple) or not all(isinstance(k, str) and isinstance(v, int) and not isinstance(v, bool) for k, v in self.derivation): raise TypeError("derivation must be a tuple of string, integer pairs")
        if self.direction is RelationshipDirection.SYMMETRIC and self.source > self.target: raise ValueError("symmetric endpoints must use canonical order")

    @property
    def direction(self) -> RelationshipDirection:
        return RelationshipDirection.SYMMETRIC if self.kind in _SYMMETRIC else RelationshipDirection.DIRECTED
    def __eq__(self, other: object) -> bool: return isinstance(other, StructuralRelationship) and self.identity == other.identity
    def __hash__(self) -> int: return hash(self.identity)
    def canonical_key(self) -> tuple[object, ...]: return (self.kind, self.source, self.target, self.parent_frame, self.derivation)


@dataclass(frozen=True)
class RelationshipSet:
    identity: StableIdentifier; relationships: tuple[StructuralRelationship, ...]; producing_capability: str
    def __post_init__(self) -> None:
        if not isinstance(self.identity, StableIdentifier): raise TypeError("relationship set identity must be a StableIdentifier")
        if not isinstance(self.relationships, tuple) or not self.relationships: raise ValueError("relationship set relationships must be a non-empty tuple")
        if not all(isinstance(x, StructuralRelationship) for x in self.relationships): raise TypeError("relationship set must contain StructuralRelationship values")
        if len({x.identity for x in self.relationships}) != len(self.relationships) or len({x.canonical_key() for x in self.relationships}) != len(self.relationships): raise ValueError("relationship set must not contain duplicates")
    def __iter__(self) -> Iterator[StructuralRelationship]: return iter(self.relationships)


@dataclass
class RelationshipRegistry:
    _relationships: dict[StableIdentifier, StructuralRelationship] = field(default_factory=dict)
    def register(self, relationship: StructuralRelationship) -> StructuralRelationship:
        if not isinstance(relationship, StructuralRelationship): raise TypeError("relationship must be a StructuralRelationship")
        if relationship.identity in self._relationships: raise ValueError(f"relationship already registered: {relationship.identity}")
        if any(x.canonical_key() == relationship.canonical_key() for x in self._relationships.values()): raise ValueError("duplicate canonical relationship fact")
        self._relationships[relationship.identity] = relationship; return relationship
    def get(self, identity: StableIdentifier) -> StructuralRelationship: return self._relationships[identity]
    def all(self) -> tuple[StructuralRelationship, ...]: return tuple(self._relationships.values())
    def by_kind(self, kind: RelationshipKind) -> tuple[StructuralRelationship, ...]: return tuple(x for x in self.all() if x.kind is kind)
    def by_source(self, identity: StableIdentifier) -> tuple[StructuralRelationship, ...]: return tuple(x for x in self.all() if x.source == identity)
    def by_target(self, identity: StableIdentifier) -> tuple[StructuralRelationship, ...]: return tuple(x for x in self.all() if x.target == identity)
    def involving(self, identity: StableIdentifier) -> tuple[StructuralRelationship, ...]: return tuple(x for x in self.all() if identity in (x.source, x.target))
    def by_capability(self, capability: str) -> tuple[StructuralRelationship, ...]: return tuple(x for x in self.all() if x.producing_capability == capability)
    def by_parent_frame(self, identity: StableIdentifier) -> tuple[StructuralRelationship, ...]: return tuple(x for x in self.all() if x.parent_frame == identity)
    def by_measurement(self, identity: StableIdentifier) -> tuple[StructuralRelationship, ...]: return tuple(x for x in self.all() if identity in x.supporting_measurements)


@dataclass(frozen=True)
class PerceptGraph:
    """A read-only graph view; it never derives or mutates edges."""
    percepts: tuple[Percept, ...]; relationships: tuple[StructuralRelationship, ...]
    @classmethod
    def from_registries(cls, percepts: PerceptRegistry, relationships: RelationshipRegistry) -> "PerceptGraph": return cls(percepts.all(), relationships.all())
    def outgoing(self, identity: StableIdentifier) -> tuple[StructuralRelationship, ...]: return tuple(x for x in self.relationships if x.source == identity)
    def incoming(self, identity: StableIdentifier) -> tuple[StructuralRelationship, ...]: return tuple(x for x in self.relationships if x.target == identity)
    def involving(self, identity: StableIdentifier) -> tuple[StructuralRelationship, ...]: return tuple(x for x in self.relationships if identity in (x.source, x.target))
    def neighbors(self, identity: StableIdentifier, kind: RelationshipKind) -> tuple[StableIdentifier, ...]:
        return tuple(x.target if x.source == identity else x.source for x in self.involving(identity) if x.kind is kind)
    def frame_percepts(self, frame: StableIdentifier) -> tuple[Percept, ...]: return tuple(x for x in self.percepts if x.parent_frame == frame)
    def frame_relationships(self, frame: StableIdentifier) -> tuple[StructuralRelationship, ...]: return tuple(x for x in self.relationships if x.parent_frame == frame)


def _data(percept: Percept, observations: Mapping[StableIdentifier, Observation]):
    cells = tuple((observations[x].value[0], observations[x].value[1]) for x in percept.observation_references)
    coords = frozenset(c for c, _ in cells); values = frozenset(v for _, v in cells)
    rows, cols = zip(*coords); return coords, values, (min(rows), max(rows), min(cols), max(cols))
def _add(out, kind, a, b, cap, observations, frame, derivation=()):
    if kind in _SYMMETRIC and b.identity < a.identity: a, b = b, a
    n = len(out) + 1
    support = tuple(dict.fromkeys(a.observation_references + b.observation_references))
    out.append(StructuralRelationship(StableIdentifier("relationship", f"{frame.local_name}-{n}", frame.revision), kind, a.identity, b.identity, cap, frame, support, tuple(sorted(set(a.measurement_references + b.measurement_references))), tuple(a.evidence), tuple(derivation)))


def derive_relationships(percepts: tuple[Percept, ...], observations: Mapping[StableIdentifier, Observation], frame: StableIdentifier, maximum_percepts: int = 64) -> tuple[StructuralRelationship, ...]:
    """Derive bounded O(n²) facts in percept registration order, then kind order."""
    if len(percepts) > maximum_percepts: raise ValueError("relationship derivation exceeds maximum percept count")
    regions = tuple(x for x in percepts if x.kind is PerceptKind.REGION); frames = tuple(x for x in percepts if x.kind is PerceptKind.FRAME)
    if len(frames) != 1: raise ValueError("relationship derivation requires exactly one frame percept")
    whole = frames[0]; out=[]
    # Pair comparisons are intentionally limited to regions; frame facts follow.
    for index, a in enumerate(regions):
      ac,av,ab = _data(a, observations)
      for b in regions[index+1:]:
        bc,bv,bb = _data(b, observations); overlap=ac & bc
        if overlap: _add(out, RelationshipKind.OVERLAPS,a,b,"derive_topological_relationships",observations,frame)
        else:
          orth=any(abs(r-s)+abs(c-d)==1 for r,c in ac for s,d in bc); diag=any(abs(r-s)==1 and abs(c-d)==1 for r,c in ac for s,d in bc)
          if orth: _add(out,RelationshipKind.ORTHOGONALLY_ADJACENT,a,b,"derive_topological_relationships",observations,frame)
          if diag: _add(out,RelationshipKind.DIAGONALLY_ADJACENT,a,b,"derive_topological_relationships",observations,frame)
        if ab[3] < bb[2]: _add(out,RelationshipKind.LEFT_OF,a,b,"derive_spatial_relationships",observations,frame); _add(out,RelationshipKind.RIGHT_OF,b,a,"derive_spatial_relationships",observations,frame)
        elif bb[3] < ab[2]: _add(out,RelationshipKind.LEFT_OF,b,a,"derive_spatial_relationships",observations,frame); _add(out,RelationshipKind.RIGHT_OF,a,b,"derive_spatial_relationships",observations,frame)
        if ab[1] < bb[0]: _add(out,RelationshipKind.ABOVE,a,b,"derive_spatial_relationships",observations,frame); _add(out,RelationshipKind.BELOW,b,a,"derive_spatial_relationships",observations,frame)
        elif bb[1] < ab[0]: _add(out,RelationshipKind.ABOVE,b,a,"derive_spatial_relationships",observations,frame); _add(out,RelationshipKind.BELOW,a,b,"derive_spatial_relationships",observations,frame)
        for kind,pred in ((RelationshipKind.SAME_ROW_SPAN,ab[:2]==bb[:2]),(RelationshipKind.SAME_COLUMN_SPAN,ab[2:]==bb[2:]),(RelationshipKind.ROW_ALIGNED,not(set(r for r,_ in ac)&set(r for r,_ in bc))==False),(RelationshipKind.COLUMN_ALIGNED,not(set(c for _,c in ac)&set(c for _,c in bc))==False),(RelationshipKind.SAME_VALUE,len(av)==len(bv)==1 and av==bv),(RelationshipKind.SAME_CELL_COUNT,len(ac)==len(bc)),(RelationshipKind.SAME_BOUNDS_SIZE,(ab[1]-ab[0],ab[3]-ab[2])==(bb[1]-bb[0],bb[3]-bb[2]))):
          if pred: _add(out,kind,a,b,"derive_comparison_relationships",observations,frame)
        na=frozenset((r-ab[0],c-ab[2]) for r,c in ac); nb=frozenset((r-bb[0],c-bb[2]) for r,c in bc)
        if na==nb:
          _add(out,RelationshipKind.SAME_COORDINATE_SHAPE,a,b,"derive_comparison_relationships",observations,frame)
          _add(out,RelationshipKind.TRANSLATED_COPY,a,b,"derive_comparison_relationships",observations,frame,(("delta_row",bb[0]-ab[0]),("delta_column",bb[2]-ab[2])))
    fc,_,fb=_data(whole, observations)
    for a in regions:
      ac,_,ab=_data(a,observations)
      _add(out,RelationshipKind.COORDINATE_SUBSET_OF,a,whole,"derive_frame_relationships",observations,frame)
      _add(out,RelationshipKind.BOUNDS_WITHIN,a,whole,"derive_frame_relationships",observations,frame)
      touches=[]
      for kind, yes in ((RelationshipKind.TOUCHES_TOP_BOUNDARY,ab[0]==fb[0]),(RelationshipKind.TOUCHES_BOTTOM_BOUNDARY,ab[1]==fb[1]),(RelationshipKind.TOUCHES_LEFT_BOUNDARY,ab[2]==fb[2]),(RelationshipKind.TOUCHES_RIGHT_BOUNDARY,ab[3]==fb[3])):
        if yes: _add(out,kind,a,whole,"derive_frame_relationships",observations,frame); touches.append(kind)
      if touches: _add(out,RelationshipKind.TOUCHES_ANY_BOUNDARY,a,whole,"derive_frame_relationships",observations,frame)
      if len(touches)==4: _add(out,RelationshipKind.TOUCHES_ALL_BOUNDARIES,a,whole,"derive_frame_relationships",observations,frame)
    return tuple(out)


def _focused(kinds: frozenset[RelationshipKind], percepts: tuple[Percept, ...], observations: Mapping[StableIdentifier, Observation], frame: StableIdentifier, maximum_percepts: int = 64) -> tuple[StructuralRelationship, ...]:
    return tuple(item for item in derive_relationships(percepts, observations, frame, maximum_percepts) if item.kind in kinds)

def derive_topological_relationships(percepts, observations, frame, maximum_percepts=64):
    return _focused(frozenset({RelationshipKind.ORTHOGONALLY_ADJACENT, RelationshipKind.DIAGONALLY_ADJACENT, RelationshipKind.OVERLAPS}), percepts, observations, frame, maximum_percepts)
def derive_spatial_relationships(percepts, observations, frame, maximum_percepts=64):
    return _focused(frozenset({RelationshipKind.LEFT_OF, RelationshipKind.RIGHT_OF, RelationshipKind.ABOVE, RelationshipKind.BELOW}), percepts, observations, frame, maximum_percepts)
def derive_alignment_relationships(percepts, observations, frame, maximum_percepts=64):
    return _focused(frozenset({RelationshipKind.SAME_ROW_SPAN, RelationshipKind.SAME_COLUMN_SPAN, RelationshipKind.ROW_ALIGNED, RelationshipKind.COLUMN_ALIGNED}), percepts, observations, frame, maximum_percepts)
def derive_exact_comparison_relationships(percepts, observations, frame, maximum_percepts=64):
    return _focused(frozenset({RelationshipKind.SAME_VALUE, RelationshipKind.SAME_CELL_COUNT, RelationshipKind.SAME_BOUNDS_SIZE, RelationshipKind.SAME_COORDINATE_SHAPE, RelationshipKind.TRANSLATED_COPY}), percepts, observations, frame, maximum_percepts)
def derive_frame_relationships(percepts, observations, frame, maximum_percepts=64):
    return _focused(frozenset({RelationshipKind.COORDINATE_SUBSET_OF, RelationshipKind.BOUNDS_WITHIN, RelationshipKind.TOUCHES_TOP_BOUNDARY, RelationshipKind.TOUCHES_BOTTOM_BOUNDARY, RelationshipKind.TOUCHES_LEFT_BOUNDARY, RelationshipKind.TOUCHES_RIGHT_BOUNDARY, RelationshipKind.TOUCHES_ANY_BOUNDARY, RelationshipKind.TOUCHES_ALL_BOUNDARIES}), percepts, observations, frame, maximum_percepts)
