import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from psycopg2 import sql

def check_if_table_exists(conn, table_name):
    cur = conn.cursor()
    cur.execute(sql.SQL("""
                        SELECT EXISTS ( SELECT 1 
                        FROM information_schema.tables 
                        WHERE table_schema = 'db' 
                        AND table_name = '{table}' );""").format(
                            table=sql.Identifier(table_name)
                        ))
    res = cur.fetchone()
    cur.close()
    return res


def load_crimes(conn, parquet_path, table_name):
    df = pd.read_parquet(parquet_path)
    cols = ['id', 'persistent_id', 'month', 'category', 'location_type', 
            'location_subtype', 'latitude', 'longitude', 'street_id', 'street_name', 
            'context', 'outcome_status_category', 'outcome_status_date']
    rows = list(df[cols].itertuples(index=False, name=None))

    stmt = sql.SQL("""
                INSERT INTO {table} ({columns})
                VALUES %s
                ON CONFLICT ({conflict_col}) DO NOTHING""").format(
                    table=sql.Identifier(table_name),
                    columns=sql.SQL(', ').join(map(sql.Identifier, cols)),
                    conflict_col=sql.Identifier('persistent_id'))
    
    cur = conn.cursor()
    execute_values(cur, stmt, rows)
    conn.commit()
    cur.close()
