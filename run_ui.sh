#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$ROOT_DIR"
exec "$ROOT_DIR/.venv/bin/python" -m streamlit run dashboard.py --server.headless true --server.port 8501 --server.address 127.0.0.1

