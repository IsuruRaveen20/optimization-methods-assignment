"""Regenerate data/distance_matrix_km.csv from data/colombo_delivery_locations.csv.

Author: IsuruRaveen20 <isururaveen4520@gmail.com>
Created: 2026-10-09
"""
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))
from tsp import data  # noqa: E402

if __name__ == "__main__":
    points = data.load_locations()
    data.write_matrix_csv(points)
    print(f"Wrote {len(points)}x{len(points)} Haversine matrix to {data.MATRIX_CSV}")
