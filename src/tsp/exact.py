"""Exact TSP solver: Held-Karp dynamic programming, O(n^2 * 2^n) time."""


def held_karp(d):
    """Return (optimal_length, tour) for a closed tour starting/ending at node 0.

    State dp[mask][j]: shortest path that starts at node 0, visits exactly the
    nodes in `mask` (bit k stands for node k+1) and ends at node j+1.
    """
    n = len(d)
    if n < 3:
        raise ValueError("need at least 3 nodes")
    m = n - 1
    full = (1 << m) - 1
    inf = float("inf")
    dp = [[inf] * m for _ in range(1 << m)]
    parent = [[-1] * m for _ in range(1 << m)]
    for j in range(m):
        dp[1 << j][j] = d[0][j + 1]
    for mask in range(1, full + 1):
        row = dp[mask]
        for j in range(m):
            cur = row[j]
            if cur == inf:
                continue
            dj = d[j + 1]
            for k in range(m):
                bit = 1 << k
                if mask & bit:
                    continue
                nxt = mask | bit
                val = cur + dj[k + 1]
                if val < dp[nxt][k]:
                    dp[nxt][k] = val
                    parent[nxt][k] = j
    best, last = min((dp[full][j] + d[j + 1][0], j) for j in range(m))
    tour, mask, j = [0], full, last
    path = []
    while j != -1:
        path.append(j + 1)
        prev = parent[mask][j]
        mask ^= 1 << j
        j = prev
    tour += path[::-1] + [0]
    return best, tour


def one_tree_bound(d):
    """Lower bound on the optimal tour length (1-tree relaxation).

    Minimum spanning tree over nodes 1..n-1 (Prim) plus the two cheapest edges
    at the depot. Every tour contains such a structure, so tour >= bound.
    """
    n = len(d)
    in_tree = [False] * n
    key = [float("inf")] * n
    key[1] = 0.0
    total = 0.0
    for _ in range(n - 1):
        u = min((v for v in range(1, n) if not in_tree[v]), key=lambda v: key[v])
        in_tree[u] = True
        total += key[u]
        for v in range(1, n):
            if not in_tree[v] and d[u][v] < key[v]:
                key[v] = d[u][v]
    return total + sum(sorted(d[0][1:])[:2])
