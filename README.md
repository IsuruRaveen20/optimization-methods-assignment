# Colombo Metro Delivery Route Optimisation (TSP, 100 nodes)

<!--
  Author: IsuruRaveen20 <isururaveen4520@gmail.com>
  Created: 2026-10-11
-->

Optimization Methods – Programming Assignment (group of 2). One vehicle starts at Colombo Fort,
visits 99 localities in the Colombo / Gampaha / Kalutara corridor exactly once and returns.
We compare an **exact** method (Held–Karp dynamic programming) with **heuristics**
(Nearest Neighbour, 2-opt, 2-opt + Or-opt, multi-start 2-opt, iterated local search).

## Key results
| | |
|---|---|
| Exact Held–Karp | optimal up to 20 nodes (5 s at n = 20); runtime ×5 per +2 nodes |
| Iterated local search | matches the optimum on all 35 random instances of 8–20 nodes |
| Full 100-node instance | best tour 334.96 km (NN 432.72 km, 2-opt 355.09 km); 1-tree lower bound 269.44 km |

## Repository layout
```
data/      colombo_delivery_locations.csv  input (100 nodes)      distance_matrix_km.csv  derived Haversine matrix
           osm_validation.csv              OpenStreetMap cross-check      DATASET_NOTES.txt  provenance and corrections
src/tsp/   data.py (loading, Haversine, validation)  exact.py (Held-Karp, 1-tree bound)  heuristics.py
src/       run_experiments.py  make_plots.py  validate_data.py  build_matrix.py  validate_against_osm.py
tests/     test_solvers.py     unit tests (Held-Karp vs brute force, feasibility, lower bound, dataset checks)
results/   CSV results, best_route.txt, best_tour.csv, figures/
docs/      code_appendix.txt (all source code as plain text), build_code_appendix.py
```

## Run
Python 3.9+. The solvers use only the standard library; plots need `matplotlib`.
```bash
pip install -r requirements.txt           # matplotlib only
python -m unittest discover -s tests      # unit tests
python src/validate_data.py               # dataset quality checks
python src/run_experiments.py             # all experiments, ~1 min (--quick for a smoke test)
python src/make_plots.py                  # figures in results/figures
python docs/build_code_appendix.py        # rebuilds docs/code_appendix.txt
```

## Attribution
© OpenStreetMap contributors, ODbL 1.0 – https://www.openstreetmap.org/copyright
