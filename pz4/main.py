import os
import sys
import time

import pygame

import scenarios
from algorithms import ALGORITHMS
from grid import Grid, get_neighbors
from settings import (
    WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, FPS,
    PANEL_X, PANEL_WIDTH, PANEL_PAD,
    CLOSED, OPEN, PATH,
    ALGORITHM_NAMES, SPEEDS, DEFAULT_SPEED_INDEX, MAX_STEPS_PER_FRAME,
)
from visualizer import Visualizer, Button

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


IDLE, RUNNING, PAUSED, FINISHED = "IDLE", "RUNNING", "PAUSED", "FINISHED"


class Stats:

    def __init__(self, algorithm):
        self.algorithm = algorithm
        self.visited = 0           
        self.path_length = None    
        self.path_cost = None       
        self.steps = 0            
        self.status = "Ready"
        self.frontier = 0           
        self.time_ms = 0.0         


class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()

        self.grid = Grid()
        self.viz = Visualizer()

        self.algo_name = "BFS"
        self.speed_index = DEFAULT_SPEED_INDEX
        self.results = {}           
        self.hover = None
        self.painting = None        
        self.message = ""
        self.message_time = 0.0
        self.running = True

        self.buttons = self._create_buttons()
        self.reset_search()

    @property
    def speed(self):
        return SPEEDS[self.speed_index]

    def _create_buttons(self):
        x0 = PANEL_X + PANEL_PAD
        width = PANEL_WIDTH - 2 * PANEL_PAD
        gap = 8
        buttons = []

        w3 = (width - 2 * gap) // 3
        for i, name in enumerate(ALGORITHM_NAMES):
            label = f"{i + 1}  {name}"
            buttons.append(Button((x0 + i * (w3 + gap), 88, w3, 34), label, f"algo:{name}"))

        w2 = (width - gap) // 2
        buttons.append(Button((x0, 128, w2, 34), "Start", "toggle"))
        buttons.append(Button((x0 + w2 + gap, 128, w2, 34), "Step (N)", "step"))
        buttons.append(Button((x0, 168, w2, 34), "Reset search (R)", "reset"))
        buttons.append(Button((x0 + w2 + gap, 168, w2, 34), "Clear map (C)", "clear"))
        return buttons

    def _update_toggle_label(self):
        label = {IDLE: "Start (SPACE)", RUNNING: "Pause (SPACE)",
                 PAUSED: "Resume (SPACE)", FINISHED: "Run again (SPACE)"}[self.mode]
        for button in self.buttons:
            if button.action == "toggle":
                button.label = label

    def show_message(self, text):
        self.message = text
        self.message_time = time.time()


    def reset_search(self):
        self.grid.clear_search()
        self.generator = None
        self.mode = IDLE
        self.step_timer = 0.0
        self.stats = Stats(self.algo_name)
        self.g_values = {}
        self.current = None

    def invalidate(self):
        self.results.clear()

    def select_algorithm(self, name):
        if name == self.algo_name and self.mode == IDLE:
            return
        self.algo_name = name
        self.reset_search()         

    def _make_generator(self):
        grid = self.grid
        algorithm = ALGORITHMS[self.algo_name]
        return algorithm(
            grid.start, grid.goal,
            lambda node: get_neighbors(node, grid),
            grid.cost,
        )

    def toggle_run(self):
        if self.mode == FINISHED:
            self.reset_search()
        if self.mode == IDLE:
            self.generator = self._make_generator()
            self.g_values = {self.grid.start: 0}
            self.stats.status = "Searching..."
            self.mode = RUNNING
        elif self.mode == RUNNING:
            self.mode = PAUSED
            self.stats.status = "Paused"
        elif self.mode == PAUSED:
            self.mode = RUNNING
            self.stats.status = "Searching..."

    def single_step(self):
        if self.mode == FINISHED:
            return
        if self.mode == IDLE:
            self.generator = self._make_generator()
            self.g_values = {self.grid.start: 0}
        self.mode = PAUSED
        self.stats.status = "Paused"
        self.do_step()

    def do_step(self):
        started = time.perf_counter()
        try:
            event = next(self.generator)
        except StopIteration:
            self.mode = FINISHED
            return
        self.stats.time_ms += (time.perf_counter() - started) * 1000.0
        self.stats.steps += 1
        self.apply_event(event)

    def apply_event(self, event):
        grid = self.grid
        stats = self.stats

        if event["type"] == "visit":
            node = event["node"]
            stats.visited += 1
            stats.frontier = event["frontier_size"]
            self.current = node
            if node not in (grid.start, grid.goal):
                grid.marks[node] = CLOSED
            for found_node, g in event["opened"] + event["updated"]:
                self.g_values[found_node] = g
                if found_node not in (grid.start, grid.goal):
                    grid.marks[found_node] = OPEN

        elif event["type"] == "found":
            for node in event["path"]:
                if node not in (grid.start, grid.goal):
                    grid.marks[node] = PATH
            stats.path_length = len(event["path"]) - 1
            stats.path_cost = event["cost"]
            stats.status = "Path found"
            self._finish()

        elif event["type"] == "not_found":
            stats.status = "Path not found"
            self._finish()

    def _finish(self):
        self.mode = FINISHED
        self.current = None
        self.results[self.algo_name] = {
            "visited": self.stats.visited,
            "length": self.stats.path_length,
            "cost": self.stats.path_cost,
            "steps": self.stats.steps,
        }

    def paint(self, pos):
        node = self.grid.pixel_to_cell(pos)
        if node is None:
            return
        keys = pygame.key.get_pressed()
        grid = self.grid

        if self.painting == 3 or keys[pygame.K_e]:
            changed = grid.erase(node)
        elif keys[pygame.K_s]:
            changed = grid.set_start(node)
        elif keys[pygame.K_g]:
            changed = grid.set_goal(node)
        elif keys[pygame.K_w]:
            changed = grid.add_weighted(node)
        else:
            changed = grid.add_wall(node)

        if changed:
            self.invalidate()       

    def run_button(self, action):
        if action.startswith("algo:"):
            self.select_algorithm(action.split(":", 1)[1])
        elif action == "toggle":
            self.toggle_run()
        elif action == "step":
            self.single_step()
        elif action == "reset":
            self.reset_search()
        elif action == "clear":
            self.grid.clear_map()
            self.invalidate()

    def save_screenshot(self):
        folder = os.path.join(BASE_DIR, "screenshots")
        os.makedirs(folder, exist_ok=True)
        name = self.algo_name.replace("*", "Star")
        path = os.path.join(folder, f"{name}_{time.strftime('%Y%m%d_%H%M%S')}.png")
        pygame.image.save(self.screen, path)
        self.show_message(f"Screenshot saved: screenshots/{os.path.basename(path)}")

    def handle_key(self, key):
        if key == pygame.K_ESCAPE:
            self.running = False
        elif key == pygame.K_SPACE:
            self.toggle_run()
        elif key == pygame.K_n:
            self.single_step()
        elif key == pygame.K_r:
            self.reset_search()
        elif key == pygame.K_c:
            self.grid.clear_map()
            self.invalidate()
        elif key == pygame.K_UP:
            self.speed_index = min(self.speed_index + 1, len(SPEEDS) - 1)
        elif key == pygame.K_DOWN:
            self.speed_index = max(self.speed_index - 1, 0)
        elif key in (pygame.K_1, pygame.K_2, pygame.K_3):
            index = key - pygame.K_1
            self.select_algorithm(ALGORITHM_NAMES[index])
        elif pygame.K_4 <= key <= pygame.K_9:
            index = key - pygame.K_4
            title = scenarios.apply(self.grid, index)
            self.invalidate()
            self.show_message(f"Scenario loaded: {title}")
        elif key == pygame.K_p:
            self.save_screenshot()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                self.handle_key(event.key)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button in (1, 3):
                handled = False
                if event.button == 1:
                    for button in self.buttons:
                        if button.hit(event.pos):
                            self.run_button(button.action)
                            handled = True
                            break
                if not handled and self.grid.pixel_to_cell(event.pos) is not None:
                    self.painting = event.button
                    self.paint(event.pos)

            elif event.type == pygame.MOUSEBUTTONUP and event.button in (1, 3):
                self.painting = None

            elif event.type == pygame.MOUSEMOTION:
                self.hover = self.grid.pixel_to_cell(event.pos)
                if self.painting is not None:
                    self.paint(event.pos)


    def update(self, dt):

        if self.mode == RUNNING:
            self.step_timer += dt
            interval = 1.0 / self.speed
            done = 0
            while (self.step_timer >= interval and self.mode == RUNNING
                   and done < MAX_STEPS_PER_FRAME):
                self.step_timer -= interval
                self.do_step()
                done += 1
            if done == MAX_STEPS_PER_FRAME:
                self.step_timer = 0.0

        if self.message and time.time() - self.message_time > 4:
            self.message = ""

        self._update_toggle_label()

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.viz.draw(self.screen, self)
            pygame.display.flip()
        pygame.quit()


if __name__ == "__main__":
    App().run()
    sys.exit()