import pygame
from settings import *

def draw_bars(screen, values, step_info, algorithm):
    n = len(values)
    if n == 0:
        return
    
    area_width = WIDTH - 100
    area_height = HEIGHT - 250
    start_x = 50
    start_y = 150
    
    bar_width = area_width // n
    max_val = max(values) if values else 100
    
   
    active_indices = set()
    if step_info:
        if 'indices' in step_info:
            active_indices.update(step_info['indices'])
        if 'index' in step_info:
            active_indices.add(step_info['index'])
            
    left_idx = step_info.get('left', 0) if step_info else 0
    right_idx = step_info.get('right', n - 1) if step_info else n - 1
    mid_idx = step_info.get('mid', -1) if step_info else -1

    for i, val in enumerate(values):
        x = start_x + i * bar_width
        height = int((val / max_val) * area_height)
        y = start_y + area_height - height
        
        color = BAR_DEFAULT
        
        if step_info:
            step_type = step_info.get('type', '')
            
          
            if algorithm in ('bubble', 'choice'):
                if step_type == 'sorted':
                    color = BAR_SORTED
                elif i in active_indices:
                    if step_type == 'compare':
                        color = BAR_COMPARE
                    elif step_type == 'swap':
                        color = BAR_SWAP
                    elif step_type == 'new_min':
                        color = BAR_MIN
            
            elif algorithm == 'binary':
                if step_type == 'found' and i == step_info.get('index'):
                    color = BAR_FOUND
                elif step_type == 'not_found':
                    color = BAR_EXCLUDED
                elif i == mid_idx:
                    color = BAR_MID
                elif left_idx <= i <= right_idx:
                    color = BAR_SEARCH_ACTIVE
                else:
                    color = BAR_EXCLUDED
                    
   
        pygame.draw.rect(screen, color, (x, y, bar_width - 2, height))
        
        if n <= 30:
            text = FONT_SMALL.render(str(val), True, BLACK)
            text_rect = text.get_rect(center=(x + (bar_width - 2) // 2, y - 10))
            screen.blit(text, text_rect)

def draw_ui(screen, algorithm_name, stats, step_info, target=None):
    title = FONT_BIG.render(algorithm_name, True, BLACK)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))
    
    stats_y = HEIGHT - 150
    pygame.draw.rect(screen, DARK_GRAY, (20, stats_y, WIDTH - 40, 130))
    pygame.draw.rect(screen, WHITE, (20, stats_y, WIDTH - 40, 130), 2)
    
    y_offset = stats_y + 15
    if algorithm_name == "Bubble Sort":
        lines = [
            f"Comparisons: {stats.get('comparisons', 0)}",
            f"Swaps: {stats.get('swaps', 0)}",
            f"Pass: {stats.get('pass', 0)}",
            f"Steps: {stats.get('stxeps', 0)}"
        ]
    elif algorithm_name == "Selection Sort":
        lines = [
            f"Comparisons: {stats.get('comparisons', 0)}",
            f"Swaps: {stats.get('swaps', 0)}",
            f"Pass: {stats.get('pass', 0)}",
            f"Steps: {stats.get('steps', 0)}"
        ]
    elif algorithm_name == "Binary Search":
        lines = [
            f"Target: {target if target is not None else 'N/A'}",
            f"Comparisons: {stats.get('comparisons', 0)}",
            f"Steps: {stats.get('steps', 0)}",
            f"Current range: [{stats.get('left', 0)}, {stats.get('right', 0)}]",
            f"Result: {stats.get('result', 'Searching...')}"
        ]
    else:
        lines = [
            "Press 1, 2, or 3 to select an algorithm",
            "Press R to generate new array"
        ]
        
    for i, line in enumerate(lines):
        text = FONT_MEDIUM.render(line, True, WHITE)
        screen.blit(text, (40, y_offset + i * 25))

    legend_x = WIDTH - 250
    legend_y = 80
    legend_items = [
        ("Default", BAR_DEFAULT),
        ("Compare", BAR_COMPARE),
        ("Swap", BAR_SWAP),
        ("Min", BAR_MIN),
        ("Sorted", BAR_SORTED),
        ("Search Active", BAR_SEARCH_ACTIVE),
        ("Mid", BAR_MID),
        ("Found", BAR_FOUND),
        ("Excluded", BAR_EXCLUDED)
    ]
    
    for i, (name, color) in enumerate(legend_items):
        y = legend_y + i * 20
        pygame.draw.rect(screen, color, (legend_x, y, 15, 15))
        text = FONT_SMALL.render(name, True, BLACK)
        screen.blit(text, (legend_x + 25, y - 2))

def draw_controls(screen):
    controls = [
        "1: Bubble Sort   2: Selection Sort   3: Binary Search",
        "SPACE: Start/Pause   N: Next Step   R: New Array   ESC: Exit"
    ]
    y = HEIGHT - 40
    for i, text in enumerate(controls):
        surf = FONT_SMALL.render(text, True, GRAY)
        screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, y + i * 20))