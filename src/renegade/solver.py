"""Bounded, deterministic symbolic program search over public ARC task data.

The search is deliberately small: it enumerates public-operation prefixes,
deduplicates their complete training-state tuples, then fits a final operation
against the observed training outputs.  It never receives task metadata or
test labels.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable

from .tasks import Task, inspect_task

Grid = tuple[tuple[Any, ...], ...]


class ChangeKind(str, Enum):
    UNCHANGED = "unchanged"; RECOLORED = "recolored"; MOVED = "moved"
    CROPPED = "cropped"; ROTATED = "rotated"; REFLECTED = "reflected"
    FILLED = "filled"; OUTLINED = "outlined"; DIMENSION_CHANGED = "dimension_changed"; UNKNOWN = "unknown"


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
    def depth(self) -> int: return len(self.operations)

    @property
    def families(self) -> tuple[str, ...]: return tuple(op.kind for op in self.operations)

    @property
    def canonical(self) -> str:
        return " -> ".join(op.kind + ("(" + ",".join(f"{k}={v!r}" for k, v in op.parameters) + ")" if op.parameters else "") for op in self.operations)


@dataclass(frozen=True)
class SearchConfig:
    """Explicit finite bounds for public symbolic search."""
    max_depth: int = 2
    max_candidates: int = 512
    max_prefix_states: int = 128
    max_displacement: int = 2

    def __post_init__(self) -> None:
        if not 1 <= self.max_depth <= 3: raise ValueError("max_depth must be between 1 and 3")
        if self.max_candidates < 1 or self.max_prefix_states < 1 or self.max_displacement < 0: raise ValueError("search bounds must be positive")


@dataclass(frozen=True)
class Correspondence:
    input_region: tuple[Any, tuple[tuple[int, int], ...]] | None
    output_region: tuple[Any, tuple[tuple[int, int], ...]] | None
    evidence: tuple[str, ...]
    rank: int


@dataclass(frozen=True)
class ChangeSummary:
    kinds: tuple[ChangeKind, ...]; input_dimensions: tuple[int, int]; output_dimensions: tuple[int, int]
    changed_cells: tuple[tuple[int, int], ...]; correspondences: tuple[Correspondence, ...]


@dataclass(frozen=True)
class Validation:
    program: Program; passed: bool; pair_index: int | None; reason: str | None = None
    differing_cells: tuple[tuple[int, int], ...] = ()


@dataclass(frozen=True)
class SolverResult:
    task_identifier: str; status: str; selected_program: Program | None; alternatives: tuple[Program, ...]
    predictions: tuple[Grid, ...]; validations: tuple[Validation, ...]; rejected: tuple[Validation, ...]
    changes: tuple[ChangeSummary, ...]; candidates_explored: int; max_candidates: int
    failure_reason: str | None = None; telemetry: dict[str, Any] = field(default_factory=dict)


def background(grid: Grid) -> Any:
    counts = Counter(cell for row in grid for cell in row)
    return min(counts, key=lambda value: (-counts[value], repr(value)))


def regions(grid: Grid) -> tuple[tuple[Any, tuple[tuple[int, int], ...]], ...]:
    seen, answer = set(), []
    for r, row in enumerate(grid):
        for c, value in enumerate(row):
            if (r, c) in seen: continue
            stack, cells = [(r, c)], []; seen.add((r, c))
            while stack:
                x, y = stack.pop(); cells.append((x, y))
                for nx, ny in ((x-1,y), (x+1,y), (x,y-1), (x,y+1)):
                    if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]) and (nx, ny) not in seen and grid[nx][ny] == value:
                        seen.add((nx, ny)); stack.append((nx, ny))
            answer.append((value, tuple(sorted(cells))))
    return tuple(answer)


def correspondence(input_grid: Grid, output_grid: Grid) -> tuple[Correspondence, ...]:
    # Correspondence remains diagnostic only; search does not depend on it.
    ins, outs, result, used = regions(input_grid), regions(output_grid), [], set()
    for source in ins:
        shape = lambda item: tuple((r-min(x for x,_ in item[1]), c-min(y for _,y in item[1])) for r,c in item[1])
        choices = [(i, target) for i, target in enumerate(outs) if i not in used and len(target[1]) == len(source[1]) and shape(target) == shape(source)]
        if len(choices) == 1:
            i, target = choices[0]; used.add(i); evidence = ["same_cell_count", "same_normalized_shape"]
            if source[0] == target[0]: evidence.append("same_color")
            result.append(Correspondence(source, target, tuple(evidence), 0))
        else: result.append(Correspondence(source, None, ("unmatched" if not choices else "ambiguous",), len(choices)))
    result.extend(Correspondence(None, target, ("unmatched",), 0) for i, target in enumerate(outs) if i not in used)
    return tuple(result)


def apply(operation: Operation, grid: Grid) -> Grid:
    k = operation.kind
    if k == "identity": return grid
    if k == "recolor":
        mapping = dict(operation.parameter("mapping")); return tuple(tuple(mapping.get(v, v) for v in row) for row in grid)
    if k == "rotate":
        for _ in range(operation.parameter("turns") % 4): grid = tuple(tuple(grid[len(grid)-1-c][r] for c in range(len(grid))) for r in range(len(grid[0])))
        return grid
    if k == "reflect": return tuple(reversed(grid)) if operation.parameter("axis") == "horizontal" else tuple(tuple(reversed(row)) for row in grid)
    if k == "crop":
        bg = operation.parameter("background"); cells = [(r,c) for r,row in enumerate(grid) for c,v in enumerate(row) if v != bg]
        if not cells: return grid
        rs, cs = zip(*cells); return tuple(tuple(row[min(cs):max(cs)+1]) for row in grid[min(rs):max(rs)+1])
    if k == "translate":
        dr, dc = operation.parameter("offset"); bg = operation.parameter("background"); canvas = [[bg] * len(grid[0]) for _ in grid]
        for r, row in enumerate(grid):
            for c, value in enumerate(row):
                if value != bg and 0 <= r + dr < len(grid) and 0 <= c + dc < len(row): canvas[r + dr][c + dc] = value
        return tuple(tuple(row) for row in canvas)
    if k == "fill" or k == "outline":
        # Preserve existing executable semantics for direct primitive fitting.
        bg = operation.parameter("background")
        if k == "outline":
            canvas = [list(row) for row in grid]
            for r,row in enumerate(grid):
                for c,v in enumerate(row):
                    if v != bg and all(0 <= nr < len(grid) and 0 <= nc < len(row) and grid[nr][nc] == v for nr,nc in ((r-1,c),(r+1,c),(r,c-1),(r,c+1))): canvas[r][c] = bg
            return tuple(tuple(row) for row in canvas)
        canvas=[list(row) for row in grid]; exterior=set(); stack=[]
        for r in range(len(grid)):
            for c in range(len(grid[0])):
                if (r in (0,len(grid)-1) or c in (0,len(grid[0])-1)) and grid[r][c] == bg: exterior.add((r,c)); stack.append((r,c))
        while stack:
            r,c=stack.pop()
            for nr,nc in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)):
                if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] == bg and (nr,nc) not in exterior: exterior.add((nr,nc)); stack.append((nr,nc))
        color = operation.parameter("color")
        for r,row in enumerate(grid):
            for c,v in enumerate(row):
                if v == bg and (r,c) not in exterior: canvas[r][c] = bg if color == "enclosing" else color
        return tuple(tuple(row) for row in canvas)
    raise ValueError(f"unsupported operation: {k}")


def execute(program: Program, grid: Grid) -> Grid:
    for operation in program.operations: grid = apply(operation, grid)
    return grid


def _summary(a: Grid, b: Grid) -> ChangeSummary:
    changed = tuple((r,c) for r in range(min(len(a),len(b))) for c in range(min(len(a[0]),len(b[0]))) if a[r][c] != b[r][c])
    kinds = [ChangeKind.UNCHANGED] if a == b else []
    if (len(a),len(a[0])) != (len(b),len(b[0])): kinds.append(ChangeKind.DIMENSION_CHANGED)
    corr = correspondence(a,b)
    if any(x.input_region and x.output_region and x.input_region[0] != x.output_region[0] for x in corr): kinds.append(ChangeKind.RECOLORED)
    if any(x.input_region and x.output_region and x.input_region[1] != x.output_region[1] for x in corr): kinds.append(ChangeKind.MOVED)
    return ChangeSummary(tuple(kinds or [ChangeKind.UNKNOWN]), (len(a),len(a[0])), (len(b),len(b[0])), changed, corr)


def _fits(operation: Operation, pairs: tuple[tuple[Grid, Grid], ...]) -> bool:
    try: return all(apply(operation, source) == target for source, target in pairs)
    except (KeyError, TypeError, ValueError): return False


def _infer_primitives(pairs: tuple[tuple[Grid, Grid], ...]) -> tuple[Program, ...]:
    """Fit parameterized one-step hypotheses to arbitrary aligned tuples."""
    candidates = [Operation.make("identity")]
    candidates += [Operation.make("rotate", turns=turns) for turns in (1,2,3)]
    candidates += [Operation.make("reflect", axis=axis) for axis in ("horizontal", "vertical")]
    mapping: dict[Any, Any] = {}; consistent = True
    for source, target in pairs:
        if len(source) != len(target) or len(source[0]) != len(target[0]): consistent = False; break
        for left, right in zip((x for row in source for x in row), (x for row in target for x in row)):
            if left in mapping and mapping[left] != right: consistent = False
            mapping[left] = right
    if consistent and mapping: candidates.append(Operation.make("recolor", mapping=tuple(sorted(mapping.items(), key=repr))))
    backgrounds = {background(source) for source, _ in pairs}
    if len(backgrounds) == 1:
        bg = next(iter(backgrounds)); candidates += [Operation.make("crop", background=bg), Operation.make("fill", background=bg, color="enclosing"), Operation.make("outline", background=bg)]
        h, w = len(pairs[0][0]), len(pairs[0][0][0])
        candidates += [Operation.make("translate", offset=(dr,dc), background=bg) for dr in range(-h,h+1) for dc in range(-w,w+1)]
    return tuple(Program((op,)) for op in candidates if _fits(op, pairs))


def _prefix_operations(sources: tuple[Grid, ...], targets: tuple[Grid, ...], config: SearchConfig) -> tuple[Operation, ...]:
    """Finite public prefix vocabulary; recolor targets use only observed palette."""
    palette = sorted({v for grid in sources + targets for row in grid for v in row}, key=repr)
    colors = sorted({v for grid in sources for row in grid for v in row}, key=repr)
    ops = [Operation.make("rotate", turns=x) for x in (1,2,3)] + [Operation.make("reflect", axis=x) for x in ("horizontal","vertical")]
    for source in colors:
        for target in palette:
            if source != target: ops.append(Operation.make("recolor", mapping=((source,target),)))
    bgs = {background(grid) for grid in sources}
    if len(bgs) == 1:
        bg = next(iter(bgs))
        ops += [Operation.make("translate", offset=(dr,dc), background=bg) for dr in range(-config.max_displacement,config.max_displacement+1) for dc in range(-config.max_displacement,config.max_displacement+1) if (dr,dc) != (0,0)]
    return tuple(ops)


def _validate(program: Program, pairs: tuple[tuple[Grid, Grid], ...]) -> Validation:
    for index, (source, expected) in enumerate(pairs, 1):
        try: actual = execute(program, source)
        except (KeyError, TypeError, ValueError) as error: return Validation(program, False, index, f"execution failure: {error}")
        if actual != expected:
            diffs = () if len(actual) != len(expected) or len(actual[0]) != len(expected[0]) else tuple((r,c) for r in range(len(actual)) for c in range(len(actual[0])) if actual[r][c] != expected[r][c])
            return Validation(program, False, index, "dimension mismatch" if not diffs else "cell mismatch", diffs)
    return Validation(program, True, None)


def solve_task(task: Task, *, max_depth: int = 2, max_candidates: int = 512, config: SearchConfig | None = None) -> SolverResult:
    if not isinstance(task, Task): raise TypeError("task must be a Task")
    config = config or SearchConfig(max_depth=max_depth, max_candidates=max_candidates)
    inspected = inspect_task(task) if not task.trace else task
    pairs = tuple((p.input_grid.raw_grid, p.output_grid.raw_grid) for p in inspected.training_pairs)
    sources, targets = tuple(x for x,_ in pairs), tuple(y for _,y in pairs)
    telemetry: dict[str, Any] = {"config":{"max_depth":config.max_depth,"max_candidates":config.max_candidates,"max_prefix_states":config.max_prefix_states,"max_displacement":config.max_displacement}, "primitive_candidates_attempted":0,"primitive_candidates_train_valid":0,"depth_two_prefixes_attempted":0,"depth_two_unique_intermediate_states":0,"depth_two_complete_programs_attempted":0,"depth_two_train_valid":0,"depth_three_prefixes_attempted":0,"depth_three_complete_programs_attempted":0,"depth_three_train_valid":0,"duplicate_states_removed":0,"rejected_by_reason":defaultdict(int)}
    rejected: list[Validation] = []; valid: dict[str, Program] = {}; explored = 0
    def consider(program: Program, depth_key: str) -> None:
        nonlocal explored
        if explored >= config.max_candidates: return
        explored += 1; verdict = _validate(program, pairs)
        if verdict.passed: valid.setdefault(program.canonical, program); telemetry[f"{depth_key}_train_valid"] = telemetry.get(f"{depth_key}_train_valid", 0) + 1
        else: rejected.append(verdict); telemetry["rejected_by_reason"][verdict.reason or "unknown"] += 1
    for program in _infer_primitives(pairs):
        telemetry["primitive_candidates_attempted"] += 1; consider(program, "primitive_candidates")
    telemetry["primitive_candidates_train_valid"] = len([p for p in valid.values() if p.depth == 1])
    prefixes = {tuple(sources): Program(())}
    for depth in range(1, config.max_depth):
        next_prefixes: dict[tuple[Grid, ...], Program] = {}
        for state, prefix in sorted(prefixes.items(), key=lambda item: item[1].canonical):
            for op in _prefix_operations(state, targets, config):
                key = f"depth_{depth + 1}"
                telemetry[f"{key}_prefixes_attempted"] = telemetry.get(f"{key}_prefixes_attempted", 0) + 1
                try: next_state = tuple(apply(op, grid) for grid in state)
                except (KeyError, TypeError, ValueError): telemetry["rejected_by_reason"]["prefix_execution_failure"] += 1; continue
                candidate_prefix = Program(prefix.operations + (op,))
                old = next_prefixes.get(next_state)
                if old is None or candidate_prefix.canonical < old.canonical: next_prefixes[next_state] = candidate_prefix
                else: telemetry["duplicate_states_removed"] += 1
        prefixes = dict(sorted(next_prefixes.items(), key=lambda item: item[1].canonical)[:config.max_prefix_states])
        telemetry[f"depth_{depth}_unique_intermediate_states"] = len(prefixes)
        for state, prefix in prefixes.items():
            for final in _infer_primitives(tuple(zip(state, targets))):
                program = Program(prefix.operations + final.operations)
                if program.depth != depth + 1: continue
                telemetry[f"depth_{depth + 1}_complete_programs_attempted"] = telemetry.get(f"depth_{depth + 1}_complete_programs_attempted", 0) + 1
                consider(program, f"depth_{depth + 1}")
        # For the next layer, prefixes must be exactly this depth, not fitted finals.
    if not rejected and not valid:
        rejected.append(_validate(Program((Operation.make("identity"),)), pairs))
    # Preserve the prior primitive preference (identity, rotations, reflections,
    # recolor, then shape/translation operations) as the deterministic
    # ambiguity fallback; composition remains secondary to a shorter program.
    operation_rank = {"identity": 0, "rotate": 1, "reflect": 2, "recolor": 3, "crop": 4, "fill": 5, "outline": 6, "translate": 7}
    ordered = tuple(sorted(valid.values(), key=lambda p: (p.depth, tuple(operation_rank.get(op.kind, 99) for op in p.operations), p.canonical)))
    predictions_by_output: dict[tuple[Grid, ...], list[Program]] = defaultdict(list)
    for program in ordered: predictions_by_output[tuple(execute(program, grid.raw_grid) for grid in inspected.test_inputs)].append(program)
    selected = ordered[0] if ordered else None
    predictions: tuple[Grid, ...] = ()
    if selected:
        # Existing solver behavior ranked exact hypotheses by stable canonical
        # order.  Preserve that documented deterministic fallback while making
        # disagreement explicit in telemetry and status.
        predictions = tuple(execute(selected, grid.raw_grid) for grid in inspected.test_inputs)
    telemetry["train_valid_candidate_count"] = len(ordered); telemetry["distinct_test_prediction_count"] = len(predictions_by_output)
    telemetry["selected_program"] = selected.canonical if selected else None; telemetry["selected_program_depth"] = selected.depth if selected else None
    telemetry["selection_reason"] = "unanimous_prediction" if len(predictions_by_output) == 1 and selected else "deterministic_ranked_ambiguity" if selected else "no_train_valid_program"
    telemetry["search_exhausted"] = explored >= config.max_candidates; telemetry["rejected_by_reason"] = dict(sorted(telemetry["rejected_by_reason"].items()))
    status = "solved" if predictions and len(ordered) == 1 else "multiple_exact_hypotheses" if predictions else "search_bound_reached" if telemetry["search_exhausted"] else "no_exact_training_hypothesis"
    return SolverResult(inspected.identifier, status, selected, ordered[1:], predictions, tuple(Validation(p, True, None) for p in ordered), tuple(rejected), tuple(_summary(*pair) for pair in pairs), explored, config.max_candidates, None if selected else "No candidate constructed every training output exactly.", telemetry)
