"""Run all experiments and write the CSV/TXT files in results/.

1. Scalability study  - exact Held-Karp vs heuristics on random subsets of 8..20 nodes.
2. Full instance      - all heuristics on the complete 100-node instance, repeated runs.

Usage:  python src/run_experiments.py          (about 2-3 minutes)
        python src/run_experiments.py --quick  (smaller, for a smoke test)
"""
import argparse
import csv
import random
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tsp import data, exact, heuristics as h  # noqa: E402

RESULTS = data.ROOT / "results"


def timed(fn, *args, **kwargs):
    t0 = time.perf_counter()
    out = fn(*args, **kwargs)
    return out, time.perf_counter() - t0


def submatrix(d, idx):
    return [[d[i][j] for j in idx] for i in idx]


def is_feasible(tour, n):
    return tour[0] == 0 and tour[-1] == 0 and sorted(tour[:-1]) == list(range(n))


def scalability(d, sizes, subsets):
    rows = []
    for n in sizes:
        for s in range(subsets):
            rng = random.Random(1000 * n + s)
            idx = [0] + rng.sample(range(1, len(d)), n - 1)
            sub = submatrix(d, idx)
            (opt, _), t_exact = timed(exact.held_karp, sub)
            runs = {
                "Nearest Neighbour": lambda: h.nearest_neighbour(sub),
                "NN + 2-opt": lambda: h.two_opt(h.nearest_neighbour(sub), sub),
                "NN + 2-opt + Or-opt": lambda: h.local_search(h.nearest_neighbour(sub), sub),
                "Multi-start 2-opt (10 starts)": lambda: h.multi_start(sub, 10, seed=s),
                "Iterated local search (50 it.)": lambda: h.iterated_local_search(sub, 50, seed=s),
            }
            row = {"n": n, "subset": s, "exact_km": round(opt, 4), "exact_s": round(t_exact, 5)}
            for name, fn in runs.items():
                tour, t = timed(fn)
                assert is_feasible(tour, n)
                length = h.tour_length(tour, sub)
                row[name + " gap_%"] = round(100 * (length - opt) / opt, 3)
                row[name + " s"] = round(t, 6)
            rows.append(row)
            print(f"n={n:2d} subset={s} exact={opt:8.3f} km in {t_exact:6.2f}s", flush=True)
    return rows


def summarise(rows, methods):
    out = []
    for n in sorted({r["n"] for r in rows}):
        sel = [r for r in rows if r["n"] == n]
        row = {"n": n, "subsets": len(sel),
               "exact_median_s": round(statistics.median(r["exact_s"] for r in sel), 5)}
        for m in methods:
            row[m + " mean_gap_%"] = round(statistics.mean(r[m + " gap_%"] for r in sel), 3)
            row[m + " max_gap_%"] = round(max(r[m + " gap_%"] for r in sel), 3)
            row[m + " median_s"] = round(statistics.median(r[m + " s"] for r in sel), 6)
        out.append(row)
    return out


def full_instance(d, points, repeats, ils_iters):
    n = len(d)
    lower = exact.one_tree_bound(d)
    specs = [
        ("Nearest Neighbour", False, lambda s: h.nearest_neighbour(d)),
        ("NN + 2-opt", False, lambda s: h.two_opt(h.nearest_neighbour(d), d)),
        ("NN + 2-opt + Or-opt", False, lambda s: h.local_search(h.nearest_neighbour(d), d)),
        ("Multi-start 2-opt (30 starts)", True, lambda s: h.multi_start(d, 30, seed=s)),
        (f"Iterated local search ({ils_iters} it.)", True, lambda s: h.iterated_local_search(d, ils_iters, seed=s)),
    ]
    results, best_tour, best_len = [], None, float("inf")
    for name, randomised, fn in specs:
        lengths, times = [], []
        for s in range(1, repeats + 1):
            tour, t = timed(fn, s)
            assert is_feasible(tour, n)
            length = h.tour_length(tour, d)
            lengths.append(length)
            times.append(t)
            if length < best_len:
                best_len, best_tour = length, tour
        results.append({
            "method": name, "randomised": randomised, "runs": repeats,
            "best_km": round(min(lengths), 4), "mean_km": round(statistics.mean(lengths), 4),
            "std_km": round(statistics.pstdev(lengths), 4),
            "median_runtime_s": round(statistics.median(times), 5), "feasible": True,
        })
        print(f"{name:34s} best={min(lengths):8.3f} mean={statistics.mean(lengths):8.3f} "
              f"median_t={statistics.median(times):.3f}s", flush=True)
    for r in results:
        r["gap_to_best_found_%"] = round(100 * (r["best_km"] - best_len) / best_len, 3)
        r["gap_to_lower_bound_%"] = round(100 * (r["best_km"] - lower) / lower, 3)
    return results, best_tour, best_len, lower


def write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    sizes = [8, 10, 12] if args.quick else [8, 10, 12, 14, 16, 18, 20]
    subsets, repeats, ils_iters = (2, 2, 20) if args.quick else (5, 5, 300)

    points = data.load_locations()
    d = data.distance_matrix(points)
    RESULTS.mkdir(exist_ok=True)

    print("== Scalability: exact vs heuristics ==")
    rows = scalability(d, sizes, subsets)
    methods = [k[:-6] for k in rows[0] if k.endswith(" gap_%")]
    write_csv(RESULTS / "scalability_runs.csv", rows)
    write_csv(RESULTS / "scalability_summary.csv", summarise(rows, methods))

    print("== Full instance ==")
    results, tour, length, lower = full_instance(d, points, repeats, ils_iters)
    write_csv(RESULTS / "full_instance_results.csv", results)
    with open(RESULTS / "best_tour.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["visit_order", "node_id", "location_name", "latitude", "longitude"])
        for k, node in enumerate(tour):
            w.writerow([k, node, points[node][0], points[node][1], points[node][2]])
    with open(RESULTS / "best_route.txt", "w", encoding="utf-8") as f:
        f.write(f"Best tour found on the {len(d)}-node instance: {length:.4f} km\n")
        f.write(f"1-tree lower bound: {lower:.4f} km (best tour is at most "
                f"{100 * (length - lower) / lower:.2f}% above the optimum)\n\n")
        f.write("Node ids:\n" + " -> ".join(map(str, tour)) + "\n\n")
        f.write("Locations:\n" + " -> ".join(points[i][0] for i in tour) + "\n")
    print(f"best={length:.4f} km, lower bound={lower:.4f} km")


if __name__ == "__main__":
    main()
