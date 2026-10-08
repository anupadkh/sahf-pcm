#!/usr/bin/env bash
# Installed once at /opt/pcm/bin/deploy.sh. Run as pcm, never root.
set -Eeuo pipefail
[[ "$(id -u)" != 0 ]] || { echo "Run this script as pcm, not root" >&2; exit 1; }
DEPLOY_ROOT=/opt/pcm
RELEASE_ID="${1:?Usage: deploy.sh COMMIT_SHA}"
[[ "$RELEASE_ID" =~ ^[0-9a-f]{40}$ ]] || { echo "Invalid commit SHA" >&2; exit 1; }
exec 9>"$DEPLOY_ROOT/shared/deploy.lock"
flock -n 9 || { echo "Another deployment is running" >&2; exit 1; }
ARCHIVE="$DEPLOY_ROOT/uploads/$RELEASE_ID.tar.gz"
RELEASE="$DEPLOY_ROOT/releases/$RELEASE_ID-$(date -u +%Y%m%d%H%M%S)"
mkdir "$RELEASE"
# Archives are produced by the trusted CI job and contain backend, frontend and server only.
tar -xzf "$ARCHIVE" -C "$RELEASE" --no-same-owner
[[ -f "$RELEASE/backend/requirements.txt" && -f "$RELEASE/frontend/dist/pcm/browser/index.html" ]] || { echo "Incomplete release" >&2; exit 1; }
python3 -m venv "$RELEASE/backend/.venv"
"$RELEASE/backend/.venv/bin/python" -m pip install --disable-pip-version-check -r "$RELEASE/backend/requirements.txt"
"$RELEASE/backend/.venv/bin/python" -m pip check
chmod +x "$RELEASE"/server/scripts/*.sh
set -a; source "$DEPLOY_ROOT/shared/pcm.env"; set +a
[[ "$PCM_DB" == "$DEPLOY_ROOT/shared/pcm.sqlite3" ]] || { echo "Unexpected database location" >&2; exit 1; }
PREVIOUS="$(readlink -f "$DEPLOY_ROOT/current" || true)"
if [[ -f "$PCM_DB" ]]; then
    BACKUP="$DEPLOY_ROOT/shared/backups/before-$RELEASE_ID-$(date -u +%Y%m%d%H%M%S).sqlite3"
    "$RELEASE/backend/.venv/bin/python" - "$PCM_DB" "$BACKUP" <<'PY'
import sqlite3, sys
with sqlite3.connect(sys.argv[1]) as source, sqlite3.connect(sys.argv[2]) as target:
    source.backup(target)
PY
fi
activate() {
    ln -sfn "$1" "$DEPLOY_ROOT/current.next"
    mv -Tf "$DEPLOY_ROOT/current.next" "$DEPLOY_ROOT/current"
    sudo /usr/bin/supervisorctl restart pcm-backend
}
if activate "$RELEASE"; then
    for attempt in $(seq 1 30); do
        if curl --fail --silent http://127.0.0.1:8000/api/health >/dev/null; then
            echo "Deployed $RELEASE_ID"; exit 0
        fi
        sleep 2
    done
fi
echo "Deployment failed; rolling code back" >&2
if [[ -n "$PREVIOUS" && -d "$PREVIOUS" ]]; then activate "$PREVIOUS"; fi
# Keep the database and backup intact. Restore DB only with deliberate operator review.
exit 1
