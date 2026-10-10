"""Constructive heuristics and local search for the TSP.

Tours are lists of node ids that start and end at the depot (node 0),
e.g. [0, 5, 3, 1, 0]. Internally local search works on the open list
without the repeated depot at the end.
"""
import random


def tour_length(tour, d):
    return sum(d[tour[i]][tour[i + 1]] for i in range(len(tour) - 1))


def nearest_neighbour(d, first=None):
    """Greedy construction. `first` optionally forces the first customer visited."""
    n = len(d)
    unvisited = set(range(1, n))
    tour = [0]
    if first is not None and first != 0:
        tour.append(first)
        unvisited.remove(first)
    cur = tour[-1]
    while unvisited:
        nxt = min(unvisited, key=lambda j: d[cur][j])
        tour.append(nxt)
        unvisited.remove(nxt)
        cur = nxt
    tour.append(0)
    return tour


def _two_opt(t, d):
    """First-improvement 2-opt on an open list t (t[0] is the depot). Returns True if improved."""
    n = len(t)
    improved_any = False
    improved = True
    while improved:
        improved = False
        for i in range(1, n - 1):
            a, b = t[i - 1], t[i]
            for j in range(i + 1, n):
                c, e = t[j], t[(j + 1) % n]
                if d[a][c] + d[b][e] < d[a][b] + d[c][e] - 1e-9:
                    t[i:j + 1] = reversed(t[i:j + 1])
                    a, b = t[i - 1], t[i]
                    improved = improved_any = True
    return improved_any


def _or_opt(t, d, max_seg=3):
    """Move a segment of 1..max_seg nodes (optionally reversed) to a better place. One move per call."""
    n = len(t)
    for seg_len in range(1, max_seg + 1):
        for i in range(1, n - seg_len + 1):
            seg = t[i:i + seg_len]
            prev, nxt = t[i - 1], t[(i + seg_len) % n]
            removal_gain = d[prev][seg[0]] + d[seg[-1]][nxt] - d[prev][nxt]
            rest = t[:i] + t[i + seg_len:]
            r = len(rest)
            for j in range(r):
                u, v = rest[j], rest[(j + 1) % r]
                base = d[u][v]
                fwd = d[u][seg[0]] + d[seg[-1]][v] - base
                rev = d[u][seg[-1]] + d[seg[0]][v] - base
                if fwd < removal_gain - 1e-9:
                    t[:] = rest[:j + 1] + seg + rest[j + 1:]
                    return True
                if rev < removal_gain - 1e-9:
                    t[:] = rest[:j + 1] + seg[::-1] + rest[j + 1:]
                    return True
    return False


def two_opt(tour, d):
    """2-opt local search on a closed tour (depot at both ends)."""
    t = tour[:-1]
    _two_opt(t, d)
    return t + [0]


def local_search(tour, d):
    """Alternate 2-opt and Or-opt until no move improves the tour."""
    t = tour[:-1]
    while True:
        a = _two_opt(t, d)
        b = _or_opt(t, d)
        if not (a or b):
            break
    return t + [0]


def multi_start(d, starts, seed=0, search=two_opt):
    """Run nearest neighbour from `starts` random first customers, improve each, keep the best."""
    rng = random.Random(seed)
    firsts = rng.sample(range(1, len(d)), min(starts, len(d) - 1))
    best = None
    for f in firsts:
        t = search(nearest_neighbour(d, f), d)
        if best is None or tour_length(t, d) < tour_length(best, d):
            best = t
    return best


def iterated_local_search(d, iterations, seed=0):
    """ILS: double-bridge perturbation + 2-opt/Or-opt, accept only improvements."""
    rng = random.Random(seed)
    best = local_search(nearest_neighbour(d), d)
    best_len = tour_length(best, d)
    n = len(best) - 1
    if n < 8:
        return best
    for _ in range(iterations):
        t = best[:-1]
        a, b, c = sorted(rng.sample(range(1, n), 3))
        cand = local_search(t[:a] + t[b:c] + t[a:b] + t[c:] + [0], d)
        cand_len = tour_length(cand, d)
        if cand_len < best_len - 1e-9:
            best, best_len = cand, cand_len
    return best
