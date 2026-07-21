"""Architectural regression tests over the reusable golden corpus."""

import unittest

from golden_corpus import GOLDEN_GRIDS
from renegade import EventKind, inspect_grid, summarize_pipeline


class GoldenCorpusTests(unittest.TestCase):
    def test_every_representative_grid_completes_deterministically(self):
        for sample in GOLDEN_GRIDS:
            with self.subTest(grid=sample.name):
                first = inspect_grid(sample.grid, sample.name)
                second = inspect_grid(sample.grid, sample.name)
                self.assertEqual(first, second)
                self.assertEqual(first.observations, tuple(first.frame))
                self.assertEqual(len(first.measurements), 3)
                self.assertEqual(
                    [event.sequence for event in first.trace],
                    list(range(1, len(first.trace) + 1)),
                )
                self.assertIn(EventKind.GRAPH_ASSEMBLED, [event.kind for event in first.trace])
                self.assertEqual(
                    summarize_pipeline(first).execution_event_count, len(first.trace)
                )

    def test_corpus_covers_declared_input_families(self):
        expected = {
            "empty", "single_cell", "solid_region", "horizontal_line",
            "vertical_line", "filled_rectangle", "hollow_rectangle",
            "checkerboard", "cross", "plus", "l_shape", "t_shape",
            "u_shape", "nested_regions", "disconnected_regions",
            "touching_edges", "touching_corners", "translation_pattern",
            "symmetry",
        }
        self.assertEqual({sample.name for sample in GOLDEN_GRIDS}, expected)
