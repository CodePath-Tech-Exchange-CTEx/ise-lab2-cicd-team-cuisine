#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if [ -f .venv/bin/activate ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

python -m playwright install chromium
E2E_BASE_URL=${E2E_BASE_URL:-http://localhost:8080} PYTHONPATH=. python -m pytest tests/e2e -q
