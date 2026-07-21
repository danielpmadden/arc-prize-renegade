# ARC Prize Renegade

Renegade is an early deterministic symbolic-architecture experiment and **not an ARC solver**. This tracked checkout implements observations, reproducible measurements, whole-frame and four-directional same-value region percept formation, explicit structural relationships, and a small deterministic percept graph.

## Run
```bash
python -m pip install --editable .
python -m renegade
python -m renegade.playground
python -m renegade.playground --grid '[[1,0,1],[0,0,0],[1,0,1]]'
python -m unittest discover -s tests -v
```

## Implemented pipeline
```
supplied input → observations → measurements → percepts
 → explicit relationship derivation → structural relationships
 → percept graph → workspace and trace
```

`renegade.relationships` exports `StructuralRelationship`, `RelationshipKind`, `RelationshipDirection`, `RelationshipSet`, `RelationshipRegistry`, `PerceptGraph`, and focused derivation functions. A relationship is immutable and identity-based. Symmetric relationships use canonical ascending endpoint order; strict directional relationships are emitted with explicit inverses. The graph is a read-only exact view with outgoing, incoming, involving, neighbor, and frame-scoped retrieval; it does not derive edges, search paths, or infer closure.

Relationships include orthogonal and diagonal adjacency, strict left/right/above/below, row and column spans/alignment, exact value/count/bounds/normalized-coordinate comparisons, translation vectors, frame-boundary contact, coordinate subset, and bounds-within. Pairwise analysis runs in deterministic registry order and is capped at 64 percepts (O(n²)).

The playground reports **RELATIONSHIPS**, **PERCEPT GRAPH**, and relationship-kind summary counts. Connected regions are not objects. `SAME_COORDINATE_SHAPE` is not object recognition; `TRANSLATED_COPY` does not imply movement or intended transformation; boundary contact does not imply frame, border, background, or container.

## Not implemented
Concept association, semantic interpretation, hypotheses, reasoning, reflection, learning, semantic graph behavior, ARC task loading, evaluation, and solving remain absent. No relationship expresses semantic meaning.

## Layout
- `src/renegade/relationships.py`: relationship values, registry, graph, and bounded exact derivation.
- `src/renegade/pipeline.py`: grid pipeline integration.
- `src/renegade/playground.py`: deterministic inspection report.
- `docs/architecture/overview.md`: architecture boundary.
- `docs/research/0007-structural-relationships.md`: Pass 7 rationale.

See `AGENTS.md`, `EPISTEMOLOGY.md`, and `MILESTONES.md` for contributor guidance, status rules, and append-only history.

## Structural invariants

The pipeline also derives immutable, identity-based structural invariants from existing relationship records: `SameValueGroup`, `SameShapeGroup`, `SameCellCountGroup`, `SameBoundsGroup`, and `TranslationFamily`. They compress connected groups of exact relationships, preserve relationship provenance and frame context, and never inspect raw observations directly. An invariant is not a concept, semantic label, interpretation, hypothesis, prediction, or reasoning result. The playground's **INVARIANTS** section displays deterministic members and translation vectors where applicable.

## Structural archetypes

The final implemented structural layer is **archetypes**: immutable,
identity-based exact motifs derived solely from structural invariants. The
initial vocabulary is `SingleCell`, `HorizontalLine`, `VerticalLine`,
`FilledRectangle`, `HollowRectangle`, `Square`, `LinearChain`,
`TranslationArray`, and `Checkerboard`. Archetypes preserve invariant
provenance and frame context; they never inspect raw observations and are not
concepts, semantic labels, interpretations, hypotheses, reasoning, learning,
or predictions. The playground reports an **ARCHETYPES** section.

The boundary is: relationships record pairwise structure → invariants compress
exact relationship regularities → archetypes recognize exact structural motifs
→ a future concept-association layer may attach meaning. No concept association
exists in this checkout.
