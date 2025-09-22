from __future__ import annotations

import pygame
from typing import Tuple
from vrp_models import Solution
from vrp_fitness import (
    PenaltyWeights,
    evaluate_route_time,
    capacity_violation,
    time_window_violation,
    refrigeration_violation,
    max_route_time_violation,
)


def draw_solution(
    sol: Solution,
    width: int = 980,
    height: int = 520,
    scale_map: bool = True,
    weights: PenaltyWeights | None = None,
) -> None:
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("VRP Solution Viewer")
    clock = pygame.time.Clock()

    colors = [
        (66, 135, 245),
        (255, 99, 132),
        (99, 255, 132),
        (255, 205, 86),
        (153, 102, 255),
        (255, 159, 64),
        (54, 162, 235),
    ]

    base_font_size = 18
    base_title_size = 22
    font = pygame.font.SysFont(None, base_font_size)
    title_font = pygame.font.SysFont(None, base_title_size)

    # Layout areas
    map_rect = pygame.Rect(0, 0, 760, height)
    panel_rect = pygame.Rect(760, 0, width - 760, height)

    # UI state
    show_panel = True
    scroll_offset = 0.0
    scroll_step = 20
    compact = False
    page = 0
    h_scroll_offset = 0.0
    h_scroll_step = 30

    # Map transform
    zoom = 1.0
    pan_x, pan_y = 0.0, 0.0
    pan_step = 30

    def compute_map_scale_and_offset() -> Tuple[float, Tuple[float, float]]:
        xs, ys = [], []
        for r in sol.routes:
            xs.extend([r.vehicle.start_depot[0], r.vehicle.end_depot[0]])
            ys.extend([r.vehicle.start_depot[1], r.vehicle.end_depot[1]])
            for c in r.clients:
                xs.append(c.x)
                ys.append(c.y)
        if not xs or not ys:
            return 1.0, (0.0, 0.0)
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        span_x = max(1.0, max_x - min_x)
        span_y = max(1.0, max_y - min_y)
        pad = 20
        sx = (map_rect.width - 2 * pad) / span_x
        sy = (map_rect.height - 2 * pad) / span_y
        s = min(sx, sy)
        off_x = map_rect.x + pad - min_x * s + (map_rect.width - 2 * pad - span_x * s) / 2
        off_y = map_rect.y + pad - min_y * s + (map_rect.height - 2 * pad - span_y * s) / 2
        return s, (off_x, off_y)

    def tx(pt, s, off):
        return int(pt[0] * s + off[0]), int(pt[1] * s + off[1])

    def wrap_text(text: str, font_obj: pygame.font.Font, max_width: int) -> list[str]:
        words = text.split()
        lines = []
        cur = ""
        for w in words:
            trial = (cur + " " + w).strip()
            if font_obj.size(trial)[0] <= max_width:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                if font_obj.size(w)[0] > max_width:
                    el = w
                    while font_obj.size(el + "…")[0] > max_width and len(el) > 1:
                        el = el[:-1]
                    lines.append((el + "…") if el != w else el)
                    cur = ""
                else:
                    cur = w
        if cur:
            lines.append(cur)
        return lines

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    show_panel = not show_panel
                elif event.key == pygame.K_UP:
                    scroll_offset -= scroll_step
                elif event.key == pygame.K_DOWN:
                    scroll_offset += scroll_step
                elif event.key == pygame.K_c:
                    compact = not compact
                    fs = 14 if compact else base_font_size
                    ts = 18 if compact else base_title_size
                    font = pygame.font.SysFont(None, fs)
                    title_font = pygame.font.SysFont(None, ts)
                elif event.key == pygame.K_PAGEUP:
                    page = max(0, page - 1)
                    scroll_offset = 0
                elif event.key == pygame.K_PAGEDOWN:
                    page += 1
                    scroll_offset = 0
                elif event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_EQUALS:
                    zoom = min(10.0, zoom * 1.1)
                elif event.key == pygame.K_MINUS:
                    zoom = max(0.2, zoom / 1.1)
                elif event.key == pygame.K_0:
                    zoom = 1.0
                    pan_x, pan_y = 0.0, 0.0
                elif event.key == pygame.K_a:
                    pan_x += pan_step
                elif event.key == pygame.K_d:
                    pan_x -= pan_step
                elif event.key == pygame.K_w:
                    pan_y += pan_step
                elif event.key == pygame.K_s:
                    pan_y -= pan_step
                elif event.key == pygame.K_LEFT:
                    h_scroll_offset -= h_scroll_step
                elif event.key == pygame.K_RIGHT:
                    h_scroll_offset += h_scroll_step
            elif event.type == pygame.MOUSEWHEEL:
                mods = pygame.key.get_mods()
                if mods & pygame.KMOD_CTRL:
                    if event.y > 0:
                        zoom = min(10.0, zoom * 1.1)
                    elif event.y < 0:
                        zoom = max(0.2, zoom / 1.1)
                elif mods & pygame.KMOD_SHIFT:
                    h_scroll_offset -= event.y * h_scroll_step
                else:
                    scroll_offset -= event.y * scroll_step

        screen.fill((255, 255, 255))
        if show_panel:
            pygame.draw.rect(screen, (245, 245, 245), panel_rect)
            pygame.draw.rect(screen, (210, 210, 210), panel_rect, width=1)

        s_fit, off_fit = (1.0, (0.0, 0.0)) if not scale_map else compute_map_scale_and_offset()
        s_eff = s_fit * zoom
        off_eff = (off_fit[0] + pan_x, off_fit[1] + pan_y)

        # Map drawing
        screen.set_clip(map_rect)
        mouse_pos = pygame.mouse.get_pos()
        hover_info = None

        def pt_seg_dist(p, a, b):
            (px, py), (ax, ay), (bx, by) = p, a, b
            abx, aby = bx - ax, by - ay
            apx, apy = px - ax, py - ay
            ab2 = abx * abx + aby * aby
            t = 0.0 if ab2 == 0 else max(0.0, min(1.0, (apx * abx + apy * aby) / ab2))
            cx, cy = ax + t * abx, ay + t * aby
            dx, dy = px - cx, py - cy
            return (dx * dx + dy * dy) ** 0.5

        for idx, r in enumerate(sol.routes):
            color = colors[idx % len(colors)]
            pts = [r.vehicle.start_depot] + [c.pos for c in r.clients] + [r.vehicle.end_depot]
            if len(pts) >= 2:
                tpts = [tx(p, s_eff, off_eff) for p in pts]
                pygame.draw.lines(screen, color, False, tpts, width=2)
                if map_rect.collidepoint(mouse_pos):
                    mind = 1e9
                    for a, b in zip(tpts[:-1], tpts[1:]):
                        d = pt_seg_dist(mouse_pos, a, b)
                        if d < mind:
                            mind = d
                    if mind < 8.0:
                        demand = r.total_demand()
                        cap = r.vehicle.capacity
                        dist = r.distance()
                        rtime = evaluate_route_time(r)
                        cap_v = capacity_violation(r)
                        tw_v = time_window_violation(r)
                        refr_v = refrigeration_violation(r)
                        mrt_v = max_route_time_violation(r)
                        hover_info = (
                            mouse_pos,
                            color,
                            [
                                f"Rota V{r.vehicle.id}",
                                f"Clientes: {len(r.clients)} | Dem {demand}/{cap}",
                                f"Dist {dist:.1f} | Tempo {rtime:.1f}",
                                f"Viol: cap {cap_v:.1f}, tw {tw_v:.1f}, refr {refr_v:.1f}, mrt {mrt_v:.1f}",
                            ],
                        )
            for c in r.clients:
                cx, cy = tx((c.x, c.y), s_eff, off_eff)
                pygame.draw.circle(screen, color, (int(cx), int(cy)), 5)
            dx, dy = tx((r.vehicle.start_depot[0], r.vehicle.start_depot[1]), s_eff, off_eff)
            pygame.draw.circle(screen, (0, 0, 0), (dx, dy), 6, width=2)
        screen.set_clip(None)

        # Tooltip
        if hover_info is not None:
            (mx, my), color, lines = hover_info
            pad = 6
            tw = max(font.size(s)[0] for s in lines) + pad * 2
            th = (len(lines) * (18 if compact else 20)) + pad * 2
            tip_x = mx + 12
            tip_y = my + 12
            if tip_x + tw > map_rect.right - 6:
                tip_x = map_rect.right - 6 - tw
            if tip_y + th > map_rect.bottom - 6:
                tip_y = map_rect.bottom - 6 - th
            tip_rect = pygame.Rect(tip_x, tip_y, tw, th)
            pygame.draw.rect(screen, (255, 255, 255), tip_rect)
            pygame.draw.rect(screen, color, tip_rect, width=2)
            cy = tip_y + pad
            for sline in lines:
                surf = font.render(sline, True, (20, 20, 20))
                screen.blit(surf, (tip_x + pad, cy))
                cy += (18 if compact else 20)

        # Mini-map
        mini_w, mini_h = 140, 100
        mini_rect = pygame.Rect(map_rect.x + 10, map_rect.bottom - 10 - mini_h, mini_w, mini_h)
        pygame.draw.rect(screen, (250, 250, 250), mini_rect)
        pygame.draw.rect(screen, (210, 210, 210), mini_rect, width=1)

        def compute_mini_transform():
            xs, ys = [], []
            for r in sol.routes:
                xs.extend([r.vehicle.start_depot[0], r.vehicle.end_depot[0]])
                ys.extend([r.vehicle.start_depot[1], r.vehicle.end_depot[1]])
                for c in r.clients:
                    xs.append(c.x)
                    ys.append(c.y)
            if not xs or not ys:
                return 1.0, (mini_rect.x, mini_rect.y)
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            span_x = max(1.0, max_x - min_x)
            span_y = max(1.0, max_y - min_y)
            pad = 6
            sx = (mini_rect.width - 2 * pad) / span_x
            sy = (mini_rect.height - 2 * pad) / span_y
            sm = min(sx, sy)
            off_x = mini_rect.x + pad - min_x * sm + (mini_rect.width - 2 * pad - span_x * sm) / 2
            off_y = mini_rect.y + pad - min_y * sm + (mini_rect.height - 2 * pad - span_y * sm) / 2
            return sm, (off_x, off_y)

        sm, offm = compute_mini_transform()
        for idx, r in enumerate(sol.routes):
            color = colors[idx % len(colors)]
            pts = [r.vehicle.start_depot] + [c.pos for c in r.clients] + [r.vehicle.end_depot]
            if len(pts) >= 2:
                mpts = [tx(p, sm, offm) for p in pts]
                pygame.draw.lines(screen, color, False, mpts, width=1)

        vx0 = (map_rect.left - off_eff[0]) / (s_eff if s_eff != 0 else 1)
        vy0 = (map_rect.top - off_eff[1]) / (s_eff if s_eff != 0 else 1)
        vx1 = (map_rect.right - off_eff[0]) / (s_eff if s_eff != 0 else 1)
        vy1 = (map_rect.bottom - off_eff[1]) / (s_eff if s_eff != 0 else 1)
        vpts = [(vx0, vy0), (vx1, vy0), (vx1, vy1), (vx0, vy1)]
        vmini = [tx(p, sm, offm) for p in vpts]
        pygame.draw.lines(screen, (80, 80, 80), True, vmini, width=1)

        # Right panel
        if show_panel:
            screen.set_clip(panel_rect)

            panel_y = 10 - int(scroll_offset)
            title = title_font.render(
                "Rotas e Métricas (P: oculta | C: compacto | PgUp/PgDn: páginas)", True, (20, 20, 20)
            )
            screen.blit(title, (panel_rect.x + 10, panel_y))
            panel_y += (24 if compact else 28)

            line_h = (18 if compact else 20)
            detail_gap = (2 if compact else 4)

            total_dist = sum(r.distance() for r in sol.routes)
            tot_cap_v = sum(capacity_violation(r) for r in sol.routes)
            tot_tw_v = sum(time_window_violation(r) for r in sol.routes)
            tot_refr_v = sum(refrigeration_violation(r) for r in sol.routes)
            tot_mrt_v = sum(max_route_time_violation(r) for r in sol.routes)
            totals_line1 = f"Dist total: {total_dist:.1f}"
            if weights is not None:
                pen_w = (
                    weights.capacity * tot_cap_v
                    + weights.time_window * tot_tw_v
                    + weights.refrigeration * tot_refr_v
                    + weights.max_route_time * tot_mrt_v
                )
                totals_line2 = (
                    f"Pen (peso): {pen_w:.1f} = cap {weights.capacity}*{tot_cap_v:.1f} + "
                    f"tw {weights.time_window}*{tot_tw_v:.1f} + refr {weights.refrigeration}*{tot_refr_v:.1f} + "
                    f"mrt {weights.max_route_time}*{tot_mrt_v:.1f}"
                )
                totals_line3 = f"Custo total: {(total_dist + pen_w):.1f}"
            else:
                totals_line2 = (
                    f"Viol (soma): cap {tot_cap_v:.1f}, tw {tot_tw_v:.1f}, refr {tot_refr_v:.1f}, mrt {tot_mrt_v:.1f}"
                )
                totals_line3 = None
            t1 = font.render(totals_line1, True, (25, 25, 25))
            t2 = font.render(totals_line2, True, (60, 60, 60))
            screen.blit(t1, (panel_rect.x + 10, panel_y))
            panel_y += (line_h if not compact else 16)
            screen.blit(t2, (panel_rect.x + 10, panel_y))
            panel_y += (line_h + 6 if not compact else 18)
            if totals_line3 is not None:
                t3 = font.render(totals_line3, True, (25, 25, 25))
                screen.blit(t3, (panel_rect.x + 10, panel_y))
                panel_y += (line_h + 2 if not compact else 16)

            header_h = panel_y - (10 - int(scroll_offset))
            avail_h = panel_rect.height - header_h - 10
            per_route_h = line_h * 2 + detail_gap
            routes_per_page = max(1, avail_h // per_route_h) if avail_h > 0 else 5

            total_routes = len(sol.routes)
            total_pages = max(1, (total_routes + routes_per_page - 1) // routes_per_page)
            if page >= total_pages:
                page = total_pages - 1
            if page < 0:
                page = 0

            start_idx = page * routes_per_page
            end_idx = min(start_idx + routes_per_page, total_routes)
            routes_slice = list(enumerate(sol.routes))[start_idx:end_idx]

            content_max_width = 0
            for idx, r in routes_slice:
                color = colors[idx % len(colors)]
                demand = r.total_demand()
                cap = r.vehicle.capacity
                dist = r.distance()
                rtime = evaluate_route_time(r)
                sw = 12
                pygame.draw.rect(screen, color, pygame.Rect(panel_rect.x + 10, panel_y + 3, sw, sw))
                label = f"V{r.vehicle.id}: dem {demand}/{cap} | dist {dist:.1f} | time {rtime:.1f}"
                base_x = panel_rect.x + 10 + sw + 8
                maxw = panel_rect.width - (base_x - panel_rect.x) - 10
                wrapped = wrap_text(label, font, maxw)
                measure_line = " ".join(wrapped) if wrapped else label
                content_max_width = max(content_max_width, font.size(measure_line)[0])
                for sub in wrapped:
                    text = font.render(sub, True, (30, 30, 30))
                    screen.blit(text, (base_x - int(h_scroll_offset), panel_y))
                    panel_y += line_h

                cap_v = capacity_violation(r)
                tw_v = time_window_violation(r)
                refr_v = refrigeration_violation(r)
                mrt_v = max_route_time_violation(r)
                viol = f"viol: cap {cap_v:.1f}, tw {tw_v:.1f}, refr {refr_v:.1f}, mrt {mrt_v:.1f}"
                wrapped2 = wrap_text(viol, font, maxw)
                measure_line2 = " ".join(wrapped2) if wrapped2 else viol
                content_max_width = max(content_max_width, font.size(measure_line2)[0])
                for sub in wrapped2:
                    text2 = font.render(sub, True, (60, 60, 60))
                    screen.blit(text2, (base_x - int(h_scroll_offset), panel_y))
                    panel_y += line_h
                panel_y += detail_gap

            screen.set_clip(None)

            content_height = panel_y + int(scroll_offset)
            visible_h = panel_rect.height
            if content_height > visible_h:
                max_offset = max(0, content_height - visible_h)
                if scroll_offset < 0:
                    scroll_offset = 0
                elif scroll_offset > max_offset:
                    scroll_offset = max_offset

                track_w = 8
                track_rect = pygame.Rect(
                    panel_rect.right - track_w - 4, panel_rect.top + 4, track_w, panel_rect.height - 8
                )
                pygame.draw.rect(screen, (225, 225, 225), track_rect)
                pygame.draw.rect(screen, (200, 200, 200), track_rect, width=1)

                thumb_h = max(24, int(visible_h * (visible_h / content_height)))
                thumb_y = (
                    track_rect.y
                    + int((track_rect.height - thumb_h) * (scroll_offset / max_offset))
                    if max_offset > 0
                    else track_rect.y
                )
                thumb_rect = pygame.Rect(track_rect.x + 1, thumb_y, track_w - 2, thumb_h)
                pygame.draw.rect(screen, (160, 160, 160), thumb_rect)

            visible_w = panel_rect.width - (base_x - panel_rect.x) - 10 if 'base_x' in locals() else panel_rect.width - 20
            if content_max_width > visible_w:
                max_h_off = max(0, content_max_width - visible_w)
                if h_scroll_offset < 0:
                    h_scroll_offset = 0
                elif h_scroll_offset > max_h_off:
                    h_scroll_offset = max_h_off
                htrack_h = 8
                htrack_rect = pygame.Rect(panel_rect.x + 10, panel_rect.bottom - 34, panel_rect.width - 20, htrack_h)
                pygame.draw.rect(screen, (225, 225, 225), htrack_rect)
                pygame.draw.rect(screen, (200, 200, 200), htrack_rect, width=1)
                hthumb_w = max(24, int(htrack_rect.width * (visible_w / (content_max_width))))
                hthumb_x = (
                    htrack_rect.x
                    + int((htrack_rect.width - hthumb_w) * (h_scroll_offset / max_h_off))
                    if max_h_off > 0
                    else htrack_rect.x
                )
                hthumb_rect = pygame.Rect(hthumb_x, htrack_rect.y + 1, hthumb_w, htrack_h - 2)
                pygame.draw.rect(screen, (160, 160, 160), hthumb_rect)

            footer = font.render(f"Página {page + 1}/{total_pages}", True, (90, 90, 90))
            screen.blit(footer, (panel_rect.x + 10, panel_rect.bottom - 22))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
