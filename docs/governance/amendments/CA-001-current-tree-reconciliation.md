# CA-001 — Current-tree ARC and capability-claim reconciliation

- **Status:** accepted by maintainer authorization in the typed-composition implementation instruction; implementation in this branch remains experimental until merged.
- **Date:** 2026-07-21
- **Modifies:** Constitution purpose and “What Renegade Is Not”.
- **Original claim:** Renegade is not an ARC-specific solver and ARC is not an implemented capability.
- **New claim:** ARC is the primary proving ground; this tree contains an experimental bounded deterministic ARC solver vertical slice. It is neither general reasoning nor official transfer without separately measured evidence.
- **Reason:** Current `solver.py`, `benchmark.py`, generator, and tests materially exceed the historical structural-only description.
- **Evidence:** `src/renegade/solver.py`; `src/renegade/benchmark.py`; `tests/test_official_arc.py`.
- **Compatibility implications:** Existing structural pipeline remains intact; solver remains experimental.
- **Code implications:** Seed-bank registry must distinguish concepts from operations and exclude ontology from search.
- **Test implications:** Privacy and exact-training tests remain mandatory.
- **Migration status:** accepted amendment; typed-composition registry and curriculum extend the documented experimental solver boundary.
- **Decision authority:** repository maintainer.
- **Affected documents:** `README.md`, `docs/reports/typed-composition-grammar-v1.md`, Seed Bank, and this amendment.
- **Lineage:** Passes 12–17 solver vertical slice → object-centric constructive programs → typed composition grammar v1.
- **Commit:** populated when accepted/merged.
