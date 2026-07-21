# Research Note 0010: Capability characterization

> **Status:** Pass 10 implementation-pass journal, pending human review.

## Purpose

This pass treats the existing structural pipeline as an object of measurement.
It adds no cognitive layer and derives no additional artifacts during
characterization. The harness executes `inspect_grid`, then reports existing
record counts and explicit validation failures.

## Findings

The 19-case corpus, 107 exhaustive tiny inputs, representative snapshots, and
focused boundaries are deterministic under repeated execution. Rectangular
non-empty tuple/list grids with recursively supported immutable cell values are
accepted. Empty grids, empty rows, ragged rows, scalar rows, mappings, and
unsupported cell values are rejected by deterministic validation errors.

Observed recognition is narrower than the archetype vocabulary suggests:
translation-family invariants can yield `linear_chain` and
`translation_array`; representative filled, hollow, single-cell, and
checkerboard inputs do not currently emit their namesake archetypes. This is
an observed false-negative class, not a semantic conclusion. Repeated
translation archetypes on checkerboards are a known structural false-positive
risk because they do not assert a checkerboard archetype.

## Unresolved questions

Relationship derivation remains pairwise and is capped at 64 percepts. Dense
inputs near that limit can grow relationship and invariant records sharply;
Pass 10 records this as a bottleneck rather than changing the policy. Future
experiments should measure valid near-limit inputs with bounded profiling,
audit archetype metadata availability, and preserve the distinction between
structural motifs and future semantic layers.
