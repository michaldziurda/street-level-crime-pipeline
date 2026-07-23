import psycopg2
from pathlib import Path
import os
from dotenv import load_dotenv

from utils.config import Config
from utils.db_setup import setup_database
from etl.extract.uk_crime_api_call import UKCrimeAPICall
from etl.transform.uk_crime_preprocessing import preprocess_json_data
from etl.load.uk_crime_load import ensure_table, load_crimes


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
    conn = psycopg2.connect(
        dbname = os.getenv("POSTGRES_DB"),
        user = os.getenv("POSTGRES_USER"),
        password = os.getenv("POSTGRES_PASSWORD"),
        host = os.getenv("POSTGRES_HOST"),
        port = os.getenv("POSTGRES_PORT"))

    # Check for DB, create if needed
    res = ensure_table(conn, 'crime_data')
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

            load_crimes(conn, full_path, 'db.crime_data')

if __name__ == '__main__':
    main()

