"""Optional: fetch a reproducible set of real OSM named POIs around Colombo.
Requires internet access and requests. Respect the Overpass API usage policy.
This script is optional; the packaged CSV remains usable offline.
"""
import csv, datetime, json, urllib.request
QUERY = """[out:json][timeout:60];
(
 node[\"name\"][\"amenity\"](6.70,79.75,7.30,80.25);
 way[\"name\"][\"amenity\"](6.70,79.75,7.30,80.25);
 node[\"name\"][\"shop\"](6.70,79.75,7.30,80.25);
);
out center tags;"""
URL = "https://overpass-api.de/api/interpreter"
req=urllib.request.Request(URL,data=QUERY.encode(),headers={"User-Agent":"MSc-Optimization-Assignment/1.0"})
with urllib.request.urlopen(req,timeout=90) as response:
    data=json.loads(response.read().decode("utf-8"))
seen=set(); rows=[]
for el in data.get("elements",[]):
    tags=el.get("tags",{})
    name=tags.get("name")
    lat=el.get("lat",el.get("center",{}).get("lat"))
    lon=el.get("lon",el.get("center",{}).get("lon"))
    if not name or lat is None or lon is None: continue
    key=(name.strip().lower(),round(float(lat),5),round(float(lon),5))
    if key in seen: continue
    seen.add(key)
    rows.append((len(rows),name,float(lat),float(lon),tags.get("amenity",tags.get("shop","POI"))))
rows.sort(key=lambda x:(x[2],x[3],x[1]))
out="data/osm_poi_snapshot_"+datetime.datetime.now().strftime("%Y%m%d_%H%M%S")+".csv"
with open(out,"w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["node_id","name","latitude","longitude","category"]); w.writerows(rows)
print(f"Saved {len(rows)} named OSM POIs to {out}")
print("Record the retrieval timestamp and attribute OpenStreetMap contributors. Check ODbL terms.")
