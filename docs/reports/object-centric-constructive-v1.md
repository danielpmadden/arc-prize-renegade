# Object-centric constructive layer v1

**Status:** experimental branch implementation. This report describes code and
local tests in this checkout, not official ARC transfer.

## Baseline and change

The prior object foundation provided four-connected monochrome components,
unique extrema, five passive relations, and single-object extraction. This pass
adds immutable object-set predicates, optional eight-connectivity, relation
queries, canonical alignment/touching/directional relation edges, rebased
multi-object rendering, selected-object recolouring, and bounded repetition.

## Executable forms

`render_objects(predicate, canvas=input|bbox)` constructs an output from every
matching object. `render_related(reference, relation, canvas)` constructs a
scene from objects related to one unambiguous reference. `recolor_objects`
implements a finite filter-map operation while preserving all other cells.
`repeat_object` renders a uniquely selected mask horizontally or vertically;
its count can be the explicitly bounded number of objects. These forms are
fitted only against every public training pair and executed on test inputs only
after fitting. No expected test output is supplied to selection or execution.

## Controls and limitations

Scene interpretations are capped to the caller-selected connectivity (the
solver currently searches four-connectivity); no permutations or arbitrary
arithmetic are enumerated. Existing maximum depth, candidate, prefix-state,
and displacement bounds remain telemetry-visible. Correspondence diagnostic
records remain shape-based; pair transfer, multicolour segmentation,
containment, symmetry completion, scaling, and general placement are deferred.
No official aggregate benchmark was run in this pass, so there are no claimed
newly solved tasks, regressions, or performance measurements.

## Reproduction

```bash
PYTHONPATH=src python -m unittest discover -s tests -p 'test_object_programs.py' -v
PYTHONPATH=src python -m unittest discover -s tests -v
```
