import json
import tempfile
import unittest
from pathlib import Path

from renegade.arc_corpus import internal_name, load_official_corpus
from renegade.benchmark import evaluate_predictions, run_official
from renegade.solver import SearchConfig


class OfficialArcTests(unittest.TestCase):
    def files(self, challenges, solutions):
        directory = tempfile.TemporaryDirectory()
        c, s = Path(directory.name) / "c.json", Path(directory.name) / "s.json"
        c.write_text(json.dumps(challenges)); s.write_text(json.dumps(solutions))
        return directory, c, s

    def test_normalization_and_private_boundary(self):
        challenges = {"00576224": {"train": [{"input": [[1]], "output": [[2]]}], "test": [{"input": [[1]]}]}}
        holder, c, s = self.files(challenges, {"00576224": [[[2]]]})
        with holder:
            record = load_official_corpus(c, s)[0]
            self.assertEqual(record.internal_name, "arc_00576224")
            self.assertTrue(all(item is None for item in record.public_task.expected_outputs))
            report = run_official((record,), SearchConfig(max_depth=1))
            self.assertEqual(report["summary"]["task_level_exact_solves"], 1)

    def test_id_mismatch_rejected(self):
        holder, c, s = self.files({"a": {"train": [{"input": [[1]], "output": [[1]]}], "test": [{"input": [[1]]}]}}, {"b": [[[1]]]})
        with holder:
            with self.assertRaisesRegex(ValueError, "mismatch"):
                load_official_corpus(c, s)

    def test_prediction_cardinality_is_required(self):
        expected = (((1,),), ((2,),))
        self.assertTrue(evaluate_predictions(expected, expected)["task_exact"])
        self.assertFalse(evaluate_predictions((expected[0],), expected)["task_exact"])
        self.assertFalse(evaluate_predictions(expected + (((3,),),), (expected[0],))["task_exact"])
        self.assertFalse(evaluate_predictions((), (expected[0],))["task_exact"])
        self.assertFalse(evaluate_predictions((expected[0],), (None,))["task_exact"])

if __name__ == "__main__":
    unittest.main()
