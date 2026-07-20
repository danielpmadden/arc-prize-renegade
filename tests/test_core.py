"""Tests for deterministic reasoning and explicit foundation primitives."""

from __future__ import annotations

import subprocess
import sys
import unittest

from renegade import (
    Capability,
    EventKind,
    EvidenceKind,
    EvidenceReference,
    Executive,
    LifecycleState,
    LifecycleTransitionError,
    LineageEdge,
    LineageRelation,
    Memory,
    Observation,
    Outcome,
    StableIdentifier,
    decide_transition,
    double_number,
)


EVIDENCE = EvidenceReference(EvidenceKind.TEST, "tests:test_core:fixture")


def capability_identity(name: str = "double_number", revision: int = 1) -> StableIdentifier:
    return StableIdentifier("capability", name, revision)


class RenegadeCoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.memory = Memory()
        self.capability = Capability(
            name="double_number",
            description="Multiply an integer by two.",
            function=double_number,
            identity=capability_identity(),
        )
        self.memory.remember_capability(self.capability)
        self.executive = Executive(self.memory)

    def test_stable_identifier_is_deterministic_ordered_and_hashable(self) -> None:
        first = StableIdentifier("capability", "double_number", 1)
        second = StableIdentifier("capability", "double_number", 1)
        later = StableIdentifier("capability", "double_number", 2)

        self.assertEqual(first, second)
        self.assertLess(first, later)
        self.assertEqual(str(first), "capability:double_number:1")
        self.assertEqual({first: "registered"}[second], "registered")
        self.assertEqual({first, second}, {first})

    def test_stable_identifier_rejects_malformed_values(self) -> None:
        with self.assertRaisesRegex(ValueError, "category"):
            StableIdentifier("Capability", "double_number", 1)
        with self.assertRaisesRegex(ValueError, "local_name"):
            StableIdentifier("capability", "double number", 1)
        with self.assertRaisesRegex(ValueError, "revision"):
            StableIdentifier("capability", "double_number", 0)

    def test_valid_lifecycle_transition_preserves_evidence(self) -> None:
        transition = decide_transition(
            LifecycleState.PROTOTYPE,
            LifecycleState.EXPERIMENTAL,
            "Ready for bounded experiments.",
            (EVIDENCE,),
        )

        self.assertEqual(transition.previous_state, LifecycleState.PROTOTYPE)
        self.assertEqual(transition.requested_state, LifecycleState.EXPERIMENTAL)
        self.assertEqual(transition.reason, "Ready for bounded experiments.")
        self.assertEqual(transition.evidence, (EVIDENCE,))

    def test_rejected_lifecycle_transition_preserves_attempt(self) -> None:
        with self.assertRaises(LifecycleTransitionError) as raised:
            decide_transition(
                LifecycleState.IDEA,
                LifecycleState.TRUSTED,
                "Skip evaluation.",
                (EVIDENCE,),
            )

        self.assertEqual(raised.exception.transition.previous_state, LifecycleState.IDEA)
        self.assertEqual(raised.exception.transition.requested_state, LifecycleState.TRUSTED)
        self.assertEqual(raised.exception.transition.evidence, (EVIDENCE,))

    def test_capability_transition_returns_a_new_record(self) -> None:
        transitioned = self.capability.transition_to(
            LifecycleState.EXPERIMENTAL,
            "Approve an experiment.",
            (EVIDENCE,),
        )

        self.assertEqual(self.capability.lifecycle_state, LifecycleState.PROTOTYPE)
        self.assertEqual(transitioned.lifecycle_state, LifecycleState.EXPERIMENTAL)
        self.assertEqual(transitioned.lifecycle_history[0].evidence, (EVIDENCE,))

    def test_lineage_edge_construction(self) -> None:
        edge = LineageEdge(
            source=capability_identity("double_number", 2),
            target=capability_identity("double_number", 1),
            relation=LineageRelation.REVISED_FROM,
            reason="Clarifies integer input handling.",
            evidence=(EVIDENCE,),
        )

        self.assertEqual(edge.relation, LineageRelation.REVISED_FROM)
        self.assertEqual(edge.evidence, (EVIDENCE,))

    def test_lineage_edge_rejects_self_reference(self) -> None:
        identity = capability_identity()
        with self.assertRaisesRegex(ValueError, "cannot refer to itself"):
            LineageEdge(
                source=identity,
                target=identity,
                relation=LineageRelation.DERIVED_FROM,
                reason="Invalid self relationship.",
                evidence=(EVIDENCE,),
            )

    def test_capability_preserves_its_applicable_lineage(self) -> None:
        identity = capability_identity("revised_double", 2)
        lineage = LineageEdge(
            source=identity,
            target=capability_identity("double_number", 1),
            relation=LineageRelation.REVISED_FROM,
            reason="Preserve the predecessor relationship.",
            evidence=(EVIDENCE,),
        )

        capability = Capability(
            name="revised_double",
            description="A revised integer doubling capability.",
            function=double_number,
            identity=identity,
            lineage=(lineage,),
        )

        self.assertEqual(capability.lineage, (lineage,))

    def test_capability_registration_preserves_identity(self) -> None:
        self.assertIs(self.memory.capabilities["double_number"], self.capability)
        self.assertEqual(self.capability.identity, capability_identity())
        self.assertEqual(self.capability.version, "0.1.0")
        self.assertEqual(self.capability.source, "foundational primitive")

    def test_successful_execution_records_result_and_memory(self) -> None:
        workspace = self.executive.solve(
            Observation(name="test_number", value=5), "double_number"
        )

        self.assertEqual(workspace.outcome, Outcome.SUCCEEDED)
        self.assertEqual(workspace.result, 10)
        self.assertIsNone(workspace.failure_reason)
        self.assertEqual(self.memory.history[0].capability_name, "double_number")
        self.assertEqual(self.memory.history[0].observation_name, "test_number")
        self.assertEqual(self.memory.history[0].outcome, Outcome.SUCCEEDED)

    def test_missing_capability_produces_inspectable_failure(self) -> None:
        workspace = self.executive.solve(
            Observation(name="test_number", value=5), "unknown_capability"
        )

        self.assertEqual(workspace.outcome, Outcome.FAILED)
        self.assertIsNone(workspace.result)
        self.assertEqual(workspace.failure_reason, "Capability not found: unknown_capability")
        self.assertEqual(
            [event.kind for event in workspace.trace],
            [EventKind.OBSERVATION_RECORDED, EventKind.CAPABILITY_MISSING],
        )
        self.assertEqual(self.memory.history, [])

    def test_invalid_capability_input_produces_inspectable_failure(self) -> None:
        workspace = self.executive.solve(
            Observation(name="invalid_value", value="five"), "double_number"
        )

        self.assertEqual(workspace.outcome, Outcome.FAILED)
        self.assertEqual(workspace.failure_reason, "double_number requires an integer")
        self.assertEqual(workspace.trace[2].kind, EventKind.EXECUTION_FAILED)
        self.assertEqual(dict(workspace.trace[2].details)["error_type"], "TypeError")
        self.assertEqual(self.memory.history[0].outcome, Outcome.FAILED)

    def test_retired_capability_is_rejected_before_execution(self) -> None:
        retired = Capability(
            name="retired_double",
            description="A retired integer doubling capability.",
            function=double_number,
            identity=capability_identity("retired_double"),
            lifecycle_state=LifecycleState.RETIRED,
        )
        self.memory.remember_capability(retired)

        workspace = self.executive.solve(Observation(name="value", value=2), "retired_double")

        self.assertEqual(workspace.outcome, Outcome.FAILED)
        self.assertIn("retired", workspace.failure_reason or "")
        self.assertEqual(workspace.trace[-1].kind, EventKind.CAPABILITY_INELIGIBLE)
        self.assertEqual(self.memory.history, [])

    def test_deprecated_and_archived_capabilities_are_not_executable(self) -> None:
        for state in (LifecycleState.DEPRECATED, LifecycleState.ARCHIVED):
            capability = Capability(
                name=f"{state.value}_double",
                description="A non-active integer doubling capability.",
                function=double_number,
                identity=capability_identity(f"{state.value}_double"),
                lifecycle_state=state,
            )
            self.memory.remember_capability(capability)
            workspace = self.executive.solve(
                Observation(name="value", value=2), capability.name
            )
            self.assertEqual(workspace.trace[-1].kind, EventKind.CAPABILITY_INELIGIBLE)

    def test_invalid_request_objects_raise_documented_exceptions(self) -> None:
        with self.assertRaisesRegex(TypeError, "observation must be an Observation"):
            self.executive.solve("not an observation", "double_number")  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "capability_name must be a non-empty string"):
            self.executive.solve(Observation(name="valid", value=1), "")

    def test_repeated_execution_has_equivalent_trace(self) -> None:
        observation = Observation(name="repeatable_number", value=8)
        first_run = self.executive.solve(observation, "double_number")
        second_run = self.executive.solve(observation, "double_number")

        self.assertEqual(first_run.result, second_run.result)
        self.assertEqual(first_run.outcome, second_run.outcome)
        self.assertEqual(first_run.trace, second_run.trace)

    def test_trace_has_ordered_structured_events(self) -> None:
        workspace = self.executive.solve(
            Observation(name="ordered_number", value=3), "double_number"
        )

        self.assertEqual([event.sequence for event in workspace.trace], [1, 2, 3, 4])
        self.assertEqual(
            [event.kind for event in workspace.trace],
            [
                EventKind.OBSERVATION_RECORDED,
                EventKind.CAPABILITY_RETRIEVED,
                EventKind.EXECUTION_SUCCEEDED,
                EventKind.MEMORY_RECORDED,
            ],
        )
        self.assertEqual(dict(workspace.trace[0].details)["observation_name"], "ordered_number")

    def test_package_entry_point_execution(self) -> None:
        completed = subprocess.run(
            [sys.executable, "-m", "renegade"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("ARC Prize Renegade", completed.stdout)
        self.assertIn("[execution.succeeded]", completed.stdout)


if __name__ == "__main__":
    unittest.main()
