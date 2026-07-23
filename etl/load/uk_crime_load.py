import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

def ensure_table(conn, table_name):
    cur = conn.cursor()
    cur.execute(f"""SELECT EXISTS ( SELECT 1 
                                    FROM information_schema.tables 
                                    WHERE table_schema = 'db' 
                                    AND table_name = '{table_name}' );""")
    res = cur.fetchone()
    cur.close()
    return res


def load_crimes(conn, parquet_path, table_name):
    df = pd.read_parquet(parquet_path)
    cols = ['id', 'persistent_id', 'month', 'category', 'location_type', 
            'location_subtype', 'latitude', 'longitude', 'street_id', 'street_name', 
            'context', 'outcome_status_category', 'outcome_status_date']
    rows = list(df[cols].itertuples(index=False, name=None))

    cols_str = ", ".join(f"{el}" for el in cols)
    sql = f"""INSERT INTO {table_name} ({cols_str})
                VALUES %s
                ON CONFLICT (persistent_id) DO NOTHING"""
    
    cur = conn.cursor()
    execute_values(
        cur, sql
       , rows
    )
    conn.commit()
    cur.close()
