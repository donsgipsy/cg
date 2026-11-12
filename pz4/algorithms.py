import heapq
from collections import deque
class BaseSearch:
    def __init__(self, grid):
        self.grid = grid
        self.start = grid.start
        self.goal = grid.goal

    def reconstruct_path(self, came_from):
        path = []
        curr = (self.goal.row, self.goal.col)
        start_pos = (self.start.row, self.start.col)
        while curr != start_pos:
            path.append(curr)
            curr = came_from.get(curr)
            if curr is None:
                yield {"type": "not_found"}
                return
        path.append(start_pos)
        path.reverse()
        for r, c in path:
            cell = self.grid.get_cell(r, c)
            if cell and cell.state not in ('START', 'GOAL'):
                yield {"type": "path", "r": r, "c": c}
class BFS(BaseSearch):
    def steps(self):
        queue = deque([self.start])
        visited = {(self.start.row, self.start.col)}
        came_from = {}
        while queue:
            current = queue.popleft()
            yield {"type": "close", "r": current.row, "c": current.col}
            if current.state == 'GOAL':
                break
            for neighbor in self.grid.get_neighbors(current):
                n_pos = (neighbor.row, neighbor.col)
                if n_pos not in visited:
                    visited.add(n_pos)
                    came_from[n_pos] = (current.row, current.col)
                    yield {"type": "open", "r": neighbor.row, "c": neighbor.col}
                    queue.append(neighbor)
        yield from self.reconstruct_path(came_from)
class Dijkstra(BaseSearch):
    def steps(self):
        frontier = [(0, self.start.row, self.start.col)]
        cost_so_far = {(self.start.row, self.start.col): 0}
        came_from = {}
        while frontier:
            current_cost, r, c = heapq.heappop(frontier)
            if current_cost > cost_so_far.get((r, c), float('inf')):
                continue
            yield {"type": "close", "r": r, "c": c}
            if self.grid.get_cell(r, c).state == 'GOAL':
                break
            for neighbor in self.grid.get_neighbors(self.grid.get_cell(r, c)):
                new_cost = current_cost + neighbor.cost
                n_pos = (neighbor.row, neighbor.col)
                if n_pos not in cost_so_far or new_cost < cost_so_far[n_pos]:
                    cost_so_far[n_pos] = new_cost
                    came_from[n_pos] = (r, c)
                    yield {"type": "open", "r": neighbor.row, "c": neighbor.col}
                    heapq.heappush(frontier, (new_cost, neighbor.row, neighbor.col))
        yield from self.reconstruct_path(came_from)
class AStar(BaseSearch):
    @staticmethod
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    def steps(self):
        start_pos = (self.start.row, self.start.col)
        goal_pos = (self.goal.row, self.goal.col)
        h0 = self.heuristic(start_pos, goal_pos)
        frontier = [(h0, 0, self.start.row, self.start.col)]
        cost_so_far = {start_pos: 0}
        came_from = {}
        while frontier:
            f_score, g_score, r, c = heapq.heappop(frontier)
            if g_score > cost_so_far.get((r, c), float('inf')):
                continue
            yield {"type": "close", "r": r, "c": c}
            if self.grid.get_cell(r, c).state == 'GOAL':
                break
            for neighbor in self.grid.get_neighbors(self.grid.get_cell(r, c)):
                new_g = g_score + neighbor.cost
                n_pos = (neighbor.row, neighbor.col)
                if n_pos not in cost_so_far or new_g < cost_so_far[n_pos]:
                    cost_so_far[n_pos] = new_g
                    came_from[n_pos] = (r, c)
                    h = self.heuristic(n_pos, goal_pos)
                    yield {"type": "open", "r": neighbor.row, "c": neighbor.col}
                    heapq.heappush(frontier, (new_g + h, new_g, neighbor.row, neighbor.col))
        yield from self.reconstruct_path(came_from)