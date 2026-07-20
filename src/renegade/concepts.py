"""Small immutable concept values used only as explicit observation references.

Concepts are abstractions.  This module deliberately does not recognize them
from observations or provide interpretation behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .foundation import EvidenceReference, StableIdentifier


class ConceptCategory(str, Enum):
    """Broad, non-domain-specific categories for explicitly created concepts."""

    ENTITY = "entity"
    PROPERTY = "property"
    RELATION = "relation"
    PROCESS = "process"


@dataclass(frozen=True, eq=False)
class Concept:
    """An immutable abstraction whose equality is exclusively its identity."""

    identity: StableIdentifier
    category: ConceptCategory
    name: str
    description: str = ""
    evidence: tuple[EvidenceReference, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.identity, StableIdentifier):
            raise TypeError("concept identity must be a StableIdentifier")
        if not isinstance(self.category, ConceptCategory):
            raise TypeError("concept category must be a ConceptCategory")
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("concept name must be a non-empty string")
        if not isinstance(self.description, str):
            raise TypeError("concept description must be a string")
        if not isinstance(self.evidence, tuple) or not all(
            isinstance(reference, EvidenceReference) for reference in self.evidence
        ):
            raise TypeError("concept evidence must be a tuple of EvidenceReference values")

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Concept) and self.identity == other.identity

    def __hash__(self) -> int:
        return hash(self.identity)
