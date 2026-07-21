# Root-cause note: `00576224`

**Status:** implementation investigation; not a claim of an ARC solve.

The prior bounded solver could execute a `crop` operation and could fit it as a
final primitive, but its forward prefix vocabulary omitted `crop`.  Therefore
the search could not use a dimension-changing intermediate grid before fitting
a later operation.  This was a language/search integration gap rather than
evidence that a task-specific rule was needed.

This pass adds the existing, general non-background bounding-box crop to the
prefix vocabulary, with bounded deterministic state deduplication.  It does
not add any task-ID-dependent rule.  Whether this is sufficient for
`00576224` is determined only by fitting all of its public training pairs and
by post-solve evaluation of its withheld test output.
