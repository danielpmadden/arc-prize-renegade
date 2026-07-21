# Performance and boundedness review — 2026-07-21

The depth-two compositional test previously did not complete in the available
interactive window. Cause: object operations were both prefix generators and
fitted finals, repeatedly constructing scenes across each intermediate state.
The repair keeps object operations executable and one-step searchable, but
excludes them from prefix/final composition until a typed bounded object
composition grammar and curriculum justify their cost. Existing object-centric
one-step tests remain covered. In this environment, the focused compositional,
object, and knowledge suite completed in 4.95 seconds (12 tests).

Current explicit controls remain `max_depth`, `max_candidates`,
`max_prefix_states`, `max_displacement`, canonical state deduplication, and
operation ordering. Remaining exposure: per-symbolic-type memory metrics and
object-composition completeness are not implemented; this is an intentionally
recorded search gap, not a silent capability removal.
