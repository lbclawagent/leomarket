#!/usr/bin/env bash
set -euo pipefail
cd "${PROJECT_ROOT:-$HOME/.openclaw/workspace/leopump}"

echo "== 🐍 User-space Python venv (uv) =="
if ! command -v uv &> /dev/null; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi
uv venv .venv
source .venv/bin/activate

echo "== 📦 Installing dependencies =="
uv pip install -r requirements.txt

echo "== 🌐 Playwright browsers (user-space) =="
playwright install chromium --with-deps

echo "== 📁 Creating pipeline directories =="
mkdir -p data/raw data/parsed data/outputs logs

echo "== ✅ Bootstrap complete. Run: source .venv/bin/activate =="