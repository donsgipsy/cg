import pygame
pygame.font.init()
WIDTH, HEIGHT = 1200, 750
ROWS, COLS = 25, 40
CELL_SIZE = 25
GRID_OFFSET_X = 50
GRID_OFFSET_Y = 50
FPS = 60
STEPS_PER_SECOND = 20
C_EMPTY = (255, 255, 255)
C_WALL = (50, 50, 50)
C_START = (0, 255, 0)
C_GOAL = (255, 0, 0)
C_OPEN = (173, 216, 230)
C_CLOSED = (100, 149, 237)
C_PATH = (255, 215, 0)
C_WEIGHTED = (255, 165, 0)
FONT_SMALL = pygame.font.Font(None, 24)
FONT_MEDIUM = pygame.font.Font(None, 32)
FONT_BIG = pygame.font.Font(None, 48)