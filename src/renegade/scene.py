"""Immutable, canonical scene values used by the experimental object solver.

The module deliberately keeps interpretation finite: a scene is either a
four- or eight-connected, same-colour component interpretation.  Selection
returns an ordered *set*; callers which need one object must ask explicitly
and receive ``None`` for ambiguity.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import Enum
from typing import Any

Grid = tuple[tuple[Any, ...], ...]

@dataclass(frozen=True, order=True)
class BoundingBox:
    top: int; left: int; bottom: int; right: int
    @property
    def height(self) -> int: return self.bottom - self.top + 1
    @property
    def width(self) -> int: return self.right - self.left + 1
    @property
    def area(self) -> int: return self.height * self.width

@dataclass(frozen=True, order=True)
class SceneObject:
    color: Any; cells: tuple[tuple[int, int], ...]; bounding_box: BoundingBox
    mask: tuple[tuple[int, int], ...]; scene_shape: tuple[int, int]
    @property
    def cell_count(self) -> int: return len(self.cells)
    @property
    def touches_border(self) -> bool:
        h, w = self.scene_shape
        return any(r in (0, h - 1) or c in (0, w - 1) for r, c in self.cells)
    @property
    def shape_signature(self) -> tuple[tuple[int, int], ...]: return self.mask

class SelectorKind(str, Enum):
    LARGEST="largest"; SMALLEST="smallest"; LEFTMOST="leftmost"; RIGHTMOST="rightmost"; TOPMOST="topmost"; BOTTOMMOST="bottommost"

class PredicateKind(str, Enum):
    ALL="all"; BORDER="border"; INTERIOR="interior"; UNIQUE_COLOR="unique_color"; UNIQUE_SHAPE="unique_shape"; UNIQUE_SIZE="unique_size"
    LARGEST="largest"; SMALLEST="smallest"; WIDEST="widest"; TALLEST="tallest"; LEFTMOST="leftmost"; RIGHTMOST="rightmost"; TOPMOST="topmost"; BOTTOMMOST="bottommost"

@dataclass(frozen=True, order=True)
class ObjectPredicate:
    kind: PredicateKind
    def matches(self, scene: "Scene", index: int) -> bool:
        obj = scene.objects[index]
        if self.kind is PredicateKind.ALL: return True
        if self.kind is PredicateKind.BORDER: return obj.touches_border
        if self.kind is PredicateKind.INTERIOR: return not obj.touches_border
        counts = {
            PredicateKind.UNIQUE_COLOR: Counter(x.color for x in scene.objects)[obj.color],
            PredicateKind.UNIQUE_SHAPE: Counter(x.mask for x in scene.objects)[obj.mask],
            PredicateKind.UNIQUE_SIZE: Counter(x.cell_count for x in scene.objects)[obj.cell_count],
        }
        if self.kind in counts: return counts[self.kind] == 1
        values = {
            PredicateKind.LARGEST: (obj.cell_count, max(x.cell_count for x in scene.objects)),
            PredicateKind.SMALLEST: (-obj.cell_count, max(-x.cell_count for x in scene.objects)),
            PredicateKind.WIDEST: (obj.bounding_box.width, max(x.bounding_box.width for x in scene.objects)),
            PredicateKind.TALLEST: (obj.bounding_box.height, max(x.bounding_box.height for x in scene.objects)),
            PredicateKind.LEFTMOST: (-obj.bounding_box.left, max(-x.bounding_box.left for x in scene.objects)),
            PredicateKind.RIGHTMOST: (obj.bounding_box.right, max(x.bounding_box.right for x in scene.objects)),
            PredicateKind.TOPMOST: (-obj.bounding_box.top, max(-x.bounding_box.top for x in scene.objects)),
            PredicateKind.BOTTOMMOST: (obj.bounding_box.bottom, max(x.bounding_box.bottom for x in scene.objects)),
        }
        return values[self.kind][0] == values[self.kind][1]

@dataclass(frozen=True)
class ObjectSelector:
    kind: SelectorKind
    def select_all(self, scene: "Scene") -> tuple[SceneObject, ...]:
        return tuple(obj for i, obj in enumerate(scene.objects) if ObjectPredicate(PredicateKind(self.kind.value)).matches(scene, i))
    def select(self, scene: "Scene") -> SceneObject | None:
        found = self.select_all(scene)
        return found[0] if len(found) == 1 else None

class RelationKind(str, Enum):
    LEFT_OF="left_of"; RIGHT_OF="right_of"; ABOVE="above"; BELOW="below"; SAME_SHAPE="same_shape"; SAME_SIZE="same_size"; SAME_COLOR="same_color"; ALIGNED_ROW="aligned_row"; ALIGNED_COLUMN="aligned_column"; TOUCHING="touching"; NEAREST="nearest"

@dataclass(frozen=True, order=True)
class ObjectRelation:
    source_index: int; target_index: int; kind: RelationKind

@dataclass(frozen=True)
class Scene:
    grid: Grid; background: Any; objects: tuple[SceneObject, ...]; relations: tuple[ObjectRelation, ...]; connectivity: int = 4
    @classmethod
    def from_grid(cls, grid: Grid, background: Any | None = None, connectivity: int = 4) -> "Scene":
        if connectivity not in (4, 8): raise ValueError("connectivity must be 4 or 8")
        if not grid or not grid[0] or any(len(row) != len(grid[0]) for row in grid): raise ValueError("scene grid must be non-empty and rectangular")
        bg = background if background is not None else min(Counter(v for row in grid for v in row), key=lambda v: (-sum(row.count(v) for row in grid), repr(v)))
        seen: set[tuple[int,int]] = set(); objects=[]; directions=[(-1,0),(1,0),(0,-1),(0,1)]
        if connectivity == 8: directions += [(-1,-1),(-1,1),(1,-1),(1,1)]
        for r,row in enumerate(grid):
            for c,color in enumerate(row):
                if color == bg or (r,c) in seen: continue
                seen.add((r,c)); stack=[(r,c)]; cells=[]
                while stack:
                    x,y=stack.pop(); cells.append((x,y))
                    for dx,dy in directions:
                        nx,ny=x+dx,y+dy
                        if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]) and (nx,ny) not in seen and grid[nx][ny] == color:
                            seen.add((nx,ny)); stack.append((nx,ny))
                cells=sorted(cells); box=BoundingBox(min(x for x,_ in cells),min(y for _,y in cells),max(x for x,_ in cells),max(y for _,y in cells))
                objects.append(SceneObject(color,tuple(cells),box,tuple((x-box.top,y-box.left) for x,y in cells),(len(grid),len(grid[0]))))
        objects.sort(key=lambda o:(o.bounding_box.top,o.bounding_box.left,repr(o.color),o.cells)); rel=[]
        for i,a in enumerate(objects):
            for j,b in enumerate(objects):
                if i == j: continue
                if a.bounding_box.right < b.bounding_box.left: rel.append(ObjectRelation(i,j,RelationKind.LEFT_OF)); rel.append(ObjectRelation(j,i,RelationKind.RIGHT_OF))
                if a.bounding_box.bottom < b.bounding_box.top: rel.append(ObjectRelation(i,j,RelationKind.ABOVE)); rel.append(ObjectRelation(j,i,RelationKind.BELOW))
                if a.mask == b.mask: rel.append(ObjectRelation(i,j,RelationKind.SAME_SHAPE))
                if (a.bounding_box.height,a.bounding_box.width)==(b.bounding_box.height,b.bounding_box.width): rel.append(ObjectRelation(i,j,RelationKind.SAME_SIZE))
                if a.color == b.color: rel.append(ObjectRelation(i,j,RelationKind.SAME_COLOR))
                if not (a.bounding_box.bottom < b.bounding_box.top or b.bounding_box.bottom < a.bounding_box.top): rel.append(ObjectRelation(i,j,RelationKind.ALIGNED_ROW))
                if not (a.bounding_box.right < b.bounding_box.left or b.bounding_box.right < a.bounding_box.left): rel.append(ObjectRelation(i,j,RelationKind.ALIGNED_COLUMN))
                if any(abs(r-x)+abs(c-y)==1 for r,c in a.cells for x,y in b.cells): rel.append(ObjectRelation(i,j,RelationKind.TOUCHING))
        return cls(grid,bg,tuple(objects),tuple(sorted(set(rel))),connectivity)
    def select(self, predicate: ObjectPredicate) -> tuple[SceneObject,...]: return tuple(x for i,x in enumerate(self.objects) if predicate.matches(self,i))
    def related(self, source: SceneObject, kind: RelationKind) -> tuple[SceneObject,...]:
        i=self.objects.index(source); return tuple(self.objects[x.target_index] for x in self.relations if x.source_index==i and x.kind is kind)
    def render(self, objects: tuple[SceneObject,...] | None = None, *, rebase: bool = False, background: Any | None = None) -> Grid:
        objects=self.objects if objects is None else objects; bg=self.background if background is None else background
        if rebase and objects:
            top=min(x.bounding_box.top for x in objects); left=min(x.bounding_box.left for x in objects); bottom=max(x.bounding_box.bottom for x in objects); right=max(x.bounding_box.right for x in objects)
            canvas=[[bg]*(right-left+1) for _ in range(bottom-top+1)]; shift=(-top,-left)
        else: canvas=[[bg for _ in self.grid[0]] for _ in self.grid]; shift=(0,0)
        for obj in objects:
            for r,c in obj.cells: canvas[r+shift[0]][c+shift[1]]=obj.color
        return tuple(tuple(row) for row in canvas)
    def extract(self, selector: ObjectSelector) -> Grid | None:
        obj=selector.select(self)
        return None if obj is None else self.render((obj,),rebase=True)
