#!/bin/bash
set -e

create_database() {
    local db_name=$1
    echo "  Creating database '$db_name'"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
        CREATE DATABASE "$db_name";
EOSQL
}

if [ -n "$POSTGRES_MULTIPLE_DBS" ]; then
    echo "Multiple database creation requested: $POSTGRES_MULTIPLE_DBS"
    for db in $(echo "$POSTGRES_MULTIPLE_DBS" | tr ',' ' '); do
        create_database "$db"
    done
    echo "Multiple databases created"
fi 