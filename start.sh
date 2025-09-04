#!/usr/bin/env bash
set -euo pipefail

# Render provides $PORT
: "${PORT:=10000}"

exec gunicorn --bind 0.0.0.0:"${PORT}" run:app
