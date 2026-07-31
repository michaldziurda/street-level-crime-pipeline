import requests
import json
import time
from pathlib import Path
from shapely import Polygon
from collections import deque
import itertools

from utils.config import Config
from utils.split_poly import split_polygon_into_n
from utils.function_timer import function_timer

class UKCrimeAPICall:
    def __init__(self, config_path):
        if isinstance(config_path, Config):
            self.config = config_path
        else:
            self.config = Config(config_path)

        # Empty list means that all the deinfed spaces will be used
        if self.config.areas is None:
            self.config.areas = []
            for f in Path(Path(self.config.config_file_path).parent, 'areas').iterdir():
                if not f.name.startswith('_'):
                    self.config.areas.append(f)
            
    def post_request(self, session, data):
        for attempt in range(self.config.max_retries):
            try:
                r = session.post(self.config.api_url, data=data, timeout=self.config.timeout)
                #print(r.status_code)
            
            except requests.RequestException as e:
                print(e)
                time.sleep(self.config.wait_on_error)
                continue
        
            if r.status_code == 503:
                # too many responses for asked polygon, need to split
                return {503: None}
            
            if r.status_code == 200:
                # OK 
                time.sleep(self.config.wait_on_success)
                return {200: r.json()}
            
            if 500 <= r.status_code < 600:
                # transient server error: retry with backoff
                time.sleep(self.config.wait_on_error)
                continue
            
            if r.status_code == 429:
                # Too many requests
                retry_after = r.headers.get("Retry-After")
                try:
                    wait = int(retry_after) if retry_after else None
                    if wait != self.config.wait_on_429:
                        self.config.wait_on_429 = wait
                except ValueError:
                    wait = None
                print(f"429 received. Sleeping for {self.config.wait_on_429:.1f}s (attempt {attempt})")
                time.sleep(self.config.wait_on_429)
                continue
            
            # other client error: return empty and log
            print(f"Unexpected status {r.status_code}: {r.text[:200]}")
            return {r.status_code: r.text[:200]}
        # exhausted retries
        print("Max retries exceeded for a polygon; skipping.")
        return None
    
    @function_timer
    def run(self):
        session = requests.Session()
        self.res = {}

        # Iterate over product of selected areas and months (defined in main api config) 
        prd = itertools.product(self.config.areas, self.config.months)
        for ix, (area_config_file, month) in enumerate(prd): 
            print(f"Progress: {ix}/{len(self.config.areas) * len(self.config.months)}")
            area_config = Config(area_config_file)
            area_name = area_config.area_name
            area_coordinates = area_config.coordinates
            gdf = split_polygon_into_n(Polygon(area_coordinates), self.config.initial_poly_split)
            process_polys = deque(list(gdf['geometry']))

            print(area_config_file, month)

            while process_polys:
                current_poly = process_polys.popleft()
                #poly_str = ":".join([f"{round(x[1], 3)},{round(x[0],3)}" for x in current_poly.exterior.coords])
                #full_api_url = f"{self.config.api_url}?date={self.config.month}&poly={poly_str}"
                
                data = {
                    "poly": ":".join([f"{round(x[1], 3)},{round(x[0],3)}" for x in current_poly.exterior.coords]),
                    "date": month
                    }

                print(f"Requesting data for: {data}")
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
                        with open(Path(rf"{self.config.output_dir_raw}/out_{area_name}_{data['date']}_{data['poly'].replace(':', '_')}.json"), 'w', encoding='utf-8') as f:
                            print(f"Fetched responses: {len(values)}")
                            json.dump(values, f, indent=2)

                print(f"Polygons left: {len(process_polys)}")


if __name__ == "__main__":
    api = UKCrimeAPICall(Path("config/uk_crime_api/config_api_call.yml"))
    api.run()

