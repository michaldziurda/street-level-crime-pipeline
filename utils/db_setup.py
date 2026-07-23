import psycopg2
from psycopg2.extras import execute_values
from pathlib import Path
import yaml
import sys

sys.path.insert(1, str(Path(__file__).parent.parent.parent))
from utils.config import Config

def setup_database(config_path:str):
    # Load config (using your Config class)
    config = Config(config_path)
    
    conn = psycopg2.connect(**config.database)
    cur = conn.cursor()
    
    # Create schema
    cur.execute("CREATE SCHEMA IF NOT EXISTS db;")
    
    # Create tables
    cur.execute("""
        CREATE TABLE IF NOT EXISTS db.crime_data (
            id SERIAL PRIMARY KEY,
            cell_id INTEGER,
            polygon_geojson JSONB,
            api_response JSONB,
            fetched_at TIMESTAMP DEFAULT NOW(),
            request_metadata JSONB
        );
    """)
    
    # Add indexes
    #cur.execute("CREATE INDEX IF NOT EXISTS idx_cell_id ON db.crime_data (cell_id);")
    #cur.execute("CREATE INDEX IF NOT EXISTS idx_api_response_gin ON db.crime_data USING GIN (api_response);")
    
    conn.commit()
    print("Schema and tables created successfully.")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()