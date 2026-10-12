<!--
  Report sections 1-4: problem, data quality, MTZ formulation, Held-Karp.
  Author: IsuruRaveen20 <isururaveen4520@gmail.com>
  Created: 2026-10-11
-->
**Group members:** {{MEMBER1}} · {{MEMBER2}}

**Code, data and commit history:** {{GITHUB_URL}}

# 1. Problem selection and context


A courier based at Colombo Fort must deliver parcels to 99 localities spread over the Colombo, Gampaha and Kalutara districts, from Kochchikade in the north to Kalutara in the south and Avissawella in the east. One vehicle starts at the depot, visits every locality exactly once and returns. The objective is to minimise the total distance driven, which is the classic **Travelling Salesperson Problem (TSP)**.

The problem is realistic because every courier, field-service and waste-collection round has this structure, and it is non-trivial because it is NP-hard: with $n$ stops there are $(n-1)!/2$ distinct tours (about $10^{155}$ for $n=100$), so enumeration is impossible and the quality of the solution method matters. It also lets us study the trade-off the assignment asks about: an exact method that gives a proof of optimality but scales exponentially, against heuristics that scale well but give no guarantee. Real deployments would add capacities and time windows; Section 9 explains how the model extends to those.

# 2. Data description

The instance has **100 nodes**: node 0 is the depot (Colombo Fort) and nodes 1–99 are named localities. The file `data/colombo_delivery_locations.csv` stores node id, name, latitude and longitude. The distance between two nodes is the great-circle (Haversine) distance in kilometres, so the cost matrix is symmetric and satisfies the triangle inequality. `data/distance_matrix_km.csv` is the derived matrix; the solvers recompute it from the locations file and a test checks that the two agree.

**Provenance and quality checks.** The locality names are real places, but the coordinates are approximate representative centre points curated by the team, not customer addresses. Because real-world data is preferred, every name was cross-checked against OpenStreetMap (Nominatim, retrieved 14 October 2026; script `src/validate_against_osm.py`, output `data/osm_validation.csv`). Of the 102 names in the first version of the file, 95 returned a match; the median offset between our point and OSM was 0.75 km and 77 of the 95 were within 2 km. The check found real errors, which were fixed:

* Bandaragama was 21.7 km from its OSM position and Ganemulla 5.2 km; both were corrected.
* Pannipitiya Junction and Moratuwa Town had *exactly* the same coordinates as Pannipitiya and Moratuwa, adding zero-distance nodes, so they were removed (102 → 100 nodes).
* "Kochchikade" was renamed "Kochchikade (Negombo)" to avoid confusion with a Colombo-15 locality of the same name.

Several other OSM matches were homonyms or district centroids and were reviewed by hand and left unchanged (column `status` in the validation file). Some localities are very close (e.g. Narahenpita and Thimbirigasyaya, 0.11 km apart); they are distinct places but make part of the instance easy. **Limitations:** straight-line distances are shorter than road distances, and the instance has no demands or time windows. The data is used only to instantiate and evaluate the optimisation models, not for training.

# 3. Mathematical formulation

Let $N=\{0,1,\dots,n-1\}$ be the nodes with depot $0$, $C=N\mathbin{\backslash}\{0\}$ the customers and $c_{ij}$ the Haversine distance from $i$ to $j$. Decision variables:

* $x_{ij}\in\{0,1\}$ for $i\neq j$: equal to 1 if the vehicle drives directly from $i$ to $j$;
* $u_i\in\mathbb{R}$ for $i\in C$: the position of customer $i$ in the tour (used only to forbid sub-tours).

$$\min \sum_{i\in N}\sum_{j\in N,\, j\neq i} c_{ij}\,x_{ij}$$

subject to

$$\sum_{j\in N,\, j\neq i} x_{ij}=1 \quad \forall i\in N \qquad\text{(leave every node exactly once)}$$
$$\sum_{i\in N,\, i\neq j} x_{ij}=1 \quad \forall j\in N \qquad\text{(enter every node exactly once)}$$
$$u_i-u_j+(n-1)\,x_{ij}\le n-2 \quad \forall i,j\in C,\ i\neq j \qquad\text{(Miller–Tucker–Zemlin sub-tour elimination)}$$
$$1\le u_i\le n-1 \quad \forall i\in C,\qquad x_{ij}\in\{0,1\}.$$

The degree constraints alone allow several disjoint cycles; the MTZ constraints force the order variables $u$ to increase along any route that does not pass through the depot, which rules out a cycle on customers only, so every feasible $x$ is one Hamiltonian cycle through the depot. An equivalent formulation replaces the MTZ rows by the Dantzig–Fulkerson–Johnson constraints $\sum_{i\in S}\sum_{j\in S,\,j\neq i}x_{ij}\le |S|-1$ for every $S\subseteq C$, $|S|\ge 2$, which is tighter but has exponentially many rows. **Assumptions:** one vehicle, symmetric costs, every locality visited once, no capacity, service time or time window.

# 4. Exact method: Held–Karp dynamic programming

**Why this method.** The assignment allows ILP, branch and bound or dynamic programming. Held–Karp needs no solver licence, is easy to verify (we check it against brute-force enumeration on random 8-node instances), and its runtime and memory are predictable, which suits a scalability study.

**Recurrence.** Let $C(S,j)$ be the length of the shortest path that starts at the depot, visits exactly the customers in $S\subseteq C$ and ends at $j\in S$:

$$C(\{j\},j)=c_{0j},\qquad C(S,j)=\min_{k\in S\mathbin{\backslash}\{j\}}\bigl[C(S\mathbin{\backslash}\{j\},k)+c_{kj}\bigr],$$
$$\text{optimal tour length}=\min_{j\in C}\bigl[C(C,j)+c_{j0}\bigr].$$

Parent pointers recover the tour. There are $(n-1)2^{\,n-1}$ states with $O(n)$ work each, so time is $O(n^2 2^n)$ and memory $O(n2^n)$. Our array-based implementation is in `src/tsp/exact.py`. Because the DP table for $n=30$ would already need about $1.6\times10^{10}$ entries, the exact method is applied to random subsets of up to 20 nodes (Section 6), and for the full 100 nodes ($\approx6\times10^{31}$ entries) it is impossible.

For the full instance we also compute the **1-tree lower bound** (minimum spanning tree on the customers plus the two cheapest depot edges; Held and Karp, 1970). Every tour contains such a structure, so no tour can be shorter. The bound is cheap but weak, and is used only to put a provable limit on the optimality gap.
