import requests
import json
import time
from pathlib import Path
import yaml
import sys
from shapely import Polygon
from collections import deque
import json
import os

sys.path.insert(1, str(Path(__file__).parent.parent.parent))
from utils.config import Config
from utils.split_poly import split_polygon_into_n

class UKCrimeAPICall:
    def __init__(self, config_path):
        self.config = Config(config_path)

    def post_request(self, session, data):
        for attempt in range(1, self.config.max_retries):
            try:
                r = session.post(self.config.api_url, data=data, timeout=self.config.timeout)
            
            except requests.RequestException as e:
                print('asdasdasdasd')
                time.sleep(self.config.timeout)
                continue
        
            if r.status_code == 503:
                # too many responses for asked polygon, need to split
                return {503: None}
            
            if r.status_code == 200:
                # OK 
                return {200: r.json()}
            
            if 500 <= r.status_code < 600:
                # transient server error: retry with backoff
                time.sleep(self.config.timeout)
                continue
            
            if r.status_code == 429:
                # Too many requests
                retry_after = r.headers.get("Retry-After")
                try:
                    wait = int(retry_after) if retry_after else None
                    if wait != self.config.timeout:
                        self.config.timeout = wait
                except ValueError:
                    wait = None
                print(f"429 received. Sleeping for {wait:.1f}s (attempt {attempt})")
                time.sleep(wait)
                continue
            
            # other client error: return empty and log
            print(f"Unexpected status {r.status_code}: {r.text[:200]}")
            return {r.status_code: r.text[:200]}
        # exhausted retries
        print("Max retries exceeded for a polygon; skipping.")
        return None
    
    def run(self):
        session = requests.Session()
        self.res = {}
        
        # initial area of interes splitting
        initial_poly = self.config.area_of_interest.coordinates
        gdf = split_polygon_into_n(Polygon(initial_poly), 25)
        process_polys = deque(list(gdf['geometry']))

        while process_polys:
            current_poly = process_polys.popleft()
            #poly_str = ":".join([f"{round(x[1], 3)},{round(x[0],3)}" for x in current_poly.exterior.coords])
            #full_api_url = f"{self.config.api_url}?date={self.config.month}&poly={poly_str}"
            
            data = {
                "poly": ":".join([f"{round(x[1], 3)},{round(x[0],3)}" for x in current_poly.exterior.coords]),
                "date": self.config.month
                }

            
            out_dict = self.post_request(session, data)
            #out_dict = {}

            if not out_dict:
                continue
            
            for key, values in out_dict.items():
                if key == 503:
                    print("Polygon split needed")
                    gdf_small = split_polygon_into_n(current_poly, 4)
                    process_polys.extend(list(gdf_small['geometry']))

                if key == 200:
                    # Handle data here
                    with open(rf"data\raw\uk_crime_api_call2\out_{data['date']}_{data['poly'].replace(":", "_")}.json", "w", encoding="utf-8") as f:
                        print(f"Fetched responses: {len(values)}")
                        json.dump(values, f, indent=2)

            print(f"Polygons left: {len(process_polys)}")


if __name__ == "__main__":
    api = UKCrimeAPICall(Path("config/config_api_call.yml"))
    api.run()

