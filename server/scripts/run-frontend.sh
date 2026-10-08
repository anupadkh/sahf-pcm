#!/usr/bin/env bash
# Development only. Production serves the compiled frontend through Nginx.
set -Eeuo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT/frontend"
exec ./node_modules/.bin/ng serve --host 127.0.0.1 --proxy-config "$SCRIPT_DIR/../conf/angular-proxy.json" --port "${PCM_FRONTEND_PORT:-4200}"
