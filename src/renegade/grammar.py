"""A small typed, immutable object-composition grammar.

This is deliberately separate from :mod:`renegade.solver`'s legacy grid
programs.  It reuses ``Scene`` rather than reconstructing a scene after each
object operation: a ``segment`` expression is evaluated once per grid and all
downstream expressions consume that immutable value.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from enum import Enum
import json
from typing import Any, Callable

from .scene import ObjectPredicate, PredicateKind, Scene, SceneObject

Grid = tuple[tuple[Any, ...], ...]

class ValueType(str, Enum):
    GRID="Grid"; SCENE="Scene"; OBJECT_SET="ObjectSet"; OBJECT="Object"; COUNT="Count"; COLOR="Color"; CANVAS_SPEC="CanvasSpec"

@dataclass(frozen=True)
class CanvasSpec:
    mode: str = "tight"
    background: Any = 0
    def __post_init__(self):
        if self.mode not in {"tight", "preserve"}: raise ValueError("canvas mode must be tight or preserve")

@dataclass(frozen=True)
class GrammarFailure:
    operation: str; reason: str

@dataclass(frozen=True)
class OperationSpec:
    identifier: str; family: str; input_types: tuple[ValueType,...]; output_type: ValueType
    literal_domains: tuple[tuple[str, tuple[Any,...]],...]; executor: Callable[..., Any] = field(compare=False, hash=False, repr=False)
    deterministic: bool=True; ambiguity: str="explicit_failure"; stage: str="object"; cost: int=1
    maturity: str="executable"; capability: str=""; serialization_version: int=1; official_solving_eligible: bool=False

@dataclass(frozen=True)
class Expr:
    """Canonical, immutable expression.  Arguments are in declared order."""
    operation: str; arguments: tuple["Expr", ...] = (); literals: tuple[tuple[str, Any], ...] = ()
    input_type: ValueType | None = None; output_type: ValueType | None = None; version: int = 1
    def __post_init__(self): object.__setattr__(self, "literals", tuple(sorted(self.literals)))
    @property
    def canonical(self) -> str:
        bits = [a.canonical for a in self.arguments] + [f"{k}={v!r}" for k,v in self.literals]
        return f"{self.operation}({','.join(bits)})"
    def to_dict(self) -> dict[str, Any]:
        return {"version": self.version, "operation": self.operation, "arguments":[x.to_dict() for x in self.arguments], "literals":[list(x) for x in self.literals]}
    @classmethod
    def from_dict(cls, data: dict[str, Any], registry: "OperationRegistry") -> "Expr":
        if data.get("version") != 1: raise ValueError("unsupported grammar expression version")
        args=tuple(cls.from_dict(x, registry) for x in data.get("arguments", []))
        return registry.expression(data["operation"], args, dict(data.get("literals", [])))
    def render(self) -> str: return self.canonical

class OperationRegistry:
    def __init__(self, specs: tuple[OperationSpec,...]): self._specs={x.identifier:x for x in specs}
    def specs(self) -> tuple[OperationSpec,...]: return tuple(self._specs[x] for x in sorted(self._specs))
    def expression(self, identifier: str, arguments: tuple[Expr,...]=(), literals: dict[str,Any]|None=None) -> Expr:
        if identifier == "input":
            if arguments or literals: raise ValueError("input accepts no arguments")
            return Expr("input", (), (), None, ValueType.GRID)
        spec=self._specs.get(identifier)
        if spec is None: raise ValueError(f"unknown grammar operation: {identifier}")
        if tuple(x.output_type for x in arguments) != spec.input_types: raise TypeError(f"{identifier} requires {spec.input_types}, got {tuple(x.output_type for x in arguments)}")
        literals=literals or {}; domains=dict(spec.literal_domains)
        if set(literals) != set(domains): raise ValueError(f"{identifier} literals must be {tuple(domains)}")
        if any(value not in domains[key] for key,value in literals.items()): raise ValueError(f"invalid literal for {identifier}")
        return Expr(identifier, arguments, tuple(literals.items()), spec.input_types[0] if len(spec.input_types)==1 else None, spec.output_type, spec.serialization_version)
    def spec(self, identifier: str) -> OperationSpec: return self._specs[identifier]

def _segment(grid: Grid, *, background: Any, connectivity: int) -> Scene: return Scene.from_grid(grid, background, connectivity)
def _objects(scene: Scene) -> tuple[SceneObject,...]: return scene.objects
def _filter(objects: tuple[SceneObject,...], *, predicate: str) -> tuple[SceneObject,...]:
    # Objects retain their originating scene shape; evaluate the existing predicate on a reconstructed immutable scene only once here is unnecessary.
    # Predicate facts needing the complete scene are calculated from the set deterministically.
    if predicate == "all": return objects
    if not objects: return ()
    if predicate == "largest": return tuple(x for x in objects if x.cell_count == max(y.cell_count for y in objects))
    if predicate == "smallest": return tuple(x for x in objects if x.cell_count == min(y.cell_count for y in objects))
    if predicate == "border": return tuple(x for x in objects if x.touches_border)
    return tuple(x for x in objects if not x.touches_border)
def _unique(objects: tuple[SceneObject,...]) -> SceneObject:
    if len(objects) != 1: raise ValueError("selection is absent or ambiguous")
    return objects[0]
def _singleton(obj: SceneObject) -> tuple[SceneObject,...]: return (obj,)
def _recolor(objects: tuple[SceneObject,...], *, color: Any) -> tuple[SceneObject,...]:
    return tuple(SceneObject(color, x.cells, x.bounding_box, x.mask, x.scene_shape) for x in objects)
def _canvas(scene: Scene, *, mode: str) -> CanvasSpec: return CanvasSpec(mode, scene.background)
def _render(objects: tuple[SceneObject,...], canvas: CanvasSpec) -> Grid:
    if not objects: raise ValueError("cannot render an empty object set")
    if canvas.mode == "preserve":
        h,w=objects[0].scene_shape; out=[[canvas.background]*w for _ in range(h)]; top=left=0
    else:
        top=min(x.bounding_box.top for x in objects); left=min(x.bounding_box.left for x in objects)
        bottom=max(x.bounding_box.bottom for x in objects); right=max(x.bounding_box.right for x in objects); out=[[canvas.background]*(right-left+1) for _ in range(bottom-top+1)]
    for obj in objects:
        for r,c in obj.cells: out[r-top][c-left]=obj.color
    return tuple(tuple(row) for row in out)

DEFAULT_REGISTRY=OperationRegistry((
    OperationSpec("segment","perception",(ValueType.GRID,),ValueType.SCENE,(("background",tuple(range(10))),("connectivity",(4,8))),_segment,cost=1,capability="scene_components"),
    OperationSpec("objects","extraction",(ValueType.SCENE,),ValueType.OBJECT_SET,(),_objects,cost=1,capability="scene_components"),
    OperationSpec("filter","selection",(ValueType.OBJECT_SET,),ValueType.OBJECT_SET,(("predicate",("all","largest","smallest","border","interior")),),_filter,cost=1,capability="object_render"),
    OperationSpec("unique","selection",(ValueType.OBJECT_SET,),ValueType.OBJECT,(),_unique,cost=1,capability="object_render"),
    OperationSpec("singleton","selection",(ValueType.OBJECT,),ValueType.OBJECT_SET,(),_singleton,cost=1,capability="object_render"),
    OperationSpec("recolor_set","transform",(ValueType.OBJECT_SET,),ValueType.OBJECT_SET,(("color",tuple(range(10))),),_recolor,cost=1,capability="object_render"),
    OperationSpec("canvas","layout",(ValueType.SCENE,),ValueType.CANVAS_SPEC,(("mode",("tight","preserve")),),_canvas,cost=1,capability="object_render"),
    OperationSpec("render","render",(ValueType.OBJECT_SET,ValueType.CANVAS_SPEC),ValueType.GRID,(),_render,cost=1,capability="object_render"),
))

@dataclass(frozen=True)
class GrammarConfig:
    max_depth:int=6; max_candidates:int=256; max_per_type:int=64; max_scene_interpretations:int=1; max_literals:int=10
    def __post_init__(self):
        if not (1<=self.max_depth<=8 and self.max_candidates>0 and self.max_per_type>0 and self.max_scene_interpretations>0): raise ValueError("invalid finite grammar budget")

@dataclass(frozen=True)
class GrammarResult:
    program: Expr|None; alternatives: tuple[Expr,...]; predictions: tuple[Grid,...]; telemetry: dict[str,Any]; failure: GrammarFailure|None=None

def evaluate(expr: Expr, grid: Grid, *, registry: OperationRegistry=DEFAULT_REGISTRY, cache: dict[tuple[str,Grid],Any]|None=None) -> Any:
    cache={} if cache is None else cache; key=(expr.canonical,grid)
    stats=cache.setdefault(("__grammar_stats__", ()), {"hits":0,"misses":0})
    if key in cache:
        stats["hits"]+=1
        return cache[key]
    stats["misses"]+=1
    if expr.operation == "input": value=grid
    else:
        spec=registry.spec(expr.operation); values=tuple(evaluate(x,grid,registry=registry,cache=cache) for x in expr.arguments)
        value=spec.executor(*values, **dict(expr.literals))
    cache[key]=value; return value

def _depth(expression: Expr) -> int:
    """Return the longest typed-expression path, not its serialized size."""
    return 1 + max((_depth(argument) for argument in expression.arguments), default=0)


def _selection_expressions(
    registry: OperationRegistry, scene: Expr, palette: tuple[Any, ...], max_depth: int,
) -> tuple[Expr, ...]:
    """Build the finite, typed selection sublanguage already in the registry.

    This deliberately introduces no operation or literal.  In particular, an
    object set may be refined more than once before rendering.  Expressions
    are retained structurally (rather than by evaluated
    value) so training pairs remain the sole validation evidence.
    """
    initial = registry.expression("objects", (scene,))
    by_depth: dict[int, set[Expr]] = {_depth(initial): {initial}}
    all_sets: set[Expr] = {initial}
    for depth in range(_depth(initial) + 1, max_depth + 1):
        produced: set[Expr] = set()
        for parent_depth in range(1, depth):
            for expression in sorted(by_depth.get(parent_depth, ()), key=lambda item: item.canonical):
                if expression.output_type is ValueType.OBJECT_SET:
                    # ``all`` is represented by the unmodified initial set;
                    # adding it again would only consume finite search budget.
                    for predicate in ("largest", "smallest", "border", "interior"):
                        produced.add(registry.expression("filter", (expression,), {"predicate": predicate}))
                    for color in palette:
                        produced.add(registry.expression("recolor_set", (expression,), {"color": color}))
        exact = {item for item in produced if _depth(item) == depth}
        if exact:
            by_depth[depth] = exact
            all_sets.update(exact)
    return tuple(sorted(all_sets, key=lambda item: (_depth(item), item.canonical)))

def _expression_depth(expr: Expr) -> int:
    """Return the longest operation path below ``expr`` (excluding input)."""
    if expr.operation == "input": return 0
    return 1 + max((_expression_depth(argument) for argument in expr.arguments), default=0)

def search(training: tuple[tuple[Grid,Grid],...], test_inputs: tuple[Grid,...], *, config: GrammarConfig=GrammarConfig(), registry: OperationRegistry=DEFAULT_REGISTRY) -> GrammarResult:
    """Enumerate finite typed compositions; targets only validate completed programs."""
    if not training: raise ValueError("training pairs required")
    palette=sorted({v for a,b in training for g in (a,b) for row in g for v in row}, key=repr)[:config.max_literals]
    backgrounds=sorted({max(Counter(v for row in a for v in row), key=lambda x:(Counter(v for row in a for v in row)[x],repr(x))) for a,_ in training},key=repr)[:config.max_scene_interpretations]
    telemetry={"generated":defaultdict(int),"rejected":0,"depth_rejected":0,"retained":defaultdict(int),"cache_hits":0,"cache_misses":0,"scene_interpretations":len(backgrounds),"truncated":False,"max_candidates":config.max_candidates,"max_depth":config.max_depth}
    found=[]; cache={}
    for bg in backgrounds:
      for predicate in ("all","largest","smallest","border","interior"):
       for color in [-1,*palette]:
        for mode in ("tight","preserve"):
         if len(found)+telemetry["rejected"] >= config.max_candidates: telemetry["truncated"]=True; break
         expr=_chain(registry,bg,color,predicate,mode); telemetry["generated"][expr.output_type.value]+=1
         if _expression_depth(expr) > config.max_depth:
             telemetry["depth_rejected"] += 1
             continue
         try: fits=all(evaluate(expr,a,registry=registry,cache=cache)==b for a,b in training)
         except (ValueError,TypeError,IndexError): fits=False
         if fits: found.append(expr); telemetry["retained"][expr.output_type.value]+=1
         else: telemetry["rejected"]+=1
    found=sorted(set(found),key=lambda x:(x.canonical.count("("),x.canonical))
    if not found: return GrammarResult(None,(),(),dict(telemetry),GrammarFailure("search","no exact typed composition within budget"))
    selected=found[0]
    try: predictions=tuple(evaluate(selected,x,registry=registry,cache=cache) for x in test_inputs)
    except (ValueError,TypeError,IndexError) as e: return GrammarResult(None,tuple(found),(),dict(telemetry),GrammarFailure("test_execution",str(e)))
    return GrammarResult(selected,tuple(found[1:]),predictions,dict(telemetry))

def validate_registry(registry: OperationRegistry=DEFAULT_REGISTRY) -> dict[str,Any]:
    specs=registry.specs()
    if len({x.identifier for x in specs}) != len(specs): raise ValueError("duplicate operation identifiers")
    return {"schema_version":1,"operation_count":len(specs),"operations":[x.identifier for x in specs]}

def serialize(expr: Expr) -> str: return json.dumps(expr.to_dict(),sort_keys=True,separators=(",",":"),default=str)
def deserialize(text: str, registry: OperationRegistry=DEFAULT_REGISTRY) -> Expr: return Expr.from_dict(json.loads(text),registry)
