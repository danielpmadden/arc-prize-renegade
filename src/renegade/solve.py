"""Command line interface for the bounded deterministic solver."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from .solver import solve_task
from .tasks import load_task

def _payload(result):
 return {"task":result.task_identifier,"status":result.status,"program":result.selected_program.canonical if result.selected_program else None,"predictions":[[list(row) for row in grid] for grid in result.predictions],"candidates_explored":result.candidates_explored,"exact_survivors":len(result.validations),"telemetry":result.telemetry,"rejected":[{"program":v.program.canonical,"pair":v.pair_index,"reason":v.reason,"differing_cells":[list(x) for x in v.differing_cells]} for v in result.rejected],"failure_reason":result.failure_reason,"changes":[{"kinds":[x.value for x in c.kinds],"changed_cells":[list(x) for x in c.changed_cells],"correspondences":len(c.correspondences)} for c in result.changes]}
def main(argv=None):
 p=argparse.ArgumentParser();p.add_argument("task_path");p.add_argument("--json",action="store_true");p.add_argument("--max-depth",type=int,default=2);p.add_argument("--max-candidates",type=int,default=128);p.add_argument("--show-rejections",action="store_true"); args=p.parse_args(argv)
 try:
  data=json.loads(Path(args.task_path).read_text(encoding="utf-8")); result=solve_task(load_task(data,Path(args.task_path).stem,str(args.task_path)),max_depth=args.max_depth,max_candidates=args.max_candidates)
 except (OSError,ValueError,TypeError,json.JSONDecodeError) as error: p.error(str(error))
 payload=_payload(result)
 if args.json: print(json.dumps(payload,sort_keys=True,separators=(",",":"),default=str)); return 0
 print(f"Task: {payload['task']}\nStatus: {payload['status']}\nCandidates: {payload['candidates_explored']}\nExact survivors: {payload['exact_survivors']}\nProgram: {payload['program'] or 'none'}")
 for i,grid in enumerate(payload['predictions'],1): print(f"Prediction {i}: {grid}")
 if args.show_rejections: print("Rejected:", payload['rejected'])
 if payload['failure_reason']: print("Failure:",payload['failure_reason'])
 return 0
if __name__=="__main__": main()
