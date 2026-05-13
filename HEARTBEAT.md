# Heartbeat Tasks

## Z.ai GLM Quota Monitor
- Check current quota status at http://127.0.0.1:8484 (dashboard running on port 8484)
- If dashboard is down: restart with `cd /Users/lbagent/.openclaw/workspace/leopump && nohup uv run python scripts/zai_quota_dashboard.py > /tmp/zai_dashboard.log 2>&1 &`
- Alert rules:
  - If any limit > 90%: warn user
  - If any limit hits 100%: notify immediately and suggest switching to glm-4.5-air
  - Check quota API directly: `curl -s 'https://api.z.ai/api/monitor/usage/quota/limit' -H 'Authorization: 657f634573244b32b07f4210de73f923.yuNbmYMxCdJeH7e4' -H 'Content-Type: application/json'`
