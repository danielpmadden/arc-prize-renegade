import json
import tempfile
import unittest
from pathlib import Path

from renegade import DIFFICULTIES, generate_batch, generate_task, solve_task
from renegade.audit_generation import main as audit_main
from renegade.experiment import main as experiment_main
from renegade.tasks import load_task

class SyntheticLaboratoryTests(unittest.TestCase):
    def test_difficulties_have_real_depth_and_public_boundary(self):
        for level, spec in DIFFICULTIES.items():
            item = generate_task(31, difficulty=level)
            self.assertEqual(len(item.program.operations), spec["depth"])
            public = item.public_json()
            self.assertNotIn("output", public["test"][0]); self.assertNotIn("seed", json.dumps(public))
            isolated = load_task(public, item.task.identifier)
            self.assertTrue(all(x is None for x in isolated.expected_outputs))
            solve_task(isolated)
        with self.assertRaises(ValueError): generate_task(1, difficulty=4)

    def test_batch_and_hashes_are_deterministic_and_seed_changes_fixture(self):
        first, second = generate_batch(7, 3, difficulty=2), generate_batch(7, 3, difficulty=2)
        self.assertEqual([x.public_hash for x in first], [x.public_hash for x in second])
        self.assertNotEqual(first[0].public_hash, generate_batch(8, 3, difficulty=2)[0].public_hash)

    def test_audit_and_experiment_exports_and_empty_experiment(self):
        with tempfile.TemporaryDirectory() as root:
            audit = Path(root, "audit"); self.assertEqual(audit_main(["--count","1","--difficulty","1","--seed","2","--output",str(audit)]), 0)
            self.assertEqual(set(x.name for x in audit.iterdir()), {"audit.json","audit.md","tasks.csv","operations.csv","compositions.csv"})
            experiment = Path(root, "experiment"); self.assertEqual(experiment_main(["--count","1","--difficulty","1","--seed","2","--output",str(experiment)]), 0)
            self.assertIn("exact_test_outputs_solved", json.loads(Path(experiment,"experiment.json").read_text()))
            empty = Path(root, "empty"); self.assertEqual(experiment_main(["--count","0","--difficulty","1","--seed","2","--output",str(empty)]), 0)

if __name__ == "__main__": unittest.main()
