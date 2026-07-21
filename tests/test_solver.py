import json, tempfile, unittest
from pathlib import Path
from contextlib import redirect_stdout
import io
from renegade import Operation, Program, execute, load_task, solve_task
from renegade.solve import main as solve_main
from renegade.benchmark import main as benchmark_main

class SolverTests(unittest.TestCase):
 def task(self, train, test): return load_task({"train":train,"test":test}, "synthetic")
 def test_recolor_and_exact_evaluation_independent_of_labels(self):
  task=self.task([{"input":[[1,0],[0,1]],"output":[[2,0],[0,2]]}], [{"input":[[1,0]],"output":[[2,0]]}])
  result=solve_task(task); self.assertTrue(result.predictions); self.assertEqual(result.predictions[0],((2,0),)); self.assertIn(result.status,{"solved","multiple_exact_hypotheses"})
 def test_rotation_crop_fill_outline_translation_and_composition(self):
  cases=[
   ([{"input":[[1,2],[3,4]],"output":[[3,1],[4,2]]}], [[1,2,3],[4,5,6]], ((4,1),(5,2),(6,3))),
   ([{"input":[[0,0,0],[0,1,0],[0,0,0]],"output":[[1]]}], [[0,2,0],[0,0,0],[0,0,0]], ((2,),)),
   ([{"input":[[1,1,1],[1,0,1],[1,1,1]],"output":[[1,1,1],[1,1,1],[1,1,1]]}], [[1,1,1],[1,0,1],[1,1,1]], ((1,1,1),(1,1,1),(1,1,1))),
   ([{"input":[[0,1,0]],"output":[[0,0,1]]}], [[0,2,0]], ((0,0,2),)),
  ]
  for train,test,expected in cases:
   with self.subTest(train=train): self.assertEqual(solve_task(self.task(train,[{"input":test}])).predictions[0],expected)
 def test_operations_and_rejection_are_deterministic(self):
  self.assertEqual(execute(Program((Operation.make("reflect",axis="vertical"),)),((1,2),)),((2,1),))
  bad=self.task([{"input":[[1]],"output":[[2]]},{"input":[[1]],"output":[[3]]}],[{"input":[[1]]}]); result=solve_task(bad); self.assertEqual(result.status,"no_exact_training_hypothesis"); self.assertTrue(result.rejected)
 def test_cli_and_benchmark_json(self):
  data={"train":[{"input":[[1]],"output":[[2]]}],"test":[{"input":[[1]],"output":[[2]]}]}
  with tempfile.TemporaryDirectory() as directory:
   path=f"{directory}/x.json"; Path(path).write_text(json.dumps(data)); out=io.StringIO()
   with redirect_stdout(out): self.assertEqual(solve_main([path,"--json"]),0)
   self.assertEqual(json.loads(out.getvalue())["predictions"],[[[2]]]); out=io.StringIO()
   with redirect_stdout(out): self.assertEqual(benchmark_main([directory,"--json"]),0)
   self.assertEqual(json.loads(out.getvalue())["exact_test_outputs"],1)
if __name__ == "__main__": unittest.main()
