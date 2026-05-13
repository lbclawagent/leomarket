#!/usr/bin/env python3
"""Leo Pump LLM Router v2.4 — Cloud-Only GLM Routing.
Fast extraction → glm-4.5-air | Heavy reasoning → glm-5.1
"""
import os, sys, json, backoff, requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")
PROJECT_ROOT = os.getenv("PROJECT_ROOT", str(Path(__file__).parent.parent))
if PROJECT_ROOT.startswith("$HOME"):
    PROJECT_ROOT = str(Path.home() / ".openclaw/workspace/leopump")
API_KEY = os.getenv("ZLM_API_KEY")
BASE_URL = os.getenv("ZLM_BASE_URL", "https://api.z.ai/api/anthropic")
TIMEOUT = int(os.getenv("API_TIMEOUT_MS", 120000)) / 1000

# ─── Fast Extraction (glm-4.5-air) ───
@backoff.on_exception(backoff.expo, Exception, max_tries=int(os.getenv("MAX_RETRIES", 3)))
def call_fast(prompt: str, system: str = "Extract structured JSON only.") -> dict:
    """Fast extraction: cleaning, translation, price normalization, field mapping."""
    headers = {
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    payload = {
        "model": os.getenv("FAST_MODEL", "glm-4.5-air"),
        "max_tokens": 4096,
        "system": system,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": float(os.getenv("FAST_TEMPERATURE", 0.2))
    }
    r = requests.post(f"{BASE_URL}/v1/messages", headers=headers, json=payload, timeout=TIMEOUT)
    r.raise_for_status()
    response_text = r.json()["content"][0]["text"]
    # Try to parse as JSON, fallback to raw text
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        return {"raw_text": response_text}

# ─── Heavy Reasoning (glm-5.1) ───
@backoff.on_exception(backoff.expo, Exception, max_tries=int(os.getenv("MAX_RETRIES", 3)))
def call_reasoning(prompt: str, system: str = "You are a Dhaka-based senior market analyst specializing in infrastructure, agriculture, and industrial equipment in Bangladesh.") -> dict:
    """Heavy reasoning: triangulation, strategy synthesis, zone sizing, competitor analysis."""
    headers = {
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    payload = {
        "model": os.getenv("REASONING_MODEL", "glm-5.1"),
        "max_tokens": int(os.getenv("REASONING_MAX_TOKENS", 4096)),
        "system": system,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": float(os.getenv("REASONING_TEMPERATURE", 0.3))
    }
    r = requests.post(f"{BASE_URL}/v1/messages", headers=headers, json=payload, timeout=TIMEOUT)
    r.raise_for_status()
    response_text = r.json()["content"][0]["text"]
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        return {"raw_text": response_text}

# ─── Legacy aliases (backward compat) ───
call_deepseek = call_fast
call_zlm = call_reasoning

# ─── Output helpers ───
def save_output(filename: str, data: dict):
    out_dir = Path(f"{PROJECT_ROOT}/data/outputs")
    out_dir.mkdir(parents=True, exist_ok=True)
    filepath = out_dir / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  💾 Saved: {filepath}")
    return filepath

def save_markdown(filename: str, content: str):
    out_dir = Path(f"{PROJECT_ROOT}/data/outputs")
    out_dir.mkdir(parents=True, exist_ok=True)
    filepath = out_dir / filename
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  💾 Saved: {filepath}")
    return filepath

# ─── Phase Execution ───
def run_phase(phase: str):
    """Run a specific pipeline phase."""
    print(f"\n{'='*60}")
    print(f"🚀 Phase: {phase}")
    print(f"{'='*60}")
    
    if phase == "zone_sizing":
        run_zone_sizing()
    elif phase == "competitor_heatmap":
        run_competitor_heatmap()
    elif phase == "consumer_insights":
        run_consumer_insights()
    elif phase == "gtm_strategy":
        run_gtm_strategy()
    elif phase == "all":
        run_zone_sizing()
        run_competitor_heatmap()
        run_consumer_insights()
        run_gtm_strategy()
    else:
        print(f"Unknown phase: {phase}")
        print("Available: zone_sizing, competitor_heatmap, consumer_insights, gtm_strategy, all")

def run_zone_sizing():
    """Phase 1a: Zone-based market sizing using installed base + replacement rates."""
    print("\n📊 Phase 1a: Zone-Based Market Sizing")
    
    prompt = """Based on the following Bangladesh irrigation pump market data, generate zone-based market sizing:

INSTALLED BASE (BADC 2023-24):
- DTW (Deep Tube Wells): 34,040
- STW (Shallow Tube Wells): 1,479,266
- LLP (Low Lift Pumps): 207,368
- Total irrigation equipment: ~1,720,674 units

BMDA BARIND DATA:
- 15,553 DTW in Rajshahi+Rangpur
- 509,233 hectares irrigated
- 962,380 farmers

NBR IMPORT DATA (5 months, Dec 2025-Apr 2026):
- HS 8413 total: ~BDT 28.7B annualized
- HS 8413.70 (Centrifugal): ~BDT 17.5B
- HS 8413.81 (Submersible): ~BDT 4.4B

DEALER PRICING (352 prices, BDStall/MEL/Othoba):
- Median: ৳12,000-19,700
- Core market: ৳5,000-25,000 = 59% of listings

ZONE REPLACEMENT RATES:
- Barind: 0.20-0.25
- Haor: 0.17-0.20
- Coastal: 0.25-0.33
- Urban: 0.11-0.14

Calculate for each zone: annual demand (units), market value (BDT Cr), confidence level, and key drivers.
If data is unavailable for a zone, use estimation and educated guesses. Clearly flag estimates.
Output as JSON with keys: barind, haor, coastal, urban."""

    result = call_reasoning(prompt, "You are a Bangladesh market analyst. Output valid JSON only. Use BDT Crore for valuations. When data is sparse, estimate and flag clearly.")
    save_output("zone_market_sizing.json", result)
    return result

def run_competitor_heatmap():
    """Phase 1b: Competitor heatmap from dealer/e-commerce data."""
    print("\n🗺️ Phase 1b: Competitor Heatmap")
    
    prompt = """Based on the following Bangladesh water pump market data, generate a competitor heatmap:

DEALER DATA (BDStall/MEL Mart/Othoba, 352 prices):
- RFL: Dominant mass-market brand on Othoba
- MARQUIS: Premium segment on MEL Mart
- Walton: Domestic/urban presence
- Pedrollo: International brand, specialized dealers
- Chinese imports: Price range ৳3,000-8,000, coastal/haor markets
- NO Leo brand found anywhere — clear market entry opportunity

NBR IMPORT DATA:
- Total HS 8413: ~BDT 29.5B/year imports
- Major source countries: China, India, Japan, South Korea, Italy

PRICE BANDS:
- Budget (৳3,000-8,000): Chinese imports, basic STW
- Core (৳8,000-20,000): RFL, Walton, domestic assembly
- Premium (৳20,000-50,000+): MARQUIS, Pedrollo, Kirloskar

For each competitor, estimate: zone presence, market capture %, key weakness.
Identify Leo Pump white space opportunities.
If data is unavailable, use estimation. Flag estimates clearly.
Output as JSON."""

    result = call_reasoning(prompt, "You are a Bangladesh competitive intelligence analyst. Output valid JSON only. Estimate where data is missing, flag estimates.")
    save_output("competitor_heatmap.json", result)
    return result

def run_consumer_insights():
    """Phase 2: Consumer personas and switching triggers."""
    print("\n👤 Phase 2: Consumer Insights & Pain Mapping")
    
    prompt = """Generate consumer personas and switching triggers for the Bangladesh water pump market across 4 segments:

1. FARMER (Agricultural - Barind/Haor/Coastal)
   - Decision: village dealer recommendation, IDCOL subsidy eligibility, BADC/BMDA programs
   - Pain: voltage spikes burn motors, spare parts take weeks, diesel cost rising
   - WTP: ৳8,000-25,000, seasonal cash flow

2. FISH FARMER (Aquaculture - Haor/Coastal)
   - Decision: continuous operation reliability, salinity resistance
   - Pain: pump failure = fish kill, corrosion from brackish water
   - WTP: ৳15,000-40,000, premium for reliability

3. URBAN HOMEOWNER (Dhaka/Chittagong)
   - Decision: apartment builder spec, online reviews, brand trust
   - Pain: noise, pressure drops during peak hours, no technician on call
   - WTP: ৳5,000-15,000 for booster, ৳15,000-35,000 for building system

4. MUNICIPAL/INDUSTRIAL (City Corp, Textile, Pharma)
   - Decision: tender specifications, BSTI certification, service SLA
   - Pain: downtime costs, counterfeit parts in supply chain
   - WTP: ৳50,000-500,000+ depending on scale

For each persona: decision hierarchy, pain points, switching triggers, WTP elasticity (High/Medium/Low).
If data is unavailable, use estimation based on typical Bangladesh market dynamics. Flag estimates.
Output as JSON."""

    result = call_reasoning(prompt, "You are a Bangladesh consumer research analyst. Output valid JSON only. Estimate where needed, flag clearly.")
    save_output("consumer_persona_map.json", result)
    return result

def run_gtm_strategy():
    """Phase 3: GTM strategy synthesis."""
    print("\n🎯 Phase 3: GTM Strategy & 90-Day Activation")
    
    # Load prior outputs
    zone_data = {}
    competitor_data = {}
    consumer_data = {}
    
    try:
        with open(Path(f"{PROJECT_ROOT}/data/outputs/zone_market_sizing.json")) as f:
            zone_data = json.load(f)
    except: pass
    try:
        with open(Path(f"{PROJECT_ROOT}/data/outputs/competitor_heatmap.json")) as f:
            competitor_data = json.load(f)
    except: pass
    try:
        with open(Path(f"{PROJECT_ROOT}/data/outputs/consumer_persona_map.json")) as f:
            consumer_data = json.load(f)
    except: pass

    prompt = f"""Synthesize the following into an actionable GTM strategy for Leo Pump Bangladesh market entry:

ZONE SIZING: {json.dumps(zone_data, indent=2) if zone_data else "Use estimates: Barind BDT 120-140 Cr, Haor 65-80 Cr, Coastal 85-105 Cr, Urban 110-135 Cr"}

COMPETITOR LANDSCAPE: {json.dumps(competitor_data, indent=2) if competitor_data else "RFL 32-38%, Walton 18-22%, Chinese imports 25-30%, Kirloskar 12-15%"}

CONSUMER INSIGHTS: {json.dumps(consumer_data, indent=2) if consumer_data else "Farmers: price + subsidy driven. Urban: brand + warranty. Coastal: durability + salinity resistance."}

Produce:
1. Target zone sequencing (Priority 1-3)
2. Positioning pillars per zone
3. 90-day activation checklist with specific actions
4. Risk flags (policy, currency, competition)
5. Channel strategy (dealer, e-commerce, tender, NGO)

Output as markdown-ready JSON with a 'markdown' field containing the full strategy document.
Estimate where data is missing. Flag estimates."""

    result = call_reasoning(prompt, "You are a GTM strategist for Bangladesh market entry. Be specific and actionable. Use BDT for all monetary values.")
    save_output("gtm_strategy.json", result)
    
    # Also save as markdown if the result has a markdown field
    if isinstance(result, dict) and "markdown" in result:
        save_markdown("gtm_strategy.md", result["markdown"])
    elif isinstance(result, dict) and "raw_text" in result:
        save_markdown("gtm_strategy.md", result["raw_text"])
    
    return result


if __name__ == "__main__":
    phase = sys.argv[1] if len(sys.argv) > 1 else "all"
    run_phase(phase)
