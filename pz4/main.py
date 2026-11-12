import pygame
import sys
from settings import *
from grid import Grid
from algorithms import BFS, Dijkstra, AStar
from visualizer import Visualizer
class App:
    ALGORITHMS = {
        'bfs': BFS,
        'dijkstra': Dijkstra,
        'astar': AStar,
    }
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("пути визуализация")
        self.clock = pygame.time.Clock()
        self.grid = Grid(ROWS, COLS)
        self.grid.set_start(5, 5)
        self.grid.set_goal(20, 35)
        self.algorithm_mode = 'none'
        self.state = 'IDLE'
        self.generator = None
        self.step_timer = 0.0
        self.steps_per_second = STEPS_PER_SECOND
        self.stats = {
            'visited': 0,
            'path_len': 0,
            'path_cost': 0,
            'status': 'Ready'
        }
        self.visualizer = Visualizer(self.screen)
    def reset_search(self):
        self.grid.clear_search()
        self.state = 'IDLE'
        self.generator = None
        self.stats = {'visited': 0, 'path_len': 0, 'path_cost': 0, 'status': 'Ready'}
    def start_algorithm(self, mode):
        self.reset_search()
        self.algorithm_mode = mode
        self.state = 'RUNNING'
        self.step_timer = 0.0
        if not self.grid.start or not self.grid.goal:
            self.stats['status'] = 'Error: No Start/Goal'
            self.state = 'FINISHED'
            return
        algo_class = self.ALGORITHMS.get(mode)
        if algo_class:
            self.generator = algo_class(self.grid).steps()
            self.process_step()
    def process_step(self):
        if not self.generator:
            return
        try:
            step = next(self.generator)
            self.stats['visited'] += 1
            if step['type'] == 'open':
                cell = self.grid.get_cell(step['r'], step['c'])
                if cell and cell.state not in ('START', 'GOAL', 'WEIGHTED'):
                    cell.state = 'OPEN'
            elif step['type'] == 'close':
                cell = self.grid.get_cell(step['r'], step['c'])
                if cell and cell.state not in ('START', 'GOAL', 'WEIGHTED'):
                    cell.state = 'CLOSED'
            elif step['type'] == 'path':
                cell = self.grid.get_cell(step['r'], step['c'])
                if cell:
                    cell.state = 'PATH'
                    self.stats['path_len'] += 1
                    self.stats['path_cost'] += cell.cost
            elif step['type'] == 'not_found':
                self.stats['status'] = 'Path not found'
                self.state = 'FINISHED'
                return
        except StopIteration:
            self.stats['status'] = 'Finished'
            self.state = 'FINISHED'
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.start_algorithm('bfs')
                elif event.key == pygame.K_2:
                    self.start_algorithm('dijkstra')
                elif event.key == pygame.K_3:
                    self.start_algorithm('astar')
                elif event.key == pygame.K_SPACE:
                    if self.state == 'RUNNING':
                        self.state = 'PAUSED'
                    elif self.state in ('PAUSED', 'IDLE'):
                        if self.algorithm_mode != 'none':
                            self.start_algorithm(self.algorithm_mode)
                elif event.key == pygame.K_n:
                    if self.state in ('IDLE', 'FINISHED'):
                        if self.algorithm_mode != 'none':
                            self.start_algorithm(self.algorithm_mode)
                    elif self.state == 'PAUSED':
                        self.process_step()
                elif event.key == pygame.K_r:
                    self.reset_search()
                elif event.key == pygame.K_c:
                    self.grid.clear_all()
                    self.grid.set_start(5, 5)
                    self.grid.set_goal(20, 35)
                    self.reset_search()
                    self.algorithm_mode = 'none'
                elif event.key == pygame.K_UP:
                    self.steps_per_second = min(60, self.steps_per_second + 5)
                elif event.key == pygame.K_DOWN:
                    self.steps_per_second = max(1, self.steps_per_second - 5)
            if event.type == pygame.MOUSEBUTTONDOWN and self.state in ('IDLE', 'FINISHED'):
                mx, my = event.pos
                if (GRID_OFFSET_X <= mx < GRID_OFFSET_X + COLS * CELL_SIZE and
                        GRID_OFFSET_Y <= my < GRID_OFFSET_Y + ROWS * CELL_SIZE):
                    c = (mx - GRID_OFFSET_X) // CELL_SIZE
                    r = (my - GRID_OFFSET_Y) // CELL_SIZE
                    keys = pygame.key.get_pressed()
                    if event.button == 1:
                        if keys[pygame.K_s]:
                            self.grid.set_start(r, c)
                        elif keys[pygame.K_g]:
                            self.grid.set_goal(r, c)
                        elif keys[pygame.K_w]:
                            self.grid.set_weighted(r, c)
                        else:
                            self.grid.set_wall(r, c)
                    elif event.button == 3:
                        self.grid.clear_cell(r, c)
                    self.reset_search()
        return True
    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            if not self.handle_events():
                running = False
                continue
            if self.state == 'RUNNING' and self.generator:
                self.step_timer += dt
                if self.step_timer >= 1.0 / self.steps_per_second:
                    self.step_timer = 0.0
                    self.process_step()
            self.screen.fill((255, 255, 255))
            self.visualizer.draw_grid(self.grid)
            algo_name = "BFS" if self.algorithm_mode == 'bfs' else \
                        "Dijkstra" if self.algorithm_mode == 'dijkstra' else \
                        "A*" if self.algorithm_mode == 'astar' else "выбрать алгоритм 1, 2, 3"
            self.visualizer.draw_ui(self.stats, algo_name)
            self.visualizer.draw_controls()
            pygame.display.flip()
        pygame.quit()
        sys.exit()
if __name__ == "__main__":
    app = App()
    app.run()