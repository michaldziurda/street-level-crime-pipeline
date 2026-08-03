from pathlib import Path
import os
from dotenv import load_dotenv
from tqdm import tqdm

from utils.config import Config
from utils.db_setup import setup_uk_database, connect_to_db
from utils.ensure_paths import ensure_paths
from etl.extract.uk_crime_api_call import UKCrimeAPICall
from etl.transform.uk_crime_preprocessing import preprocess_json_data
from etl.load.uk_crime_load import check_if_table_exists, load_crimes
import time


def main():
    load_dotenv()
    config_path = 'config/uk_crime_api/config_api_call.yml'
    config = Config(config_path)

    # Ensure the data paths are there - for Docker
    ensure_paths(config.output_dir_raw)
    ensure_paths(config.output_dir_processed)

    # Call API
    api = UKCrimeAPICall(config)
    api.run()

    # Clean and structurize data
    preprocess_json_data(config)

    # DB interaction
    conn = connect_to_db()

    # Check for DB, create if needed
    res = check_if_table_exists(conn, os.getenv("UK_CRIMES_TABLE"))
    # Query returns a one-element tuple with True or False:
    if not all(res):
        setup_uk_database(conn)
    else:
        print("Table already in place")

    # Ingest data
    start = time.perf_counter()
    for data_file in tqdm(os.listdir(Path(config.output_dir_processed))):
        if ".parquet" in data_file:
            #print(f"Loading files to DB: {data_file}")
            full_path = Path(config.output_dir_processed, data_file)

            load_crimes(conn, full_path, os.getenv("UK_CRIMES_TABLE"))
    
    end = time.perf_counter()
    print(f"Loading dat to the dababase took {end - start:.6f} seconds")

if __name__ == '__main__':
    main()

