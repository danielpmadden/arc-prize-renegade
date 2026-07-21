# Bounded compositional symbolic-search implementation

This experimental change replaces the defective depth-two candidate generation
described in `compositional-search-root-cause.md`.  It is a generator-native,
public-data measurement mechanism, not evidence of ARC transfer, learning, or
semantic program recovery.

## Program and search model

`Program` is an immutable tuple of immutable `Operation` values.  Its ordered
steps execute deterministically, have structural equality and hashing, expose
`depth`, operation-family sequence, and canonical serialization.  `SearchConfig`
has bounded defaults: depth 2, 512 complete candidates, 128 retained prefix
states, and displacement magnitude 2.  Depth 3 is supported by the same
layered prefix search but has a materially higher finite cost.

Prefix candidates use the public executable vocabulary: rotations, reflections,
single-color recolors over the observed source/output palette, and bounded
translations using an observed background.  Final-stage inference is performed
on arbitrary aligned tuples, so it works from an intermediate state to an
observed output.  Crop, fill, and outline remain primitive-only fitting paths.

## Pruning, deduplication, and ambiguity

Prefix states are keyed by the tuple of grids across *all* training examples;
the canonical representative is retained.  This is sound behavioral
deduplication for future fitting on the observed training data.  Prefix and
complete candidate counts are hard bounded.  Identity is not generated as a
prefix.  No unsafe translation algebra is applied: clipped translations are
never collapsed.

All train-valid programs are run on test inputs and grouped by output tuple.
Telemetry reports the distinct prediction count.  To preserve the existing
solver's documented deterministic fallback, disagreement chooses the shortest
then stable operation-order/canonical program and records
`deterministic_ranked_ambiguity`; private labels are never consulted.

## Telemetry

`SolverResult.telemetry` contains configuration, per-depth prefix/complete
attempts, unique intermediate-state counts, duplicate removals, train-valid
counts, rejection reasons, selected program/depth, distinct predicted outputs,
and search-exhaustion status.  `python -m renegade.solve --json` exposes it.

## Reproducible commands

```powershell
python -m pip install --editable .
python -m unittest tests.test_solver tests.test_compositional_search -v
python -m unittest discover -s tests -v
python -m renegade.experiment --count 20 --difficulty 2 --seed 102 --sampling balanced --output experiments\d2-smoke
python -m renegade.experiment --count 1000 --difficulty 1 --seed 101 --sampling balanced --output experiments\d1-1000
python -m renegade.experiment --count 1000 --difficulty 2 --seed 102 --sampling balanced --output experiments\d2-1000
python -m renegade.experiment --count 200 --difficulty 2 --seed 201 --sampling balanced --output experiments\d2-seed-201
python -m renegade.solve path\to\task.json --max-depth 3 --json
```

The full requested corpus and multi-seed experiments are intentionally not
claimed in this report until their generated artifacts are retained.  The
focused tests establish only bounded mechanism behavior.
