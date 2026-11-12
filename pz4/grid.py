class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.state = 'EMPTY'
        self.cost = 1
    def reset_search_state(self):
        if self.state in ('OPEN', 'CLOSED', 'PATH'):
            self.state = 'EMPTY'
    def is_walkable(self):
        return self.state != 'WALL'
class Grid:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.cells = [[Cell(r, c) for c in range(cols)] for r in range(rows)]
        self.start = None
        self.goal = None
    def get_cell(self, row, col):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.cells[row][col]
        return None
    def get_neighbors(self, cell):
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            neighbor = self.get_cell(cell.row + dr, cell.col + dc)
            if neighbor and neighbor.is_walkable():
                neighbors.append(neighbor)
        return neighbors
    def set_start(self, row, col):
        if self.start:
            self.start.state = 'EMPTY'
        cell = self.get_cell(row, col)
        if cell and cell.state != 'GOAL':
            cell.state = 'START'
            self.start = cell
    def set_goal(self, row, col):
        if self.goal:
            self.goal.state = 'EMPTY'
        cell = self.get_cell(row, col)
        if cell and cell.state != 'START':
            cell.state = 'GOAL'
            self.goal = cell
    def set_wall(self, row, col):
        cell = self.get_cell(row, col)
        if cell and cell.state not in ('START', 'GOAL'):
            cell.state = 'WALL'
    def set_weighted(self, row, col):
        cell = self.get_cell(row, col)
        if cell and cell.state not in ('START', 'GOAL'):
            cell.state = 'WEIGHTED'
            cell.cost = 4
    def clear_cell(self, row, col):
        cell = self.get_cell(row, col)
        if cell and cell.state not in ('START', 'GOAL'):
            cell.state = 'EMPTY'
            cell.cost = 1
    def clear_search(self):
        for row in self.cells:
            for cell in row:
                cell.reset_search_state()
    def clear_all(self):
        self.cells = [[Cell(r, c) for c in range(self.cols)] for r in range(self.rows)]
        self.start = None
        self.goal = None