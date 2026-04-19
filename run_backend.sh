#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$ROOT_DIR/JDParserAgent"
exec "$ROOT_DIR/.venv/bin/python" -m uvicorn api:app --host 127.0.0.1 --port 8001

