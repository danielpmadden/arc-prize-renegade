# Renegade Capability Contract

> **Document role: specification.** This is the admission contract for future
> architectural capabilities. The current minimal `Capability` implementation
> does not yet satisfy every requirement below; see `README.md` for its actual
> scope.

A capability is a bounded, deterministic unit of reusable reasoning.

Every capability must satisfy this contract.

## Required Identity

Each capability must declare:

- stable name
- version
- purpose
- conceptual location in the spine
- owner or source
- creation reason

## Required Relationships

Each capability must declare:

- dependencies
- accepted input types
- produced output types
- related concepts
- known companions
- known conflicts

No capability may exist as an isolated function with no declared place.

## Applicability

A capability must be able to explain when it should be considered.

It must provide:

- required conditions
- supporting signals
- disqualifying conditions
- estimated relevance
- estimated cost

Capabilities must not activate merely because they are available.

## Execution

Execution must be:

- deterministic
- bounded
- inspectable
- repeatable
- free of hidden state changes

The same capability, input, configuration, and memory state must produce the same result.

## Result

Every execution result must include:

- success or failure
- produced value
- evidence
- assumptions
- cost
- trace
- failure reason when applicable

A silent failure is not acceptable.

## Provenance

Every capability must record where it came from.

Possible origins include:

- foundational primitive
- manually implemented tool
- composed program
- repaired program
- generalized pattern
- promoted learned capability

Learned capabilities must retain the episodes and evidence that justified promotion.

## Validation

A capability may propose a result.

It may not validate itself.

Validation must remain separate from execution.

Memory, historical reward, or previous success may influence ranking but may never bypass validation.

## Composition

A capability should be composable whenever its output type satisfies another capability's input type.

Composition must preserve:

- type safety
- provenance
- determinism
- budget accounting
- execution trace

## Promotion

A candidate capability may become trusted only after demonstrating:

- exact success
- repeated usefulness
- transfer beyond its original case
- no unresolved contradictions
- acceptable complexity
- stable execution

A single successful use does not prove generality.

## Dormancy

Capabilities remain dormant unless retrieved through relevance.

The system must not execute every registered capability against every problem.

Inactive capabilities remain available without consuming active reasoning attention.

## Consolidation

Capabilities may be:

- merged
- generalized
- compressed
- demoted
- archived

Equivalent capabilities should not remain permanently duplicated.

## Archival

Archival is preferred over deletion.

Archived capabilities retain:

- provenance
- historical evidence
- failure history
- retrieval path

They receive lower retrieval priority but remain recoverable.

## Prohibited Capabilities

A capability must not:

- rely on hidden randomness
- mutate unrelated state
- bypass the executive
- bypass validation
- conceal assumptions
- depend on benchmark answers
- memorize a task output and present it as reasoning
- claim learning based only on metadata
- perform unbounded search
- execute arbitrary generated Python source

## Admission Questions

Before adding a capability, answer:

1. Why does it exist?
2. Where does it belong?
3. What does it depend on?
4. When should it activate?
5. What can it produce?
6. How can it fail?
7. How will it be validated?
8. Can it compose with other capabilities?
9. What evidence would justify promoting it?
10. What would justify archiving it?

If these questions cannot be answered, the capability is not ready.
