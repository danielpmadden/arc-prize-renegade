"""Bounded, deterministic symbolic ARC solver.

This module is intentionally a small vertical slice: programs operate on whole
rectangular grids, are inferred only from training pairs, and are accepted only
on exact training equality.  Test labels are never consulted during inference.
"""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

from .pipeline import normalize_grid
from .tasks import Task, inspect_task

Grid = tuple[tuple[Any, ...], ...]

class ChangeKind(str, Enum):
    UNCHANGED="unchanged"; RECOLORED="recolored"; MOVED="moved"; CROPPED="cropped"; ROTATED="rotated"; REFLECTED="reflected"; FILLED="filled"; OUTLINED="outlined"; DIMENSION_CHANGED="dimension_changed"; UNKNOWN="unknown"

@dataclass(frozen=True, order=True)
class Operation:
    kind: str
    parameters: tuple[tuple[str, Any], ...] = ()
    @classmethod
    def make(cls, kind: str, **parameters: Any) -> "Operation":
        return cls(kind, tuple(sorted(parameters.items())))
    def parameter(self, name: str) -> Any:
        return dict(self.parameters)[name]

@dataclass(frozen=True, order=True)
class Program:
    operations: tuple[Operation, ...]
    @property
    def canonical(self) -> str:
        return " -> ".join(op.kind + ("(" + ",".join(f"{k}={v!r}" for k,v in op.parameters) + ")" if op.parameters else "") for op in self.operations)

@dataclass(frozen=True)
class Correspondence:
    input_region: tuple[Any, tuple[tuple[int,int],...]] | None
    output_region: tuple[Any, tuple[tuple[int,int],...]] | None
    evidence: tuple[str, ...]
    rank: int

@dataclass(frozen=True)
class ChangeSummary:
    kinds: tuple[ChangeKind, ...]
    input_dimensions: tuple[int,int]
    output_dimensions: tuple[int,int]
    changed_cells: tuple[tuple[int,int], ...]
    correspondences: tuple[Correspondence, ...]

@dataclass(frozen=True)
class Validation:
    program: Program
    passed: bool
    pair_index: int | None
    reason: str | None = None
    differing_cells: tuple[tuple[int,int], ...] = ()

@dataclass(frozen=True)
class SolverResult:
    task_identifier: str
    status: str
    selected_program: Program | None
    alternatives: tuple[Program, ...]
    predictions: tuple[Grid, ...]
    validations: tuple[Validation, ...]
    rejected: tuple[Validation, ...]
    changes: tuple[ChangeSummary, ...]
    candidates_explored: int
    max_candidates: int
    failure_reason: str | None = None


def background(grid: Grid) -> Any:
    counts=Counter(cell for row in grid for cell in row)
    return min(counts, key=lambda value: (-counts[value], repr(value)))

def regions(grid: Grid) -> tuple[tuple[Any, tuple[tuple[int,int],...]], ...]:
    seen=set(); answer=[]
    for r,row in enumerate(grid):
      for c,value in enumerate(row):
       if (r,c) in seen: continue
       todo=[(r,c)]; seen.add((r,c)); cells=[]
       while todo:
        x,y=todo.pop(); cells.append((x,y))
        for nx,ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
         if 0<=nx<len(grid) and 0<=ny<len(grid[0]) and (nx,ny) not in seen and grid[nx][ny]==value:
          seen.add((nx,ny)); todo.append((nx,ny))
       answer.append((value,tuple(sorted(cells))))
    return tuple(answer)

def correspondence(input_grid: Grid, output_grid: Grid) -> tuple[Correspondence,...]:
    ins, outs=regions(input_grid), regions(output_grid); result=[]; used=set()
    for source in ins:
      normalized=lambda item: tuple((r-min(x for x,_ in item[1]),c-min(y for _,y in item[1])) for r,c in item[1])
      choices=[(i,target) for i,target in enumerate(outs) if i not in used and len(target[1])==len(source[1]) and normalized(target)==normalized(source)]
      if len(choices)==1:
       i,target=choices[0]; used.add(i); evidence=["same_cell_count","same_normalized_shape"]
       if source[0]==target[0]: evidence.append("same_color")
       result.append(Correspondence(source,target,tuple(evidence),0))
      else: result.append(Correspondence(source,None,("unmatched" if not choices else "ambiguous",),len(choices)))
    result.extend(Correspondence(None,target,("unmatched",),0) for i,target in enumerate(outs) if i not in used)
    return tuple(result)

