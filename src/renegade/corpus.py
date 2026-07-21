"""Reusable, deterministic structural regression grids and expectations.

The corpus is deliberately data-only: it supplies representative inputs without
encoding conclusions that a future semantic layer should reach.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GoldenGrid:
    name: str
    grid: tuple[tuple[int, ...], ...]
    required_archetypes: tuple[str, ...] = ()
    required_relationships: tuple[str, ...] = ()
    minimum_regions: int = 1


GOLDEN_GRIDS = (
    GoldenGrid("empty", ((0, 0, 0), (0, 0, 0), (0, 0, 0))),
    GoldenGrid("single_cell", ((0, 0, 0), (0, 1, 0), (0, 0, 0)), required_relationships=("diagonally_adjacent",), minimum_regions=2),
    GoldenGrid("solid_region", ((2, 2, 2), (2, 2, 2), (2, 2, 2))),
    GoldenGrid("horizontal_line", ((0, 0, 0, 0, 0), (3, 3, 3, 3, 3), (0, 0, 0, 0, 0)), ("translation_array",), ("translated_copy",), 3),
    GoldenGrid("vertical_line", ((0, 4, 0), (0, 4, 0), (0, 4, 0), (0, 4, 0)), ("translation_array",), ("translated_copy",), 3),
    GoldenGrid("filled_rectangle", ((0, 0, 0, 0), (0, 5, 5, 0), (0, 5, 5, 0), (0, 0, 0, 0))),
    GoldenGrid("hollow_rectangle", ((6, 6, 6, 6), (6, 0, 0, 6), (6, 0, 0, 6), (6, 6, 6, 6))),
    GoldenGrid("checkerboard", ((1, 0, 1, 0, 1), (0, 1, 0, 1, 0), (1, 0, 1, 0, 1), (0, 1, 0, 1, 0), (1, 0, 1, 0, 1)), ("translation_array",), ("diagonally_adjacent",), 25),
    GoldenGrid("cross", ((0, 7, 0), (7, 7, 7), (0, 7, 0))),
    GoldenGrid("plus", ((0, 8, 0), (8, 8, 8), (0, 8, 0))),
    GoldenGrid("l_shape", ((9, 0, 0), (9, 0, 0), (9, 9, 9))),
    GoldenGrid("t_shape", ((10, 10, 10), (0, 10, 0), (0, 10, 0))),
    GoldenGrid("u_shape", ((11, 0, 11), (11, 0, 11), (11, 11, 11))),
    GoldenGrid("nested_regions", ((1, 1, 1, 1, 1), (1, 2, 2, 2, 1), (1, 2, 3, 2, 1), (1, 2, 2, 2, 1), (1, 1, 1, 1, 1))),
    GoldenGrid("disconnected_regions", ((1, 0, 2, 0, 1), (0, 0, 0, 0, 0), (3, 0, 4, 0, 3))),
    GoldenGrid("touching_edges", ((1, 1, 0), (2, 2, 0), (0, 0, 0))),
    GoldenGrid("touching_corners", ((1, 0), (0, 2))),
    GoldenGrid("translation_pattern", ((1, 1, 0, 1, 1), (0, 0, 0, 0, 0), (1, 1, 0, 1, 1)), required_relationships=("translated_copy",), minimum_regions=5),
    GoldenGrid("symmetry", ((1, 0, 2, 0, 1), (0, 3, 0, 3, 0), (1, 0, 2, 0, 1))),
)
