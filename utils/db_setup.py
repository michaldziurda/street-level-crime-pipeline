import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

def connect_to_db():
    load_dotenv()
    conn = psycopg2.connect(
        dbname = os.getenv("DB_NAME"),
        user = os.getenv("DB_USER"),
        password = os.getenv("DB_PASSWORD"),
        host = os.getenv("DB_HOST"),
        port = os.getenv("DB_PORT"),
        options=f'-c search_path={os.getenv("DB_SCHEMA")}')
    
    return conn
    
def setup_uk_database(conn):
    load_dotenv()
    print("DB setup...")
    cur = conn.cursor()
    
    # Create schema
    cur.execute(f"""CREATE SCHEMA IF NOT EXISTS {sql.Identifier(os.getenv('DB_SCHEMA'))};""")
    
    # Create tables
    cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {sql.Identifier(os.getenv("DB_SCHEMA"))}.{sql.Identifier(os.getenv("UK_CRIMES_TABLE"))} (
                pk                          SERIAL PRIMARY KEY,
                id                          INTEGER,
                persistent_id               TEXT UNIQUE,
                month                       TEXT,
                category                    TEXT,
                location_type               TEXT,
                location_subtype            TEXT,
                latitude                    NUMERIC(9,6),
                longitude                   NUMERIC(9,6),
                region                      TEXT,
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
    setup_uk_database(conn)
    conn.close()

