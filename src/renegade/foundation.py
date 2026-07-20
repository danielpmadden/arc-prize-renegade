"""Explicit identity, evidence, lifecycle, and lineage primitives.

These values represent decisions and references; they do not infer relationships,
validate evidence, or manage lifecycle changes automatically.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re


_IDENTIFIER_PART = re.compile(r"[a-z][a-z0-9_-]*\Z")


@dataclass(frozen=True, order=True)
class StableIdentifier:
    """A deterministic ``category:local_name:revision`` identifier."""

    category: str
    local_name: str
    revision: int

    def __post_init__(self) -> None:
        for label, value in (("category", self.category), ("local_name", self.local_name)):
            if not isinstance(value, str) or not _IDENTIFIER_PART.fullmatch(value):
                raise ValueError(f"{label} must match [a-z][a-z0-9_-]*")
        if not isinstance(self.revision, int) or isinstance(self.revision, bool) or self.revision < 1:
            raise ValueError("revision must be a positive integer")

    def __str__(self) -> str:
        return f"{self.category}:{self.local_name}:{self.revision}"


class EvidenceKind(str, Enum):
    """The kind of source referenced as evidence, without asserting its truth."""

    EXECUTION_EVENT = "execution_event"
    MEMORY_EVENT = "memory_event"
    OBSERVATION = "observation"
    TEST = "test"
    MANUAL_SOURCE = "manual_source"


@dataclass(frozen=True)
class EvidenceReference:
    """An immutable pointer to possible evidence, not a claim of validation."""

    kind: EvidenceKind
    reference: str

    def __post_init__(self) -> None:
        if not isinstance(self.reference, str) or not self.reference:
            raise ValueError("evidence reference must be a non-empty string")


class LifecycleState(str, Enum):
    """The small set of lifecycle states represented in this foundation."""

    IDEA = "idea"
    PROTOTYPE = "prototype"
    EXPERIMENTAL = "experimental"
    VALIDATED = "validated"
    TRUSTED = "trusted"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"
    RETIRED = "retired"


_ALLOWED_TRANSITIONS: dict[LifecycleState, frozenset[LifecycleState]] = {
    LifecycleState.IDEA: frozenset({LifecycleState.PROTOTYPE, LifecycleState.ARCHIVED}),
    LifecycleState.PROTOTYPE: frozenset(
        {LifecycleState.EXPERIMENTAL, LifecycleState.DEPRECATED, LifecycleState.ARCHIVED}
    ),
    LifecycleState.EXPERIMENTAL: frozenset(
        {LifecycleState.VALIDATED, LifecycleState.DEPRECATED, LifecycleState.ARCHIVED}
    ),
    LifecycleState.VALIDATED: frozenset(
        {LifecycleState.TRUSTED, LifecycleState.EXPERIMENTAL, LifecycleState.DEPRECATED, LifecycleState.ARCHIVED}
    ),
    LifecycleState.TRUSTED: frozenset({LifecycleState.DEPRECATED, LifecycleState.ARCHIVED}),
    LifecycleState.DEPRECATED: frozenset({LifecycleState.EXPERIMENTAL, LifecycleState.ARCHIVED}),
    LifecycleState.ARCHIVED: frozenset({LifecycleState.EXPERIMENTAL, LifecycleState.RETIRED}),
    LifecycleState.RETIRED: frozenset(),
}


@dataclass(frozen=True)
class LifecycleTransition:
    """A deliberate lifecycle decision with explicit supporting references."""

    previous_state: LifecycleState
    requested_state: LifecycleState
    reason: str
    evidence: tuple[EvidenceReference, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.reason, str) or not self.reason:
            raise ValueError("transition reason must be a non-empty string")
        if not self.evidence:
            raise ValueError("a lifecycle transition requires at least one evidence reference")


class LifecycleTransitionError(ValueError):
    """An invalid transition plus its preserved, inspectable attempted decision."""

    def __init__(self, transition: LifecycleTransition) -> None:
        self.transition = transition
        super().__init__(
            f"transition from {transition.previous_state.value} to "
            f"{transition.requested_state.value} is not allowed"
        )


def decide_transition(
    previous_state: LifecycleState,
    requested_state: LifecycleState,
    reason: str,
    evidence: tuple[EvidenceReference, ...],
) -> LifecycleTransition:
    """Create a permitted explicit transition or reject the recorded request."""
    transition = LifecycleTransition(previous_state, requested_state, reason, evidence)
    if requested_state not in _ALLOWED_TRANSITIONS[previous_state]:
        raise LifecycleTransitionError(transition)
    return transition


class LineageRelation(str, Enum):
    """Supported, non-inferred relationships between meaningful entities."""

    DERIVED_FROM = "derived_from"
    INSPIRED_BY = "inspired_by"
    REVISED_FROM = "revised_from"
    COMPOSED_FROM = "composed_from"
    CONTRADICTED_BY = "contradicted_by"
    SUPERSEDES = "supersedes"


@dataclass(frozen=True)
class LineageEdge:
    """A directed, evidence-backed lineage relationship without graph behavior."""

    source: StableIdentifier
    target: StableIdentifier
    relation: LineageRelation
    reason: str
    evidence: tuple[EvidenceReference, ...]

    def __post_init__(self) -> None:
        if self.source == self.target:
            raise ValueError("a lineage edge cannot refer to itself")
        if not isinstance(self.reason, str) or not self.reason:
            raise ValueError("lineage reason must be a non-empty string")
        if not self.evidence:
            raise ValueError("a lineage edge requires at least one evidence reference")
