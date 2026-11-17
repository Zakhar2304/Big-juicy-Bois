#!/bin/bash
# Локальний сайт завжди на http://127.0.0.1:56950
set -euo pipefail
cd "$(dirname "$0")/.."
set -a
# shellcheck disable=SC1091
[ -f .env ] && . ./.env
set +a
HOST="${FLET_WEB_HOST:-127.0.0.1}"
PORT="${FLET_WEB_PORT:-56950}"
exec flet run --web --host "$HOST" -p "$PORT" main.py
