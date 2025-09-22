from __future__ import annotations

from typing import List
from vrp_models import Solution, Route, Vehicle, Client


def repair_solution(solution: Solution, vehicles: List[Vehicle]) -> Solution:
    """Simple greedy repair:
    - If a route lacks refrigeration for required clients, try moving those clients to a refrigerated vehicle route.
    - If capacity exceeded, shift last clients to next vehicle with remaining capacity.
    Note: This is a basic heuristic to illustrate the migration; it can be improved substantially.
    """
    # Ensure there's at least one refrigerated route if needed
    refr_routes = [r for r in solution.routes if r.vehicle.has_refrigeration]
    non_refr_routes = [r for r in solution.routes if not r.vehicle.has_refrigeration]

    # Move refrigerated-required clients
    for r in list(non_refr_routes):
        i = 0
        while i < len(r.clients):
            c = r.clients[i]
            if c.requires_refrigeration:
                # find a refr route with capacity room
                moved = False
                for rr in solution.routes:
                    if not rr.vehicle.has_refrigeration:
                        continue
                    if rr.vehicle.capacity - sum(x.demand for x in rr.clients) >= c.demand:
                        rr.clients.append(c)
                        del r.clients[i]
                        moved = True
                        break
                if not moved:
                    i += 1
            else:
                i += 1

    # Capacity repair: try to push tail clients forward to later routes/vehicles
    for idx, r in enumerate(solution.routes):
        while sum(x.demand for x in r.clients) > r.vehicle.capacity and r.clients:
            c = r.clients.pop()  # remove from end
            placed = False
            # look ahead for a route with space
            for j in range(idx + 1, len(solution.routes)):
                rr = solution.routes[j]
                if rr.vehicle.capacity - sum(x.demand for x in rr.clients) >= c.demand:
                    rr.clients.append(c)
                    placed = True
                    break
            # if not placed, try to create a new route if there are spare vehicles
            if not placed:
                remaining = [v for v in vehicles if v not in [rt.vehicle for rt in solution.routes]]
                if remaining:
                    new_r = Route(vehicle=remaining[0], clients=[c])
                    solution.routes.append(new_r)
                    placed = True
            # if still not placed, put back (will incur penalty)
            if not placed:
                r.clients.append(c)
                break

    return solution
