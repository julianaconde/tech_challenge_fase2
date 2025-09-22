from __future__ import annotations

import random
from typing import List
from vrp_models import Client, Vehicle, Solution
from vrp_split import split_giant_tour
from vrp_repair import repair_solution
from vrp_fitness import fitness, PenaltyWeights


def build_demo(n_clients: int = 12, seed: int = 42) -> tuple[List[Client], List[Vehicle]]:
    random.seed(seed)
    clients: List[Client] = []
    for i in range(1, n_clients + 1):
        x, y = random.randint(0, 400), random.randint(0, 300)
        demand = random.randint(1, 5)
        service = random.uniform(1.0, 3.0)
        # add time windows to ~1/3 of clients
        if i % 3 == 0:
            tw_start = random.uniform(10.0, 50.0)
            tw_end = tw_start + random.uniform(10.0, 30.0)
        else:
            tw_start = None
            tw_end = None
        requires_refrigeration = (i % 5 == 0)
        clients.append(
            Client(
                id=i,
                x=x,
                y=y,
                demand=demand,
                service_time=service,
                tw_start=tw_start,
                tw_end=tw_end,
                requires_refrigeration=requires_refrigeration,
            )
        )

    # two vehicles: one refrigerated, one not
    vehicles = [
        Vehicle(id=1, capacity=12, max_route_time=300.0, has_refrigeration=True, start_depot=(200, 150), end_depot=(200, 150)),
        Vehicle(id=2, capacity=10, max_route_time=300.0, has_refrigeration=False, start_depot=(200, 150), end_depot=(200, 150)),
    ]
    return clients, vehicles


def main():
    clients, vehicles = build_demo()
    # create a random giant tour
    tour = clients[:]
    random.shuffle(tour)

    sol = split_giant_tour(tour, vehicles)
    # try repair
    sol = repair_solution(sol, vehicles)

    w = PenaltyWeights(capacity=1000.0, time_window=500.0, refrigeration=5000.0, max_route_time=200.0)
    f = fitness(sol, w)

    print("Rotas geradas:")
    for r in sol.routes:
        route_ids = [c.id for c in r.clients]
        print(f"  Veículo {r.vehicle.id} (cap={r.vehicle.capacity}, refrig={r.vehicle.has_refrigeration}) -> clientes {route_ids}; demanda={sum(c.demand for c in r.clients)}; dist={r.distance():.1f}")
    print(f"Fitness com penalidades: {f:.2f}")


if __name__ == "__main__":
    main()
