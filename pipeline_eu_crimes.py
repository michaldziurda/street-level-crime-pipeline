from pathlib import Path
import os
from dotenv import load_dotenv
from tqdm import tqdm

from utils.config import Config
from utils.db_setup import setup_eu_database, connect_to_db
from utils.ensure_paths import ensure_paths
from etl.transform.eurostat_preprocessing import preprocess_eurostat_data
from etl.load.eu_crime_load import check_if_table_exists, load_crimes
import time


def main():
    load_dotenv()
    config_path = 'config/eu_crime/config_eurostat.yml'
    config = Config(config_path)

    # Ensure the data paths are there - for Docker
    ensure_paths(config.output_dir_raw)
    ensure_paths(config.output_dir_processed)

    # Clean and structurize data
    preprocess_eurostat_data(config)

    # DB interaction
    conn = connect_to_db()

    # Check for DB, create if needed
    res = check_if_table_exists(conn, os.getenv("EU_CRIMES_TABLE"))
    # Query returns a one-element tuple with True or False:
    if not all(res):
        setup_eu_database(conn)
    else:
        print("Table already in place")

    # Ingest data
    start = time.perf_counter()
    for data_file in tqdm(os.listdir(Path(config.output_dir_processed))):
        if ".parquet" in data_file:
            #print(f"Loading files to DB: {data_file}")
            full_path = Path(config.output_dir_processed, data_file)

            load_crimes(conn, full_path, os.getenv("EU_CRIMES_TABLE"))
    
    end = time.perf_counter()
    print(f"Loading dat to the dababase took {end - start:.6f} seconds")

if __name__ == '__main__':
    main()
