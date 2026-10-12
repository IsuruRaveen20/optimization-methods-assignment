<!--
  Report sections 5-9: heuristics, experimental design, results, discussion, future work.
  Author: sharmilak99 <sharmilakavi822@gmail.com>
  Created: 2026-10-12
-->
# 5. Heuristic methods

All heuristics are in `src/tsp/heuristics.py`. A tour is a list of node ids that starts and ends at the depot.


1. **Nearest Neighbour (NN)** – start at the depot and repeatedly drive to the closest unvisited locality. $O(n^2)$, very fast, but greedy: early choices leave long return trips at the end.
2. **2-opt** – repeatedly remove two edges and reconnect the tour by reversing the segment between them whenever this shortens the tour (Croes, 1958). It removes crossing edges. Moves are evaluated from four distances only, so one pass costs $O(n^2)$.
3. **2-opt + Or-opt** – additionally move a segment of 1–3 consecutive customers (also reversed) to a cheaper place in the tour (Or, 1976). The two neighbourhoods are alternated until neither improves the tour.
4. **Multi-start 2-opt** – run NN from 30 different random first customers, improve each with 2-opt and keep the best (diversification).
5. **Iterated local search (ILS)** – start from the local optimum of method 3, then repeat 300 times: apply a random *double-bridge* perturbation (cut the tour into three pieces and reorder them), re-optimise with 2-opt + Or-opt and keep the result only if the tour became shorter (Lourenço et al., 2003). This lets the search escape local optima that 2-opt and Or-opt cannot leave.

**Why these methods.** NN is the standard baseline that every improvement is measured against. 2-opt and Or-opt are the best-known simple local searches for the TSP, and they are complementary: 2-opt repairs crossings, Or-opt repairs badly placed single stops. Multi-start and ILS are two ways of spending extra time to escape local optima, so the comparison also shows what additional runtime buys. Randomised methods use fixed seeds, so every number in this report can be reproduced.

# 6. Experimental design

**Study A – quality against the proven optimum (scalability study).** For each size $n\in\{8,10,12,14,16,18,20\}$ (depot included) we draw 5 random subsets of the 100 localities (fixed seeds), solve each with Held–Karp, and run all heuristics on the same subset (to keep these many runs cheap, multi-start uses 10 starts and ILS 50 iterations here). We record the optimal length, the runtime and the percentage gap of each heuristic to the optimum.

**Study B – full instance.** All five heuristics run on the complete 100-node instance. Deterministic methods are timed over 5 repeats; randomised methods use 5 different seeds. We report best, mean and standard deviation of the tour length, the median runtime, the gap to the best tour found, and the gap to the 1-tree lower bound. Every returned tour is checked for **feasibility** (starts and ends at the depot, every node exactly once).

Code runs in pure Python 3 (standard library) on one machine; absolute runtimes will differ on another computer, but the ratios are meaningful. Everything is reproduced by `python src/run_experiments.py`.

# 7. Results

## 7.1 Heuristics against the exact optimum

Table 1 gives the mean gap to the optimum over 5 subsets per size. Figure 1 shows runtimes and Figure 2 the gaps.

{{TABLE_SCALABILITY}}

Table: Mean gap (%) to the Held–Karp optimum; exact runtime is the median over 5 subsets.

![Median runtime against instance size (log scale).](results/figures/scalability_runtime.png){width=72%}

![Mean gap to the optimum against instance size.](results/figures/scalability_gap.png){width=72%}

## 7.2 Full 100-node instance

{{TABLE_FULL}}

Table: Results on the full instance (5 runs per method). Gap columns refer to the best tour of each method.

![Best tour length and median runtime per method.](results/figures/full_instance_comparison.png){width=72%}

![Nearest Neighbour tour (left) and best tour found (right).](results/figures/route_maps.png){width=100%}

# 8. Discussion

**Solution quality.** Nearest Neighbour is {{NN_SMALL_RANGE}}% above the optimum on the small instances and {{NN_VS_BEST}}% above the best known tour on the full instance; its route in Figure 4 (left) has long crossing legs back to the depot area. 2-opt cuts the gap to {{TWOOPT_RANGE}}% on the small instances and the full-instance length from {{NN_KM}} km to {{TWOOPT_KM}} km. Adding Or-opt reaches {{OROPT_KM}} km. Multi-start gives {{MS_KM}} km and ILS gives {{ILS_KM}} km. **ILS found the proven optimum on all 35 small instances** (gap 0.00% for every size), and on the full instance all five seeds ended on the same tour length, which suggests it is very close to optimal, although for 100 nodes this is evidence, not proof.

**What the lower bound says.** The 1-tree bound is {{LB_KM}} km, so the best tour is at most {{LB_GAP}}% above the optimum. This bound is known to be loose; we state it because it is the only *provable* statement available at this size, and we do not claim that the real gap is anywhere near {{LB_GAP}}%. The small-instance study is the better indicator of heuristic quality.

**Runtime and scalability.** The exact method multiplies its runtime by about 5 for every two extra nodes (0.3 ms at $n=8$, 8 s at $n=20$). Extrapolating, $n=30$ would take roughly eight hours (extrapolated from our measurements) and the DP table would not fit in memory; $n=100$ is out of reach by many orders of magnitude. The heuristics grow gently: at $n=100$ NN takes {{NN_T}}, 2-opt + Or-opt {{OROPT_T}} and ILS {{ILS_T}} s. ILS is about {{ILS_SLOWDOWN}} times slower than 2-opt + Or-opt but buys a {{ILS_VS_OROPT}}% shorter route. For a daily plan that is a good trade; for a real-time re-route the faster local search may be preferred.

**Feasibility.** All tours were verified feasible. The exact method guarantees optimality only up to 20 nodes; for the heuristics feasibility is guaranteed by construction and re-checked in every run.

**Trade-offs in one sentence.** The exact method gives certainty but stops being usable at about 25 nodes; 2-opt + Or-opt is nearly free and typically within a few percent; ILS spends seconds to reach what appears to be the optimum.

# 9. Limitations and future work

* **Distances.** Haversine distance underestimates road distance (and the ranking of routes may change). Replace it by road-network distances from OSRM, GraphHopper or OSMnx and keep a dated OSM snapshot.
* **Data.** Coordinates are approximate locality centres; OSM validation reduced errors but a real deployment needs geocoded customer addresses.
* **Model.** One vehicle, no demand, capacity, service time, time windows or traffic. The natural extensions are the capacitated VRP and VRP with time windows; the heuristics extend with route-splitting and Or-opt/relocate moves between routes, and the ILP gains vehicle-load and time variables.
* **Exact method.** An ILP with sub-tour cuts (branch-and-cut, e.g. via PuLP/OR-Tools or Concorde) would give the true optimum or a much tighter bound for 100 nodes; a Held–Karp subgradient bound would replace our weak 1-tree bound.
* **Experiments.** Runtimes come from one machine and one language; ILS parameters (300 iterations, double-bridge) were not tuned; a stronger metaheuristic (Lin–Kernighan, simulated annealing, genetic algorithm) could be compared.
