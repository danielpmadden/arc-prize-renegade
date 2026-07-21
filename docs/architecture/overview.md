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
