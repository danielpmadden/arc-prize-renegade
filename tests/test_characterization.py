"""Corpus expectations, exhaustive tiny grids, and boundary characterization."""
from __future__ import annotations

import itertools
import unittest

from golden_corpus import GOLDEN_GRIDS
from integrity import assert_result_integrity
from renegade import Percept, PerceptKind, RelationshipKind, StableIdentifier, inspect_grid, summarize_pipeline
from renegade.relationships import derive_relationships


class CorpusExpectationTests(unittest.TestCase):
    def test_corpus_has_structural_expectations_and_valid_provenance(self):
        for sample in GOLDEN_GRIDS:
            with self.subTest(sample=sample.name):
                result = inspect_grid(sample.grid, sample.name)
                assert_result_integrity(self, result)
                self.assertGreaterEqual(len(result.region_percepts), sample.minimum_regions)
                kinds = {item.kind.value for item in result.archetypes}
                relationships = {item.kind.value for item in result.relationships}
                self.assertTrue(set(sample.required_archetypes) <= kinds)
                self.assertTrue(set(sample.required_relationships) <= relationships)


class ExhaustiveTinyGridTests(unittest.TestCase):
    def test_all_binary_and_bounded_ternary_tiny_grids(self):
        cases = []
        for height, width, values in ((1, 1, range(2)), (1, 2, range(2)),
                                      (2, 1, range(2)), (2, 2, range(2)),
                                      (2, 2, range(3))):
            for cells in itertools.product(values, repeat=height * width):
                cases.append(tuple(tuple(cells[row * width:(row + 1) * width]) for row in range(height)))
        self.assertEqual(len(cases), 107)
        for index, grid in enumerate(cases):
            with self.subTest(index=index, grid=grid):
                first = inspect_grid(grid, f"tiny-{index}")
                second = inspect_grid(grid, f"tiny-{index}")
                self.assertEqual(first, second)
                assert_result_integrity(self, first)
                before = summarize_pipeline(first)
                self.assertEqual(before, summarize_pipeline(first))


class BoundaryTests(unittest.TestCase):
    def test_malformed_inputs_fail_deterministically(self):
        malformed = ([], [[]], [[1], [1, 2]], [1, 2], [[object()]], {"row": [1]})
        for value in malformed:
            with self.subTest(value=repr(value)):
                with self.assertRaises((TypeError, ValueError)):
                    inspect_grid(value)

    def test_limits_shapes_and_relationship_heavy_cases(self):
        cases = {
            "row": ((1, 0, 1, 0, 1),),
            "column": ((1,), (0,), (1,), (0,), (1,)),
            "uniform": tuple(tuple(1 for _ in range(20)) for _ in range(20)),
            "dense_checkerboard": tuple(tuple((row + col) % 2 for col in range(5)) for row in range(5)),
            "diagonal": ((1, 0), (0, 2)),
            "equal_disconnected": ((1, 0, 1, 0, 1, 0, 1),),
        }
        for name, grid in cases.items():
            with self.subTest(case=name):
                result = inspect_grid(grid, name)
                assert_result_integrity(self, result)
        diagonal = inspect_grid(cases["diagonal"], "diagonal")
        self.assertIn(RelationshipKind.DIAGONALLY_ADJACENT, {item.kind for item in diagonal.relationships})
        frame = StableIdentifier("frame", "limit", 1)
        # A deliberately invalid 64-item collection reaches the cap check and
        # then fails at frame validation, demonstrating that equality is allowed.
        limit_percepts = tuple(Percept(StableIdentifier("percept", f"p-{index}", 1), PerceptKind.FRAME, "test", (StableIdentifier("observation", "one", 1),), parent_frame=frame) for index in range(64))
        with self.assertRaisesRegex(ValueError, "exactly one frame percept"):
            derive_relationships(limit_percepts, {}, frame)
        with self.assertRaisesRegex(ValueError, "maximum percept count"):
            derive_relationships(limit_percepts + (limit_percepts[0],), {}, frame)
