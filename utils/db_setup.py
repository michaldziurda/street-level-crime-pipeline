import psycopg2
import os
from dotenv import load_dotenv

def connect_to_db():
    load_dotenv()
    conn = psycopg2.connect(
        dbname = os.getenv("POSTGRES_DB"),
        user = os.getenv("POSTGRES_USER"),
        password = os.getenv("POSTGRES_PASSWORD"),
        host = os.getenv("POSTGRES_HOST"),
        port = os.getenv("POSTGRES_PORT"),
        options=f'-c search_path={os.getenv("POSTGRES_SCHEMA")}')
    
    return conn
    
def setup_database(conn):
    print("DB setup...")
    cur = conn.cursor()
    
    # Create schema
    cur.execute("CREATE SCHEMA IF NOT EXISTS db;")
    
    # Create tables
    cur.execute("""
        CREATE TABLE IF NOT EXISTS db.crime_data (
                pk                          SERIAL PRIMARY KEY,
                id                          INTEGER,
                persistent_id               TEXT UNIQUE,
                month                       TEXT,
                category                    TEXT,
                location_type               TEXT,
                location_subtype            TEXT,
                latitude                    NUMERIC(9,6),
                longitude                   NUMERIC(9,6),
                street_id                   INTEGER,
                street_name                 TEXT,
                context                     TEXT,
                outcome_status_category     TEXT,
                outcome_status_date         TEXT,
                loaded_at                   TIMESTAMP DEFAULT NOW()
                );
            """)

    conn.commit()
    print("Schema and tables created successfully.")
    
    cur.close()

if __name__ == "__main__":
    conn = connect_to_db()
    setup_database(conn)
    conn.close()

