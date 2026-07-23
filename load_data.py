#!/usr/bin/env python3
"""
Harvest crimes-street for Greater London for June 2026.
Writes deduplicated results to crimes_jun2026_london.csv
"""

import requests
import time
import csv
from shapely.geometry import box, Polygon
from shapely.ops import split
from tqdm import tqdm

API_URL = "https://data.police.uk/api/crimes-street/all-crime"
MONTH = "2026-06"
OUT_CSV = "crimes_jun2026_london.csv"

# London bbox (minx, miny, maxx, maxy) as lon/lat
MIN_LON, MIN_LAT, MAX_LON, MAX_LAT = -0.5103, 51.2868, 0.3340, 51.6919

# Initial tile size in degrees (approx). Smaller -> more requests but fewer 503s.
INITIAL_TILE_DEG = 0.005  # ~5 km; tune smaller if you still get 503s

# Rate limiting and retries
WAIT_TIME = 10
MAX_RETRIES = 5


session = requests.Session()
session.headers.update({"User-Agent": "london-harvester/1.0 (+your-email@example.com)"})

def poly_to_param(poly: Polygon) -> str:
    """Convert shapely polygon to API poly string: 'lat1,lon1:lat2,lon2:...'"""
    coords = list(poly.exterior.coords)[:-1]  # drop closing coord
    return ":".join(f"{lat},{lon}" for lon, lat in coords)

def fetch_poly(poly: Polygon):
    """POST polygon + date; return list or raise for 503/other errors."""
    poly_param = poly_to_param(poly)
    data = {"poly": poly_param, "date": MONTH}
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = session.post(API_URL, data=data, timeout=30)
        except requests.RequestException as e:
            time.sleep(WAIT_TIME)
            continue
        if r.status_code == 200:
            return r.json()
        if r.status_code == 503:
            # signal caller to subdivide
            return {"_status": 503}
        if 500 <= r.status_code < 600:
            # transient server error: retry with backoff
            time.sleep(WAIT_TIME)
            continue
        if r.status_code == 429:
            # Too many requests
            retry_after = r.headers.get("Retry-After")
            try:
                wait = int(retry_after) if retry_after else None
            except ValueError:
                wait = None
            print(f"429 received. Sleeping for {wait:.1f}s (attempt {attempt})")
            time.sleep(wait)
            continue
        # other client error: return empty and log
        print(f"Unexpected status {r.status_code}: {r.text[:200]}")
        return []
    # exhausted retries
    print("Max retries exceeded for a polygon; skipping.")
    return []

def subdivide_polygon(poly: Polygon):
    """Split polygon into 4 roughly equal boxes."""
    minx, miny, maxx, maxy = poly.bounds
    midx = (minx + maxx) / 2
    midy = (miny + maxy) / 2
    boxes = [
        box(minx, miny, midx, midy),
        box(midx, miny, maxx, midy),
        box(minx, midy, midx, maxy),
        box(midx, midy, maxx, maxy),
    ]
    return boxes

def tile_bbox(minx, miny, maxx, maxy, step):
    x = minx
    while x < maxx:
        y = miny
        x2 = min(x + step, maxx)
        while y < maxy:
            y2 = min(y + step, maxy)
            yield box(x, y, x2, y2)
            y = y2
        x = x2

def write_rows_to_csv(rows, writer):
    for r in rows:
        # flatten nested dicts if needed; keep keys consistent
        writer.writerow(r)

def normalize_item(item):
    # ensure stable keys and simple values for CSV
    # keep common fields; add raw JSON as fallback
    out = {
        "persistent_id": item.get("persistent_id") or "",
        "id": item.get("id") or "",
        "category": item.get("category") or "",
        "location_type": item.get("location_type") or "",
        "location_lat": item.get("location", {}).get("latitude") or "",
        "location_lon": item.get("location", {}).get("longitude") or "",
        "location_street_name": item.get("location", {}).get("street", {}).get("name") or "",
        "context": item.get("context") or "",
        "month": item.get("month") or "",
        "outcome_status": (item.get("outcome_status") or {}).get("category") if item.get("outcome_status") else "",
        "raw_json": str(item)
    }
    return out

def harvest():
    seen = set()
    fieldnames = [
        "persistent_id","id","category","location_type",
        "location_lat","location_lon","location_street_name",
        "context","month","outcome_status","raw_json"
    ]
    with open(OUT_CSV, "w", newline="", encoding="utf8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        # initial tiling
        tiles = list(tile_bbox(MIN_LON, MIN_LAT, MAX_LON, MAX_LAT, INITIAL_TILE_DEG))
        pbar = tqdm(tiles, desc="tiles")
        for tile in pbar:
            stack = [tile]
            while stack:
                poly = stack.pop()
                res = fetch_poly(poly)
                if isinstance(res, dict) and res.get("_status") == 503:
                    # subdivide if tile is still reasonably large
                    minx, miny, maxx, maxy = poly.bounds
                    # stop subdividing if tile is tiny to avoid infinite loop
                    if (maxx - minx) < 0.0005 or (maxy - miny) < 0.0005:
                        print("Tile too small but still 503; skipping tile.")
                        continue
                    subs = subdivide_polygon(poly)
                    stack.extend(subs)
                    continue
                if not isinstance(res, list):
                    # empty or error; skip
                    time.sleep(WAIT_TIME)
                    continue
                rows = []
                for item in res:
                    pid = item.get("persistent_id") or f"id:{item.get('id')}"
                    if pid in seen:
                        continue
                    seen.add(pid)
                    rows.append(normalize_item(item))
                if rows:
                    write_rows_to_csv(rows, writer)
                time.sleep(WAIT_TIME)

if __name__ == "__main__":
    print("Starting harvest for London, month:", MONTH)
    harvest()
    print("Done. Output:", OUT_CSV)
