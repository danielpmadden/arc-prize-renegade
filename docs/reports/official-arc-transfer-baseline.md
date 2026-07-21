# Official ARC aggregate research harness

This implementation pass adds local-only aggregate corpus loading, evaluator
privacy boundaries, cardinality-correct scoring, atomic report writing, and
bounded search controls.  It does not claim ARC mastery or general transfer.

## Method

`arc_corpus.load_official_corpus` keeps challenge records public to the solver
and stores solution grids only in `ArcEvaluationRecord`.  The benchmark invokes
`solve_task(public_task)` before comparing returned predictions.  Reports use
task-level exactness only when every expected output is present and exact;
individual-output metrics are reported separately.

The canonical search telemetry is `search_by_depth`, with attempted prefixes,
unique states, complete programs, valid programs, and duplicates per depth.
Legacy flat fields are derived compatibility views only.

## Reproduction

Run corpus validation with `python -m renegade.benchmark --challenges
arc-agi_training_challenges.json --solutions arc-agi_training_solutions.json
--validate-only`.  A bounded smoke run is documented in the README.  Full
depth-two runs are deliberately user-invoked rather than automatically run.

## Capability boundary

Non-background bounding-box crop was already executable and fittable as a
final operation.  It is now also a bounded compositional prefix, so a
dimension-changing intermediate grid can feed recolor, rotation, reflection,
or another fitted operation.  The operation language remains limited; no
claim is made that every dimension-changing ARC transformation is expressed.
