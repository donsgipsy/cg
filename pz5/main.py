import pygame
import sys
import numpy as np
from settings import *
from objects import Shape, create_house
from transformations import get_inverse
from renderer import Renderer
class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Affine Transform Studio")
        self.clock = pygame.time.Clock()
        self.view_offset = (400, 400)
        self.shape = create_house()
        self.renderer = Renderer(self.screen, self.view_offset)
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_r:
                    self.shape.reset()
                elif event.key == pygame.K_m:
                    self.shape.composition_mode = (
                        'RT' if self.shape.composition_mode == 'TR' else 'TR'
                    )
                elif event.key == pygame.K_h:
                    self.shape.toggle_reflect_x()
                elif event.key == pygame.K_v:
                    self.shape.toggle_reflect_y()
                elif event.key == pygame.K_z:
                    self.shape.scale_x(-0.1)
                elif event.key == pygame.K_x:
                    self.shape.scale_x(0.1)
                elif event.key == pygame.K_a:
                    self.shape.scale_y(-0.1)
                elif event.key == pygame.K_d:
                    self.shape.scale_y(0.1)
                elif event.key == pygame.K_j:
                    self.shape.shear_x(-0.1)
                elif event.key == pygame.K_l:
                    self.shape.shear_x(0.1)
                elif event.key == pygame.K_u:
                    self.shape.shear_y(-0.1)
                elif event.key == pygame.K_o:
                    self.shape.shear_y(0.1)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_p]:
                        self.set_pivot_from_mouse(event.pos)
                    else:
                        self.select_shape_from_mouse(event.pos)
        return True
    def set_pivot_from_mouse(self, screen_pos):
        matrix = self.shape.compute_matrix()
        V = np.array([
            [1.0, 0.0, self.view_offset[0]],
            [0.0, 1.0, self.view_offset[1]],
            [0.0, 0.0, 1.0]
        ])
        full_matrix = V @ matrix
        inverse = get_inverse(full_matrix)
        if inverse is not None:
            sx, sy = screen_pos
            local = inverse @ np.array([sx, sy, 1.0])
            self.shape.set_pivot((local[0], local[1]))
    def select_shape_from_mouse(self, screen_pos):
        matrix = self.shape.compute_matrix()
        V = np.array([
            [1.0, 0.0, self.view_offset[0]],
            [0.0, 1.0, self.view_offset[1]],
            [0.0, 0.0, 1.0]
        ])
        full_matrix = V @ matrix
        inverse = get_inverse(full_matrix)
        if self.shape.hit_test(screen_pos, self.view_offset, inverse):
            self.shape.toggle_selection()
    def update(self, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.shape.move(-MOVE_SPEED * dt, 0)
        if keys[pygame.K_RIGHT]:
            self.shape.move(MOVE_SPEED * dt, 0)
        if keys[pygame.K_UP]:
            self.shape.move(0, -MOVE_SPEED * dt)
        if keys[pygame.K_DOWN]:
            self.shape.move(0, MOVE_SPEED * dt)
        if keys[pygame.K_q]:
            self.shape.rotate(-ROTATE_SPEED * dt)
        if keys[pygame.K_e]:
            self.shape.rotate(ROTATE_SPEED * dt)
    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            if not self.handle_events():
                running = False
                continue
            self.update(dt)
            matrix = self.shape.compute_matrix()
            self.screen.fill((255, 255, 255))
            self.renderer.draw_grid()
            self.renderer.draw_shape(self.shape)
            self.renderer.draw_ui(self.shape, matrix)
            self.renderer.draw_controls()
            pygame.display.flip()
        pygame.quit()
        sys.exit()
if __name__ == "__main__":
    app = App()
    app.run()