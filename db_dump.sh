#!/bin/sh
set -e
# RUN BEFORE UPGRADING THE POSTGRES IMAGE TO A NEW MAJOR VERSION.
# The PostgreSQL data directory is not compatible across majors, so the upgrade is:
#   ./db_dump.sh  ->  edit POSTGRES_IMAGE in .env  ->  docker volume rm <project>_postgres  ->  ./db_restore.sh

# Follow .env instead of hardcoding credentials.
[ -f .env ] && . ./.env
PGUSER="${POSTGRES_USER:-zabbix}"

docker compose down
docker compose up -d postgres

# Wait for the healthcheck rather than guessing with a fixed sleep.
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

docker compose exec -T postgres pg_dumpall -U "$PGUSER" > pgdump.sql

if [ ! -s pgdump.sql ]; then
    echo "Dump is empty - aborting so it cannot overwrite good data later" >&2
    exit 1
fi

echo "Dump created: $(wc -c < pgdump.sql) bytes"
docker compose down
