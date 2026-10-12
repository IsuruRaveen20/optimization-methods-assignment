"""Build docs/final_report.pdf from docs/report/*.md and the CSV files in results/.

All numbers in the report come from results/*.csv, so the PDF always matches the
last experiment run. Requires pandoc and xelatex.
    python docs/build_report.py

Author: sharmilak99 <sharmilakavi822@gmail.com>
Created: 2026-10-12
"""
import csv
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PARTS = sorted((ROOT / "docs" / "report").glob("0[1-9]_*.md"))
OUT = ROOT / "docs" / "final_report.pdf"


def read(name):
    with open(ROOT / "results" / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def field(path, label, fallback):
    """Value after 'label:' in a text file, or fallback if missing/still a placeholder."""
    try:
        for line in (ROOT / path).read_text(encoding="utf-8").splitlines():
            if line.lower().startswith(label.lower()):
                value = line.split(":", 1)[1].strip()
                if value and "[" not in value:
                    return value
    except FileNotFoundError:
        pass
    return fallback


def md_table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---:" if i else ":---" for i in range(len(header))) + "|"]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(out)


def build_values():
    summ = read("scalability_summary.csv")
    full = read("full_instance_results.csv")
    methods = [k[:-len(" mean_gap_%")] for k in summ[0] if k.endswith(" mean_gap_%")]
    short = {"Nearest Neighbour": "NN", "NN + 2-opt": "2-opt", "NN + 2-opt + Or-opt": "2-opt+Or",
             "Multi-start 2-opt (10 starts)": "Multi-start", "Iterated local search (50 it.)": "ILS"}
    header = ["n", "Exact (s)"] + [short.get(m, m) for m in methods]
    rows = [[r["n"], f"{float(r['exact_median_s']):.4g}"] + [f"{float(r[m + ' mean_gap_%']):.2f}" for m in methods]
            for r in summ]
    t1 = md_table(header, rows)
    header = ["Method", "Best (km)", "Mean (km)", "Std (km)", "Median time (s)", "Gap to best found (%)", "Gap to lower bound (%)"]
    rows = [[r["method"], r["best_km"], f"{float(r['mean_km']):.2f}", f"{float(r['std_km']):.2f}",
             f"{float(r['median_runtime_s']):.4g}", f"{max(0.0, float(r['gap_to_best_found_%'])):.2f}",
             f"{float(r['gap_to_lower_bound_%']):.2f}"] for r in full]
    t2 = md_table(header, rows)
    by = {r["method"].split(" (")[0]: r for r in full}
    nn, two, orr = by["Nearest Neighbour"], by["NN + 2-opt"], by["NN + 2-opt + Or-opt"]
    ms, ils = by["Multi-start 2-opt"], by["Iterated local search"]
    best = min(float(r["best_km"]) for r in full)
    lb_gap = float(ils["gap_to_lower_bound_%"])
    lb = best / (1 + lb_gap / 100)
    g = lambda m: [float(r[m + " mean_gap_%"]) for r in summ]
    return {
        "TABLE_SCALABILITY": t1, "TABLE_FULL": t2,
        "NN_KM": f"{float(nn['best_km']):.1f}", "TWOOPT_KM": f"{float(two['best_km']):.1f}",
        "OROPT_KM": f"{float(orr['best_km']):.1f}", "MS_KM": f"{float(ms['best_km']):.1f}",
        "ILS_KM": f"{float(ils['best_km']):.1f}", "LB_KM": f"{lb:.1f}", "LB_GAP": f"{lb_gap:.1f}",
        "NN_VS_BEST": f"{100 * (float(nn['best_km']) - best) / best:.1f}",
        "NN_SMALL_RANGE": f"{min(g('Nearest Neighbour')):.0f}–{max(g('Nearest Neighbour')):.0f}",
        "TWOOPT_RANGE": f"{min(g('NN + 2-opt')):.1f}–{max(g('NN + 2-opt')):.1f}",
        "NN_T": f"{float(nn['median_runtime_s']):.4f} s", "OROPT_T": f"{float(orr['median_runtime_s']):.3f}",
        "ILS_T": f"{float(ils['median_runtime_s']):.1f}",
        "ILS_VS_OROPT": f"{100 * (float(orr['best_km']) - float(ils['best_km'])) / float(orr['best_km']):.1f}",
        "ILS_SLOWDOWN": f"{float(ils['median_runtime_s']) / float(orr['median_runtime_s']):.0f}",
        "MEMBER1": field("members.txt", "Group Member 1", "[FULL NAME AND STUDENT ID - fill in members.txt]"),
        "MEMBER2": field("members.txt", "Group Member 2", "[FULL NAME AND STUDENT ID - fill in members.txt]"),
        "GITHUB_URL": field("submission.txt", "GitHub repository", "[GITHUB URL - fill in submission.txt]"),
    }


def main():
    values = build_values()
    text = "\n\n".join(p.read_text(encoding="utf-8") for p in PARTS)
    text = re.sub(r"\{\{(\w+)\}\}", lambda m: values[m.group(1)], text)
    merged = ROOT / "docs" / "report" / "_merged.md"
    merged.write_text(text, encoding="utf-8")
    cmd = ["pandoc", str(ROOT / "docs/report/00_header.yaml"), str(merged), "-o", str(OUT),
           "--pdf-engine=xelatex", "--resource-path", str(ROOT), "-V", "mainfont=Latin Modern Roman"]
    subprocess.run(cmd, check=True)
    merged.unlink()
    print("Wrote", OUT)


if __name__ == "__main__":
    sys.exit(main())
