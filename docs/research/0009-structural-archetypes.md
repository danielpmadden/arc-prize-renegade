# Research Note 0009: Structural Archetypes

## Status
Experimental implementation-pass note; this is not a claim of merged or
official capability.

## Scope
Structural archetypes are deterministic, immutable, identity-based records of
exact structural motifs. They consume only existing `Invariant` records and
preserve invariant references, evidence, and parent-frame provenance. The
initial vocabulary is SingleCell, HorizontalLine, VerticalLine,
FilledRectangle, HollowRectangle, Square, LinearChain, TranslationArray, and
Checkerboard.

## Boundary
The pipeline is observations → measurements → percepts → relationships →
invariants → archetypes. Relationships state exact structural facts.
Invariants group or compress those facts. Archetypes recognize explicit,
reusable structural arrangements encoded by those invariant records. A future
concept-association layer, if introduced, belongs after archetypes and is not
implemented here.

Archetypes do not inspect raw observations and are not concepts, semantic
labels, interpretations, hypotheses, reasoning, learning, predictions, or ARC
solving.

## Exactness
Recognition only accepts complete invariant metadata and applies equality-based
conditions. There is no probabilistic score, fallback classification, random
choice, search, or semantic inference. `TranslationFamily` groups with three or
more members provide the exact basis for `LinearChain` and `TranslationArray`.
