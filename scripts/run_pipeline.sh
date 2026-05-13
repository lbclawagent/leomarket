#!/usr/bin/env bash
set -euo pipefail
cd "${PROJECT_ROOT:-$HOME/.openclaw/workspace/leopump}"
source .env
source .venv/bin/activate

echo "== 🧹 Cleaning zombie browsers =="
pkill -f "chromium" 2>/dev/null || true
pkill -f "playwright" 2>/dev/null || true

echo "== 🚀 Starting OpenClaw Cloud-Only Pipeline =="
python tools/llm_router.py --task "pilot_landscape"
echo "== ✅ Execution complete =="