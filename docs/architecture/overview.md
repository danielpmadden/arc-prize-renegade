# Architecture Overview

> **Document role: current implementation overview.** This is the canonical
> explanation of the structural pipeline in this checkout. It does not promote
> branch work to official status or describe future semantic capabilities.

## Pipeline and boundary

```
supplied rectangular grid
  → observations → measurements → percepts → relationships
  → invariants → archetypes → workspace, graph, and ordered trace
```

`inspect_grid` is the explicit orchestration entry point. It normalizes a
non-empty rectangular grid, records one coordinate/value observation per cell,
and forms an observation frame. It then produces dimensions, bounds, and count
measurements; a whole-frame percept; and four-directionally connected,
same-value region percepts in deterministic discovery order.

The relationship layer performs bounded, exact pairwise analysis over percepts
and records geometric facts only. The graph is a read-only index over those
records. The invariant layer groups connected exact relationship facts. The
archetype layer recognizes a small vocabulary of exact motifs only from
invariant metadata and provenance. None of these layers assigns semantic
meaning, recognizes objects, infers intent, or solves ARC tasks.

## Architectural guarantees

- Public records are immutable and compare by stable identity where their
  value types specify identity semantics.
- Registries preserve insertion order and reject duplicate identities and
  duplicate canonical records.
- Structural records retain frame context and supporting provenance.
- Relationship derivation is capped at 64 percepts to keep pairwise work
  bounded.
- Workspace events are attempt-local and sequential. Diagnostics summarize an
  existing result and derive no new facts.

## Package map

- `foundation.py` — stable identifiers and evidence references.
- `observations.py`, `measurements.py`, `percepts.py` — the first three
  structural record layers and their registries.
- `relationships.py`, `invariants.py`, `archetypes.py` — exact structural
  derivation layers.
- `pipeline.py` — grid orchestration and result value.
- `diagnostics.py` — count-only result summary.
- `playground.py` — command-line rendering for inspection.
- `core.py` — general one-capability execution foundation and workspace.

For an entry point and commands, see the [root README](../../README.md). For
document roles and preserved pass journals, see the
[documentation guide](../README.md).

## Characterization evidence

`python -m renegade.characterize` executes the packaged 19-case corpus and
selected boundary inputs, reporting existing record counts, compression ratios,
and explicit failure reasons. `--json` emits a deterministic JSON array. The
utility only runs `inspect_grid` and summarizes its returned records; it does
not create cognitive artifacts. Unit tests additionally exhaust 107 tiny
binary and bounded ternary grids, validate cross-layer references and event
order, and retain exact normalized snapshots for six representative inputs.

The direct relationship policy accepts at most 64 supplied percepts and rejects
65 or more with `ValueError`. Pipeline inputs that produce too many percepts
therefore fail explicitly during relationship derivation. Non-empty rectangular
list/tuple grids are supported; malformed grid structures and unsupported cell
values fail through existing deterministic validation.
