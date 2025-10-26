#!/usr/bin/with-contenv bash
set -euo pipefail

export PORT="${INGRESS_PORT:-8099}"
exec /venv/bin/python -m app.main
