# ARC Prize Renegade

> *Build the spine before teaching the body to move.*

**ARC Prize Renegade** is an experiment in building a deterministic symbolic cognitive architecture from first principles.

It is **not** an ARC solver.

Not yet.

The goal is to construct the smallest correct reasoning kernel capable of growing into one.

This repository intentionally begins **without ARC training tasks**, **without handcrafted ARC rules**, and **without legacy solver code**. The architecture should earn the right to solve problems by first developing the machinery required to reason about them.

---

# Philosophy

Most solvers begin with the benchmark.

Renegade begins with cognition.

A human doesn't learn calculus by memorizing calculus.

They first develop:

- identity
- counting
- comparison
- grouping
- ordering
- spatial reasoning
- abstraction
- composition

Each concept becomes part of a larger structure that future reasoning can build upon.

Renegade follows the same philosophy.

---

# The Spine

The architecture revolves around a single idea:

> Intelligence is easier to build when knowledge has structure.

Not every capability should be active all the time.

Instead, the system should organize itself into a hierarchy of concepts, capabilities, and dependencies.

```
Perception
│
├── Objects
│
├── Geometry
│
├── Relations
│
└── Topology

↓

Reasoning

↓

Memory

↓

Learning

↓

Executive
```

Every concept has a place.

Every capability has parents.

Every capability has children.

Every capability knows:

- what it depends on
- what depends on it
- when it should activate
- when it should remain dormant

The executive navigates this structure instead of searching every possible tool.

---

# The Workshop

Imagine an enormous workshop.

Thousands of tools exist.

A master craftsman doesn't dump them all onto the floor.

They walk directly to the cabinet.

Open one drawer.

Retrieve one tool.

Solve the problem.

Put it back.

Renegade should behave the same way.

Capabilities are retrieved because they appear relevant—not because they exist.

---

# Learning

Learning is **not**:

- remembering names
- increasing counters
- storing rewards
- recording metadata
- caching outputs

Learning means the architecture acquires something executable or structurally meaningful.

Examples include:

- synthesizing a reusable symbolic program
- discovering a transferable abstraction
- compressing multiple solutions into one concept
- replacing literal solutions with structural ones
- improving retrieval through verified conceptual organization

If nothing reusable was created, nothing was learned.

---

# Memory

Memory exists to support reasoning—not replace it.

Memories may suggest ideas.

They never override evidence.

Every recalled concept must still prove itself on the current problem.

The architecture should remember because remembering is useful, not because storage is cheap.

---

# Organization

Knowledge should resemble a living registry.

Everything has:

- an address
- relationships
- dependencies
- evidence
- history
- provenance

Concepts should naturally organize themselves over time.

Frequently co-occurring capabilities may become higher-order concepts.

Rarely useful branches should be archived.

Nothing should become active unless the executive has a reason to retrieve it.

---

# Expansion and Consolidation

Reasoning alternates between two modes.

## Expansion

Explore.

Generate ideas.

Test hypotheses.

Search for new abstractions.

## Consolidation

Organize.

Merge duplicates.

Promote successful concepts.

Archive weak ones.

Prune unnecessary complexity.

Intelligence is not endless accumulation.

It is organized accumulation.

---

# Determinism

Given identical inputs:

- the same observations
- the same memory
- the same configuration

Renegade must produce identical reasoning.

No hidden randomness.

No stochastic search.

No nondeterministic execution.

Reasoning should always be reproducible.

---

# Core Principles

- Deterministic
- Symbolic
- Explainable
- Modular
- Composable
- Hierarchical
- Inspectable
- Testable
- Transfer-oriented
- Domain-independent

---

# Current Goal

Do **not** solve ARC.

Build the spine.

Develop:

- observations
- representations
- capabilities
- symbolic programs
- executive control
- workspace
- critics
- repair
- memory
- retrieval
- learning
- transfer

Only after the architecture demonstrates genuine reasoning should ARC become another domain connected to the spine.

---

# Long-Term Vision

The objective is not merely to improve an ARC benchmark.

The objective is to construct a deterministic symbolic architecture capable of continually organizing its own knowledge, forming reusable abstractions, and applying previous understanding to unfamiliar problems.

If successful, ARC will simply become one demonstration of a much more general system.

---

> **"Everything must have a place before it has an implementation."**