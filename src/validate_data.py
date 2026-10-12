"""Run the dataset quality checks (duplicates, bounding box, matrix consistency).

Author: IsuruRaveen20 <isururaveen4520@gmail.com>
Created: 2026-10-09
"""
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))
from tsp import data  # noqa: E402

if __name__ == "__main__":
    points = data.load_locations()
    problems = data.validate(points)
    print(f"{len(points)} nodes checked.")
    if problems:
        print("PROBLEMS:", *problems, sep="\n - ")
        sys.exit(1)
    print("All dataset checks passed.")
