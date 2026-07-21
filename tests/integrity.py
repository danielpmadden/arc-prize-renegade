"""Shared integrity assertions for structural-pipeline characterization tests."""
from __future__ import annotations

from renegade import PerceptPipelineResult, summarize_pipeline


def assert_result_integrity(test, result: PerceptPipelineResult) -> None:
    """Check registry-equivalent uniqueness, references, frame, and event order."""
    percepts = (result.frame_percept,) + result.region_percepts
    test.assertEqual(result.observations, tuple(result.frame))
    for records in (result.observations, result.measurements, percepts,
                    result.relationships, result.invariants, result.archetypes):
        test.assertEqual(len(records), len({record.identity for record in records}))
    observation_ids = {item.identity for item in result.observations}
    measurement_ids = {item.identity for item in result.measurements}
    percept_ids = {item.identity for item in percepts}
    relationship_ids = {item.identity for item in result.relationships}
    invariant_ids = {item.identity for item in result.invariants}
    test.assertTrue(all(item.parent_frame == result.frame.identity for item in percepts))
    test.assertTrue(all(item.parent_frame == result.frame.identity for item in result.relationships))
    test.assertTrue(all(item.parent_frame == result.frame.identity for item in result.invariants))
    test.assertTrue(all(item.parent_frame == result.frame.identity for item in result.archetypes))
    test.assertTrue(all(set(item.observation_references) <= observation_ids for item in result.measurements))
    test.assertTrue(all(set(item.observation_references) <= observation_ids for item in percepts))
    test.assertTrue(all({item.source, item.target} <= percept_ids for item in result.relationships))
    test.assertTrue(all(set(item.member_percepts) <= percept_ids and set(item.relationship_references) <= relationship_ids for item in result.invariants))
    test.assertTrue(all(set(item.invariant_references) <= invariant_ids for item in result.archetypes))
    test.assertEqual(result.percept_graph.percepts, percepts)
    test.assertEqual(result.percept_graph.relationships, result.relationships)
    test.assertEqual([item.sequence for item in result.trace], list(range(1, len(result.trace) + 1)))
    test.assertEqual(summarize_pipeline(result).execution_event_count, len(result.trace))
