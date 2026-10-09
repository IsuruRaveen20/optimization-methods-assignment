"""Cross-check every locality in the dataset against OpenStreetMap (Nominatim).

For each location name the top-ranked OSM result inside the Western Province
bounding box is retrieved and compared with the coordinate stored in
data/colombo_delivery_locations.csv. The result is written to
data/osm_validation.csv together with the retrieval timestamp.

Requires internet access. Nominatim usage policy: max 1 request per second and
an identifying User-Agent. Data (c) OpenStreetMap contributors, ODbL 1.0.
"""
import csv
import datetime
import json
import math
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "colombo_delivery_locations.csv"
OUT = ROOT / "data" / "osm_validation.csv"
VIEWBOX = "79.75,7.35,80.30,6.45"  # left,top,right,bottom
HEADERS = {"User-Agent": "MSc-Optimization-Assignment/1.0 (student coursework)"}


def haversine_km(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 6371.0 * 2 * math.asin(math.sqrt(h))


def query(name):
    clean = name.replace("Depot - ", "")
    params = urllib.parse.urlencode({
        "q": f"{clean}, Sri Lanka", "format": "json", "limit": 1,
        "viewbox": VIEWBOX, "bounded": 1, "countrycodes": "lk",
    })
    req = urllib.request.Request("https://nominatim.openstreetmap.org/search?" + params, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rows = []
    with open(SRC, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            lat, lon = float(r["latitude"]), float(r["longitude"])
            try:
                hits = query(r["location_name"])
            except Exception as exc:  # network problems should not abort the run
                print("error", r["location_name"], exc, file=sys.stderr)
                hits = []
            if hits:
                h = hits[0]
                olat, olon = float(h["lat"]), float(h["lon"])
                rows.append([r["node_id"], r["location_name"], lat, lon, olat, olon,
                             round(haversine_km(lat, lon, olat, olon), 3),
                             h.get("type", ""), h.get("display_name", "").replace(",", ";"), stamp])
            else:
                rows.append([r["node_id"], r["location_name"], lat, lon, "", "", "", "", "no OSM match", stamp])
            time.sleep(1.0)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["node_id", "location_name", "dataset_lat", "dataset_lon", "osm_lat", "osm_lon",
                    "offset_km", "osm_type", "osm_display_name", "retrieved_utc"])
        w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {OUT}")


if __name__ == "__main__":
    main()
