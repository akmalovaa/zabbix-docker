# Docker compose services: Zabbix NGINX PostgreSQL + Grafana

- [Official Zabbix Dockerfiles](https://github.com/zabbix/zabbix-docker)
- [Zabbix plugin for Grafana dashboard](https://github.com/grafana/grafana-zabbix)

![scheme](./.images/scheme.excalidraw.png)

For those who are used to using zabbix to collect metrics, but want to start drawing dashboards more beautifully

Example simple docker-compose service

- **Postgresql:**                16.2
- **Zabbix Server:**             7.0.0rc1 | 6.4
- **Zabbix Frontend NGINX:**     7.0.0rc1 | 6.4
- **Zabbix Agent:**              7.0.0rc1 | 6.4
- **Grafana:**                   10.3.5

### Guide

1) Clone repo:
```
git clone https://github.com/akmalovaa/zabbix-docker.git
cd zabbix-docker
```

2) Check or change settings in the `.env` file

3) Run docker-compose:
```
docker-compose up -d
```

The first launch takes 1-2 minutes

Zabbix default user password
- login: Admin
- password: zabbix

Grafana default user password (change `grafana/grafana.ini` auth.anonymous enabled)
- login: admin
- password: 12345

### Debug
```
docker-compose logs --tail=1 -f
```
