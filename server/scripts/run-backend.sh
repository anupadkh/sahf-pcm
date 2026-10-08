#!/usr/bin/env bash
set -Eeuo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ENV_FILE="${PCM_ENV_FILE:-/opt/pcm/shared/pcm.env}"
if [[ -f "$ENV_FILE" ]]; then set -a; source "$ENV_FILE"; set +a; fi
cd "$PROJECT_ROOT/backend"
exec "${PCM_PYTHON:-$PROJECT_ROOT/backend/.venv/bin/python}" -m uvicorn app.main:app --host "${PCM_HOST:-127.0.0.1}" --port "${PCM_PORT:-8000}" --workers 1 --proxy-headers --forwarded-allow-ips=127.0.0.1
