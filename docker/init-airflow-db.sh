#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FIL="$SCRIPT_DIR/../.env"

if [ ! -f "$ENV_FILE" ]; then
    echo "Error: .env file not found at $ENV_FILE" >&2
    exit 1
fi

set -a
source <(sed 's/[[:space:]]*=[[:space:]]*/=/' "$ENV_FILE")
set +a

export PGPASSWORD="$POSTGRES_PASSWORD"

psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
    -v new_user="$POSTGRES_USER_AIRFLOW" \
    -v new_pass="$POSTGRES_PASSWORD_AIRFLOW" \
    -c "CREATE USER :new_user WITH PASSWORD :new_pass IF NOT EXISTS;"

echo "Created user $POSTGRES_USER_AIRFLOW"

psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
    -v db_name="$POSTGRES_DB_AIRFLOW" \
    -v db_owner="$POSTGRES_USER_AIRFLOW"
    -c "CREATE DATABASE :db_name OWNER :db_owner;"

echo "DB $POSTGRES_DB_AIRFLOW exists"