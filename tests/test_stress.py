"""Seeded robustness checks for the bounded deterministic grid pipeline."""

import random
import unittest

from renegade import inspect_grid


class PipelineStressTests(unittest.TestCase):
    def test_seeded_varying_grids_are_stable_and_registry_safe(self):
        generator = random.Random(20260721)
        # Small sizes intentionally keep the O(n²) structural layer well inside
        # its documented bound while still exercising 24 varied inputs.
        for size in range(1, 4):
            for case in range(8):
                grid = tuple(
                    tuple(generator.randrange(4) for _ in range(size))
                    for _ in range(size)
                )
                with self.subTest(size=size, case=case):
                    first = inspect_grid(grid, f"stress-{size}-{case}")
                    second = inspect_grid(grid, f"stress-{size}-{case}")
                    self.assertEqual(first, second)
                    self.assertEqual(
                        len(first.relationships),
                        len({item.identity for item in first.relationships}),
                    )
                    self.assertEqual(
                        len(first.invariants), len({item.identity for item in first.invariants})
                    )
                    self.assertEqual(
                        len(first.archetypes), len({item.identity for item in first.archetypes})
                    )
