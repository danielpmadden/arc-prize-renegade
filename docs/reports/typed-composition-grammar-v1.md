# Typed composition grammar v1

## Current implementation

`renegade.grammar` adds a separate, experimental typed IR rather than changing
legacy `solver.Program`.  Expressions are frozen dataclasses with canonical
forms and version-one JSON serialization.  The registry declares eight
operations and their types, literal domains, costs, maturity, capability link,
determinism, ambiguity policy, and official-solving eligibility.

The executable slice is `Grid → Scene → ObjectSet → ObjectSet → Grid`, with a
separate `Scene → CanvasSpec` branch.  Segmentation is represented by a single
expression and execution cache key; downstream filtering, recolouring and
rendering consume its immutable scene-derived values.  Empty selection and
non-unique selection fail explicitly.

## Bounded search and evidence

Search enumerates only typed filter/recolour/render chains.  Its finite config
limits expression depth, candidates, values per type, scene interpretations,
and literal palette.  Training outputs are used solely to validate completed
candidates; held-out test inputs are executed only after selection.  Telemetry
records generation, rejection, retention, cache entries/hits/misses, scene
interpretations and truncation.

`composition_curriculum.py` supplies two deterministic v1 cases: largest
object filter → recolour → tight render, and smallest-object filter → tight
render.  They have multiple training pairs, held-out inputs, distractors and
documented shortcut controls.  They are synthetic evidence only, not official
ARC results or a promotion to stable capability.

## Compatibility and limitations

Legacy grid programs remain unchanged.  The v1 grammar has no general
re-segmentation loop, relation-guided selection, count/repetition, transforms,
or official solver integration.  Those are explicitly not claimed by this
report.  Pattern promotion is not automatic and the Seed Bank remains dormant.
