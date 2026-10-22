import heapq
import itertools
from collections import deque
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def reconstruct_path(came_from, start, goal):
    current = goal
    path = []
    while current != start:
        path.append(current)
        current = came_from[current]
    path.append(start)
    path.reverse()
    return path


def path_cost(path, cost):
    return sum(cost(node) for node in path[1:])


def _found(came_from, start, goal, cost):
    path = reconstruct_path(came_from, start, goal)
    return {"type": "found", "path": path, "cost": path_cost(path, cost)}

def bfs_steps(start, goal, neighbors, cost):
    queue = deque([start])
    visited = {start}
    came_from = {}
    g = {start: 0}

    while queue:
        current = queue.popleft()
        opened = []

        if current != goal:
            for next_node in neighbors(current):
                if next_node in visited:
                    continue
                visited.add(next_node)
                came_from[next_node] = current
                g[next_node] = g[current] + cost(next_node)
                queue.append(next_node)
                opened.append((next_node, g[next_node]))

        yield {
            "type": "visit",
            "node": current,
            "opened": opened,
            "updated": [],
            "frontier_size": len(queue),
        }

        if current == goal:
            yield _found(came_from, start, goal, cost)
            return

    yield {"type": "not_found"}
def dijkstra_steps(start, goal, neighbors, cost):
    counter = itertools.count()                
    frontier = [(0, next(counter), start)]
    cost_so_far = {start: 0}
    came_from = {}
    open_nodes = {start}                      
    closed = set()

    while frontier:
        current_cost, _, current = heapq.heappop(frontier)

        if current in closed or current_cost > cost_so_far[current]:
            continue

        open_nodes.discard(current)
        closed.add(current)
        opened = []
        updated = []

        if current != goal:
            for next_node in neighbors(current):
                if next_node in closed:
                    continue

                new_cost = cost_so_far[current] + cost(next_node)

                if next_node not in cost_so_far:
                    opened.append((next_node, new_cost))
                elif new_cost < cost_so_far[next_node]:
                    updated.append((next_node, new_cost))
                else:
                    continue

                cost_so_far[next_node] = new_cost
                came_from[next_node] = current
                open_nodes.add(next_node)
                heapq.heappush(frontier, (new_cost, next(counter), next_node))

        yield {
            "type": "visit",
            "node": current,
            "opened": opened,
            "updated": updated,
            "frontier_size": len(open_nodes),
        }

        if current == goal:
            yield _found(came_from, start, goal, cost)
            return

    yield {"type": "not_found"}


def astar_steps(start, goal, neighbors, cost):
    counter = itertools.count()
    frontier = [(heuristic(start, goal), 0, next(counter), start)]   # (f, h, №, node)
    cost_so_far = {start: 0}
    came_from = {}
    open_nodes = {start}
    closed = set()

    while frontier:
        _, _, _, current = heapq.heappop(frontier)

        if current in closed:                  
            continue

        open_nodes.discard(current)
        closed.add(current)
        opened = []
        updated = []

        if current != goal:
            for next_node in neighbors(current):
                if next_node in closed:
                    continue

                new_cost = cost_so_far[current] + cost(next_node)

                if next_node not in cost_so_far:
                    opened.append((next_node, new_cost))
                elif new_cost < cost_so_far[next_node]:
                    updated.append((next_node, new_cost))
                else:
                    continue

                cost_so_far[next_node] = new_cost
                came_from[next_node] = current
                open_nodes.add(next_node)

                h = heuristic(next_node, goal)
                heapq.heappush(frontier, (new_cost + h, h, next(counter), next_node))

        yield {
            "type": "visit",
            "node": current,
            "opened": opened,
            "updated": updated,
            "frontier_size": len(open_nodes),
        }

        if current == goal:
            yield _found(came_from, start, goal, cost)
            return

    yield {"type": "not_found"}

ALGORITHMS = {
    "BFS": bfs_steps,
    "Dijkstra": dijkstra_steps,
    "A*": astar_steps,
}