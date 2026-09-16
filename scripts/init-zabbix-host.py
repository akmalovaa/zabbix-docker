#!/usr/bin/env python3
"""Point the bundled "Zabbix server" host at the agent container by DNS name.

The stock host ships from the schema import with a hardcoded 127.0.0.1 agent
interface, which inside Docker resolves to the server container's own loopback
rather than the agent. Without this, every agent item fails with
"Cannot establish TCP connection to [[127.0.0.1]:10050]".

Runs as a one-shot service on every `docker compose up` and is idempotent:
if the interface already points at the right DNS name, it exits without writing.
Standard library only - no pip install, no extra image layers.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request

API_URL = os.environ.get("ZBX_API_URL", "http://zabbix-frontend:8080/api_jsonrpc.php")
USER = os.environ.get("ZABBIX_API_USER", "Admin")
PASSWORD = os.environ.get("ZABBIX_API_PASSWORD", "zabbix")
HOST_NAME = os.environ.get("ZBX_INIT_HOST", "Zabbix server")
AGENT_DNS = os.environ.get("ZBX_INIT_DNS", "zabbix-agent")
# The schema import and the first server start take a while on a fresh volume.
TIMEOUT = int(os.environ.get("ZBX_INIT_TIMEOUT", "300"))

INTERFACE_TYPE_AGENT = "1"


def log(message):
    print(f"[init-zabbix-host] {message}", flush=True)


def call(method, params, token=None):
    """One JSON-RPC call. Raises RuntimeError on an API-level error."""
    payload = json.dumps({"jsonrpc": "2.0", "method": method, "params": params, "id": 1})
    request = urllib.request.Request(
        API_URL,
        data=payload.encode(),
        headers={"Content-Type": "application/json-rpc"},
    )
    # Zabbix 7.0+ takes the auth token in the header; the old "auth" param is rejected.
    if token:
        request.add_header("Authorization", f"Bearer {token}")

    with urllib.request.urlopen(request, timeout=10) as response:
        body = json.load(response)

    if "error" in body:
        raise RuntimeError(f"{method}: {body['error'].get('data', body['error'])}")
    return body["result"]


def wait_for_login():
    """Retry until the API answers and the credentials work, or give up."""
    deadline = time.monotonic() + TIMEOUT
    last_error = None
    while time.monotonic() < deadline:
        try:
            return call("user.login", {"username": USER, "password": PASSWORD})
        except (urllib.error.URLError, RuntimeError, OSError, ValueError) as exc:
            last_error = exc
            time.sleep(3)
    raise SystemExit(f"[init-zabbix-host] API not usable within {TIMEOUT}s: {last_error}")


def main():
    token = wait_for_login()
    log(f"authenticated at {API_URL}")

    hosts = call("host.get", {
        "filter": {"host": HOST_NAME},
        "selectInterfaces": ["interfaceid", "type", "useip", "ip", "dns", "port"],
    }, token)

    if not hosts:
        log(f"host {HOST_NAME!r} not found - nothing to do")
        return

    interfaces = [i for i in hosts[0]["interfaces"] if i["type"] == INTERFACE_TYPE_AGENT]
    if not interfaces:
        log(f"host {HOST_NAME!r} has no agent interface - nothing to do")
        return

    interface = interfaces[0]
    if interface["useip"] == "0" and interface["dns"] == AGENT_DNS:
        log(f"interface {interface['interfaceid']} already uses DNS {AGENT_DNS!r} - no change")
        return

    call("hostinterface.update", {
        "interfaceid": interface["interfaceid"],
        "useip": 0,
        "dns": AGENT_DNS,
    }, token)
    log(f"interface {interface['interfaceid']}: {interface['ip']} -> DNS {AGENT_DNS!r}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 - a failure here must not block the stack
        log(f"failed: {exc}")
        sys.exit(1)
