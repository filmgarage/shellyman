#!/usr/bin/with-contenv bash
set -euo pipefail

# Home Assistant supplies $INGRESS_PORT; default to 8099
export PORT="${INGRESS_PORT:-8099}"
exec python3 -m app.main
