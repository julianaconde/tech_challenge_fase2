from __future__ import annotations

import random
import time
from typing import List, Optional
import argparse

from vrp_models import Client, Vehicle, Solution
from vrp_split import split_giant_tour
from vrp_repair import repair_solution
from vrp_fitness import (
    fitness, PenaltyWeights,
    evaluate_route_time,
    capacity_violation,
    time_window_violation,
    refrigeration_violation,
    max_route_time_violation,
)
from vrp_mutations import mutate_vrp
from genetic_algorithm import order_crossover
from vrp_io import load_vrp_from_json
from vrp_visualize import draw_solution


def generate_random_clients(n: int, seed: int = 0) -> List[Client]:
    random.seed(seed)
    out: List[Client] = []
    for i in range(1, n + 1):
        x, y = random.randint(0, 600), random.randint(0, 400)
        demand = random.randint(1, 4)
        service = random.uniform(0.5, 2.0)
        tw_start, tw_end = (None, None)
        if i % 4 == 0:
            tw_start = random.uniform(10.0, 50.0)
            tw_end = tw_start + random.uniform(10.0, 30.0)
        requires_refrigeration = (i % 6 == 0)
        out.append(Client(id=i, x=x, y=y, demand=demand, service_time=service, tw_start=tw_start, tw_end=tw_end, requires_refrigeration=requires_refrigeration))
    return out


def build_vehicles() -> List[Vehicle]:
    return [
        Vehicle(id=1, capacity=16, has_refrigeration=True, max_route_time=400.0, start_depot=(300, 200), end_depot=(300, 200)),
        Vehicle(id=2, capacity=14, has_refrigeration=False, max_route_time=400.0, start_depot=(300, 200), end_depot=(300, 200)),
    ]


def evaluate_tour(tour: List[Client], vehicles: List[Vehicle], w: PenaltyWeights) -> float:
    sol = split_giant_tour(tour, vehicles)
    sol = repair_solution(sol, vehicles)
    return fitness(sol, w)


def run_ga(
    pop_size: int = 50,
    n_gens: int = 200,
    mutation_prob: float = 0.4,
    seed: int = 1,
    clients: Optional[List[Client]] = None,
    vehicles: Optional[List[Vehicle]] = None,
    weights_capacity: float = 1000.0,
    weights_tw: float = 500.0,
    weights_refrig: float = 5000.0,
    weights_mrt: float = 200.0,
):
    random.seed(seed)
    clients = clients if clients is not None else generate_random_clients(18, seed)
    vehicles = vehicles if vehicles is not None else build_vehicles()
    w = PenaltyWeights(capacity=weights_capacity, time_window=weights_tw, refrigeration=weights_refrig, max_route_time=weights_mrt)

    # initialize population of giant tours
    base = clients[:]
    population: List[List[Client]] = [random.sample(base, len(base)) for _ in range(pop_size)]

    # evaluate
    def fit(ind: List[Client]) -> float:
        return evaluate_tour(ind, vehicles, w)

    start = time.perf_counter()
    best = None
    best_f = float('inf')

    for g in range(1, n_gens + 1):
        fitnesses = [fit(ind) for ind in population]
        paired = list(zip(population, fitnesses))
        paired.sort(key=lambda x: x[1])
        population = [p for p, _ in paired]
        fitnesses = [f for _, f in paired]

        if fitnesses[0] < best_f:
            best_f = fitnesses[0]
            best = population[0][:]

        print(f"Gen {g}: best = {best_f:.2f}")

        new_pop: List[List[Client]] = [population[0]]  # elitism
        # fitness-proportional selection (invert for minimization)
        inv = [1.0 / (f + 1e-9) for f in fitnesses]
        for _ in range(pop_size - 1):
            p1, p2 = random.choices(population, weights=inv, k=2)
            child = order_crossover(p1, p2)
            child = mutate_vrp(child, mutation_prob)
            new_pop.append(child)
        population = new_pop

    total = time.perf_counter() - start
    print(f"Tempo total: {total:.2f}s | Melhor fitness: {best_f:.2f}")

    # return best solution materialized
    sol = split_giant_tour(best, vehicles)
    sol = repair_solution(sol, vehicles)
    return sol


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VRP GA runner")
    parser.add_argument("--data", type=str, default=None, help="Caminho para JSON com clients/vehicles (ex.: sample_vrp.json)")
    parser.add_argument("--pop-size", type=int, default=50, help="Tamanho da população")
    parser.add_argument("--gens", type=int, default=200, help="Número de gerações")
    parser.add_argument("--mutation", type=float, default=0.4, help="Probabilidade de mutação")
    parser.add_argument("--seed", type=int, default=1, help="Seed aleatória")
    parser.add_argument("--visualize", action="store_true", help="Exibir visualização Pygame ao final")
    parser.add_argument("--w-cap", type=float, default=1000.0, help="Peso penalidade de capacidade")
    parser.add_argument("--w-tw", type=float, default=500.0, help="Peso penalidade de janela de tempo")
    parser.add_argument("--w-refrig", type=float, default=5000.0, help="Peso penalidade de refrigeração")
    parser.add_argument("--w-mrt", type=float, default=200.0, help="Peso penalidade de tempo máximo de rota")
    args = parser.parse_args()

    if args.data:
        cls, vs = load_vrp_from_json(args.data)
    else:
        cls, vs = None, None

    sol = run_ga(
        pop_size=args.pop_size,
        n_gens=args.gens,
        mutation_prob=args.mutation,
        seed=args.seed,
        clients=cls,
        vehicles=vs,
        weights_capacity=args.w_cap,
        weights_tw=args.w_tw,
        weights_refrig=args.w_refrig,
        weights_mrt=args.w_mrt,
    )
    if args.visualize:
        w = PenaltyWeights(
            capacity=args.w_cap,
            time_window=args.w_tw,
            refrigeration=args.w_refrig,
            max_route_time=args.w_mrt,
        )
        draw_solution(sol, weights=w)

    # Exportação automática dos dados das rotas para relatório
    def exportar_rotas_txt(sol, arquivo="rotas_otimizadas.txt"):
        with open(arquivo, "w") as f:
            f.write("Relatório de Rotas Otimizadas\n\n")
            for idx, route in enumerate(sol.routes):
                f.write(f"Rota {idx+1}:\n")
                f.write(f"  Veículo: {route.vehicle.id}\n")
                f.write(f"  Clientes: {[c.id for c in route.clients]}\n")
                f.write(f"  Demanda total: {route.total_demand()}\n")
                f.write(f"  Distância: {route.distance():.2f}\n")
                f.write(f"  Tempo estimado: {evaluate_route_time(route):.2f}\n")
                f.write(f"  Penalidades: cap={capacity_violation(route):.2f}, tw={time_window_violation(route):.2f}, refrig={refrigeration_violation(route):.2f}, mrt={max_route_time_violation(route):.2f}\n\n")
            f.write("\nResumo:\n")
            total_dist = sum(r.distance() for r in sol.routes)
            tot_cap_v = sum(capacity_violation(r) for r in sol.routes)
            tot_tw_v = sum(time_window_violation(r) for r in sol.routes)
            tot_refr_v = sum(refrigeration_violation(r) for r in sol.routes)
            tot_mrt_v = sum(max_route_time_violation(r) for r in sol.routes)
            f.write(f"Distância total: {total_dist:.2f}\n")
            f.write(f"Violação total: cap={tot_cap_v:.2f}, tw={tot_tw_v:.2f}, refrig={tot_refr_v:.2f}, mrt={tot_mrt_v:.2f}\n")

    exportar_rotas_txt(sol)
