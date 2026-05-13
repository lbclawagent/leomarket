#!/usr/bin/env bash
cd "${PROJECT_ROOT:-$HOME/.openclaw/workspace/leopump}"
find ./data/raw -type f -mtime +3 -delete 2>/dev/null || true
find ./logs -type f -name "*.log" -mtime +7 -delete 2>/dev/null || true
find ./data/parsed -type f -name "*.json" -mtime +7 -exec gzip -f {} \; 2>/dev/null || true
echo "== ✅ SSD rotation complete =="