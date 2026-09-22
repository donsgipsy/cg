import pygame
import sys
import math

pygame.init()

WIDTH = 1000
HEIGHT = 650
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
GREEN = (34, 139, 34)
LIGHT_GREEN = (144, 238, 144)
BLUE = (65, 105, 225)
BEIGE = (245, 222, 179)
DARK_BEIGE = (200, 180, 140)
RED = (255, 0, 0)

CLIENT_COLORS = [(255, 0, 0), (0, 200, 0), (0, 0, 255), (255, 165, 0)]

PRODUCTS = [
    {'name': 'Сэндвич', 'price': 70, 'stock': 3, 'cook_time': 3},
    {'name': 'Сосиска в тесте', 'price': 90, 'stock': 4, 'cook_time': 0},
    {'name': 'Сэндвич', 'price': 180, 'stock': 2, 'cook_time': 5},
    {'name': 'Кофе', 'price': 140, 'stock': 5, 'cook_time': 3}
]
  
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Симулятор пекарни")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 28)
big_font = pygame.font.Font(None, 36)

obstacles = [
    pygame.Rect(300, 200, 400, 80),
    pygame.Rect(750, 200, 100, 80)
]

interaction_zone = pygame.Rect(300, 290, 400, 60)
pickup_zone = pygame.Rect(700, 450, 150, 100)

client = {
    'x': 100, 'y': 325, 'radius': 20,
    'color_index': 0, 'color': CLIENT_COLORS[0], 'speed': 200
}

money = 1000
order_state = 'NO_ORDER'
current_order = None
order_timer = 0
order_total_time = 0
menu_open = False
message = None
message_timer = 0

def check_collision(x, y, radius, obstacles):
    if x - radius < 0 or x + radius > WIDTH or y - radius < 0 or y + radius > HEIGHT:
        return True
    for rect in obstacles:
        closest_x = max(rect.x, min(x, rect.x + rect.width))
        closest_y = max(rect.y, min(y, rect.y + rect.height))
        distance_x = x - closest_x
        distance_y = y - closest_y
        if (distance_x ** 2) + (distance_y ** 2) < (radius ** 2):
            return True
    return False

def draw_scene(screen):
    screen.fill(BEIGE)
    
    pygame.draw.rect(screen, BLUE, (20, 250, 80, 150))
    text = font.render("ВХОД", True, WHITE)
    screen.blit(text, (35, 310))
    
    pygame.draw.rect(screen, BROWN, (300, 200, 400, 80))
    text = font.render("ПРИЛАВОК", True, WHITE)
    screen.blit(text, (460, 230))
    
    pygame.draw.rect(screen, GRAY, (750, 200, 100, 80))
    text = font.render("КАССА", True, BLACK)
    screen.blit(text, (765, 230))
    
    zone_color = LIGHT_GREEN if order_state == 'READY' else GREEN
    pygame.draw.rect(screen, zone_color, pickup_zone)
    text = font.render("ВЫДАЧА", True, WHITE)
    screen.blit(text, (740, 490))

    zone_surface = pygame.Surface((interaction_zone.width, interaction_zone.height), pygame.SRCALPHA)
    zone_surface.fill((255, 255, 0, 60))
    screen.blit(zone_surface, (interaction_zone.x, interaction_zone.y))
    pygame.draw.rect(screen, (200, 200, 0), interaction_zone, 2)

    pygame.draw.circle(screen, client['color'], (int(client['x']), int(client['y'])), client['radius'])

    if not menu_open:
        if interaction_zone.collidepoint(client['x'], client['y']) and order_state in ['NO_ORDER', 'DONE']:
            hint_text = big_font.render("E - сделать заказ", True, BLACK)
            screen.blit(hint_text, (client['x'] - 100, client['y'] - 60))
        
        if pickup_zone.collidepoint(client['x'], client['y']) and order_state == 'READY':
            hint_text = big_font.render("E - получить заказ", True, BLACK)
            screen.blit(hint_text, (client['x'] - 110, client['y'] - 60))

def draw_progress_bar(screen):
    if order_state == 'WAITING' and current_order:
        bar_x, bar_y = 300, 550
        bar_w, bar_h = 400, 30
        
        progress = max(0, order_timer / order_total_time)
        
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_w, bar_h))
        pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_w, bar_h), 2)
        
        fill_w = int(bar_w * progress)
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, fill_w, bar_h))
        
        text = big_font.render(f"Готовится: {current_order['name']} ({order_timer:.1f} с)", True, BLACK)
        screen.blit(text, (bar_x, bar_y - 35))

