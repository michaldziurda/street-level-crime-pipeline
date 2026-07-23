import sys
from pathlib import Path
import os
import json
import pandas as pd

from utils.config import Config


def clean_category(txt: str) -> str:
    txt = txt.replace("-", " ")
    return txt.capitalize()

def preprocess_json_data(input_data_dir: str, save_data_dir: str):
    # load
    full_data = list()
    for f_name in os.listdir(input_data_dir):
        file_path = os.path.join(input_data_dir, f_name)
        with open(file_path, 'r') as f:
            raw_data = json.load(f)

        # standarize
        for entry in raw_data:
            std_data = {
            'ID': entry.get('id'),
            'month': entry['month'] or None,
            'category': entry['category'] or None,
            'location_type': entry['location_type'] or None,
            'location_subtype': entry['location_subtype'] or None,
            'latitude': entry['location']['latitude'] or None,
            'longitude': entry['location']['longitude'] or None,
            'street_id': entry['location']['street']['id'] or None,
            'street_name': entry['location']['street']['name'] or None,
            'context': entry['context'] or None,
            'outcome_status_category': entry.get('outcome_status', {}).get('category'),
            'outcome_status_date': entry.get('outcome_status', {}).get('date'),
            'persistent_id': entry['persistent_id'] or None,
            }
            
            full_data.append(std_data)
    
    # clean
    df = pd.DataFrame(full_data)
    df_clean = df.drop_duplicates(subset='ID', keep='first')
    df_clean = df_clean.set_index('ID', drop=True)
    df_clean['category'] = df_clean['category'].apply(clean_category)
    df_clean['category'].unique()
        
    # save
    df_clean.to_parquet(os.path.join(save_data_dir, f"df.parquet"))


if __name__ == '__main__':
    config = Config(Path("config/config_api_call.yml"))
    preprocess_json_data(config.output_dir_raw, config.output_dir_processed)