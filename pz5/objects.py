import numpy as np 
from transformations import (
    translation, scale, rotation, reflection, shear, around_pivot, transform_points
)
from settings import (
    ORIGINAL_COLOR, TRANSFORMED_COLOR, SELECTED_COLOR,
    MIN_SCALE, MAX_SCALE, MIN_SHEAR, MAX_SHEAR
)
class Polygon: 
    def __init__(self,vertices, color): 
        self.local_vertices = np.array(vertices, dtype = float)
        self.color = color 
    def get_screen_vertices(self, matrix, view_offset): 
        world = transform_points(self.local_vertices, matrix)
        screen = world + np.array(view_offset)
        return [(int(round(x)), int(round(y))) for x, y in screen]
class Shape: 
    def __init__(self, polygons, position=(0,0)):
        self.polygons=polygons
        self.tx, self.ty = position
        self.angle = 0.0
        self.sx, self.sy = 1.0, 1.0
        self.kx, self.ky = 0.0, 0.0
        self.reflect_x = False 
        self.reflect_y = False 
        self.pivot=(0.0,0.0)
        self.composition_mode = 'TR'
        self.selected = False 
    def compute_matrix(self): 
        M = np.eye(3, dtype = float)
        if self.reflect_x:
            M = reflection('x') @ M 
        if self.reflect_y: 
            M = reflection('y') @ M 
        if self.kx !=0 or self.ky !=0: 
            M = shear(self.kx, self.ky) @ M 
        if self.sx != 1.0 or self.sy != 1.0: 
            M = scale(self.sx, self.sy ) @ M 
        if self.angle !=0 : 
            M = rotation(self.angle) @ M 
        if self.pivot != (0.0, 0.0): 
            M = around_pivot(M, self.pivot)
        T_obj = translation(self.tx, self.ty)
        if self.composition_mode == 'TR': 
            return T_obj @ M 
        else: 
            return M @ T_obj 
    def move(self, dx, dy): 
        self.tx += dx 
        self.ty += dy 
    def rotate(self, delta_angle): 
        self.angle = (self.angle + delta_angle)%360
    def scale_x(self, delta): 
        self.sx = max(MIN_SCALE, min(MAX_SCALE, self.sx+ delta))
    def scale_y(self, delta): 
        self.sy = max(MIN_SCALE, min(MAX_SCALE, self.sy +delta))
    def shear_x(self,delta): 
        self.kx = max(MIN_SHEAR, min(MAX_SHEAR, self.kx + delta))
    def shear_y(self, delta): 
        self.ky=max(MIN_SHEAR, min(MAX_SHEAR, self.ky +delta ))
    def toggle_reflect_x(self): 
        self.reflect_x = not self.reflect_x
    def toggle_reflect_y(self): 
        self.reflect_y= not self.reflect_y
    def set_pivot(self, pivot): 
        self.pivot = pivot
    def reset(self): 
        self.tx, self.ty = 0,0 
        self.angle = 0.0 
        self.sx, self.sy = 1.0, 1.0
        self.kx, self.ky = 0.0, 0.0
        self.reflect_x = False 
        self.reflect_y= False 
        self.pivot = (0.0,0.0)
    def toggle_selection(self): 
        self.selected = not self.selected
    def hit_test(self, screen_pos, view_offset, inverse_matrix): 
        if inverse_matrix is None: 
            return False 
        sx,sy = screen_pos 
        wx, wy = sx - view_offset[0], sy-view_offset[1]
        local = inverse_matrix @ np.array([wx, wy, 1.0])
        lx, ly = local[0], local[1]
        for polygon in self.polygons:
            if self._point_in_polygon(lx, ly, polygon.local_vertices):
                return True
        return False 
    @staticmethod 
    def _point_in_polygon(x,y,vertices): 
        n=len(vertices)
        inside = False 
        j = n-1 
        for i in range(n):
            xi,yi = vertices[i]
            xj,yj = vertices[j]
            if ((yi > y) != (yj > y)) and \
               (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
                inside = not inside
            j = i 
        return inside 
def create_house(): 
    body = [
        [-50.0, -25.0], 
        [50.0, -25.0],
        [50.0, 45.0], 
        [-50.0, 45.0]
    ]
    roof = [
        [-60.0, -25.0],
        [0.0, -70.0], 
        [60.0, -25.0]
    ]
    door = [
        [-15.0, 10.0],
        [15.0, 10.0],
        [15.0, 45.0],
        [-15.0, 45.0]
    ]
    window = [
        [20.0, -10.0],
        [40.0, -10.0],
        [40.0, 10.0],
        [20.0, 10.0]
    ]
    polygons = [
        Polygon(body, (139,90,43)), 
        Polygon(roof, (178,34,34)), 
        Polygon(door, (101,67,33)),
        Polygon(window, (135,206,235)),
    ]
    return Shape(polygons, position = (0,0))