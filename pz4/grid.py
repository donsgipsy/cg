import pygame

from settings import (
    ROWS, COLS, CELL_SIZE, GRID_X, GRID_Y,
    DEFAULT_START, DEFAULT_GOAL,
    EMPTY, WALL, START, GOAL, WEIGHTED,
    NORMAL_COST, WEIGHTED_COST,
)


DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


class Grid:
    def __init__(self, rows=ROWS, cols=COLS, cell_size=CELL_SIZE,
                 origin=(GRID_X, GRID_Y)):
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.origin = origin

        ox, oy = origin
        self.rects = [
            [pygame.Rect(ox + c * cell_size, oy + r * cell_size, cell_size, cell_size)
             for c in range(cols)]
            for r in range(rows)
        ]
        self.terrain = [[EMPTY for _ in range(cols)] for _ in range(rows)]
        self.marks = {}                 
        self.start = DEFAULT_START
        self.goal = DEFAULT_GOAL


    def in_bounds(self, node):
        row, col = node
        return 0 <= row < self.rows and 0 <= col < self.cols

    def is_wall(self, node):
        return self.terrain[node[0]][node[1]] == WALL

    def cost(self, node):
        if self.terrain[node[0]][node[1]] == WEIGHTED:
            return WEIGHTED_COST
        return NORMAL_COST

    def state_of(self, node):
        if node == self.start:
            return START
        if node == self.goal:
            return GOAL
        mark = self.marks.get(node)
        if mark is not None:
            return mark
        return self.terrain[node[0]][node[1]]

    def cell_rect(self, node):
        return self.rects[node[0]][node[1]]

    def pixel_to_cell(self, pos):
        col = (pos[0] - self.origin[0]) // self.cell_size
        row = (pos[1] - self.origin[1]) // self.cell_size
        node = (row, col)
        if pos[0] < self.origin[0] or pos[1] < self.origin[1] or not self.in_bounds(node):
            return None
        return node

    def add_wall(self, node):
        if node in (self.start, self.goal) or self.is_wall(node):
            return False
        self.terrain[node[0]][node[1]] = WALL
        return True

    def add_weighted(self, node):
        if node in (self.start, self.goal) or self.terrain[node[0]][node[1]] == WEIGHTED:
            return False
        self.terrain[node[0]][node[1]] = WEIGHTED    
        return True

    def erase(self, node):
        if self.terrain[node[0]][node[1]] == EMPTY:
            return False
        self.terrain[node[0]][node[1]] = EMPTY
        return True

    def set_start(self, node):
        if node in (self.start, self.goal):          
            return False
        self.terrain[node[0]][node[1]] = EMPTY      
        self.start = node
        return True

    def set_goal(self, node):
        if node in (self.start, self.goal):
            return False
        self.terrain[node[0]][node[1]] = EMPTY
        self.goal = node
        return True

    def clear_search(self):
        self.marks.clear()

    def clear_map(self):
        for row in self.terrain:
            for c in range(self.cols):
                row[c] = EMPTY
        self.marks.clear()


def get_neighbors(node, grid):
    row, col = node
    result = []
    for dr, dc in DIRECTIONS:
        next_node = (row + dr, col + dc)
        if grid.in_bounds(next_node) and not grid.is_wall(next_node):
            result.append(next_node)
    return result