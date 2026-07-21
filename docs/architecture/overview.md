# Architecture Overview

> **Document role: implementation overview.** It describes the current source tree.

```
Supplied input → observations → measurements → explicit percept formation
→ percepts → workspace and execution trace
```

An `Observation` records supplied material. A `Measurement` reports a
reproducible property. A `Percept` is an immutable, identity-based organization
of ordered observation references, optional measurement references, evidence,
a producing capability, and optional parent frame. A `Concept` remains an
explicit abstraction value only; interpretation is not implemented.

`form_frame_percept` records the supplied frame as one structural unit.
`form_connected_regions` records maximal same-value regions from a rectangular
coordinate-cell frame. It scans coordinates row-major, starts at the first
unassigned coordinate, traverses neighbors in up/right/down/left order, and
emits discovery order. Connectivity is orthogonal only. A region is structural,
not a recognized object. `Workspace` keeps exact, insertion-ordered percept,
observation, and measurement registries separately and records percept creation
and registration events. Semantic association, interpretation, reasoning,
learning, and ARC solving remain absent.

## Structural relationships (Pass 7)
The implemented pipeline is supplied grid → observations → measurements → percepts → explicit relationship derivation → structural relationships → percept graph → workspace trace. `StructuralRelationship` records an identity, typed kind, endpoints, capability, frame context, supporting references, evidence, and only necessary normalized metadata. Equality is identity-only. Symmetric facts use ascending stable endpoint order; directed facts retain source/target order and the pipeline emits both strict inverse facts (`LEFT_OF`/`RIGHT_OF`, `ABOVE`/`BELOW`).

Pairwise region analysis is deterministic registration order and bounded to 64 percepts (O(n²)); the graph only indexes registered records and has no inference, traversal, or closure. Exact predicates include orthogonal/diagonal contact, strict bounds directions, row/column span and occupancy alignment, uniform supplied value, count, bounds size, translation-normalized coordinates, translation vector, frame boundary contact, coordinate subset, and bounds-within. These are structural facts, not semantic relationships.

## Structural invariants (Pass 8)
Invariants are a separate layer after relationships: they consume only registered structural relationships and deterministically compress connected endpoint groups. `SameValueGroup`, `SameShapeGroup`, `SameCellCountGroup`, and `SameBoundsGroup` select their corresponding exact relationship kind. `TranslationFamily` additionally preserves one exact translation vector. They preserve relationship identities and frame context, but do not inspect observations, attach concepts, or claim semantic meaning.
