from airflow.sdk import DAG
from airflow.providers.standard.operators.empty import EmptyOperator

from utils.config import Config
from utils.db_setup import setup_uk_database, connect_to_db
from utils.ensure_paths import ensure_paths
from etl.extract.uk_crime_api_call import UKCrimeAPICall
from etl.transform.uk_crime_preprocessing import preprocess_json_data
from etl.load.uk_crime_load import check_if_table_exists, load_crimes

