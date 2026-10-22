import pygame

from settings import (
    WINDOW_HEIGHT, GRID_X, GRID_Y,
    PANEL_X, PANEL_WIDTH, PANEL_PAD,
    START, GOAL, OPEN, CLOSED, PATH, WEIGHTED,
    LEGEND, COLORS, ALGORITHM_NAMES,
    BG_COLOR, GRID_LINE_COLOR, PANEL_COLOR, TEXT_COLOR, MUTED_COLOR,
    ACCENT_COLOR, CURRENT_COLOR, OK_COLOR, FAIL_COLOR,
    BUTTON_COLOR, BUTTON_BORDER,
)

FONT_NAMES = "arial,helvetica,dejavusans,liberationsans"
OVERLAY_STATES = (OPEN, CLOSED, PATH)    

HINTS = [
    "LMB: wall   |   RMB or E+LMB: erase   |   S+LMB: start   |   G+LMB: goal   |   W+LMB: weighted cell",
    "1 / 2 / 3: BFS / Dijkstra / A*   |   SPACE: start / pause   |   N: one step   |   R: reset search   |   C: clear map",
    "UP / DOWN: speed   |   4-9: test scenarios   |   P: screenshot   |   Esc: quit",
]


class Button:
    def __init__(self, rect, label, action):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.action = action

    def hit(self, pos):
        return self.rect.collidepoint(pos)

    def draw(self, screen, font, active=False, hovered=False):
        if active:
            fill, border, text_color = ACCENT_COLOR, ACCENT_COLOR, (255, 255, 255)
        else:
            fill = (228, 234, 245) if hovered else BUTTON_COLOR
            border, text_color = BUTTON_BORDER, TEXT_COLOR
        pygame.draw.rect(screen, fill, self.rect, border_radius=6)
        pygame.draw.rect(screen, border, self.rect, 1, border_radius=6)
        surf = font.render(self.label, True, text_color)
        screen.blit(surf, surf.get_rect(center=self.rect.center))


