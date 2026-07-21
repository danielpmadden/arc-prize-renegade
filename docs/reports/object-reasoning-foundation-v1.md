# Object Reasoning Foundation v1

This pass introduces a permanent symbolic scene representation rather than a
collection of task rules. A scene is an immutable interpretation of a grid
under one explicit segmentation policy: same-colour, four-connected,
non-background components. It preserves component cells, bounding boxes,
translation-invariant masks, colour, and bounded pairwise geometry.

The initial selectors are only unique extrema (largest, smallest, leftmost,
rightmost, topmost, bottommost). Ties intentionally fail selection rather than
being resolved with incidental order. This is less expressive than a large
selector language but gives selector failure clear, inspectable meaning.

`extract_object` is the executable bridge to bounded search: it crops the
uniquely selected component to its bounding box. It is inferred and validated
solely from training pairs, can occur in a bounded prefix, and remains
replayable through `Program`. Candidate programs that cannot execute on a test
input are rejected explicitly; no hidden labels are consulted.

This foundation can express isolated-object extraction and object-plus-grid
composition. It does not yet model multicolour objects, containment,
copy/placement, correspondence across examples, or a constructive scene
language. It is a representational elevation, not a claim of broad ARC
transfer or semantic understanding.
