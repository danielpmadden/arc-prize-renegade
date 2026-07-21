# 0018: Program-first synthetic task generator

> **Status:** experimental engineering record. It describes current-tree work,
> not official ARC capability or benchmark evidence.

## Design

The generator selects a bounded `solver.Program` first, then samples several
compatible worlds from a local `random.Random(seed)`, executes the selected
program, and records the resulting canonical training and test pairs. It does
not read, copy, embed, or depend on official ARC data. Replay validation checks
the program against every stored output before a generated task is returned.

Current difficulties are deliberately modest: level 1 has one operation,
level 2 adds recolor composition, and level 3 adds reflection. The operation
source is exactly the solver's executable representation. Each task has two
training pairs by default and one labeled test pair; labels are ground truth
for generator evaluation, not solver input metadata.

## Limits and next work

Worlds vary in dimensions, background, palette, density, and disconnected
cells. Object selection, nested-object construction, ambiguity minimization by
solver recovery, and operations beyond the current whole-grid DSL remain future
work. The generator must not be described as an ARC clone or as evidence of
real-ARC performance.
