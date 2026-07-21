"""Authoritative deterministic generator of effective synthetic programs.

Generation is bounded and program-first.  Public JSON never includes private
program provenance or hidden test labels.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json
from random import Random
from typing import Any
from .operations import GENERATOR_OPERATION_NAMES, OPERATION_SPECS, operation_inventory
from .solver import Grid, Operation, Program, execute
from .tasks import Task, load_task

DIFFICULTIES = {1: {"depth": 1, "size": (5, 7)}, 2: {"depth": 2, "size": (6, 8)}, 3: {"depth": 3, "size": (7, 9)}}
SAMPLING_MODES = ("natural", "balanced")
# Recolor/recolor is deliberately excluded: it is behaviorally reducible to one map.
_GEOMETRY = ("rotate", "reflect", "translate")

def canonical_hash(value: Any) -> str: return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
def _json_grid(grid: Grid) -> list[list[Any]]: return [list(row) for row in grid]
def operation_inventory_json() -> list[dict[str, Any]]: return operation_inventory()
def eligible_program_kinds(depth: int) -> tuple[tuple[str, ...], ...]:
    if depth == 1: return tuple((x,) for x in GENERATOR_OPERATION_NAMES)
    if depth == 2: return tuple((a, b) for a in ("recolor",) for b in _GEOMETRY) + tuple((a, b) for a in _GEOMETRY for b in ("recolor",))
    if depth == 3: return tuple(("recolor", "recolor", g) for g in _GEOMETRY) + tuple(("recolor", g, "recolor") for g in _GEOMETRY) + tuple((g, "recolor", "recolor") for g in _GEOMETRY)
    raise ValueError(f"unsupported depth {depth}")
def difficulty_spec(level: int) -> dict[str, Any]:
    if level not in DIFFICULTIES: raise ValueError("unsupported difficulty %s; supported values are 1, 2, 3" % level)
    return dict(DIFFICULTIES[level])

@dataclass(frozen=True)
class GeneratedTask:
    task: Task; seed: int; difficulty: int; program: Program; metadata: tuple[tuple[str, Any], ...]
    def public_json(self) -> dict[str, Any]: return {"train":[{"input":_json_grid(p.input_grid.raw_grid),"output":_json_grid(p.output_grid.raw_grid)} for p in self.task.training_pairs],"test":[{"input":_json_grid(g.raw_grid)} for g in self.task.test_inputs]}
    def task_json(self) -> dict[str, Any]: return self.public_json()
    def private_json(self) -> dict[str, Any]: return {"task_id":self.task.identifier,"seed":self.seed,"difficulty":self.difficulty,"program":self.program.canonical,"hidden_test_outputs":[_json_grid(g.raw_grid) for g in self.task.expected_outputs if g is not None],**dict(self.metadata)}
    def metadata_json(self) -> dict[str, Any]: return self.private_json()
    @property
    def public_hash(self) -> str: return canonical_hash(self.public_json())
    @property
    def program_hash(self) -> str: return canonical_hash({"program":self.program.canonical})

def _world(random: Random, level: int) -> Grid:
    low, high = DIFFICULTIES[level]["size"]; h, w = random.randint(low, high), random.randint(low, high)
    grid = [[0] * w for _ in range(h)]
    # Padded, intentionally asymmetric content makes all geometric stages effective.
    positions = ((1,1),(1,w-3),(h-3,2),(h-2,w-2),(2,w//2))
    for (r,c), color in zip(positions, (1,4,5,6,1)): grid[r][c] = color
    for _ in range(random.randint(2, max(3, h*w//6))):
        r,c=random.randrange(1,h-1),random.randrange(1,w-1); grid[r][c]=random.choice((1,4,5,6))
    return tuple(tuple(row) for row in grid)

def _construct(kinds: tuple[str, ...], random: Random) -> Program:
    recolor_number=0; ops=[]
    for kind in kinds:
        if kind == "recolor":
            source,target=((1,2),(2,3))[recolor_number]; recolor_number += 1; ops.append(Operation.make("recolor",mapping=((source,target),)))
        elif kind == "rotate": ops.append(Operation.make("rotate",turns=random.choice((1,3))))
        elif kind == "reflect": ops.append(Operation.make("reflect",axis=random.choice(("horizontal","vertical"))))
        else: ops.append(Operation.make("translate",offset=random.choice(((0,1),(1,0),(0,-1),(-1,0))),background=0))
    return Program(tuple(ops))
def _apply_without(program: Program, omit: int, grid: Grid) -> Grid: return execute(Program(tuple(x for i,x in enumerate(program.operations) if i != omit)),grid)
def _effective(program: Program, grids: list[Grid]) -> tuple[bool, str]:
    for grid in grids:
        current=grid
        for op in program.operations:
            following=execute(Program((op,)),current)
            if following == current: return False,"no_op"
            current=following
        if current == grid: return False,"complete_no_op"
    # Mandatory ablation: every removed stage must change at least one labelled output.
    for index in range(len(program.operations)):
        if all(_apply_without(program,index,g) == execute(program,g) for g in grids): return False,"stage_ablation"
    return True,"accepted"
def validate_generated(generated: GeneratedTask) -> None:
    grids=[]
    for i,pair in enumerate(generated.task.training_pairs,1):
        grids.append(pair.input_grid.raw_grid)
        if execute(generated.program,pair.input_grid.raw_grid)!=pair.output_grid.raw_grid: raise ValueError(f"generated program does not reproduce training pair {i}")
    for i,(source,expected) in enumerate(zip(generated.task.test_inputs,generated.task.expected_outputs),1):
        grids.append(source.raw_grid)
        if expected is None or execute(generated.program,source.raw_grid)!=expected.raw_grid: raise ValueError(f"generated program does not reproduce test output {i}")
    ok,reason=_effective(generated.program,grids)
    if not ok: raise ValueError(f"generated program ineffective: {reason}")
def generate_task(seed:int, *, difficulty:int=1, training_pairs:int=2, test_pairs:int=1, max_attempts:int=100, program_kinds:tuple[str,...]|None=None) -> GeneratedTask:
    if not isinstance(seed,int): raise TypeError("seed must be an integer")
    spec=difficulty_spec(difficulty)
    if training_pairs<2 or test_pairs<1: raise ValueError("generation requires at least two training and one test pair")
    if max_attempts<1: raise ValueError("max_attempts must be positive")
    choices=eligible_program_kinds(spec["depth"])
    if program_kinds is not None and program_kinds not in choices: raise ValueError(f"unsupported eligible program slot: {program_kinds}")
    random=Random(seed); rejections: dict[str,int]={}
    for attempt in range(1,max_attempts+1):
        kinds=program_kinds or random.choice(choices); program=_construct(kinds,random); inputs=[_world(random,difficulty) for _ in range(training_pairs+test_pairs)]
        ok,reason=_effective(program,inputs)
        if not ok: rejections[reason]=rejections.get(reason,0)+1; continue
        data={"train":[{"input":_json_grid(x),"output":_json_grid(execute(program,x))} for x in inputs[:training_pairs]],"test":[{"input":_json_grid(x),"output":_json_grid(execute(program,x))} for x in inputs[training_pairs:]]}
        item=GeneratedTask(load_task(data,f"synthetic-{seed}-{difficulty}","synthetic program-first generator"),seed,difficulty,program,(("program_depth",len(program.operations)),("operations",kinds),("attempts",attempt),("rejected_attempts",attempt-1),("rejection_reasons",tuple(sorted(rejections.items()))),("sampling_slot"," -> ".join(kinds))))
        validate_generated(item); return item
    raise RuntimeError(f"generation exhausted {max_attempts} attempts for {program_kinds or 'natural slot'}; rejections={rejections}")
def _slots(seed:int,count:int,choices:tuple[tuple[str,...],...],sampling:str)->list[tuple[str,...]]:
    random=Random(seed)
    if sampling=="natural": return [random.choice(choices) for _ in range(count)]
    if sampling!="balanced": raise ValueError(f"unsupported sampling {sampling!r}; supported values are {', '.join(SAMPLING_MODES)}")
    # seed rotates deterministic remainder allocation, preserving even quotas.
    start=random.randrange(len(choices)) if choices else 0; ordered=choices[start:]+choices[:start]
    return [ordered[i%len(ordered)] for i in range(count)]
def generate_batch(seed:int,count:int,*,difficulty:int=1,sampling:str="balanced",**configuration:Any)->tuple[GeneratedTask,...]:
    spec=difficulty_spec(difficulty)
    if count<0: raise ValueError("count must be non-negative")
    slots=_slots(seed,count,eligible_program_kinds(spec["depth"]),sampling)
    return tuple(generate_task(seed+i,difficulty=difficulty,program_kinds=slot,**configuration) for i,slot in enumerate(slots))
