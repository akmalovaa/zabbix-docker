#!/bin/sh
# RUN AFTER UPGRADING POSTGRES IMAGE.

docker compose up -d db
cat pgdump.sql | docker compos postgres zabbix_db_1 psql -U zabbixadmin -d zabbix
docker compose down