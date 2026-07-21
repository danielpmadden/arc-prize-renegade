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

`Task`, `TrainingPair`, and `TaskGrid` add an immutable task container above
the grid pipeline. `load_task` parses canonical ARC JSON and `inspect_task`
inspects each training input, training output, test input, and optional
expected output independently in deterministic order. Task events record
creation, grid start/completion, and completion only; no cross-grid comparison
or cognition is derived.

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
- `tasks.py` — ARC task parsing, immutable task values, and independent grid inspection.
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

## Experimental solver vertical slice

## Object reasoning foundation v1

`scene.py` introduces a separate immutable scene layer for symbolic object
reasoning. Its initial segmentation policy infers a deterministic background
and forms four-connected, same-colour, non-background components. A
`SceneObject` retains its cells, bounding box, translation-invariant mask,
colour, and size. `Scene` derives a small canonical relation set, supports
unique extremal selectors, and renders exactly back to the original grid.

The solver's `extract_object` operation uses that representation only when a
selector is unambiguous on every training pair. Test execution failures remain
explicit and cannot become predictions.

Above independent task inspection, `solver.py` performs a separate bounded
cross-grid analysis. It records normalized-shape region correspondences and
objective changed-cell summaries, generates a finite ordered vocabulary of
whole-grid programs, and accepts a program only after exact execution against
every training output. It applies only exact survivors to test inputs; expected
test outputs are evaluated only by the benchmark after prediction. This layer
is experimental and does not alter the structural pipeline or its records.

## Experimental object-centric constructive layer

The solver also has an executable, bounded scene-program layer. `Scene` is an
immutable interpretation of a grid using explicitly chosen four- or
 eight-connected same-colour components. It records canonical component cells,
bounds, masks, border contact, and a relation graph (direction, alignment,
touching, equality of shape/size/colour). `ObjectPredicate` returns ordered
object sets rather than silently breaking ties; `ObjectSelector` remains the
explicit unique-object adapter.

Executable object operations are `render_objects` (on the input canvas or a
rebased bounding canvas), `render_related`, `recolor_objects`, and
`repeat_object`. The latter has a bounded `object_count` symbolic value and
bounded count limit. Rendering has deterministic overwrite ordering and no
clipping: all constructed coordinates are derived from a rebased selected
object set. Relation-driven rendering requires an unambiguous reference.

Object candidates share `Program`, exact pair validation, replay, test-label
privacy, canonical serialization, semantic prefix-state deduplication, and the
existing candidate/depth bounds. Predicates, relations, canvas modes, colours,
and repeat geometry are finite vocabularies. Empty/ambiguous unique selections
and unsupported values fail explicitly. This is an experimental solver layer,
not a claim that the structural pipeline itself performs semantic reasoning.
