"""Versioned, evaluator-private synthetic cases for typed composition."""
from __future__ import annotations
from dataclasses import dataclass
from .grammar import Grid, GrammarConfig, search

@dataclass(frozen=True)
class CompositionCase:
    identifier:str; family:str; training:tuple[tuple[Grid,Grid],...]; test_inputs:tuple[Grid,...]; expected:tuple[Grid,...]
    concepts:tuple[str,...]; expected_depth:int; shortcut_analysis:str

def _grid(*rows): return tuple(tuple(row) for row in rows)
def cases() -> tuple[CompositionCase,...]:
    # Each input has distractors, and colours/locations vary over pairs.  There
    # is no end-to-end family operation in the registry.
    return (
      CompositionCase("composition-v1-largest-recolor","filter_recolor_tight",
       ((_grid((0,2,0,0),(0,2,0,3),(0,2,0,0)),_grid((7,),(7,),(7,))), (_grid((4,0,0,0),(4,4,4,1),(0,0,0,1)),_grid((7,0,0),(7,7,7))),),
       (_grid((0,5,0,0),(0,5,0,6),(0,5,0,0)),),(_grid((7,),(7,),(7,)),),("objecthood","selection","construction"),5,"location and source colour vary; only largest component survives"),
      CompositionCase("composition-v1-smallest-tight","filter_tight_render",
       ((_grid((0,2,2,0),(0,2,0,3),(4,4,4,3)),_grid((3,),(3,))), (_grid((5,0,0),(5,5,5),(0,0,6)),_grid((6,)),)),
       (_grid((0,8,8,0),(0,8,0,9)),),(_grid((9,)),),("objecthood","selection","construction"),4,"the retained shape is selected by size, not colour or position"),
    )

def evaluate_curriculum() -> dict:
    rows=[]
    for case in cases():
        result=search(case.training,case.test_inputs,config=GrammarConfig(max_candidates=256))
        rows.append({"id":case.identifier,"family":case.family,"solved":result.predictions==case.expected,"program":result.program.canonical if result.program else None,"telemetry":result.telemetry})
    return {"schema_version":1,"case_count":len(rows),"solved":sum(x["solved"] for x in rows),"cases":rows}
