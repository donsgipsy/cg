WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 750        
WINDOW_TITLE = "Pathfinding Visualizer: BFS / Dijkstra / A*"
FPS = 60
ROWS = 30                   
COLS = 40                 
CELL_SIZE = 22
GRID_X = 20                
GRID_Y = 20             
DEFAULT_START = (15, 5)
DEFAULT_GOAL = (15, 34)
PANEL_X = GRID_X + COLS * CELL_SIZE + 16      
PANEL_WIDTH = WINDOW_WIDTH - PANEL_X - 12     
PANEL_PAD = 14
EMPTY = "EMPTY"         
WALL = "WALL"         
START = "START"          
GOAL = "GOAL"         
OPEN = "OPEN"          
CLOSED = "CLOSED"       
PATH = "PATH"           
WEIGHTED = "WEIGHTED"    
LEGEND = [
    (EMPTY, "Empty"),
    (WALL, "Wall"),
    (START, "Start"),
    (GOAL, "Goal"),
    (OPEN, "Open (frontier)"),
    (CLOSED, "Closed (visited)"),
    (PATH, "Path"),
    (WEIGHTED, "Weighted (cost 5)"),
]
NORMAL_COST = 1
WEIGHTED_COST = 5
ALGORITHM_NAMES = ("BFS", "Dijkstra", "A*")
SPEEDS = [2, 5, 10, 20, 50, 100, 200, 500, 1000]
DEFAULT_SPEED_INDEX = 3
MAX_STEPS_PER_FRAME = 200   
COLORS = {
    EMPTY: (250, 250, 250),
    WALL: (45, 52, 64),
    START: (46, 204, 113),
    GOAL: (231, 76, 60),
    OPEN: (130, 215, 235),   
    CLOSED: (70, 120, 220),    
    PATH: (255, 215, 0),       
    WEIGHTED: (150, 105, 60), 
}

BG_COLOR = (228, 232, 238)
GRID_LINE_COLOR = (205, 210, 218)
PANEL_COLOR = (255, 255, 255)
TEXT_COLOR = (30, 35, 45)
MUTED_COLOR = (110, 118, 130)
ACCENT_COLOR = (52, 120, 246)
CURRENT_COLOR = (255, 140, 0)     
OK_COLOR = (30, 150, 80)
FAIL_COLOR = (205, 50, 50)
BUTTON_COLOR = (240, 243, 248)
BUTTON_BORDER = (190, 197, 208)