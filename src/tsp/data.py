"""Dataset loading, Haversine distances and data-quality checks."""
import csv
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOCATIONS_CSV = ROOT / "data" / "colombo_delivery_locations.csv"
MATRIX_CSV = ROOT / "data" / "distance_matrix_km.csv"
EARTH_RADIUS_KM = 6371.0


def load_locations(path=LOCATIONS_CSV):
    """Return a list of (name, latitude, longitude); index == node_id, depot is 0."""
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for expected_id, row in enumerate(rows):
        if int(row["node_id"]) != expected_id:
            raise ValueError(f"node_id {row['node_id']} is out of order at row {expected_id}")
    return [(r["location_name"], float(r["latitude"]), float(r["longitude"])) for r in rows]


def haversine_km(a, b):
    """Great-circle distance in km between two (name, lat, lon) tuples."""
    p1, p2 = math.radians(a[1]), math.radians(b[1])
    dp, dl = p2 - p1, math.radians(b[2] - a[2])
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return EARTH_RADIUS_KM * 2 * math.asin(math.sqrt(h))


def distance_matrix(points):
    """Symmetric full matrix of Haversine distances (km)."""
    n = len(points)
    d = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            d[i][j] = d[j][i] = haversine_km(points[i], points[j])
    return d


def write_matrix_csv(points, path=MATRIX_CSV):
    d = distance_matrix(points)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["node_id"] + [p[0] for p in points])
        for i, row in enumerate(d):
            w.writerow([i] + [round(x, 4) for x in row])


def validate(points, matrix_path=MATRIX_CSV):
    """Return a list of human-readable problems (empty list == dataset passes)."""
    problems = []
    names = [p[0] for p in points]
    if len(set(names)) != len(names):
        problems.append("duplicate location names")
    coords = [(p[1], p[2]) for p in points]
    if len(set(coords)) != len(coords):
        problems.append("duplicate coordinates")
    for name, lat, lon in points:
        if not (6.4 <= lat <= 7.4 and 79.7 <= lon <= 80.3):
            problems.append(f"{name}: outside Western Province bounding box")
    d = distance_matrix(points)
    with open(matrix_path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    if rows[0][1:] != names or len(rows) - 1 != len(points):
        problems.append("distance matrix header/size does not match locations")
    else:
        worst = max(abs(float(rows[i + 1][j + 1]) - d[i][j])
                    for i in range(len(points)) for j in range(len(points)))
        if worst > 1e-4:
            problems.append(f"distance matrix is stale (max difference {worst:.4f} km)")
    return problems
