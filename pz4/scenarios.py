import random

from settings import WALL, WEIGHTED


def _wall(grid, row, col):
    if grid.in_bounds((row, col)):
        grid.terrain[row][col] = WALL


def _weighted(grid, row, col):
    if grid.in_bounds((row, col)):
        grid.terrain[row][col] = WEIGHTED


def _prepare(grid, start, goal):
    grid.clear_map()
    grid.start = start
    grid.goal = goal


def adjacent(grid):
    _prepare(grid, (15, 19), (15, 20))


def empty_map(grid):
    _prepare(grid, (5, 5), (24, 34))


def several_routes(grid):
    for r in range(3, 27):
        if r not in (8, 20):
            _wall(grid, r, 15)
    for r in range(3, 27):
        if r not in (5, 14, 24):
            _wall(grid, r, 27)


def goal_enclosed(grid):
    _prepare(grid, (15, 5), (15, 30))
    for r in range(14, 17):
        for c in range(29, 32):
            if (r, c) != (15, 30):
                _wall(grid, r, c)


def cheap_vs_short(grid):
    _prepare(grid, (14, 5), (14, 34))
    for r in range(6, 23):
        for c in range(15, 25):
            _weighted(grid, r, c)


def far_apart(grid):
    _prepare(grid, (1, 1), (28, 38))
    rng = random.Random(5)                     
    for r in range(grid.rows):
        for c in range(grid.cols):
            if (r, c) in (grid.start, grid.goal):
                continue
            if rng.random() < 0.25:
                _wall(grid, r, c)


SCENARIOS = [
    ("1. Start and Goal are adjacent", adjacent),
    ("2. Empty map", empty_map),
    ("3. Several possible routes", several_routes),
    ("4. Goal surrounded by walls", goal_enclosed),
    ("5. Short expensive vs long cheap", cheap_vs_short),
    ("6. Start and Goal far apart", far_apart),
]


def apply(grid, index):
    name, builder = SCENARIOS[index]
    builder(grid)
    return name