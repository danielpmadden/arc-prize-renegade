# Pass 10 capability baseline

> **Document role:** observed branch evidence, pending human review. This report
> describes runs from this checkout; it does not claim official status or
> semantic capability.

## Tested input classes

Evidence consists of the 19 packaged golden grids, 107 exhaustive tiny grids
(2 one-by-one binary, 4 one-by-two binary, 4 two-by-one binary, 16 two-by-two
binary, and 81 two-by-two ternary), six normalized snapshots, and focused
boundary inputs. The accepted class observed here is a non-empty rectangular
list/tuple grid whose cells satisfy the existing immutable-value boundary.

## Verified behavior

- All characterized accepted cases completed deterministically on repeated
  runs. Cross-layer identities were unique; percept, relationship, invariant,
  and archetype provenance references resolved; graph records agreed with
  result records; and event sequence numbers were ordered and unique.
- The pipeline records one observation per cell and three measurements. It
  forms a frame percept plus four-directionally connected same-value regions.
  Diagonal-only contact remains separate regions and emits diagonal structural
  relationships where applicable.
- The observed archetype outputs include `linear_chain` and
  `translation_array` for several repeated-region inputs. The golden
  checkerboard produced 25 region percepts, 3,202 relationships, 233
  invariants, and 88 archetypes; this is a count observation, not an
  interpretation.
- The 64-percept relationship input boundary is accepted by the cap check; 65
  supplied percepts are rejected with `relationship derivation exceeds maximum
  percept count`.

## Rejected and unsupported inputs

Empty grids, empty rows, ragged rows, non-row scalar structures, mappings, and
unsupported mutable/opaque cell values were rejected by `ValueError` or
`TypeError`. The harness reports ragged rows as `grid rows must have equal
length`. Inputs that form more than 64 percepts are not supported by the
current relationship layer.

## Known limits and observations

- **False negatives:** representative single-cell, filled-rectangle,
  hollow-rectangle, and checkerboard grids did not emit their namesake
  archetypes. Current archetype formation only consumes invariant metadata;
  these results show that required metadata is not presently available for
  those cases.
- **False-positive risk:** dense checkerboards emit many translation-family
  derived `linear_chain`/`translation_array` records. These are exact
  structural outputs but should not be treated as a checkerboard recognition.
- **Relationship growth:** pairwise derivation grows sharply with disconnected
  regions. The 5x5 checkerboard is the observed high-count corpus case above;
  it exposes the practical cost of the O(n²) layer and its downstream events.
- **Performance:** normal tests complete deterministically, but valid dense
  near-limit scenes are an architectural bottleneck. No benchmark timing or
  general performance claim is made in this pass.

## Inferred and untested behavior

It is reasonable to infer that larger disconnected inputs may amplify the
same pairwise growth, but this is not exhaustively measured. No claim is made
about arbitrary value domains, persistence, semantics, object identity,
concept association, interpretation, reasoning, learning, transfer, or ARC
solving.

## Recommended next experiments

Profile valid near-limit scenes under a fixed environment; audit which
invariant metadata is required for each existing archetype; add carefully
bounded relationship-growth measurements; and retain explicit rejected-input
behavior. Any semantic layer remains outside this baseline.
