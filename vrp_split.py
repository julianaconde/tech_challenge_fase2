from __future__ import annotations

from typing import List
from vrp_models import Client, Vehicle, Route, Solution


def split_giant_tour(
    tour: List[Client],
    vehicles: List[Vehicle],
) -> Solution:
    """Greedy split of a giant tour into routes limited by vehicle capacity.
    Assumes homogeneous capacity logic; uses vehicles in given order.
    """
    routes: List[Route] = []
    v_idx = 0
    i = 0
    while i < len(tour) and v_idx < len(vehicles):
        v = vehicles[v_idx]
        r = Route(vehicle=v)
        load = 0.0
        while i < len(tour):
            c = tour[i]
            if load + c.demand <= v.capacity:
                r.clients.append(c)
                load += c.demand
                i += 1
            else:
                break
        routes.append(r)
        v_idx += 1
    # leftover clients (if any) go into last route incurring capacity violations
    while i < len(tour):
        if not routes:
            routes.append(Route(vehicle=vehicles[0]))
        routes[-1].clients.append(tour[i])
        i += 1
    return Solution(routes=routes)
