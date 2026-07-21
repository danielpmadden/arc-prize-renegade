"""Immutable, deterministic object-centric scene representation.

This layer deliberately models one segmentation policy: four-connected,
same-colour non-background components.  Other policies can be added beside it
without changing object identity, selectors, relations, or rendering.
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
    """A component, represented by absolute cells and a translation-invariant mask."""
    color: Any
    cells: tuple[tuple[int, int], ...]
    bounding_box: BoundingBox
    mask: tuple[tuple[int, int], ...]
    scene_shape: tuple[int, int]

    @property
    def cell_count(self) -> int: return len(self.cells)
    @property
    def touches_border(self) -> bool:
        height, width = self.scene_shape
        return any(r in (0, height - 1) or c in (0, width - 1) for r, c in self.cells)


class SelectorKind(str, Enum):
    LARGEST = "largest"; SMALLEST = "smallest"; LEFTMOST = "leftmost"; RIGHTMOST = "rightmost"; TOPMOST = "topmost"; BOTTOMMOST = "bottommost"


@dataclass(frozen=True)
class ObjectSelector:
    kind: SelectorKind
    def select(self, scene: "Scene") -> SceneObject | None:
        if not scene.objects: return None
        key = {
            SelectorKind.LARGEST: lambda o: o.cell_count,
            SelectorKind.SMALLEST: lambda o: -o.cell_count,
            SelectorKind.LEFTMOST: lambda o: -o.bounding_box.left,
            SelectorKind.RIGHTMOST: lambda o: o.bounding_box.right,
            SelectorKind.TOPMOST: lambda o: -o.bounding_box.top,
            SelectorKind.BOTTOMMOST: lambda o: o.bounding_box.bottom,
        }[self.kind]
        score = max(key(obj) for obj in scene.objects)
        candidates = [obj for obj in scene.objects if key(obj) == score]
        return candidates[0] if len(candidates) == 1 else None


class RelationKind(str, Enum):
    LEFT_OF = "left_of"; ABOVE = "above"; SAME_SHAPE = "same_shape"; SAME_SIZE = "same_size"; SAME_COLOR = "same_color"


@dataclass(frozen=True, order=True)
class ObjectRelation:
    source_index: int; target_index: int; kind: RelationKind


@dataclass(frozen=True)
class Scene:
    grid: Grid
    background: Any
    objects: tuple[SceneObject, ...]
    relations: tuple[ObjectRelation, ...]

    @classmethod
    def from_grid(cls, grid: Grid, background: Any | None = None) -> "Scene":
        if not grid or not grid[0] or any(len(row) != len(grid[0]) for row in grid): raise ValueError("scene grid must be non-empty and rectangular")
        bg = background if background is not None else min(Counter(v for row in grid for v in row), key=lambda v: (-sum(row.count(v) for row in grid), repr(v)))
        seen: set[tuple[int, int]] = set(); objects: list[SceneObject] = []
        for r, row in enumerate(grid):
            for c, color in enumerate(row):
                if color == bg or (r, c) in seen: continue
                seen.add((r, c)); stack = [(r, c)]; cells = []
                while stack:
                    x, y = stack.pop(); cells.append((x, y))
                    for nx, ny in ((x-1,y), (x+1,y), (x,y-1), (x,y+1)):
                        if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]) and (nx, ny) not in seen and grid[nx][ny] == color:
                            seen.add((nx, ny)); stack.append((nx, ny))
                cells = sorted(cells); box = BoundingBox(min(x for x,_ in cells), min(y for _,y in cells), max(x for x,_ in cells), max(y for _,y in cells))
                objects.append(SceneObject(color, tuple(cells), box, tuple((x-box.top, y-box.left) for x,y in cells), (len(grid), len(grid[0]))))
        objects.sort(key=lambda o: (o.bounding_box.top, o.bounding_box.left, repr(o.color), o.cells))
        relations: list[ObjectRelation] = []
        for i, left in enumerate(objects):
            for j, right in enumerate(objects):
                if i == j: continue
                if left.bounding_box.right < right.bounding_box.left: relations.append(ObjectRelation(i, j, RelationKind.LEFT_OF))
                if left.bounding_box.bottom < right.bounding_box.top: relations.append(ObjectRelation(i, j, RelationKind.ABOVE))
                if left.mask == right.mask: relations.append(ObjectRelation(i, j, RelationKind.SAME_SHAPE))
                if left.cell_count == right.cell_count: relations.append(ObjectRelation(i, j, RelationKind.SAME_SIZE))
                if left.color == right.color: relations.append(ObjectRelation(i, j, RelationKind.SAME_COLOR))
        return cls(grid, bg, tuple(objects), tuple(sorted(relations)))

    def render(self) -> Grid:
        canvas = [[self.background for _ in self.grid[0]] for _ in self.grid]
        for obj in self.objects:
            for r, c in obj.cells: canvas[r][c] = obj.color
        return tuple(tuple(row) for row in canvas)

    def extract(self, selector: ObjectSelector) -> Grid | None:
        obj = selector.select(self)
        if obj is None: return None
        box = obj.bounding_box
        canvas = [[self.background] * box.width for _ in range(box.height)]
        for r, c in obj.cells: canvas[r-box.top][c-box.left] = obj.color
        return tuple(tuple(row) for row in canvas)
