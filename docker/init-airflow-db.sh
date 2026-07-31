#!/bin/bash

set -e

psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
    -c "CREATE USER airflow WITH PASSWORD 'airflow';"

echo "Created user $POSTGRES_USER_AIRFLOW"

psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
    -c "CREATE DATABASE airflow OWNER airflow;"

echo "DB $POSTGRES_DB_AIRFLOW exists"