# Scraping Arsenal Upgrade — GitHub Projects Research
**Date:** 2026-05-07 | **Context:** Enhance OpenClaw scraping for BD government sites

---

## Tier 1: Anti-Detection Browsers (Solves BEZA Cloudflare, BMDA JS blocks)

### 🥇 Camoufox — BEST FIT
**GitHub:** github.com/daijro/camoufox | **Stars:** ~4K+ | **Lang:** Python

**What it does:** Firefox fork built specifically for AI agents. Anti-detect by design.

**Key features:**
- **Drop-in Playwright compatibility** via Python interface (same API as Patchright!)
- Fingerprint injection & rotation **without JS injection** — navigator, screen, hardware, OS all spoofed at browser level
- Page automation hidden from JS inspection
- Minimal debloated Firefox — fast launch, low resource
- Clean DOM output, no CSS animations or tracking noise
- Headless & undetectable

**Why it beats Patchright for our use case:**
- Patchright patches Chromium → still detected by Cloudflare/Imperva
- Camoufox is Firefox-based → entirely different fingerprint surface
- Built-in fingerprint rotation = no need for BrowserForge separately
- "Built for AI agents" = designed for exactly our pattern (headless, scale, tokens)

**Install:** `pip install camoufox && python -m camoufox fetch`

**Solves:** BEZA (Cloudflare), BMDA (JS detection), any site blocking Patchright

---

### 🥈 FlareSolverr — Cloudflare-specific Bypass
**GitHub:** github.com/FlareSolverr/FlareSolverr | **Stars:** ~8K+ | **Lang:** Python/Docker

**What it does:** Proxy server that solves Cloudflare challenges using undetected-chromedriver.

**How it works:**
1. Runs as a Docker container or local process
2. You send it a URL via HTTP API
3. It launches Chrome with undetected-chromedriver
4. Solves the Cloudflare challenge automatically
5. Returns the HTML + cookies

**Integration pattern:**
```python
# Before scraping BEZA, get cookies from FlareSolverr
import requests
flaresolverr_resp = requests.post('http://localhost:8191/v1', json={
    "cmd": "request.get",
    "url": "https://www.beza.gov.bd/",
    "maxTimeout": 60000
})
cookies = flaresolverr_resp['solution']['cookies']
html = flaresolverr_resp['solution']['response']
```

**Pros:** Battle-tested, runs as a service, cookies reusable across requests
**Cons:** Extra service to manage, uses Selenium (heavier than Playwright)

**Solves:** BEZA specifically, any Cloudflare-protected site

---

## Tier 2: HTTP-Level Tools (For API-heavy sites, no browser needed)

### 🥇 curl_cffi — TLS Fingerprint Impersonation
**GitHub:** github.com/yifeikong/curl_cffi | **Stars:** ~3K+ | **Lang:** Python

**What it does:** Python binding for curl that can impersonate browser TLS/JA3 and HTTP/2 fingerprints.

**Why it matters:** Some sites (including BD government) don't need full browser rendering — they just check TLS fingerprint. If your Python `requests` library has the wrong TLS fingerprint, you get blocked. curl_cffi fixes this.

```python
from curl_cffi import requests
# Impersonate Chrome's TLS fingerprint
r = requests.get("https://some-site.gov.bd", impersonate="chrome")
```

**Solves:** BIDA (404s might be TLS-based blocks), BWDB (empty responses), any API endpoint

---

### 🥈 BrowserForge — Fingerprint Generator
**GitHub:** github.com/daijro/browserforge | **Stars:** ~1K+ | **Lang:** Python

**What it does:** Bayesian generative network to create realistic browser fingerprints (headers, screen, navigator, WebGL, etc.)

**Use with Camoufox or standalone:**
```python
from browserforge.fingerprints import FingerprintGenerator
fp = FingerprintGenerator()
fingerprint = fp.generate()
# Returns complete realistic browser fingerprint
```

**Value add:** When you need to rotate identities across many requests (e.g., paginating through NBR PDFs)

---

## Tier 3: Next-Gen Automation Frameworks

### DrissionPage — Unified Browser + HTTP
**GitHub:** github.com/g1879/DrissionPage | **Stars:** ~25K+ | **Lang:** Python

**What it does:** Combines browser automation and HTTP requests in one tool. Switch between browser mode and request mode seamlessly.

**Key advantage:** For sites that sometimes need JS rendering and sometimes don't (like BMDA), you can start with fast HTTP requests and fall back to browser mode only when needed.

**Why it's interesting for OpenClaw:**
- Chinese-developed, heavily tested on sites with anti-bot (similar to BD government sites)
- Can mix `SessionPage` (HTTP) and `ChromiumPage` (browser) in same script
- Built-in stealth features

---

### nodriver — Undetected-Chromedriver Successor
**GitHub:** github.com/ultrafunkamsterdam/nodriver | **Stars:** ~2K+ | **Lang:** Python

**What it does:** Successor to undetected-chromedriver. No Selenium, no webdriver — direct CDP-based Chrome automation.

**Pros:** Lighter than Selenium, built for Cloudflare bypass
**Cons:** Chrome-based (same detection surface as Patchright), less maintained

---

## Tier 4: AI-Powered Scraping (Future consideration)

### ScrapeGraphAI — LLM-Powered Scraping
**GitHub:** github.com/ScrapeGraphAI/Scrapegraph-ai | **Stars:** ~20K+ | **Lang:** Python

**What it does:** Uses LLMs to automatically extract structured data from any webpage. You describe what you want, it figures out the extraction.

```python
from scrapegraphai.graphs import SmartScraperGraph
graph = SmartScraperGraph(
    prompt="Extract all pump product names and prices",
    source="https://www.bdstall.com/water-pump/",
    config={"llm": {"model": "deepseek/deepseek-chat"}}
)
result = graph.run()
```

**MCP server available** — could integrate directly with OpenClaw as an MCP tool!

**Value for OpenClaw:** Could replace brittle CSS selector scraping with LLM-based extraction that adapts to any page structure. Would solve the Daraz/Othoba selector issues permanently.

---

## Recommended Installation Priority

| Priority | Tool | Install | Impact |
|----------|------|---------|--------|
| **1** | **Camoufox** | `pip install camoufox && python -m camoufox fetch` | Replaces Patchright, solves BEZA + BMDA |
| **2** | **FlareSolverr** | `docker run -p 8191:8191 flaresolverr/flaresolverr` | Cloudflare backup, lightweight service |
| **3** | **curl_cffi** | `pip install curl_cffi` | TLS impersonation for API-level requests |
| **4** | **BrowserForge** | `pip install browserforge` | Fingerprint rotation (works with Camoufox) |
| **5** | **ScrapeGraphAI** | `pip install scrapegraphai` | LLM-powered extraction (future) |

---

## Quick Win: Replace Patchright with Camoufox

```python
# OLD (Patchright — detected by BEZA, BMDA)
from patchright.sync_api import sync_playwright

# NEW (Camoufox — undetectable, Playwright API)
from camoufox.sync_api import Camoufox

with Camoufox(headless=True) as browser:
    page = browser.new_page()
    page.goto("https://www.beza.gov.bd/")
    # Cloudflare? What Cloudflare?
```

**Same Playwright API, undetectable browser.** Drop-in replacement for all existing scrapers.
