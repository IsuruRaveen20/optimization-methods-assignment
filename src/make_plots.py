"""Create the report figures from the CSV files in results/ (needs matplotlib)."""
import csv
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tsp import data, heuristics as h  # noqa: E402

RESULTS = data.ROOT / "results"
FIG = RESULTS / "figures"


def read(name):
    with open(RESULTS / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def draw_tour(ax, tour, points, title):
    xs = [points[i][2] for i in tour]
    ys = [points[i][1] for i in tour]
    ax.plot(xs, ys, "-", lw=0.8, color="#1f77b4", zorder=1)
    ax.scatter(xs[1:-1], ys[1:-1], s=9, color="#444444", zorder=2)
    ax.scatter([xs[0]], [ys[0]], s=70, color="#d62728", marker="*", zorder=3, label="Depot (Colombo Fort)")
    ax.set_title(title, fontsize=10)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.legend(loc="upper right", fontsize=7)


def route_map(points, d):
    rows = read("best_tour.csv")
    best = [int(r["node_id"]) for r in rows]
    nn = h.nearest_neighbour(d)
    fig, axes = plt.subplots(1, 2, figsize=(11, 5.5))
    draw_tour(axes[0], nn, points, f"Nearest Neighbour: {h.tour_length(nn, d):.1f} km")
    draw_tour(axes[1], best, points, f"Best tour (iterated local search): {h.tour_length(best, d):.1f} km")
    fig.tight_layout()
    fig.savefig(FIG / "route_maps.png", dpi=170)
    plt.close(fig)


def scalability_plots():
    rows = read("scalability_summary.csv")
    n = [int(r["n"]) for r in rows]
    methods = [k[:-len(" mean_gap_%")] for k in rows[0] if k.endswith(" mean_gap_%")]
    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    ax.semilogy(n, [float(r["exact_median_s"]) for r in rows], "o-", lw=2, color="#d62728", label="Exact Held-Karp")
    for m in methods:
        if m in ("Nearest Neighbour", "NN + 2-opt + Or-opt", "Iterated local search (50 it.)"):
            ax.semilogy(n, [float(r[m + " median_s"]) for r in rows], "s--", ms=4, label=m)
    ax.set_xlabel("Number of nodes n (depot included)")
    ax.set_ylabel("Median runtime (s, log scale)")
    ax.set_title("Runtime: exact method grows about 5x per +2 nodes")
    ax.grid(alpha=0.3, which="both")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "scalability_runtime.png", dpi=170)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    for m in methods:
        ax.plot(n, [float(r[m + " mean_gap_%"]) for r in rows], "o-", label=m)
    ax.set_xlabel("Number of nodes n (depot included)")
    ax.set_ylabel("Mean gap to optimum (%)")
    ax.set_title("Solution quality vs the exact optimum (5 random subsets per n)")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(FIG / "scalability_gap.png", dpi=170)
    plt.close(fig)


def full_instance_plot():
    rows = read("full_instance_results.csv")
    names = [r["method"] for r in rows]
    best = [float(r["best_km"]) for r in rows]
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    bars = ax.barh(names[::-1], best[::-1], color="#1f77b4")
    for bar, r in zip(bars, rows[::-1]):
        ax.text(bar.get_width() + 3, bar.get_y() + bar.get_height() / 2,
                f"{float(r['best_km']):.1f} km  ({float(r['median_runtime_s']):.3g} s)", va="center", fontsize=8)
    ax.set_xlim(0, max(best) * 1.35)
    ax.set_xlabel("Best tour length (km)  -  median runtime in brackets")
    ax.set_title("Full 100-node instance")
    fig.tight_layout()
    fig.savefig(FIG / "full_instance_comparison.png", dpi=170)
    plt.close(fig)


if __name__ == "__main__":
    FIG.mkdir(parents=True, exist_ok=True)
    pts = data.load_locations()
    dist = data.distance_matrix(pts)
    route_map(pts, dist)
    scalability_plots()
    full_instance_plot()
    print("Figures written to", FIG)
