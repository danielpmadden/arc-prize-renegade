"""Public-import contract tests for documented package entry points."""

import unittest

import renegade


class PublicApiTests(unittest.TestCase):
    def test_structural_and_diagnostic_exports_are_intentional(self):
        expected = {
            "Archetype", "ArchetypeKind", "ArchetypeRegistry", "ArchetypeSet",
            "PipelineDiagnostics", "derive_archetypes", "inspect_grid",
            "summarize_pipeline",
            "Task", "TaskGrid", "TrainingPair", "TaskKind", "GridRole", "load_task", "inspect_task", "summarize_task",
        }
        self.assertTrue(expected <= set(renegade.__all__))
        for name in expected:
            self.assertTrue(hasattr(renegade, name), name)
