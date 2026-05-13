#!/usr/bin/env python3
"""Z.ai GLM API Rate Tracker Dashboard v2.
Features: Quota monitoring, prompt counts, per-model breakdown, multi-day trends, yesterday comparison.
"""
import json, urllib.request, urllib.parse, ssl, os, time
from datetime import datetime, timezone, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

API_KEY = os.environ.get("ZAI_API_KEY", "657f634573244b32b07f4210de73f923.yuNbmYMxCdJeH7e4")
PORT = 8484
REFRESH_INTERVAL = 60
DATA_FILE = Path(os.environ.get("ZAI_DATA_DIR", "/Users/lbagent/.openclaw/workspace/leopump/data")) / "zai_quota_history.jsonl"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BDT = timezone(timedelta(hours=6))

def fetch_json(url):
    req = urllib.request.Request(url, headers={
        "Authorization": API_KEY,
        "Content-Type": "application/json",
        "User-Agent": "LeoPump-Dashboard/2.0"
    })
    with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
        return json.loads(resp.read().decode())

def fetch_quota():
    try:
        data = fetch_json("https://api.z.ai/api/monitor/usage/quota/limit")
        return data.get("data", {})
    except Exception as e:
        return {"error": str(e)}

def fetch_usage(day_offset=0):
    """Fetch hourly usage for a specific day."""
    target = datetime.now(BDT) - timedelta(days=day_offset)
    start = target.replace(hour=0, minute=0, second=0)
    end = target.replace(hour=23, minute=59, second=59)
    start_str = start.strftime("%Y-%m-%d %H:%M:%S")
    end_str = end.strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        url = f"https://api.z.ai/api/monitor/usage/model-usage?startTime={urllib.parse.quote(start_str)}&endTime={urllib.parse.quote(end_str)}"
        data = fetch_json(url)
        return data.get("data", {})
    except Exception as e:
        return {"error": str(e)}