class Visualizer:
    def __init__(self):
        pygame.font.init()
        self.font_title = pygame.font.SysFont(FONT_NAMES, 24, bold=True)
        self.font = pygame.font.SysFont(FONT_NAMES, 17)
        self.font_bold = pygame.font.SysFont(FONT_NAMES, 17, bold=True)
        self.font_small = pygame.font.SysFont(FONT_NAMES, 14)
        self.font_cell = pygame.font.SysFont(FONT_NAMES, 15, bold=True)

    def draw(self, screen, app):
        screen.fill(BG_COLOR)
        self._draw_grid(screen, app)
        self._draw_hints(screen, app.grid)
        self._draw_panel(screen, app)


    def _draw_grid(self, screen, app):
        grid = app.grid

        for r in range(grid.rows):
            for c in range(grid.cols):
                node = (r, c)
                rect = grid.rects[r][c]
                state = grid.state_of(node)

                pygame.draw.rect(screen, COLORS[state], rect)

                # Взвешенная клетка под OPEN/CLOSED/PATH остаётся заметной
                if state in OVERLAY_STATES and grid.terrain[r][c] == WEIGHTED:
                    pygame.draw.rect(screen, COLORS[WEIGHTED], rect.inflate(-12, -12))

                pygame.draw.rect(screen, GRID_LINE_COLOR, rect, 1)

                if state in (START, GOAL):
                    letter = "S" if state == START else "G"
                    surf = self.font_cell.render(letter, True, (255, 255, 255))
                    screen.blit(surf, surf.get_rect(center=rect.center))

       
        if app.current is not None:
            pygame.draw.rect(screen, CURRENT_COLOR, grid.cell_rect(app.current), 3)

       
        if app.hover is not None:
            pygame.draw.rect(screen, ACCENT_COLOR, grid.cell_rect(app.hover), 2)

        outer = pygame.Rect(GRID_X, GRID_Y, grid.cols * grid.cell_size, grid.rows * grid.cell_size)
        pygame.draw.rect(screen, TEXT_COLOR, outer, 2)

    def _draw_hints(self, screen, grid):
        y = GRID_Y + grid.rows * grid.cell_size + 12    
        for line in HINTS:
            surf = self.font_small.render(line, True, MUTED_COLOR)
            screen.blit(surf, (GRID_X, y))
            y += 18

    def _text(self, screen, font, string, pos, color=TEXT_COLOR, right=False):
        surf = font.render(string, True, color)
        rect = surf.get_rect()
        if right:
            rect.topright = pos
        else:
            rect.topleft = pos
        screen.blit(surf, rect)

    def _draw_panel(self, screen, app):
        panel = pygame.Rect(PANEL_X, 10, PANEL_WIDTH, WINDOW_HEIGHT - 20)
        pygame.draw.rect(screen, PANEL_COLOR, panel, border_radius=10)
        pygame.draw.rect(screen, BUTTON_BORDER, panel, 1, border_radius=10)

        x0 = PANEL_X + PANEL_PAD
        x1 = PANEL_X + PANEL_WIDTH - PANEL_PAD

       
        self._text(screen, self.font_title, "Pathfinding Visualizer", (x0, 22))
        self._text(screen, self.font_bold, "Selected algorithm:", (x0, 58), MUTED_COLOR)
        self._text(screen, self.font_bold, app.algo_name, (x1, 58), ACCENT_COLOR, right=True)

        
        mouse = pygame.mouse.get_pos()
        for button in app.buttons:
            active = button.action == f"algo:{app.algo_name}"
            button.draw(screen, self.font, active, button.hit(mouse))

      
        self._text(screen, self.font, f"Speed: {app.speed} steps/s   (UP / DOWN)", (x0, 212))

        
        self._text(screen, self.font_bold, "Legend", (x0, 242))
        col_w = (x1 - x0) // 2
        for i, (state, label) in enumerate(LEGEND):
            col, row = divmod(i, 4)
            lx = x0 + col * col_w
            ly = 268 + row * 22
            swatch = pygame.Rect(lx, ly, 16, 16)
            pygame.draw.rect(screen, COLORS[state], swatch)
            pygame.draw.rect(screen, BUTTON_BORDER, swatch, 1)
            self._text(screen, self.font_small, label, (lx + 22, ly + 1))

     
        stats = app.stats
        self._text(screen, self.font_bold, "Statistics (current run)", (x0, 368))

        def val(v, suffix=""):
            return "-" if v is None else f"{v}{suffix}"

        status_color = TEXT_COLOR
        if stats.status == "Path found":
            status_color = OK_COLOR
        elif stats.status == "Path not found":
            status_color = FAIL_COLOR

        rows = [
            ("Algorithm", stats.algorithm, TEXT_COLOR),
            ("Visited nodes", str(stats.visited), TEXT_COLOR),
            ("Path length", val(stats.path_length), TEXT_COLOR),
            ("Path cost", val(stats.path_cost), TEXT_COLOR),
            ("Steps", str(stats.steps), TEXT_COLOR),
            ("Search status", stats.status, status_color),
            ("Frontier size", str(stats.frontier), TEXT_COLOR),
            ("Search time", f"{stats.time_ms:.2f} ms", TEXT_COLOR),
        ]
        y = 392
        for label, value, color in rows:
            self._text(screen, self.font, label, (x0, y), MUTED_COLOR)
            self._text(screen, self.font_bold, value, (x1, y), color, right=True)
            y += 21

      
        self._text(screen, self.font_bold, "Comparison (current map)", (x0, 572))
        cols = [x0, x0 + 98, x0 + 172, x0 + 236, x0 + 296]
        for cx, title in zip(cols, ("Algorithm", "Visited", "Length", "Cost", "Steps")):
            self._text(screen, self.font_small, title, (cx, 596), MUTED_COLOR)
        y = 616
        for name in ALGORITHM_NAMES:
            res = app.results.get(name)
            font = self.font_bold if name == app.algo_name else self.font
            if res is None:
                cells = [name, "-", "-", "-", "-"]
            else:
                cells = [name, str(res["visited"]), val(res["length"]),
                         val(res["cost"]), str(res["steps"])]
            for cx, text in zip(cols, cells):
                self._text(screen, font, text, (cx, y))
            y += 20

        if app.hover is not None:
            r, c = app.hover
            state = app.grid.state_of(app.hover).capitalize()
            info = f"Cell ({r}, {c}): {state}"
            g = app.g_values.get(app.hover)
            if g is not None:
                info += f",  g = {g}"
            self._text(screen, self.font_small, info, (x0, 690), MUTED_COLOR)
        if app.message:
            self._text(screen, self.font_small, app.message, (x0, 712), ACCENT_COLOR)