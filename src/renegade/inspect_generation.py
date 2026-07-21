"""Write deterministic public and private generated-task inspection artifacts."""
from __future__ import annotations
import argparse
from pathlib import Path
from .generator import generate_batch
from .laboratory import prepare_output

def _grid(grid): return "\n".join(" ".join(map(str,row)) for row in grid)
def main(argv=None):
 p=argparse.ArgumentParser(); p.add_argument('--count',type=int,required=True); p.add_argument('--difficulty',type=int,required=True); p.add_argument('--seed',type=int,required=True); p.add_argument('--sampling',choices=('natural','balanced'),default='balanced'); p.add_argument('--output',type=Path,required=True); p.add_argument('--force',action='store_true'); a=p.parse_args(argv)
 try: prepare_output(a.output,a.force); tasks=generate_batch(a.seed,a.count,difficulty=a.difficulty,sampling=a.sampling)
 except (ValueError,TypeError,RuntimeError) as e: p.error(str(e))
 public=['# Public generated-task inspection',''] ; private=['# PRIVATE generated-task inspection','', 'This file contains hidden labels and provenance. Never pass it to a solver.','']
 for item in tasks:
  public += [f'## {item.task.identifier}', f'public hash: `{item.public_hash}`']
  private += [f'## {item.task.identifier}',f'program: `{item.program.canonical}`',f'program hash: `{item.program_hash}`',f'stage effectiveness: `passed`']
  for n,pair in enumerate(item.task.training_pairs,1): public += [f'### training {n} input','```text',_grid(pair.input_grid.raw_grid),'```','output','```text',_grid(pair.output_grid.raw_grid),'```']
  for n,test in enumerate(item.task.test_inputs,1): public += [f'### test {n} input','```text',_grid(test.raw_grid),'```']; private += [f'### hidden test {n} output','```text',_grid(item.task.expected_outputs[n-1].raw_grid),'```']
 (a.output/'public-inspection.md').write_text('\n'.join(public)+'\n',encoding='utf-8'); (a.output/'PRIVATE-inspection.md').write_text('\n'.join(private)+'\n',encoding='utf-8'); return 0
if __name__=='__main__': raise SystemExit(main())
