"""Tests for the non-deriving pipeline diagnostics utility."""

import unittest

from renegade import PipelineDiagnostics, inspect_grid, summarize_pipeline


class DiagnosticsTests(unittest.TestCase):
    def test_summary_reports_existing_pipeline_counts(self):
        result = inspect_grid(((1, 0), (0, 1)))
        summary = summarize_pipeline(result)
        self.assertIsInstance(summary, PipelineDiagnostics)
        self.assertEqual(summary.observation_count, 4)
        self.assertEqual(summary.measurement_count, 3)
        self.assertEqual(summary.percept_count, 5)
        self.assertEqual(summary.relationship_count, len(result.relationships))
        self.assertEqual(summary.execution_event_count, len(result.trace))

    def test_summary_rejects_non_pipeline_values(self):
        with self.assertRaises(TypeError):
            summarize_pipeline(object())