def apply(operation: Operation, grid: Grid) -> Grid:
    k=operation.kind
    if k=="identity": return grid
    if k=="recolor":
      mapping=dict(operation.parameter("mapping")); return tuple(tuple(mapping.get(v,v) for v in row) for row in grid)
    if k=="rotate":
      turns=operation.parameter("turns") % 4
      for _ in range(turns): grid=tuple(tuple(grid[len(grid)-1-c][r] for c in range(len(grid))) for r in range(len(grid[0])))
      return grid
    if k=="reflect":
      return tuple(reversed(grid)) if operation.parameter("axis")=="horizontal" else tuple(tuple(reversed(row)) for row in grid)
    if k=="crop":
      bg=operation.parameter("background"); cells=[(r,c) for r,row in enumerate(grid) for c,v in enumerate(row) if v!=bg]
      if not cells: return grid
      rs,cs=zip(*cells); return tuple(tuple(row[min(cs):max(cs)+1]) for row in grid[min(rs):max(rs)+1])
    if k=="translate":
      dr,dc=operation.parameter("offset"); bg=operation.parameter("background"); canvas=[[bg]*len(grid[0]) for _ in grid]
      for r,row in enumerate(grid):
       for c,v in enumerate(row):
        if v!=bg and 0<=r+dr<len(grid) and 0<=c+dc<len(row): canvas[r+dr][c+dc]=v
      return tuple(tuple(row) for row in canvas)
    if k=="fill":
      bg=operation.parameter("background"); canvas=[list(row) for row in grid]; exterior=set(); todo=[]
      for r in range(len(grid)):
       for c in range(len(grid[0])):
        if (r in (0,len(grid)-1) or c in (0,len(grid[0])-1)) and grid[r][c]==bg: todo.append((r,c)); exterior.add((r,c))
      while todo:
       r,c=todo.pop()
       for nr,nc in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)):
        if 0<=nr<len(grid) and 0<=nc<len(grid[0]) and grid[nr][nc]==bg and (nr,nc) not in exterior: exterior.add((nr,nc)); todo.append((nr,nc))
      colors=Counter(v for row in grid for v in row if v!=bg); fill_color=(next((grid[nr][nc] for r,c in [(r,c) for r,row in enumerate(grid) for c,v in enumerate(row) if v==bg and (r,c) not in exterior] for nr,nc in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)) if 0<=nr<len(grid) and 0<=nc<len(grid[0]) and grid[nr][nc]!=bg), bg) if operation.parameter("color") == "enclosing" else operation.parameter("color"))
      for r,row in enumerate(grid):
       for c,v in enumerate(row):
        if v==bg and (r,c) not in exterior: canvas[r][c]=fill_color
      return tuple(tuple(row) for row in canvas)
    if k=="outline":
      bg=operation.parameter("background"); canvas=[list(row) for row in grid]
      for r,row in enumerate(grid):
       for c,v in enumerate(row):
        if v!=bg and all(0<=nr<len(grid) and 0<=nc<len(row) and grid[nr][nc]==v for nr,nc in ((r-1,c),(r+1,c),(r,c-1),(r,c+1))): canvas[r][c]=bg
      return tuple(tuple(row) for row in canvas)
    raise ValueError(f"unsupported operation: {k}")

def execute(program: Program, grid: Grid) -> Grid:
    for operation in program.operations: grid=apply(operation, grid)
    return grid

def _summary(a: Grid,b: Grid)->ChangeSummary:
    changed=tuple((r,c) for r in range(min(len(a),len(b))) for c in range(min(len(a[0]),len(b[0]))) if a[r][c]!=b[r][c])
    kinds=[]
    if a==b:kinds.append(ChangeKind.UNCHANGED)
    if (len(a),len(a[0])) != (len(b),len(b[0])): kinds.append(ChangeKind.DIMENSION_CHANGED)
    corr=correspondence(a,b)
    if any(x.input_region and x.output_region and x.input_region[0]!=x.output_region[0] for x in corr): kinds.append(ChangeKind.RECOLORED)
    if any(x.input_region and x.output_region and x.input_region[1]!=x.output_region[1] for x in corr): kinds.append(ChangeKind.MOVED)
    if not kinds:kinds.append(ChangeKind.UNKNOWN)
    return ChangeSummary(tuple(kinds),(len(a),len(a[0])),(len(b),len(b[0])),changed,corr)

