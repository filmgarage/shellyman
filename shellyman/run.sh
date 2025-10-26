#!/usr/bin/with-contenv bash
set -euo pipefail

export PORT="${INGRESS_PORT:-8099}"

# Run from FS root so the top-level package "app" is importable
cd /
exec /venv/bin/python -m app.main
