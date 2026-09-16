#!/bin/sh
set -e
# RUN AFTER UPGRADING THE POSTGRES IMAGE, against an empty postgres volume.

# Follow .env instead of hardcoding credentials.
[ -f .env ] && . ./.env
PGUSER="${POSTGRES_USER:-zabbix}"
PGDB="${POSTGRES_DB:-zabbix}"

if [ ! -s pgdump.sql ]; then
    echo "pgdump.sql is missing or empty - run ./db_dump.sh first" >&2
    exit 1
fi

docker compose up -d postgres

i=0
until docker compose exec -T postgres pg_isready -U "$PGUSER" >/dev/null 2>&1; do
    i=$((i + 1))
    if [ "$i" -gt 60 ]; then
        echo "postgres did not become ready within 60s" >&2
        docker compose logs --tail=20 postgres >&2
        exit 1
    fi
    sleep 1
done

# ON_ERROR_STOP is deliberately NOT set: pg_dumpall recreates the role and database
# that the container already created from POSTGRES_USER/POSTGRES_DB, so those two
# statements always fail harmlessly. The table count below is the real success check.
echo "Restoring (\"role/database already exists\" errors are expected)..."
docker compose exec -T postgres psql -U "$PGUSER" -d "$PGDB" < pgdump.sql

tables=$(docker compose exec -T postgres psql -U "$PGUSER" -d "$PGDB" -tAc \
    "select count(*) from information_schema.tables where table_schema = 'public'" | tr -d '[:space:]')

if [ -z "$tables" ] || [ "$tables" -eq 0 ]; then
    echo "Restore failed: no tables in database $PGDB" >&2
    exit 1
fi

echo "Restore OK: $tables tables in $PGDB"
docker compose down
