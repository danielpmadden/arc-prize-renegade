"""Deterministic evaluation-only diagnostics and grounded reasoning records."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from enum import Enum
from collections import Counter
from typing import Any, Iterable
from .solver import Grid, Program, SolverResult

class EvidenceState(str, Enum):
    NOT_OBSERVED="not_observed"; POSSIBLE="possible"; SUPPORTED="supported"; USED_BY_PROGRAM="used_by_program"; TRAINING_VALIDATED="training_validated"; OFFICIALLY_DEMONSTRATED="officially_demonstrated"
class GapKind(str, Enum):
    UNKNOWN="unknown"; REPRESENTATIONAL_GAP="representational_gap"; INFERENTIAL_GAP="inferential_gap"; EXECUTION_GAP="execution_gap"; SEARCH_GAP="search_gap"; PERCEPTUAL_GAP="perceptual_gap"; AMBIGUITY_GAP="ambiguity_gap"

@dataclass(frozen=True)
class ObserverEvidence:
    observer: str; state: EvidenceState; values: tuple[tuple[str, Any], ...]; hypothesis: bool = True

def observe_grid(grid: Grid) -> tuple[ObserverEvidence,...]:
    """Cheap observations only; this function has no solver call path."""
    h,w=len(grid),len(grid[0]); palette=Counter(x for row in grid for x in row)
    vertical=all(tuple(row)==tuple(reversed(row)) for row in grid)
    horizontal=tuple(grid)==tuple(reversed(grid))
    return (ObserverEvidence("symmetry_axis", EvidenceState.POSSIBLE if vertical or horizontal else EvidenceState.NOT_OBSERVED, (("horizontal",horizontal),("vertical",vertical))), ObserverEvidence("color_frequency_uniqueness", EvidenceState.SUPPORTED if any(n==1 for n in palette.values()) else EvidenceState.NOT_OBSERVED, tuple(sorted(((repr(k),v) for k,v in palette.items())))), ObserverEvidence("dimensions", EvidenceState.SUPPORTED, (("height",h),("width",w)), False))

def semantic_near_miss(predicted: Grid, expected: Grid) -> dict[str, Any]:
    """Evaluator-only comparison. Caller must invoke after prediction exists."""
    ph,pw=len(predicted),len(predicted[0]); eh,ew=len(expected),len(expected[0])
    flat=lambda g: tuple(x for row in g for x in row)
    pc,ec=Counter(flat(predicted)),Counter(flat(expected)); bg=min(ec,key=lambda x:(-ec[x],repr(x)))
    return {"dimensions_match":(ph,pw)==(eh,ew),"palette_match":set(pc)==set(ec),"non_background_cells_match":sum(v for k,v in pc.items() if k!=bg)==sum(v for k,v in ec.items() if k!=bg),"exact":predicted==expected,"provenance":"evaluator_private_post_prediction"}

def classify_gap(result: SolverResult) -> tuple[GapKind,float,str]:
    if result.status=="search_bound_reached": return GapKind.SEARCH_GAP,.75,"configured candidate bound reached"
    if result.status=="multiple_exact_hypotheses": return GapKind.AMBIGUITY_GAP,.7,"multiple public-training-exact hypotheses"
    return GapKind.UNKNOWN,.2,"no private-output comparison or counterfactual capability test supports a stronger diagnosis"

def reasoning_record(result: SolverResult) -> dict[str,Any]:
    gap,confidence,basis=classify_gap(result)
    return {"schema_version":1,"task":result.task_identifier,"configuration":result.telemetry.get("config",{}),"candidate_programs":[x.program.canonical for x in result.validations],"selected_program":result.selected_program.canonical if result.selected_program else None,"training_validation":{"exact_program_count":len(result.validations),"rejections":len(result.rejected)},"test_execution":{"prediction_count":len(result.predictions),"prediction_available":bool(result.predictions)},"ambiguities":result.status=="multiple_exact_hypotheses","bounds":{"search_exhausted":result.telemetry.get("search_exhausted",False),"candidates_explored":result.candidates_explored,"max_candidates":result.max_candidates},"gap":{"kind":gap.value,"confidence":confidence,"basis":basis},"grounding":"all statements derive from SolverResult public-training search telemetry; expected test outputs are absent"}

def render_reasoning(record:dict[str,Any])->str:
    return "\n".join((f"# Reasoning report: {record['task']}",f"Selected program: `{record['selected_program'] or 'none'}`",f"Training-exact programs: {record['training_validation']['exact_program_count']}",f"Predictions produced: {record['test_execution']['prediction_count']}",f"Gap diagnosis: {record['gap']['kind']} ({record['gap']['confidence']:.2f}; {record['gap']['basis']})",f"Grounding: {record['grounding']}"))

def mine_program_patterns(programs: Iterable[tuple[str,str,Program]]) -> tuple[dict[str,Any],...]:
    """Bounded canonical contiguous-subsequence count; proposals are never executable."""
    occurrences:dict[str,list[tuple[str,str]]]={}
    for task,corpus,program in programs:
        ops=program.operations
        for size in range(2,min(4,len(ops)+1)):
            for start in range(len(ops)-size+1): occurrences.setdefault(" -> ".join(x.kind for x in ops[start:start+size]),[]).append((task,corpus))
    return tuple({"canonical_structure":key,"occurrence_count":len(value),"distinct_task_count":len(set(x[0] for x in value)),"distinct_corpus_count":len(set(x[1] for x in value)),"promotion_status":"observed","estimated_description_length_savings":max(0,len(key)-len(key.split(" -> ")))} for key,value in sorted(occurrences.items()) if len(value)>1)
