import pygame
import sys
import random
from settings import *
import algorithms
import visualizer

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Визуализация алгоритмов")
clock = pygame.time.Clock()

values = algorithms.gen_array(ARRAY_SIZE, MIN_VALUE, MAX_VALUE)
sorted_values = sorted(values)

algorithm_mode = 'none'   
state = 'IDLE'         

generator = None
step_info = None
step_timer = 0.0

target_value = random.randint(MIN_VALUE, MAX_VALUE)


def new_stats():
    return {
        'comparisons': 0,
        'swaps': 0,
        'pass': 0,
        'steps': 0,
        'left': 0,
        'right': len(values) - 1,
        'result': 'Searching...'
    }


stats = new_stats()


def reset_state():
    global state, generator, step_info, stats, step_timer
    global values, sorted_values, target_value

    values = algorithms.gen_array(ARRAY_SIZE, MIN_VALUE, MAX_VALUE)
    sorted_values = sorted(values)
    target_value = random.randint(MIN_VALUE, MAX_VALUE)

    state = 'IDLE'
    generator = None
    step_info = None
    step_timer = 0.0
    stats = new_stats()


def start_algorithm(mode, new_array=False):
    global algorithm_mode, state, generator, step_info, stats
    global target_value, step_timer

    if algorithm_mode != mode or new_array:
        reset_state()
        algorithm_mode = mode

    state = 'RUNNING'
    step_timer = 0.0
    step_info = None
    stats = new_stats()

    if mode == 'bubble':
        generator = algorithms.bubble_sort(values)
    elif mode == 'choice':
        generator = algorithms.sort_choice(values)
    elif mode == 'binary':
        if target_value not in sorted_values:
            target_value = sorted_values[len(sorted_values) // 2]
        generator = algorithms.binary_search(sorted_values, target_value)

    try:
        step_info = next(generator)
        update_stats(step_info)
    except StopIteration:
        state = 'FINISHED'


def restart_current():
    mode = algorithm_mode if algorithm_mode != 'none' else 'bubble'
    start_algorithm(mode, new_array=(mode in ('bubble', 'choice')))


def update_stats(info):
    if not info:
        return

    step_type = info.get('type', '')
    stats['steps'] += 1

    if step_type in ('compare', 'check'):
        stats['comparisons'] += 1
    elif step_type == 'swap':
        stats['swaps'] += 1
    elif step_type == 'new_min':
        stats['comparisons'] += 1

    if algorithm_mode in ('bubble', 'choice'):
        if step_type in ('swap', 'sorted'):
            stats['pass'] += 1

    if algorithm_mode == 'binary':
        stats['left'] = info.get('left', 0)
        stats['right'] = info.get('right', len(sorted_values) - 1)
        if step_type == 'found':
            stats['result'] = f"Found at index {info.get('index')}"
        elif step_type == 'not_found':
            stats['result'] = "Not found"


def make_next_step():
    global step_info, state

    if not generator:
        return
    try:
        step_info = next(generator)
        update_stats(step_info)
    except StopIteration:
        state = 'FINISHED'


def change_target(delta):

    global target_value

    if target_value in sorted_values:
        idx = (sorted_values.index(target_value) + delta) % len(sorted_values)
        target_value = sorted_values[idx]
    else:
        target_value = sorted_values[len(sorted_values) // 2]
    start_algorithm('binary')


def handle_events():
    global state, algorithm_mode, target_value

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

        if event.type != pygame.KEYDOWN:
            continue

        if event.key == pygame.K_ESCAPE:
            return False

        # --- Выбор алгоритма ---
        if event.key == pygame.K_1:
            start_algorithm('bubble', new_array=True)
        elif event.key == pygame.K_2:
            start_algorithm('choice', new_array=True)
        elif event.key == pygame.K_3:
            start_algorithm('binary', new_array=True)

        elif event.key == pygame.K_SPACE:
            if state == 'RUNNING':
                state = 'PAUSED'
            elif state == 'PAUSED':
                state = 'RUNNING'
            else: 
                restart_current()

       
        elif event.key in (pygame.K_n, pygame.K_t):
            if state in ('IDLE', 'FINISHED'):
                restart_current()     
                if state == 'RUNNING':
                    state = 'PAUSED'
            else:
                state = 'PAUSED'
                make_next_step()

       
        elif event.key in (pygame.K_r, pygame.K_k):
            reset_state()
            algorithm_mode = 'none'

     
        elif event.key == pygame.K_UP and algorithm_mode == 'binary':
            change_target(1)
        elif event.key == pygame.K_DOWN and algorithm_mode == 'binary':
            change_target(-1)
        elif event.key == pygame.K_f and algorithm_mode == 'binary':
            target_value = random.randint(MIN_VALUE, MAX_VALUE)
            start_algorithm('binary')

    return True


def main():
    global step_timer

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        if not handle_events():
            running = False
            continue

     
        if state == 'RUNNING' and generator:
            step_timer += dt
            if step_timer >= 1.0 / STEPS_PER_SECOND:
                step_timer = 0.0
                make_next_step()

    
        screen.fill(WHITE)

        current_values = sorted_values if algorithm_mode == 'binary' else values
        if algorithm_mode == 'bubble':
            algo_name = "Bubble Sort"
        elif algorithm_mode == 'choice':
            algo_name = "Selection Sort"
        elif algorithm_mode == 'binary':
            algo_name = "Binary Search"
        else:
            algo_name = "Select an Algorithm (1, 2, 3)"

        visualizer.draw_bars(screen, current_values, step_info, algorithm_mode)
        visualizer.draw_ui(screen, algo_name, stats, step_info,
                           target_value if algorithm_mode == 'binary' else None)
        visualizer.draw_controls(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
