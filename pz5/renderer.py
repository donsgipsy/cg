import pygame
from settings import *
import numpy as np
class Renderer:
    def __init__(self, screen, view_offset):
        self.screen = screen
        self.view_offset = view_offset  
    def draw_grid(self):
        w, h = self.screen.get_size()
        ox, oy = self.view_offset
        for x in range(0, w, GRID_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (x, 0), (x, h))
        for y in range(0, h, GRID_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (w, y))
        pygame.draw.line(self.screen, AXIS_COLOR, (0, oy), (w, oy), 2)
        pygame.draw.line(self.screen, AXIS_COLOR, (ox, 0), (ox, h), 2)
        pygame.draw.circle(self.screen, ORIGIN_COLOR, (ox, oy), 5)
    def draw_shape(self, shape):
        matrix = shape.compute_matrix()
        for polygon in shape.polygons:
            pts = polygon.get_screen_vertices(np.eye(3), self.view_offset)
            if len(pts) >= 3:
                pygame.draw.polygon(self.screen, ORIGINAL_COLOR, pts, 2)
        color = SELECTED_COLOR if shape.selected else TRANSFORMED_COLOR
        for polygon in shape.polygons:
            pts = polygon.get_screen_vertices(matrix, self.view_offset)
            if len(pts) >= 3:
                pygame.draw.polygon(self.screen, color, pts)
                pygame.draw.polygon(self.screen, (0, 0, 0), pts, 1)
        pivot_screen = (
            int(self.view_offset[0] + shape.pivot[0]),
            int(self.view_offset[1] + shape.pivot[1])
        )
        pygame.draw.circle(self.screen, PIVOT_COLOR, pivot_screen, 6)
    def draw_ui(self, shape, matrix):
        panel_x = 850
        panel_y = 20
        panel_w = 330
        panel_h = 500
        pygame.draw.rect(self.screen, (240, 240, 240), (panel_x, panel_y, panel_w, panel_h))
        pygame.draw.rect(self.screen, (100, 100, 100), (panel_x, panel_y, panel_w, panel_h), 2)
        title = FONT_BIG.render("Affine Studio", True, (0, 0, 0))
        self.screen.blit(title, (panel_x + 10, panel_y + 10))
        y = panel_y + 60
        lines = [
            f"Position: ({shape.tx:.1f}, {shape.ty:.1f})",
            f"Rotation: {shape.angle:.1f}°",
            f"Scale: ({shape.sx:.2f}, {shape.sy:.2f})",
            f"Shear: ({shape.kx:.2f}, {shape.ky:.2f})",
            f"Reflect X: {'ON' if shape.reflect_x else 'OFF'}",
            f"Reflect Y: {'ON' if shape.reflect_y else 'OFF'}",
            f"Pivot: ({shape.pivot[0]:.1f}, {shape.pivot[1]:.1f})",
            f"Mode: {shape.composition_mode}",
            f"Selected: {'YES' if shape.selected else 'NO'}",
        ]
        for line in lines:
            text = FONT_SMALL.render(line, True, (0, 0, 0))
            self.screen.blit(text, (panel_x + 10, y))
            y += 22
        y += 10
        matrix_title = FONT_MEDIUM.render("Matrix 3x3:", True, (0, 0, 0))
        self.screen.blit(matrix_title, (panel_x + 10, y))
        y += 25
        for row in range(3):
            row_str = "  ".join(f"{matrix[row, col]:7.3f}" for col in range(3))
            text = FONT_SMALL.render(f"[ {row_str} ]", True, (0, 0, 128))
            self.screen.blit(text, (panel_x + 10, y))
            y += 20
    def draw_controls(self):
        controls = [
            "Arrows: Move | Q/E: Rotate | Z/X: Scale X | A/D: Scale Y",
            "J/L: Shear X | U/O: Shear Y | H: Reflect X | V: Reflect Y",
            "P+LMB: Set Pivot | LMB: Select | M: Mode | R: Reset | Esc: Exit"
        ]
        y = HEIGHT - 50
        for i, text in enumerate(controls):
            surf = FONT_SMALL.render(text, True, (80, 80, 80))
            self.screen.blit(surf, (20, y + i * 20))