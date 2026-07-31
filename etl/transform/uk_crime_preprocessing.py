from pathlib import Path
import os
import json
import pandas as pd
from tqdm import tqdm

from utils.config import Config
from utils.function_timer import function_timer


def clean_category(txt: str) -> str:
    txt = txt.replace("-", " ")
    return txt.capitalize()

def get_place_time_identifier(file_name):
    return "_".join(file_name.split("_")[1:3])

@function_timer
def preprocess_json_data(input_data_dir: str, save_data_dir: str):
    # load
    full_data = dict()
    full_file_list = os.listdir(input_data_dir)
    keys = list(set([get_place_time_identifier(f) for f in full_file_list]))
    
    for key in keys:
        full_data[key] = []   

    for f_name in tqdm(full_file_list):
        identifier = get_place_time_identifier(f_name)
        file_path = os.path.join(input_data_dir, f_name)
        with open(file_path, 'r') as f:
            raw_data = json.load(f)

        # standarize
        for entry in raw_data:
            std_data = {
            'id': entry.get('id'),
            'month': entry.get('month'),
            'category': entry.get('category'),
            'location_type': entry.get('location_type'),
            'location_subtype': entry.get('location_subtype'),
            'latitude': (entry.get('location') or {}).get('latitude'),
            'longitude': (entry.get('location') or {}).get('longitude'),
            'region': f_name.split('_')[1],
            'street_id': ((entry.get('location') or {}).get('street') or {}).get('id'),
            'street_name': ((entry.get('location') or {}).get('street') or {}).get('name'),
            'context': entry.get('context'),
            'outcome_status_category': (entry.get('outcome_status') or {}).get('category'),
            'outcome_status_date': (entry.get('outcome_status') or {}).get('date'),
            'persistent_id': entry.get('persistent_id'),
            }
            
            full_data[identifier].append(std_data)
    
    for key, values in full_data.items():
        # clean
        df = pd.DataFrame(values)
        if not df.empty:
            df_clean = df.drop_duplicates(subset='id', keep='first')
            #df_clean = df_clean.set_index('id', drop=True)
            df_clean['category'] = df_clean['category'].apply(clean_category)
            df_clean.to_parquet(os.path.join(save_data_dir, f"{key}.parquet"))

if __name__ == '__main__':
    config = Config(Path("config/uk_crime_api/config_api_call.yml"))
    preprocess_json_data(config.output_dir_raw, config.output_dir_processed)