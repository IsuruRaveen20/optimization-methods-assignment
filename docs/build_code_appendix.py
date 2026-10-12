"""Concatenate all source files into docs/code_appendix.txt (plain text, as required for submission)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    "src/tsp/__init__.py", "src/tsp/data.py", "src/tsp/exact.py", "src/tsp/heuristics.py",
    "src/run_experiments.py", "src/make_plots.py", "src/validate_data.py", "src/build_matrix.py",
    "src/validate_against_osm.py", "src/fetch_osm_pois.py", "tests/test_solvers.py",
]
out = ["CODE APPENDIX - Colombo Metro Delivery Route Optimisation", "=" * 60, ""]
for name in FILES:
    out += ["", "#" * 78, f"# FILE: {name}", "#" * 78, (ROOT / name).read_text(encoding="utf-8").rstrip(), ""]
(ROOT / "docs" / "code_appendix.txt").write_text("\n".join(out), encoding="utf-8")
print("Wrote docs/code_appendix.txt")
