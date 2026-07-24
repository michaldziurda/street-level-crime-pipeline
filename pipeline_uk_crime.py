from pathlib import Path
import os
from dotenv import load_dotenv

from utils.config import Config
from utils.db_setup import setup_database, connect_to_db
from etl.extract.uk_crime_api_call import UKCrimeAPICall
from etl.transform.uk_crime_preprocessing import preprocess_json_data
from etl.load.uk_crime_load import check_if_table_exists, load_crimes


def main():
    load_dotenv()
    config_path = 'config/uk_crime_api/config_api_call.yml'
    config = Config(config_path)

    # Call API
    api = UKCrimeAPICall(config)
    #api.run()

    # Clean and structurize data
    preprocess_json_data(config.output_dir_raw, config.output_dir_processed)

    # DB interaction
    conn = connect_to_db()

    # Check for DB, create if needed
    res = check_if_table_exists(conn, 'crime_data')
    # Query returns a one-element tuple with True or False:
    if not all(res):
        setup_database(conn)
    else:
        print("Table already in place")

    # Ingest data
    for data_file in os.listdir(Path(config.output_dir_processed)):
        if ".parquet" in data_file:
            print(f"Loading files to DB: {data_file}")
            full_path = Path(config.output_dir_processed, data_file)

            load_crimes(conn, full_path, 'crime_data')

if __name__ == '__main__':
    main()

