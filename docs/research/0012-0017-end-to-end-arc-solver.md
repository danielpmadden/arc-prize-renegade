# 0012–0017: End-to-end deterministic ARC solver

> **Document role:** engineering journal. The checkout source and tests are the
> implementation evidence; this note does not establish official status.

## Implemented experiment

A compact solver vertical slice consumes the existing immutable task container,
retaining independent inspection before cross-grid analysis. It extracts
four-connected regions directly from supplied grids for correspondence, with
same cell count and translation-normalized shape as explicit evidence. It does
not force ambiguous region choices.

The executable vocabulary is identity, positionwise recolor, 90-degree
rotation, horizontal/vertical reflection, crop to non-background bounds,
translation on a background canvas, enclosed-background fill, and outline.
Programs are immutable canonical operation sequences. Generation is bounded by
depth (default two) and candidate count (default 128); it has no randomness,
timeout-dependent behavior, or test-label inference.

Validation executes every candidate on every training input and requires exact
dimensions and cells. Rejections preserve the failed training-pair index and
cell differences where dimensions permit. Multiple exact programs remain an
explicit ambiguity. The selected deterministic first survivor constructs test
predictions.

## Known limits

The vocabulary is whole-grid and intentionally does not yet provide general
object selection, copying, tiling, scaling, connectivity repair, or semantic
interpretation. Single training examples can underdetermine programs; the
solver reports alternatives but its deterministic first prediction is not a
claim of certainty.