def draw_ui(screen):
    ui_y = 10
    money_text = font.render(f"Money: {money} ₽", True, BLACK)
    screen.blit(money_text, (10, ui_y))
    
    order_name = current_order['name'] if current_order else 'Нет'
    order_text = font.render(f"Order: {order_name}", True, BLACK)
    screen.blit(order_text, (10, ui_y + 30))
    
    state_text = font.render(f"State: {order_state}", True, BLACK)
    screen.blit(state_text, (10, ui_y + 60))
    
    fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, BLACK)
    screen.blit(fps_text, (10, ui_y + 90))
    
    if message and message_timer > 0:
        msg_text = big_font.render(message, True, RED)
        screen.blit(msg_text, (WIDTH // 2 - 150, HEIGHT - 80))

def draw_menu(screen):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))
    
    menu_rect = pygame.Rect(250, 100, 500, 450)
    pygame.draw.rect(screen, DARK_BEIGE, menu_rect)
    pygame.draw.rect(screen, BLACK, menu_rect, 3)
    
    title = big_font.render("МЕНЮ ЗАКАЗА", True, BLACK)
    screen.blit(title, (370, 120))
    
    y = 180
    for i, product in enumerate(PRODUCTS):
        stock_color = GREEN if product['stock'] > 0 else RED
        line = f"{i+1}. {product['name']} - {product['price']} ₽ (остаток: {product['stock']})"
        text = font.render(line, True, stock_color)
        screen.blit(text, (280, y))
        y += 50
    
    close_text = font.render("ESC - закрыть меню", True, BLACK)
    screen.blit(close_text, (370, 480))

def handle_events():
    global money, order_state, current_order, menu_open, message, message_timer, order_timer, order_total_time
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if menu_open:
                    menu_open = False
                else:
                    return False
            if event.key == pygame.K_SPACE:
                client['color_index'] = (client['color_index'] + 1) % len(CLIENT_COLORS)
                client['color'] = CLIENT_COLORS[client['color_index']]
            
            if event.key == pygame.K_e and not menu_open:
                if interaction_zone.collidepoint(client['x'], client['y']) and order_state in ['NO_ORDER', 'DONE']:
                    menu_open = True
                elif pickup_zone.collidepoint(client['x'], client['y']) and order_state == 'READY':
                    order_state = 'DONE'
                    message = "Заказ получен!"
                    message_timer = 2.0
            
            if menu_open and event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                idx = event.key - pygame.K_1
                product = PRODUCTS[idx]
                
                if product['stock'] <= 0:
                    message = "Товар закончился!"
                    message_timer = 2.0
                elif money < product['price']:
                    message = "Недостаточно денег!"
                    message_timer = 2.0
                else:
                    money -= product['price']
                    product['stock'] -= 1
                    current_order = product.copy()
                    if product['cook_time'] > 0:
                        order_state = 'WAITING'
                        order_timer = product['cook_time']
                        order_total_time = product['cook_time']
                    else:
                        order_state = 'READY'
                    menu_open = False
                    message = "Заказ принят!"
                    message_timer = 2.0
    return True

def handle_movement(dt):
    keys = pygame.key.get_pressed()
    dx = 0
    dy = 0
    
    if keys[pygame.K_w]: dy -= 1
    if keys[pygame.K_s]: dy += 1
    if keys[pygame.K_a]: dx -= 1
    if keys[pygame.K_d]: dx += 1
    
    if dx != 0 and dy != 0:
        length = math.sqrt(dx**2 + dy**2)
        dx /= length
        dy /= length
    
    new_x = client['x'] + dx * client['speed'] * dt
    new_y = client['y'] + dy * client['speed'] * dt
    
    if not check_collision(new_x, client['y'], client['radius'], obstacles):
        client['x'] = new_x
    if not check_collision(client['x'], new_y, client['radius'], obstacles):
        client['y'] = new_y

def update_order(dt):
    global order_state, message, message_timer, order_timer
    
    if message_timer > 0:
        message_timer -= dt
        if message_timer <= 0:
            message = None
    
    if order_state == 'WAITING':
        order_timer -= dt
        if order_timer <= 0:
            order_timer = 0
            order_state = 'READY'
            message = "Заказ готов! Идите к зоне выдачи."
            message_timer = 3.0

def main():
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        
        if not handle_events():
            running = False
        
        if not menu_open:
            handle_movement(dt)
        
        update_order(dt)
        
        draw_scene(screen)
        draw_ui(screen)
        draw_progress_bar(screen)
        
        if menu_open:
            draw_menu(screen)
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()