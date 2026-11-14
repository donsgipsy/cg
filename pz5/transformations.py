import numpy as np 
import math 
def translation(tx,ty): 
    return np.array([
        [1.0, 0.0, tx],
        [0.0, 1.0, ty], 
        [0.0, 0.0, 1.0]
    ],dtype = float)
def scale(sx,sy): 
    return np.array([
        [sx, 0.0, 0.0], 
        [0.0, sy, 0.0], 
        [0.0, 0.0, 1.0]
    ], dtype = float)
def rotation(angle_degrees): 
    angle = math.radians(angle_degrees)
    c, s = math.cos(angle), math.sin(angle)
    return np.array([
        [c, -s, 0.0],
        [s, c, 0.0], 
        [0.0, 0.0, 1.0]
    ], dtype=float)
def reflection(axis): 
    if axis == 'x': 
        return np.array([
            [-1.0, 0.0, 0.0], 
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0]
        ], dtype = float)
    else: 
        return np.array([
            [1.0, 0.0, 0.0], 
            [0.0, -1.0, 0.0],
            [0.0, 0.0, 1.0]
        ], dtype = float)
def shear(kx,ky): 
    return np.array([
        [1.0, kx, 0.0], 
        [ky, 1.0, 0.0],
        [0.0, 0.0, 1.0]
    ], dtype = float)
def around_pivot(transform_matrix, pivot): 
    px, py = pivot
    T_neg = translation(-px, -py)
    T_pos = translation(px, py)
    return T_pos @ transform_matrix @ T_neg 
def transform_points(points, matrix): 
    ones = np.ones((len(points), 1))
    points_h = np.hstack((points, ones))
    transformed_h = (matrix @ points_h.T).T
    return transformed_h[:, :2]
def get_inverse(matrix): 
    try: 
        if abs(np.linalg.det(matrix)) <1e-6: 
            return None 
        return np.linalg.inv(matrix)
    except np.linalg.LinAlgError:
        return None 