#!/usr/bin/env bash
# Renews the Tailscale TLS cert and reloads nginx without downtime.
# Scheduling: crontab -e → 0 0 1 * * /path/to/scripts/renew-cert.sh
#
# TS_HOSTNAME must be set in environment or in .env at repo root.
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Load .env if TS_HOSTNAME not already set
if [ -z "$TS_HOSTNAME" ] && [ -f "$REPO_ROOT/.env" ]; then
    export $(grep -E '^TS_HOSTNAME=' "$REPO_ROOT/.env" | xargs)
fi

if [ -z "$TS_HOSTNAME" ]; then
    echo "Error: TS_HOSTNAME is not set. Add it to .env or export it." >&2
    exit 1
fi

CERTS_DIR="$REPO_ROOT/certs"
mkdir -p "$CERTS_DIR"

tailscale cert --cert-file "$CERTS_DIR/server.crt" --key-file "$CERTS_DIR/server.key" "$TS_HOSTNAME"

# Reload nginx if container is already running (renewal case)
if docker ps --format '{{.Names}}' | grep -q '^frontend$'; then
    docker exec frontend nginx -s reload
    echo "Cert renewed and nginx reloaded."
else
    echo "Cert written to $CERTS_DIR — nginx will pick it up on next start."
fi
