<!--
  Report section 10: individual contributions and references.
  Author: IsuruRaveen20 <isururaveen4520@gmail.com>
  Created: 2026-10-12
-->
# 10. Individual contributions

| Area | Member 1 (M1) | Member 2 (M2) |

|---|---|---|
| Problem and data | Dataset curation, OSM cross-check, correction of errors and duplicates (`src/validate_against_osm.py`, `src/tsp/data.py`, `data/`) | Review of the cleaned data and its limitations |
| Exact method | Held–Karp, 1-tree bound, brute-force verification (`src/tsp/exact.py`) | Review and testing of the exact solver |
| Heuristics | – | NN, 2-opt, Or-opt, multi-start, ILS (`src/tsp/heuristics.py`) and unit tests |
| Experiments and figures | Scalability study design | Experiment runner, repeated runs, plots (`src/run_experiments.py`, `src/make_plots.py`) |
| Report | Sections 1–4 (problem, data, formulation, exact method) | Sections 5–9 (heuristics, experiments, results, discussion, future work) |
| Video | Parts on problem, data, formulation and exact method | Parts on heuristics, results, discussion and conclusion |

The commit history in the repository records the work: commit messages are prefixed `M1:` or `M2:`. Both members can explain the whole code base.

# References

1. Dantzig, G., Fulkerson, R., Johnson, S. (1954). Solution of a large-scale traveling-salesman problem. *Operations Research* 2(4), 393–410.
2. Miller, C. E., Tucker, A. W., Zemlin, R. A. (1960). Integer programming formulation of traveling salesman problems. *Journal of the ACM* 7(4), 326–329.
3. Held, M., Karp, R. M. (1962). A dynamic programming approach to sequencing problems. *Journal of the SIAM* 10(1), 196–210.
4. Held, M., Karp, R. M. (1970). The traveling-salesman problem and minimum spanning trees. *Operations Research* 18(6), 1138–1162.
5. Croes, G. A. (1958). A method for solving traveling-salesman problems. *Operations Research* 6(6), 791–812.
6. Or, I. (1976). *Traveling salesman-type combinatorial problems and their relation to the logistics of regional blood banking*. PhD thesis, Northwestern University.
7. Lourenço, H. R., Martin, O. C., Stützle, T. (2003). Iterated local search. In *Handbook of Metaheuristics*, Springer, 320–353.
8. OpenStreetMap contributors. OpenStreetMap data, © OpenStreetMap contributors, ODbL 1.0. https://www.openstreetmap.org/copyright (Nominatim geocoder, retrieved 14 October 2026).
