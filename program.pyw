import pygame
import pygame.gfxdraw
import sys
import math
import numpy as np
from main_frame import Engine
from score_handling import Score
from setting_up import Carrom

WIDTH, HEIGHT = 700, 700
FPS = 60
FRICTION = 600

def draw_antialiased_circle(surface, x, y, radius, color):
    pygame.gfxdraw.aacircle(surface, int(x), int(y), int(radius), color)
    pygame.gfxdraw.filled_circle(surface, int(x), int(y), int(radius), color)

def main():
    pygame.init()
    pygame.font.init()
    font = pygame.font.SysFont('Arial', 20, bold=True)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Carrom")
    clock = pygame.time.Clock()
    engine = Engine(WIDTH, HEIGHT, FRICTION)
    board = Carrom(screen, HEIGHT, WIDTH)
    score_manager = Score()
    state = 'AIMING'
    shot_potted=False
    engine.change_turn()
    dragging = False
    mouse_start = (0, 0)

    def win():
        running=True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            screen.fill((0, 0, 0))
            winner = "Player 1" if score_manager.scores[0] > score_manager.scores[1] else "Player 2"
            msg = font.render(f"{winner} Wins!", True, (255, 255, 255))
            screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - msg.get_height() // 2))
            pygame.display.flip()

    while True:
        dt = clock.tick(FPS) / 1000.0
        current_p = 1 if engine.turn % 2 != 0 else 2
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if state == 'AIMING':
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_start = pygame.mouse.get_pos()
                    dragging = True
                if event.type == pygame.MOUSEBUTTONUP and dragging:
                    mouse_end = pygame.mouse.get_pos()
                    dx = mouse_start[0] - mouse_end[0]
                    dy = mouse_start[1] - mouse_end[1]
                    power = min(np.hypot(dx, dy) * 4, 1600)
                    angle = math.atan2(dy, dx)
                    engine.shoot(power, angle)
                    state = 'PHYSICS'
                    dragging = False
        
        if state == 'AIMING':
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RIGHT]:
                engine.striker_pos[0][0] = min(engine.striker_pos[0][0] + 5, 3*WIDTH//4 - engine.striker_radius)
            if keys[pygame.K_LEFT]:
                engine.striker_pos[0][0] = max(engine.striker_pos[0][0] - 5, WIDTH//4 + engine.striker_radius)

        if state == 'PHYSICS':
            pocketed_list = engine.update(dt)
            if pocketed_list:
                shot_potted = True
                
            for c_type in pocketed_list:
                score_manager.update_score(current_p, c_type)
                
            speeds = np.linalg.norm(engine.all_vels, axis=1)
            if np.all(speeds < 1.0):
                
                engine.all_vels[:] = 0
                
                if not shot_potted:
                    engine.turn += 1
                
                engine.change_turn()
                shot_potted = False
                state = 'AIMING'

        board.draw_board()
        text_p1 = font.render(f"P1: {score_manager.get_score(1)}", True, (255, 255, 255))
        text_p2 = font.render(f"P2: {score_manager.get_score(2)}", True, (255, 255, 255))
        screen.blit(text_p1, (20, 20))
        screen.blit(text_p2, (WIDTH - text_p2.get_width() - 20, 20))
        
        if score_manager.scores[0] >= 160 or score_manager.scores[1] >= 160:
            win()
            break

        for i in range(20):
            pos = engine.all_pos[i]
            if pos[0] > 0:
                color = (20, 20, 20)
                if i == 19: color = (200, 50, 50)
                elif i == 0: color = (255, 50, 255)
                elif engine.white_mask[i]: color = (150, 160, 150)
                draw_antialiased_circle(screen, pos[0], pos[1], engine.radii[i], color)

        if dragging:
            curr_mouse = pygame.mouse.get_pos()
            s_pos = engine.striker_pos[0]
            dx, dy = s_pos[0] - curr_mouse[0], s_pos[1] - curr_mouse[1]
            pygame.draw.aaline(screen, (255, 255, 255), (int(s_pos[0]), int(s_pos[1])), (int(s_pos[0] + dx), int(s_pos[1] + dy)))

        pygame.display.flip()
    


if __name__ == "__main__":
    main()