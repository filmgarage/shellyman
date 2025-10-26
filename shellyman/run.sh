
#!/usr/bin/with-contenv bash
set -euo pipefail

ls -R /app
ls -R /main

export PORT="${INGRESS_PORT:-8099}"
exec /venv/bin/python -m app.main