def _programs(pairs: tuple[tuple[Grid,Grid],...], max_depth:int) -> Iterable[Program]:
    yield Program((Operation.make("identity"),))
    for turns in (1,2,3): yield Program((Operation.make("rotate",turns=turns),))
    for axis in ("horizontal","vertical"): yield Program((Operation.make("reflect",axis=axis),))
    # Exact positionwise palette map; reject inconsistent input-color evidence.
    mapping={}; consistent=True
    for a,b in pairs:
      if len(a)!=len(b) or len(a[0])!=len(b[0]): consistent=False; break
      for ra,rb in zip(a,b):
       for x,y in zip(ra,rb):
        if x in mapping and mapping[x]!=y: consistent=False
        mapping[x]=y
    if consistent and mapping: yield Program((Operation.make("recolor",mapping=tuple(sorted(mapping.items(),key=repr))),))
    bgs=tuple(background(a) for a,_ in pairs)
    if len(set(bgs))==1:
      bg=bgs[0]; yield Program((Operation.make("crop",background=bg),))
      yield Program((Operation.make("fill",background=bg,color="enclosing"),))
      yield Program((Operation.make("outline",background=bg),))
      offsets=[]
      for a,b in pairs:
       if len(a)!=len(b) or len(a[0])!=len(b[0]): break
       candidates=[]
       for dr in range(-len(a),len(a)+1):
        for dc in range(-len(a[0]),len(a[0])+1):
         if execute(Program((Operation.make("translate",offset=(dr,dc),background=bg),)),a)==b:candidates.append((dr,dc))
       offsets.append(candidates)
      if offsets and all(offsets):
       common=set(offsets[0]).intersection(*map(set,offsets[1:]));
       for offset in sorted(common): yield Program((Operation.make("translate",offset=offset,background=bg),))
    if max_depth >= 2:
      singles=list(_programs(pairs, 1))
      for first in singles:
       for second in singles:
        if first.operations[0].kind in {"identity","translate"} or second.operations[0].kind in {"identity","translate"}: continue
        yield Program(first.operations+second.operations)

def solve_task(task: Task, *, max_depth:int=2, max_candidates:int=128) -> SolverResult:
    if not isinstance(task,Task): raise TypeError("task must be a Task")
    inspected=inspect_task(task) if not task.trace else task
    pairs=tuple((p.input_grid.raw_grid,p.output_grid.raw_grid) for p in inspected.training_pairs)
    changes=tuple(_summary(*pair) for pair in pairs); candidates=[]; seen=set(); rejected=[]; survivors=[]
    for program in _programs(pairs,max_depth):
      if program.canonical in seen: continue
      seen.add(program.canonical)
      if len(candidates)>=max_candidates: break
      candidates.append(program); failure=None
      for index,(source,expected) in enumerate(pairs,1):
       try: actual=execute(program,source)
       except Exception as error: failure=Validation(program,False,index,f"execution failure: {error}"); break
       if actual!=expected:
        diffs=() if len(actual)!=len(expected) or len(actual[0])!=len(expected[0]) else tuple((r,c) for r in range(len(actual)) for c in range(len(actual[0])) if actual[r][c]!=expected[r][c])
        failure=Validation(program,False,index,"dimension mismatch" if not diffs else "cell mismatch",diffs); break
      if failure: rejected.append(failure)
      else: survivors.append(Validation(program,True,None))
    selected=survivors[0].program if survivors else None
    predictions=tuple(execute(selected,grid.raw_grid) for grid in inspected.test_inputs) if selected else ()
    status="solved" if selected and len(survivors)==1 else "multiple_exact_hypotheses" if survivors else "search_bound_reached" if len(candidates)>=max_candidates else "no_exact_training_hypothesis"
    return SolverResult(inspected.identifier,status,selected,tuple(v.program for v in survivors[1:]),predictions,tuple(survivors),tuple(rejected),changes,len(candidates),max_candidates,None if selected else "No candidate constructed every training output exactly.")
