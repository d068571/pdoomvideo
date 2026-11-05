#!/usr/bin/env bash
# Recreate the AI Futures Model playground from scratch.
# Usage: bash setup.sh [target_dir]   (default: ./aifm-public)
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${1:-aifm-public}"
COMMIT=1c40ecd   # version verified identical to the live site on 2026-11-05
if [ ! -d "$TARGET/.git" ]; then
  git clone https://github.com/AI-Futures-Project/aifm-public.git "$TARGET"
fi
cd "$TARGET"
git checkout -q "$COMMIT" 2>/dev/null || echo "note: $COMMIT not found; using $(git rev-parse --short HEAD)"
# Local fix: /api/default-data references a helper missing from the public repo.
sed -i "s|resolve_serial_uplift_at_reference_date(params),|float(params.serial_uplift_at_reference_date),  # local fix|" api/index.py
# Copy playground files next to the model if this script lives elsewhere.
if [ "$HERE" != "$(pwd)/playground" ]; then mkdir -p playground && cp -n "$HERE"/{aifm.py,playground.ipynb,export_presets.ts,README.md,start.sh} playground/ 2>/dev/null || true; fi
command -v uv >/dev/null || pip install uv
uv python install 3.14
[ -d .venv ] || uv venv --python 3.14 .venv
uv pip install --python .venv/bin/python -r requirements.txt pytest jupyterlab matplotlib pandas
npm install --no-audit --no-fund
npx tsx playground/export_presets.ts playground/presets.json
echo "Done. Next: cd $TARGET && source .venv/bin/activate && python -m playground.aifm"
