from __future__ import annotations

import pygame
from typing import Tuple
from vrp_models import Solution
from vrp_fitness import evaluate_route_time


def draw_solution(sol: Solution, width: int = 800, height: int = 500) -> None:
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("VRP Solution Viewer")
    clock = pygame.time.Clock()
    colors = [(66, 135, 245), (255, 99, 132), (99, 255, 132), (255, 205, 86), (153, 102, 255)]
    font = pygame.font.SysFont(None, 18)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((255, 255, 255))

        # draw routes
        for idx, r in enumerate(sol.routes):
            color = colors[idx % len(colors)]
            pts = [r.vehicle.start_depot] + [c.pos for c in r.clients] + [r.vehicle.end_depot]
            if len(pts) >= 2:
                pygame.draw.lines(screen, color, False, pts, width=2)
            # draw clients
            for c in r.clients:
                pygame.draw.circle(screen, color, (int(c.x), int(c.y)), 5)
            # draw depot
            pygame.draw.circle(screen, (0, 0, 0), (int(r.vehicle.start_depot[0]), int(r.vehicle.start_depot[1])), 6, width=2)

            # overlay metrics near depot
            demand = r.total_demand()
            cap = r.vehicle.capacity
            dist = r.distance()
            rtime = evaluate_route_time(r)
            overlay = f"V{r.vehicle.id} | dem {demand}/{cap} | dist {dist:.1f} | time {rtime:.1f}"
            text = font.render(overlay, True, (0, 0, 0))
            tx, ty = int(r.vehicle.start_depot[0]) + 8, int(r.vehicle.start_depot[1]) - 14
            screen.blit(text, (tx, ty))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