def append_history(quota_data, usage_today):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now(BDT).isoformat(),
        "limits": quota_data.get("limits", []),
        "level": quota_data.get("level", "unknown"),
        "totalCalls": usage_today.get("totalUsage", {}).get("totalModelCallCount", 0),
        "totalTokens": usage_today.get("totalUsage", {}).get("totalTokensUsage", 0),
    }
    with open(DATA_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def fmt_tokens(t):
    if t >= 1_000_000: return f"{t/1_000_000:.2f}M"
    if t >= 1_000: return f"{t/1_000:.1f}K"
    return str(t)

def fmt_reset(ts_ms):
    if not ts_ms: return "N/A"
    dt = datetime.fromtimestamp(ts_ms / 1000, tz=BDT)
    delta = dt - datetime.now(BDT)
    if delta.total_seconds() < 0: return "Resetting..."
    h = int(delta.total_seconds() // 3600)
    m = int((delta.total_seconds() % 3600) // 60)
    return f"{dt.strftime('%H:%M')} ({h}h {m}m left)"

def generate_html(quota, usage_today, usage_yesterday):
    limits = quota.get("limits", [])
    level = quota.get("level", "unknown")
    
    # ─── LIMIT CARDS ───
    limit_cards = ""
    for lim in limits:
        ltype = lim.get("type", "")
        unit = lim.get("unit", "")
        number = lim.get("number", "")
        pct = lim.get("percentage", 0)
        usage_val = lim.get("usage", 0)
        current = lim.get("currentValue", 0)
        remaining = lim.get("remaining", 0)
        reset_ts = lim.get("nextResetTime", 0)
        details = lim.get("usageDetails", [])
        
        if pct >= 90: color, status = "#ef4444", "CRITICAL"
        elif pct >= 70: color, status = "#f59e0b", "WARNING"
        else: color, status = "#22c55e", "OK"
        
        unit_labels = {3: "3-hour", 5: "5-hour", 6: "6-hour"}
        type_labels = {"TOKENS_LIMIT": "Token Limit", "TIME_LIMIT": "Request Limit"}
        
        details_html = ""
        if details:
            details_html = '<div class="details">' + "".join(
                f'<span class="tag">{d.get("modelCode","?")}: {d.get("usage",0)}</span>' for d in details
            ) + '</div>'
        
        bar_pct = min(pct, 100)
        
        limit_cards += f"""
        <div class="card">
            <div class="card-head"><span class="label">{type_labels.get(ltype,ltype)}</span><span class="badge" style="color:{color}">● {status}</span></div>
            <div class="sublabel">{unit_labels.get(unit,f"{unit}-hour")} window</div>
            <div class="bar"><div class="fill" style="width:{bar_pct}%;background:{color}"></div></div>
            <div class="pct" style="color:{color}">{pct}%</div>
            {"<div class='info'>" + str(current) + " used / " + str(remaining) + " remaining</div>" if remaining else ""}
            {"<div class='info'>" + str(usage_val) + " requests this window</div>" if usage_val else ""}
            {details_html}
            <div class="reset">Resets: {fmt_reset(reset_ts)}</div>
        </div>"""
    
    # ─── TODAY STATS ───
    today_total = usage_today.get("totalUsage", {})
    today_calls = today_total.get("totalModelCallCount", 0)
    today_tokens = today_total.get("totalTokensUsage", 0)
    today_models = today_total.get("modelSummaryList", [])
    
    yest_total = usage_yesterday.get("totalUsage", {})
    yest_calls = yest_total.get("totalModelCallCount", 0)
    yest_tokens = yest_total.get("totalTokensUsage", 0)
    
    calls_delta = f"+{today_calls - yest_calls}" if today_calls >= yest_calls else str(today_calls - yest_calls)
    tokens_delta = f"+{fmt_tokens(today_tokens - yest_tokens)}" if today_tokens >= yest_tokens else fmt_tokens(today_tokens - yest_tokens)
    
    model_cards = ""
    for m in today_models:
        name = m.get("modelName", "?")
        tokens = m.get("totalTokens", 0)
        model_cards += f'<div class="model-chip"><span class="model-name">{name}</span><span class="model-val">{fmt_tokens(tokens)} tokens</span></div>'
    
    # ─── PROMPT COUNT CHART ───
    times = usage_today.get("x_time", [])
    calls = usage_today.get("modelCallCount", [])
    model_data = usage_today.get("modelDataList", [])
    
    max_call = max(calls) if calls and max(calls) > 0 else 1
    
    chart_bars = ""
    for i, (t, c) in enumerate(zip(times, calls)):
        height = (c / max_call * 100) if max_call > 0 else 0
        hour = t.split(" ")[-1] if " " in t else t
        chart_bars += f"""<div class="col"><div class="bar-v" style="height:{height}%"><span class="bar-n">{c}</span></div><span class="col-l">{hour}</span></div>"""
    
    # Model-specific chart
    model_charts = ""
    colors = {"GLM-5.1": "#3b82f6", "GLM-4.5-Air": "#8b5cf6", "GLM-4.5": "#f59e0b", "GLM-4.5-Flash": "#22c55e"}
    for md in model_data:
        name = md.get("modelName", "?")
        tokens_list = md.get("tokensUsage", [])
        c = colors.get(name, "#6b7280")
        max_t = max(tokens_list) if tokens_list and max(tokens_list) > 0 else 1
        
        bars = ""
        for i, (t, tv) in enumerate(zip(times, tokens_list)):
            height = (tv / max_t * 100) if max_t > 0 else 0
            hour = t.split(" ")[-1] if " " in t else t
            bars += f"""<div class="col"><div class="bar-v" style="height:{height}%;background:{c}"></div><span class="col-l">{hour}</span></div>"""
        
        model_charts += f"""
        <div class="model-chart">
            <div class="chart-title"><span style="color:{c}">●</span> {name} — {fmt_tokens(md.get('totalTokens',0))} tokens</div>
            <div class="chart">{bars}</div>
        </div>"""
    
    # ─── ACTIVE HOUR HEATMAP ───
    peak_hour = "N/A"
    peak_calls = 0
    for t, c in zip(times, calls):
        if c > peak_calls:
            peak_calls = c
            peak_hour = t.split(" ")[-1] if " " in t else t
    
    now_str = datetime.now(BDT).strftime("%H:%M:%S")
    date_str = datetime.now(BDT).strftime("%A, %B %d, %Y")
    
    return f"""<!DOCTYPE html>
<html><head>
<title>Z.ai GLM Quota Dashboard</title>
<meta http-equiv="refresh" content="{REFRESH_INTERVAL}">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'SF Mono','Fira Code',monospace;background:#0a0a0a;color:#e0e0e0;padding:20px;max-width:960px;margin:0 auto}}
.top{{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #1e1e1e;padding-bottom:12px;margin-bottom:20px}}
.top h1{{font-size:18px;font-weight:600}}.top h1 em{{color:#3b82f6;font-style:normal}}
.meta{{font-size:11px;color:#666}}.meta .plan{{background:#1e293b;padding:2px 8px;border-radius:3px;color:#60a5fa;font-weight:600;margin-left:6px}}
.section{{margin-bottom:24px}}.section h2{{font-size:13px;color:#888;margin-bottom:10px;text-transform:uppercase;letter-spacing:1px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px}}
.card{{background:#111;border:1px solid #1e1e1e;border-radius:6px;padding:14px}}.card:hover{{border-color:#333}}
.card-head{{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px}}.card-head .label{{font-size:13px;font-weight:600}}.card-head .badge{{font-size:11px;font-weight:600}}
.sublabel{{font-size:11px;color:#666;margin-bottom:6px}}
.bar{{height:6px;background:#1e1e1e;border-radius:3px;overflow:hidden;margin-bottom:6px}}.fill{{height:100%;border-radius:3px;transition:width .5s}}
.pct{{font-size:28px;font-weight:700;margin-bottom:2px}}.info{{font-size:11px;color:#666;margin-top:2px}}.reset{{font-size:10px;color:#444;margin-top:8px;padding-top:6px;border-top:1px solid #1a1a1a}}
.details{{margin-top:6px}}.tag{{display:inline-block;background:#1e293b;padding:1px 6px;border-radius:2px;font-size:10px;margin:1px 2px}}
/* Stats row */
.stats{{display:flex;gap:16px;flex-wrap:wrap;margin-bottom:16px}}
.stat{{background:#111;border:1px solid #1e1e1e;border-radius:6px;padding:12px 16px;min-width:140px}}
.stat .stat-label{{font-size:10px;color:#666;text-transform:uppercase;letter-spacing:.5px}}.stat .stat-val{{font-size:22px;font-weight:700;margin-top:2px}}.stat .stat-delta{{font-size:10px;color:#666;margin-top:2px}}
.stat .stat-delta .up{{color:#22c55e}}.stat .stat-delta .down{{color:#ef4444}}
/* Model breakdown */
.models{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px}}
.model-chip{{background:#111;border:1px solid #1e1e1e;border-radius:4px;padding:6px 12px;display:flex;gap:8px;align-items:center}}
.model-name{{font-size:12px;font-weight:600;color:#60a5fa}}.model-val{{font-size:11px;color:#888}}
/* Charts */
.chart-box{{background:#111;border:1px solid #1e1e1e;border-radius:6px;padding:14px;margin-bottom:12px}}
.chart-title{{font-size:11px;color:#888;margin-bottom:8px}}
.chart{{display:flex;align-items:flex-end;gap:1px;height:100px;border-bottom:1px solid #222;padding-bottom:2px}}
.col{{flex:1;display:flex;flex-direction:column;align-items:center;height:100%;justify-content:flex-end}}
.bar-v{{width:100%;max-width:28px;background:#3b82f6;border-radius:2px 2px 0 0;min-height:1px;position:relative;transition:height .3s}}.bar-v:hover{{opacity:.8}}
.bar-n{{position:absolute;top:-14px;left:50%;transform:translateX(-50%);font-size:8px;color:#666;white-space:nowrap}}
.col-l{{font-size:8px;color:#444;margin-top:3px}}
.model-chart{{margin-top:12px}}
/* Peak */
.peak{{display:flex;gap:12px;font-size:11px;color:#666;margin-top:8px}}.peak strong{{color:#e0e0e0}}
.foot{{margin-top:20px;padding-top:12px;border-top:1px solid #1a1a1a;font-size:10px;color:#333;display:flex;justify-content:space-between}}
</style>
</head><body>

<div class="top">
    <div>
        <h1>⚡ <em>Z.ai</em> GLM Quota Monitor</h1>
        <div class="meta">{date_str} — Updated {now_str} (auto {REFRESH_INTERVAL}s)<span class="plan">{level.upper()}</span></div>
    </div>
</div>

<!-- QUOTA LIMITS -->
<div class="section">
<h2>📊 Quota Limits</h2>
<div class="grid">{limit_cards}</div>
</div>

<!-- PROMPT STATS -->
<div class="section">
<h2>🔢 Prompt Usage Today</h2>
<div class="stats">
    <div class="stat">
        <div class="stat-label">Total Prompts</div>
        <div class="stat-val">{today_calls}</div>
        <div class="stat-delta"><span class="{"up" if today_calls >= yest_calls else "down"}">{calls_delta} vs yesterday ({yest_calls})</span></div>
    </div>
    <div class="stat">
        <div class="stat-label">Total Tokens</div>
        <div class="stat-val">{fmt_tokens(today_tokens)}</div>
        <div class="stat-delta"><span class="{"up" if today_tokens >= yest_tokens else "down"}">{tokens_delta} vs yesterday ({fmt_tokens(yest_tokens)})</span></div>
    </div>
    <div class="stat">
        <div class="stat-label">Peak Hour</div>
        <div class="stat-val">{peak_hour}</div>
        <div class="stat-delta">{peak_calls} prompts</div>
    </div>
    <div class="stat">
        <div class="stat-label">Avg Tokens/Prompt</div>
        <div class="stat-val">{fmt_tokens(today_tokens // today_calls) if today_calls > 0 else "N/A"}</div>
        <div class="stat-delta">across all models</div>
    </div>
</div>
<div class="models">{model_cards}</div>
</div>

<!-- HOURLY CHART -->
<div class="section">
<h2>📈 Hourly Activity</h2>
<div class="chart-box">
    <div class="chart-title">Prompts per Hour (all models)</div>
    <div class="chart">{chart_bars}</div>
</div>
{model_charts}
</div>

<div class="foot">
    <span>Leo Pump Project — Market Intelligence Agent</span>
    <span>api.z.ai/monitor • v2.0</span>
</div>

</body></html>"""


class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            quota = fetch_quota()
            usage_today = fetch_usage(day_offset=0)
            usage_yesterday = fetch_usage(day_offset=1)
            append_history(quota, usage_today)
            html = generate_html(quota, usage_today, usage_yesterday)
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode())
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(f"Error: {e}".encode())
    
    def log_message(self, fmt, *args): pass


if __name__ == "__main__":
    print(f"🚀 Z.ai GLM Quota Dashboard v2 on http://localhost:{PORT}")
    print(f"   Refresh: {REFRESH_INTERVAL}s | Data: {DATA_FILE}")
    server = HTTPServer(("127.0.0.1", PORT), DashboardHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Stopped")
