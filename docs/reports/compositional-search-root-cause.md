# Compositional search root cause

## Evidence from the pre-repair code path

`solve_task` called `_programs(pairs, max_depth)`.  Although the old function
accepted `max_depth=2`, its composed branch built both `first` and `second`
from `_programs(pairs, 1)`: every parameter was inferred against the original
input/output pairs, rather than a prefix's intermediate grids.  It also skipped
any composition containing `translate`.  Thus no candidate for a recolor-first
or translation-containing generated pair could be fitted.  There was no depth
three branch at all.  Exact replay and sequential `execute` already worked;
candidate construction was the failure.

The repaired solver records this explicitly.  On a public-only generated
difficulty-two fixture it reports non-zero `depth_2_prefixes_attempted`, unique
intermediate states, and complete-program attempts.  A difficulty-three public
fixture likewise reports `depth_3_prefixes_attempted`; those values are
produced by the same layered mechanism, not generator provenance.

## Repaired semantics

Depth one fits a primitive to aligned source/target tuples.  At each additional
depth, the solver enumerates a finite public operation prefix, applies it to
**every** training input, deduplicates the complete tuple of intermediate
grids, then fits the final primitive from that tuple to training outputs and
replays the whole program exactly.  The default depth is two; depth three is
available only through the explicit bounded configuration.
