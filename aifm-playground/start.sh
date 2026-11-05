#!/usr/bin/env bash
# Start the full website locally: Flask API on :5328 + Next.js on :3000.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
source .venv/bin/activate
python -m flask --app api/index run -p "${FLASK_DEV_PORT:-5328}" &
FLASK_PID=$!
trap 'kill $FLASK_PID' EXIT
npx next dev --port "${PORT:-3000}"
