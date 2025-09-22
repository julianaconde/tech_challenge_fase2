from __future__ import annotations

from typing import List, Optional
from dataclasses import dataclass
from vrp_models import Solution, Route, euclidean


@dataclass
class PenaltyWeights:
    capacity: float = 1000.0
    time_window: float = 1000.0
    refrigeration: float = 5000.0
    max_route_time: float = 1000.0


def evaluate_route_time(route: Route) -> float:
    """Compute travel + service time along the route (no waiting model)."""
    t = 0.0
    if not route.clients:
        return 0.0
    # depot to first
    t += euclidean(route.vehicle.start_depot, route.clients[0].pos)
    # service + travel
    for a, b in zip(route.clients[:-1], route.clients[1:]):
        t += a.service_time
        t += euclidean(a.pos, b.pos)
    # last service + back to depot
    t += route.clients[-1].service_time
    t += euclidean(route.clients[-1].pos, route.vehicle.end_depot)
    return t


def time_window_violation(route: Route) -> float:
    """Return total time window violation (positive lateness) without waiting model.
    If arrival < tw_start, assume waiting allowed (no penalty)."""
    if not route.clients:
        return 0.0
    t = euclidean(route.vehicle.start_depot, route.clients[0].pos)
    violation = 0.0
    for a, b in zip(route.clients[:-1], route.clients[1:]):
        # arrive at a
        if a.tw_end is not None:
            # if too late, penalize only lateness
            violation += max(0.0, t - a.tw_end)
        # serve a (if arrive earlier than start, we assume wait -> no penalty)
        start_time = max(t, a.tw_start) if a.tw_start is not None else t
        t = start_time + a.service_time + euclidean(a.pos, b.pos)
    # last client
    last = route.clients[-1]
    if last.tw_end is not None:
        violation += max(0.0, t - last.tw_end)
    # serve last and go back (no TW on depot)
    return violation


def refrigeration_violation(route: Route) -> float:
    """Penalty if route contains refrigerated-required clients but vehicle lacks it."""
    requires = any(c.requires_refrigeration for c in route.clients)
    if requires and not route.vehicle.has_refrigeration:
        return 1.0  # single unit; weight scales it
    return 0.0


def capacity_violation(route: Route) -> float:
    overload = max(0.0, route.total_demand() - route.vehicle.capacity)
    return overload


def max_route_time_violation(route: Route) -> float:
    if route.vehicle.max_route_time is None:
        return 0.0
    actual = evaluate_route_time(route)
    return max(0.0, actual - route.vehicle.max_route_time)


def fitness(solution: Solution, weights: Optional[PenaltyWeights] = None) -> float:
    if weights is None:
        weights = PenaltyWeights()
    cost = 0.0
    for r in solution.routes:
        dist = r.distance()
        cap = capacity_violation(r)
        tw = time_window_violation(r)
        refr = refrigeration_violation(r)
        mrt = max_route_time_violation(r)
        cost += dist + (weights.capacity * cap) + (weights.time_window * tw) + (weights.refrigeration * refr) + (weights.max_route_time * mrt)
    return cost
