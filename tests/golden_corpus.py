"""Reusable, deterministic structural regression grids.

The corpus is deliberately data-only: it supplies representative inputs without
encoding conclusions that a future semantic layer should reach.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GoldenGrid:
    name: str
    grid: tuple[tuple[int, ...], ...]


GOLDEN_GRIDS = (
    GoldenGrid("empty", ((0, 0, 0), (0, 0, 0), (0, 0, 0))),
    GoldenGrid("single_cell", ((0, 0, 0), (0, 1, 0), (0, 0, 0))),
    GoldenGrid("solid_region", ((2, 2, 2), (2, 2, 2), (2, 2, 2))),
    GoldenGrid("horizontal_line", ((0, 0, 0, 0, 0), (3, 3, 3, 3, 3), (0, 0, 0, 0, 0))),
    GoldenGrid("vertical_line", ((0, 4, 0), (0, 4, 0), (0, 4, 0), (0, 4, 0))),
    GoldenGrid("filled_rectangle", ((0, 0, 0, 0), (0, 5, 5, 0), (0, 5, 5, 0), (0, 0, 0, 0))),
    GoldenGrid("hollow_rectangle", ((6, 6, 6, 6), (6, 0, 0, 6), (6, 0, 0, 6), (6, 6, 6, 6))),
    GoldenGrid("checkerboard", ((1, 0, 1, 0, 1), (0, 1, 0, 1, 0), (1, 0, 1, 0, 1), (0, 1, 0, 1, 0), (1, 0, 1, 0, 1))),
    GoldenGrid("cross", ((0, 7, 0), (7, 7, 7), (0, 7, 0))),
    GoldenGrid("plus", ((0, 8, 0), (8, 8, 8), (0, 8, 0))),
    GoldenGrid("l_shape", ((9, 0, 0), (9, 0, 0), (9, 9, 9))),
    GoldenGrid("t_shape", ((10, 10, 10), (0, 10, 0), (0, 10, 0))),
    GoldenGrid("u_shape", ((11, 0, 11), (11, 0, 11), (11, 11, 11))),
    GoldenGrid("nested_regions", ((1, 1, 1, 1, 1), (1, 2, 2, 2, 1), (1, 2, 3, 2, 1), (1, 2, 2, 2, 1), (1, 1, 1, 1, 1))),
    GoldenGrid("disconnected_regions", ((1, 0, 2, 0, 1), (0, 0, 0, 0, 0), (3, 0, 4, 0, 3))),
    GoldenGrid("touching_edges", ((1, 1, 0), (2, 2, 0), (0, 0, 0))),
    GoldenGrid("touching_corners", ((1, 0), (0, 2))),
    GoldenGrid("translation_pattern", ((1, 1, 0, 1, 1), (0, 0, 0, 0, 0), (1, 1, 0, 1, 1))),
    GoldenGrid("symmetry", ((1, 0, 2, 0, 1), (0, 3, 0, 3, 0), (1, 0, 2, 0, 1))),
)
