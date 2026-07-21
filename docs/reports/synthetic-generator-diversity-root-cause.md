# Synthetic generator diversity root cause

## Evidence and conclusion

The defect was generation, not audit aggregation or serialization.  In the pre-repair implementation, `DIFFICULTIES[2]` named only `recolor`; `_program` consequently constructed the fixed sequence `recolor(1→2) -> recolor(2→3)`. The world constructor forced color 1 solely to make those two stages effective. No registry was consulted, no non-recolor parameter constructor was reached at level 2, and retry only rejected ineffective grids. Therefore every accepted program necessarily had the same two operation names. Public serialization does not contain operations, while the private sidecar retains them; audit reads private program provenance directly. The zero recovery metric is legitimate when the solver selects an output-equivalent single recolor mapping rather than this private two-stage syntax.

## Bounded diagnostic observation before repair

The preserved baseline records 100 accepted level-2 tasks, all `recolor -> recolor`, with no failed attempts. The historical 1,000-task claim in the task request is not independently reproducible from this checkout and is retained as supplied historical context rather than reasserted evidence.

| family | attempted/accepted before | rejection reason |
|---|---:|---|
| recolor | 2 stages per accepted task | none when color 1 present |
| rotate, reflect, translate | 0 / 0 at level 2 | excluded by the difficulty family list |
| crop, fill, outline | 0 / 0 | not constructively generated |

## Repair intent

The repaired explicit eligible level-2 space has six ordered slots: recolor before/after rotate, reflect, or translate. Recolor→recolor is excluded as behaviorally reducible. Generation validates every prefix and every stage ablation across all examples; failures are bounded and counted in private provenance. Balanced sampling allocates slots round-robin after a seeded rotation and never substitutes a different slot.
