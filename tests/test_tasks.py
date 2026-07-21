"""Deterministic ARC task representation and independent inspection tests."""
import unittest

from renegade import EventKind, GridRole, Task, inspect_task, load_task, summarize_task, summarize_training_pair


DATA = {"train": [{"input": [[1, 0]], "output": [[0, 1]]}], "test": [{"input": [[2, 2]], "output": [[3, 3]]}]}


class TaskTests(unittest.TestCase):
    def test_single_pair_expected_output_and_events(self):
        inspected = inspect_task(load_task(DATA, "example", "unit test"))
        self.assertEqual(inspected.test_input.role, GridRole.TEST_INPUT)
        self.assertEqual(inspected.expected_output.role, GridRole.EXPECTED_OUTPUT)
        self.assertEqual(len(inspected.training_pairs), 1)
        self.assertTrue(all(grid.pipeline_result is not None for pair in inspected.training_pairs for grid in (pair.input_grid, pair.output_grid)))
        self.assertEqual([event.kind for event in inspected.trace], [EventKind.TASK_CREATED, EventKind.TASK_GRID_STARTED, EventKind.TASK_GRID_COMPLETED, EventKind.TASK_GRID_STARTED, EventKind.TASK_GRID_COMPLETED, EventKind.TASK_GRID_STARTED, EventKind.TASK_GRID_COMPLETED, EventKind.TASK_GRID_STARTED, EventKind.TASK_GRID_COMPLETED, EventKind.TASK_COMPLETED])
        self.assertEqual([event.sequence for event in inspected.trace], list(range(1, 11)))

    def test_multi_pair_multiple_tests_order_and_identity_are_stable(self):
        data = {"train": DATA["train"] * 2, "test": [{"input": [[4]]}, {"input": [[5]]}]}
        first, second = inspect_task(load_task(data, "many")), inspect_task(load_task(data, "many"))
        self.assertEqual(first, second)
        self.assertEqual([grid.identity.local_name for pair in first.training_pairs for grid in (pair.input_grid, pair.output_grid)], ["many-training_input-1", "many-training_output-1", "many-training_input-2", "many-training_output-2"])
        self.assertEqual(len(first.test_inputs), 2)
        with self.assertRaises(ValueError): _ = first.test_input

    def test_loader_rejects_invalid_shapes_and_missing_fields(self):
        cases = ({"test": DATA["test"]}, {"train": [], "test": DATA["test"]}, {"train": [{"input": [[1]]}], "test": DATA["test"]}, {"train": DATA["train"], "test": [{"output": [[1]]}]})
        for value in cases:
            with self.subTest(value=value), self.assertRaises((TypeError, ValueError)): load_task(value, "bad")

    def test_task_diagnostics_are_count_only(self):
        task = inspect_task(load_task(DATA, "counts"))
        summary = summarize_task(task)
        self.assertEqual(summary.grid_count, 4)
        self.assertEqual(summary.pair_count, 1)
        self.assertEqual(summary.execution_event_count, len(task.trace))
        self.assertEqual(summarize_training_pair(task.training_pairs[0]).input_grid.role, "training_input")

    def test_task_requires_training_and_test_grids(self):
        with self.assertRaises(ValueError): Task("x", "test", (), ())
