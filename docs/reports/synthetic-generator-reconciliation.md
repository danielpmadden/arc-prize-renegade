# Synthetic Generator Reconciliation

## Scope and evidence

This audit inspected the `work` branch, its recent history, the generator and
solver modules, their tests, benchmark command, README, and research notes
before this reconciliation change. The reported abbreviated commits `5451c20`,
`a406aa9`, and `d1351c3` are not resolvable objects in this checkout. The
corresponding reachable evidence is `1385635` (*Add deterministic synthetic
task generator*) and `734becd` (*fix: make generated compositions effective*).
Consequently no claim is made about unpresent commits.

## Findings

- `src/renegade/generator.py` was the only reachable implementation. It owned
  `GeneratedTask`, generation, replay validation, and serialization.
- `src/renegade/generate.py` was a thin CLI, not a second generator. However,
  the stale `tests/test_generate.py` expected an earlier, nonexistent API
  (`serialize_generated`, a different validation signature, metadata embedded
  in public JSON, and difficulty 7). `tests/test_generator.py` targeted the
  reachable implementation. The stale test has been replaced rather than
  retaining a compatibility shim for code that never existed on this branch.
- There was one `GeneratedTask` model, but its `task_json()` included hidden
  test outputs. That was an ARC-shaped *labelled* format, not a safe public
  solver format. The authoritative API now calls this public serialization and
  writes hidden outputs only in the private sidecar.
- Difficulty 1--3 were the only accepted levels. The prior implementation
  rejected 4; no reachable evidence supports level 4. Its README sentence that
  complexity increased after level 3 was therefore inaccurate.
- `generate` and `benchmark` are not overlapping generator CLIs: `generate`
  exports synthetic tasks and `benchmark` solves supplied JSON. `audit_generation`
  and `experiment` now measure the same authoritative generator rather than
  implementing generation separately.

## Retained and changed components

`generator.py` is retained as the single authoritative implementation and now
owns difficulty specifications, canonical hashes, public/private serialization,
batch generation, replay validation, and effective-operation rejection.
`generate.py` remains an export-only adapter. `audit_generation.py`,
`experiment.py`, and `laboratory.py` consume that API; none creates worlds or
programs independently. The old unreachable-test expectations were removed.

## Accepted difficulty semantics

| level | depth/effective operations | allowed families | input worlds | rejection |
|---|---|---|---|---|
| 1 | exactly 1 | recolor, rotate, reflect, translate | 4--7 rows/columns | an operation is a no-op on any example |
| 2 | exactly 2 | recolor, recolor | 5--8 rows/columns; color 1 required | either recolor is ineffective or replay fails |
| 3 | exactly 3 | recolor, recolor, reflect | 6--9 rows/columns; color 1 required | any operation is ineffective or replay fails |

All levels use two training and at least one test input, bounded 100-attempt
generation, integer colors, background 0, and no object-selection or branching
language. Unsupported values fail with an explicit list of accepted levels.
