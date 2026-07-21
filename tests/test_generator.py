import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from renegade import execute, generate_batch, generate_task, solve_task, validate_generated
from renegade.generate import main

class GeneratorTests(unittest.TestCase):
    def test_seed_replay_and_program_replay(self):
        first, second = generate_task(42, difficulty=2), generate_task(42, difficulty=2)
        self.assertEqual(first, second)
        validate_generated(first)
        for pair in first.task.training_pairs:
            self.assertEqual(execute(first.program, pair.input_grid.raw_grid), pair.output_grid.raw_grid)
        self.assertEqual(first.metadata_json()["program_depth"], 2)

    def test_difficulty_batch_and_canonical_task_serialization(self):
        batch = generate_batch(9, 4, difficulty=3)
        self.assertEqual([item.seed for item in batch], [9, 10, 11, 12])
        self.assertTrue(all(len(item.program.operations) == 3 for item in batch))
        payload = batch[0].task_json()
        self.assertEqual(set(payload), {"train", "test"})
        self.assertEqual(len(payload["train"]), 2)
        self.assertNotIn("output", payload["test"][0])

    def test_cli_writes_reproducible_task_and_private_sidecar(self):
        with tempfile.TemporaryDirectory() as directory:
            output = StringIO()
            with redirect_stdout(output):
                self.assertEqual(main(["--seed", "3", "--count", "2", "--difficulty", "2", "--output", directory, "--json"]), 0)
            payload = json.loads(output.getvalue())
            self.assertEqual(len(payload), 2)
            files = sorted(Path(directory).glob("*.json"))
            self.assertEqual(len(files), 4)
            self.assertNotIn("metadata", json.loads(Path(directory, "synthetic-3-2.json").read_text()))

    def test_level_one_recolor_is_solver_compatible(self):
        generated = generate_task(2)
        result = solve_task(generated.task)
        self.assertTrue(result.predictions)
        self.assertEqual(result.predictions[0], generated.task.expected_outputs[0].raw_grid)

    def test_invalid_arguments_are_rejected(self):
        with self.assertRaises(ValueError): generate_task(1, difficulty=4)
        self.assertEqual(generate_batch(1, 0), ())
