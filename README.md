# Zabbix NGINX PostgreSQL + Grafana
## Example container (docker compose)

- [Official Zabbix Dockerfiles](https://github.com/zabbix/zabbix-docker)
- [Zabbix plugin for Grafana dashboard](https://github.com/grafana/grafana-zabbix)


![scheme](./.images/scheme.excalidraw.png)

For those who are used to using zabbix to collect metrics, but want to start drawing dashboards more beautifully

Example simple docker-compose service

Current versions:
- **Zabbix Server:** 7.2.4
- **PostgreSQL:** 16-alpine
- **Grafana:** 11.6.0

## Guide

### Clone repo:
```
git clone https://github.com/akmalovaa/zabbix-docker.git
cd zabbix-docker
```

### Check or change settings in the `.env` file

### Run docker-compose:
```
docker compose up -d
```

The first launch takes 1-2 minutes

### Zabbix `localhost:8080`
default user password 
- **login:** Admin
- **password:** zabbix


**Zabbix server** - Data Collection / Host / change use connect to DNS `zabbix-agent`
![zabbix-agent](./.images/zabbix-agent-settings.png)
![zabbix-agent](./.images/zabbix-agent-check.png)

### Grafana `localhost:3000` 

default user password (change `grafana/grafana.ini` auth.anonymous enabled)
- **login:** admin
- **password:** 12345

Test data source

`Grafana -> Connections -> Data sources -> zabbix -> Test`
![zabbix-agent](./.images/data-source-test.png)

### Debug
```
docker compose logs --tail=10 -f
```
