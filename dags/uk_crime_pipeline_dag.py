from airflow.decorators import dag, task
from airflow.models.param import Param
from datetime import datetime
from pathlib import Path
import time
import os

from utils.config import Config
from utils.db_setup import setup_uk_database, connect_to_db
from utils.ensure_paths import ensure_paths
from etl.extract.uk_crime_api_call import UKCrimeAPICall
from etl.transform.uk_crime_preprocessing import preprocess_json_data
from etl.load.uk_crime_load import check_if_table_exists, load_crimes

DEFAULT_CONFIG = r"config/uk_crime_api/config_api_call.yml"

@dag(
    dag_id='uk_crime_pipeline',
    start_date=datetime(2025,1,1),
    schedule=None,
    catchup=False,
    tags=['uk', 'crime', 'pipeline', 'api'],
    params={
        'config_path': Param(
            default=DEFAULT_CONFIG,
            type='string',
            description='Path to the YAML config file'
        )
    }
)
def uk_crime_pipeline():
    @task
    def ensure_table():
        conn = connect_to_db()
        res = check_if_table_exists(conn, os.getenv("UK_CRIMES_TABLE"))
        # Query returns a one-element tuple with True or False:
        if not all(res):
            setup_uk_database(conn)
        else:
            print("Table already in place")
        conn.close()
    
    @task
    def extract(**kwargs):
        config_path = kwargs['params']['config_path']
        config = Config(config_path)

        ensure_paths(config.output_dir_raw)
        ensure_paths(config.output_dir_processed)

        api = UKCrimeAPICall(config)
        api.run()

    @task
    def transform(**kwargs):
        config_path = kwargs['params']['config_path']
        config = Config(config_path)
        preprocess_json_data(config)

    @task
    def load(**kwargs):
        config_path = kwargs['params']['config_path']
        config = Config(config_path)
        
        conn = connect_to_db()
        
        start = time.perf_counter()
        for data_file in os.listdir(Path(config.output_dir_processed)):
            if ".parquet" in data_file:
                full_path = Path(config.output_dir_processed, data_file)
                load_crimes(conn, full_path, os.getenv("UK_CRIMES_TABLE"))
        
        end = time.perf_counter()
        print(f"Loading dat to the dababase took {end - start:.6f} seconds")
        conn.close()

    ensure_table() >> extract() >> transform() >> load()

uk_crime_pipeline()