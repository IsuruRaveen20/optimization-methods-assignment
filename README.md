# Colombo Metro Delivery Route Optimisation (TSP, 100 nodes)

Optimization Methods – Programming Assignment (group of 2). One vehicle starts at Colombo Fort,
visits 99 localities in the Colombo / Gampaha / Kalutara corridor exactly once and returns.
We compare an **exact** method (Held–Karp dynamic programming) with **heuristics**
(Nearest Neighbour, 2-opt, 2-opt + Or-opt, multi-start 2-opt, iterated local search).

## Key results (see `docs/final_report.pdf`)
| | |
|---|---|
| Exact Held–Karp | optimal up to 20 nodes (8 s at n = 20); runtime ×5 per +2 nodes |
| Iterated local search | matches the optimum on all 35 random instances of 8–20 nodes |
| Full 100-node instance | best tour 334.96 km (NN 432.72 km, 2-opt 355.09 km); 1-tree lower bound 269.44 km |

## Repository layout
```
data/      colombo_delivery_locations.csv  input (100 nodes)      distance_matrix_km.csv  derived Haversine matrix
           osm_validation.csv              OpenStreetMap cross-check      DATASET_NOTES.txt  provenance and corrections
src/tsp/   data.py (loading, Haversine, validation)  exact.py (Held-Karp, 1-tree bound)  heuristics.py
src/       run_experiments.py  make_plots.py  validate_data.py  build_matrix.py  validate_against_osm.py  fetch_osm_pois.py
tests/     test_solvers.py     unit tests (Held-Karp vs brute force, feasibility, lower bound, dataset checks)
results/   CSV results, best_route.txt, best_tour.csv, figures/
docs/      final_report.pdf, code_appendix.txt, report/ (Markdown sources), build_report.py, build_code_appendix.py,
           15_minute_video_outline.txt
```

## Run
Python 3.9+. The solvers use only the standard library; plots need `matplotlib`; the PDF needs `pandoc` + `xelatex`.
```bash
pip install -r requirements.txt           # matplotlib only
python -m unittest discover -s tests      # unit tests
python src/validate_data.py               # dataset quality checks
python src/run_experiments.py             # all experiments, ~75 s  (--quick for a smoke test)
python src/make_plots.py                  # figures in results/figures
python docs/build_report.py               # rebuilds docs/final_report.pdf from results/*.csv
python docs/build_code_appendix.py        # rebuilds docs/code_appendix.txt
python check_submission.py                # lists placeholders still to fill before upload
```

## Data and limitations
* Distances are straight-line (Haversine) distances, not road distances.
* Coordinates are approximate locality centres. Every locality was cross-checked against OpenStreetMap
  (retrieved 2026-10-14; median offset 0.75 km); errors found were corrected – details in `data/DATASET_NOTES.txt`.
* Single vehicle; no capacities, time windows or traffic. See Section 9 of the report for future work.

## Commit convention
Commit messages are prefixed `M1:` or `M2:` to show which group member made the change
(see the "Individual contributions" section of the report).

## Attribution
© OpenStreetMap contributors, ODbL 1.0 – https://www.openstreetmap.org/copyright
