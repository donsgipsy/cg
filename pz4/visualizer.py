import pygame
from settings import *
class Visualizer:
    COLOR_MAP = {
        'EMPTY': C_EMPTY,
        'WALL': C_WALL,
        'START': C_START,
        'GOAL': C_GOAL,
        'OPEN': C_OPEN,
        'CLOSED': C_CLOSED,
        'PATH': C_PATH,
        'WEIGHTED': C_WEIGHTED,
    }
    def __init__(self, screen):
        self.screen = screen
    def draw_grid(self, grid):
        for r in range(grid.rows):
            for c in range(grid.cols):
                cell = grid.cells[r][c]
                x = GRID_OFFSET_X + c * CELL_SIZE
                y = GRID_OFFSET_Y + r * CELL_SIZE
                color = self.COLOR_MAP.get(cell.state, C_EMPTY)
                pygame.draw.rect(self.screen, color, (x, y, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(self.screen, (200, 200, 200), (x, y, CELL_SIZE, CELL_SIZE), 1)
    def draw_ui(self, stats, algorithm_name):
        title = FONT_BIG.render(algorithm_name, True, (0, 0, 0))
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 10))
        stats_y = HEIGHT - 120
        pygame.draw.rect(self.screen, (50, 50, 50), (20, stats_y, 350, 100))
        lines = [
            f"алгоритм: {algorithm_name}",
            f"посещено: {stats['visited']}",
            f"длина пути: {stats['path_len']}",
            f"стоимость пути: {stats['path_cost']}",
            f"статус: {stats['status']}"
        ]
        for i, line in enumerate(lines):
            text = FONT_SMALL.render(line, True, (255, 255, 255))
            self.screen.blit(text, (30, stats_y + 10 + i * 18))
        legend_items = [
            ("старт", C_START), ("цель", C_GOAL), ("стена", C_WALL),
            ("дорогая клетка", C_WEIGHTED), ("непосещенные", C_OPEN),
            ("посещенные", C_CLOSED), ("путь", C_PATH)
        ]
        lx, ly = WIDTH - 200, 20
        for i, (name, color) in enumerate(legend_items):
            pygame.draw.rect(self.screen, color, (lx, ly + i * 25, 20, 20))
            text = FONT_SMALL.render(name, True, (0, 0, 0))
            self.screen.blit(text, (lx + 30, ly + i * 25 + 2))
    def draw_controls(self):
        controls = [
            "ЛКМ: стена | S+ЛКМ: старт | G+ЛКМ: цель | W+ЛКМ: дорогая клетка | ПКМ: стереть",
            "1: BFS | 2: Dijkstra | 3: A* | пробел: старт/пауза | N: шаг | R: сбросить | C: очистить карту"
        ]
        for i, text in enumerate(controls):
            surf = FONT_SMALL.render(text, True, (100, 100, 100))
            self.screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, HEIGHT - 30 + i * 20))