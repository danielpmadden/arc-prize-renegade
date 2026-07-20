"""Tests for the deterministic foundation value primitives."""

from __future__ import annotations

import unittest

from renegade.foundation import (
    EvidenceKind,
    EvidenceReference,
    LifecycleState,
    LifecycleTransitionError,
    LineageEdge,
    LineageRelation,
    StableIdentifier,
    decide_transition,
)


class FoundationPrimitiveTests(unittest.TestCase):
    """Verify the implemented foundation remains explicit and non-inferential."""

    def setUp(self) -> None:
        self.evidence = EvidenceReference(EvidenceKind.TEST, "foundation-test")

    def test_identifier_is_stable_and_rejects_invalid_parts(self) -> None:
        identifier = StableIdentifier("observation", "grid_1", 2)

        self.assertEqual(str(identifier), "observation:grid_1:2")
        with self.assertRaisesRegex(ValueError, "local_name"):
            StableIdentifier("observation", "Grid", 1)

    def test_transition_is_explicit_and_preserves_invalid_request(self) -> None:
        transition = decide_transition(
            LifecycleState.IDEA,
            LifecycleState.PROTOTYPE,
            "begin bounded prototype",
            (self.evidence,),
        )
        self.assertEqual(transition.requested_state, LifecycleState.PROTOTYPE)

        with self.assertRaises(LifecycleTransitionError) as raised:
            decide_transition(
                LifecycleState.IDEA,
                LifecycleState.TRUSTED,
                "skip required stages",
                (self.evidence,),
            )
        self.assertEqual(raised.exception.transition.previous_state, LifecycleState.IDEA)

    def test_lineage_edge_requires_explicit_distinct_endpoints_and_evidence(self) -> None:
        source = StableIdentifier("concept", "source", 1)
        target = StableIdentifier("concept", "target", 1)
        edge = LineageEdge(
            source,
            target,
            LineageRelation.DERIVED_FROM,
            "recorded derivation",
            (self.evidence,),
        )
        self.assertEqual(edge.relation, LineageRelation.DERIVED_FROM)
        with self.assertRaisesRegex(ValueError, "cannot refer to itself"):
            LineageEdge(source, source, LineageRelation.DERIVED_FROM, "invalid", (self.evidence,))
