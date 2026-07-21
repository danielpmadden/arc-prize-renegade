"""Validated, dormant architectural knowledge; never consulted by solver search.

This module is intentionally data-only.  It makes capability claims auditable
without treating a name in the ontology as an executable solver feature.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
from enum import Enum
import json
from pathlib import Path
from typing import Any, Iterable

class Maturity(str, Enum):
    SEEDED="seeded"; DESCRIBED="described"; OBSERVABLE="observable"; REPRESENTED="represented"; QUERYABLE="queryable"; EXECUTABLE="executable"; SEARCHABLE="searchable"; SYNTHETICALLY_VALIDATED="synthetically_validated"; OFFICIALLY_OBSERVED="officially_observed"; OFFICIALLY_DEMONSTRATED="officially_demonstrated"; STABLE="stable"; DEPRECATED="deprecated"

# Advancement is deliberately one-way; evidence does not silently promote records.
_ORDER = tuple(Maturity)
def maturity_transition_allowed(before: Maturity, after: Maturity) -> bool:
    return before is Maturity.DEPRECATED and after is Maturity.DEPRECATED or before is not Maturity.DEPRECATED and after is not Maturity.DEPRECATED and _ORDER.index(after) >= _ORDER.index(before)

@dataclass(frozen=True)
class ConceptRecord:
    identifier: str; name: str; family: str; definition: str; maturity: Maturity
    aliases: tuple[str,...] = (); prerequisites: tuple[str,...] = (); related: tuple[str,...] = ()
    observable_signals: tuple[str,...] = (); program_roles: tuple[str,...] = ()
    implementation_references: tuple[str,...] = (); evidence_references: tuple[str,...] = (); notes: str = ""

@dataclass(frozen=True)
class CapabilityRecord:
    identifier: str; concepts: tuple[str,...]; description: str; inputs: tuple[str,...]; outputs: tuple[str,...]
    entry_points: tuple[str,...]; search_integration: str; serialization: str; maturity: Maturity
    known_limits: tuple[str,...] = (); governing_constraints: tuple[str,...] = ()

@dataclass(frozen=True)
class Finding:
    identifier: str; governing_source: str; governing_claim: str; evidence: tuple[str,...]; classification: str
    severity: str; affected_modules: tuple[str,...]; consequence: str; recommended_action: str; change_kinds: tuple[str,...]; status: str

VALID_FINDING_CLASSES=frozenset({"ALIGNED","STRENGTHENED","EVOLVED","UNDERSPECIFIED","STALE","DRIFTED","CONTRADICTED","UNIMPLEMENTED","UNVERIFIED","DEPRECATED","REQUIRES_AMENDMENT"})

def _records(raw: Iterable[dict[str, Any]], cls: type[ConceptRecord]|type[CapabilityRecord]):
    answer=[]
    for item in raw:
        item=dict(item); item["maturity"]=Maturity(item["maturity"])
        for key, value in tuple(item.items()):
            if isinstance(value, list): item[key]=tuple(value)
        answer.append(cls(**item))
    return tuple(answer)

def load_knowledge(path: Path | None = None) -> tuple[tuple[ConceptRecord,...],tuple[CapabilityRecord,...]]:
    path=path or Path(__file__).resolve().parents[2]/"docs"/"knowledge"/"seed-bank.json"
    raw=json.loads(path.read_text(encoding="utf-8"))
    concepts=_records(raw["concepts"], ConceptRecord); capabilities=_records(raw["capabilities"], CapabilityRecord)
    validate_knowledge(concepts, capabilities); return concepts, capabilities

def validate_knowledge(concepts: tuple[ConceptRecord,...], capabilities: tuple[CapabilityRecord,...]) -> None:
    ids=[x.identifier for x in concepts]
    if len(ids)!=len(set(ids)) or any(not x or not x.replace("_","").isalnum() for x in ids): raise ValueError("concept identifiers must be unique stable tokens")
    known=set(ids)
    for item in concepts:
        missing=(set(item.prerequisites) | set(item.related)) - known
        if missing: raise ValueError(f"broken concept reference in {item.identifier}: {sorted(missing)}")
        if item.identifier in item.prerequisites: raise ValueError(f"self dependency: {item.identifier}")
    # Dependencies alone are acyclic; 'related' edges deliberately may cycle.
    visiting:set[str]=set(); done:set[str]=set(); lookup={x.identifier:x for x in concepts}
    def visit(key:str)->None:
        if key in visiting: raise ValueError(f"cyclic concept dependency: {key}")
        if key not in done:
            visiting.add(key)
            for child in lookup[key].prerequisites: visit(child)
            visiting.remove(key); done.add(key)
    for key in known: visit(key)
    capids=[x.identifier for x in capabilities]
    if len(capids)!=len(set(capids)): raise ValueError("capability identifiers must be unique")
    for item in capabilities:
        missing=set(item.concepts)-known
        if missing: raise ValueError(f"broken capability concept reference in {item.identifier}: {sorted(missing)}")
        if item.maturity in {Maturity.EXECUTABLE,Maturity.SEARCHABLE,Maturity.STABLE} and not item.entry_points: raise ValueError(f"executable capability lacks entry point: {item.identifier}")

def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",",":"), ensure_ascii=True)

def knowledge_report() -> dict[str, Any]:
    concepts, capabilities=load_knowledge()
    return {"concept_count":len(concepts),"capability_count":len(capabilities),"concepts_by_maturity":{m.value:sum(x.maturity is m for x in concepts) for m in Maturity},"solver_integration":"none: seed-bank records are not passed to solve_task"}
