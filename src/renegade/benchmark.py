"""Local-only deterministic ARC solver benchmark."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from .solver import solve_task
from .tasks import load_task

def main(argv=None):
 p=argparse.ArgumentParser();p.add_argument("path");p.add_argument("--json",action="store_true"); args=p.parse_args(argv); root=Path(args.path); files=[root] if root.is_file() else sorted(path for path in root.rglob("*.json") if not path.name.endswith(".meta.json")) if root.is_dir() else []
 rows=[]
 for file in files:
  try:
   result=solve_task(load_task(json.loads(file.read_text()),file.stem,str(file))); expected=load_task(json.loads(file.read_text()),file.stem).expected_outputs
   correct=bool(result.predictions) and all(x is not None and prediction==x.raw_grid for prediction,x in zip(result.predictions,expected))
   rows.append({"task":str(file),"status":result.status,"candidates":result.candidates_explored,"prediction":bool(result.predictions),"test_correct":correct})
  except (OSError,ValueError,TypeError,json.JSONDecodeError) as e: rows.append({"task":str(file),"status":"invalid","error":str(e)})
 summary={"tasks_discovered":len(files),"tasks_attempted":len(rows),"predictions":sum(x.get("prediction",False) for x in rows),"exact_test_outputs":sum(x.get("test_correct",False) for x in rows),"invalid":sum(x["status"]=="invalid" for x in rows),"tasks":rows}
 if args.json: print(json.dumps(summary,sort_keys=True,separators=(",",":")))
 else: print("Tasks discovered:",summary["tasks_discovered"]); print("Predictions:",summary["predictions"]); print("Exact test outputs:",summary["exact_test_outputs"]); [print(f"{x['task']}: {x['status']}") for x in rows]
 return 0
if __name__=="__main__": main()
