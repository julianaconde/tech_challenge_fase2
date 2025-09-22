# TSP/VRP Solver using Genetic Algorithm

This repository contains a Python implementation of a Traveling Salesman Problem (TSP) solver using a Genetic Algorithm (GA). The TSP is a classic problem in the field of combinatorial optimization, where the goal is to find the shortest possible route that visits a set of given cities exactly once and returns to the original city.

## Overview

The TSP solver employs a Genetic Algorithm to iteratively evolve a population of candidate solutions towards an optimal or near-optimal solution. The GA operates by mimicking the process of natural selection, where individuals with higher fitness (i.e., shorter route distance) are more likely to survive and produce offspring.

## Files

- **genetic_algorithm.py**: Contains the implementation of the Genetic Algorithm, including functions for generating random populations, calculating fitness, performing crossover and mutation operations, and sorting populations based on fitness.
- **tsp.py**: Implements the main TSP solver using Pygame for visualization. It initializes the problem, creates the initial population, and iteratively evolves the population while visualizing the best solution found so far.
- **draw_functions.py**: Provides functions for drawing cities, paths, and plots using Pygame.

### VRP (Vehicle Routing Problem) – migration scaffolding
- **vrp_models.py**: Data structures for VRP (`Client`, `Vehicle`, `Route`, `Solution`).
- **vrp_fitness.py**: Fitness with penalties (capacity, time window, refrigeration, max route time).
- **vrp_split.py**: Greedy split operator (giant tour → routes).
- **vrp_repair.py**: Simple repair heuristic (refrigeration/capacity).
- **vrp_mutations.py**: VRP mutations on giant tour (swap/relocate/2-opt).
- **vrp_ga.py**: Minimal GA that evolves giant tours and evaluates via split→repair→fitness.
- **vrp_visualize.py**: Pygame viewer for VRP solutions (routes per vehicle).
- **demo_vrp.py**: Small demo building a random instance, splitting, repairing and scoring.
- **sample_vrp.json**: Example JSON with clients/vehicles.

## Usage (TSP)

To run the TSP solver, execute the `tsp.py` script using Python. The solver allows you to choose between different problem instances:

- Randomly generated cities
- Default predefined problems with 10, 12, or 15 cities
- `att48` benchmark dataset (uncomment relevant code in `tsp.py`)

You can customize parameters such as population size, number of generations, and mutation probability directly in the `tsp.py` script.

## Usage (VRP)
- Run the small demo:
```bash
python demo_vrp.py
```

- Run the GA for VRP (random instance):
```bash
python vrp_ga.py
```

- Visualize a computed solution in Pygame (example):
```python
from vrp_ga import run_ga
from vrp_visualize import draw_solution

sol = run_ga(pop_size=50, n_gens=200, mutation_prob=0.4)
draw_solution(sol)
```

- Load from JSON (example file `sample_vrp.json`):
```python
from vrp_io import load_vrp_from_json
clients, vehicles = load_vrp_from_json("sample_vrp.json")
```

### CLI options (VRP GA)

You can load a dataset and configure penalty weights via command line:

```bash
python vrp_ga.py \
	--data sample_vrp.json \
	--gens 100 \
	--pop-size 80 \
	--mutation 0.4 \
	--w-cap 1000.0 \
	--w-tw 500.0 \
	--w-refrig 5000.0 \
	--w-mrt 200.0 \
	--visualize
```

- `--w-cap`: weight for capacity violation (units of demand over capacity)
- `--w-tw`: weight for time window lateness (time units over `tw_end`)
- `--w-refrig`: weight if a route with refrigerated clients uses a non-refrigerated vehicle
- `--w-mrt`: weight for exceeding the maximum route time of a vehicle

The viewer overlays per-route metrics: demand/capacity, total distance, and estimated route time.

## Dependencies

- Python 3.x
- Pygame (for visualization)
 - Matplotlib (for TSP plot)

Ensure Pygame is installed before running the solver. You can install Pygame using pip:

```bash
pip install pygame matplotlib
```

## Acknowledgments

This TSP solver was developed as a learning project and draws inspiration from various online resources and academic materials on Genetic Algorithms and the Traveling Salesman Problem. Special thanks to the authors of those resources for sharing their knowledge.

## License

This project is licensed under the [MIT License](LICENSE).

---

Feel free to contribute to this repository by providing enhancements, bug fixes, or additional features. If you encounter any issues or have suggestions for improvements, please open an issue on the repository. Happy solving!