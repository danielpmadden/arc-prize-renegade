# Documentation Guide

This index separates current implementation evidence from governance,
specification, historical records, and research journals.

## Current implementation

- [Architecture overview](architecture/overview.md) is the canonical concise
  description of the implemented structural pipeline and its boundaries.
- [Capability baseline report](reports/pass-10-capability-baseline.md) records
  observed Pass 10 characterization evidence and known limits.
- [Root README](../README.md) is the repository entry point and quick start.

## Foundations and governance

- [`foundations/`](foundations/) holds epistemic rules and intended capability,
  concept, lifecycle, lineage, and emergence specifications. They are not
  implementation claims.
- [`governance/CONSTITUTION.md`](governance/CONSTITUTION.md) states enduring
  design principles.
- [`roadmap/MILESTONES.md`](roadmap/MILESTONES.md) is append-only verified
  history and includes current-tree audit corrections.
- [`legal/PRIVACY.md`](legal/PRIVACY.md), root `LICENSE`, root `NOTICE.md`, and
  [`.github/SECURITY.md`](../.github/SECURITY.md) contain legal and security
  material.

## Research journals

The numbered files in [`research/`](research/) preserve implementation-pass
rationale and historical context. Use the architecture overview, source, and
tests—not a journal alone—to state current behavior.

## Experimental solver

`renegade.solver` is a bounded executable solver layer above task inspection.
See `python -m renegade.solve --help` and the initial solver baseline report.
