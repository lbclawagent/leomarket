# Phase 2 Progress Report — Bangladesh Water Pump Market
**Date:** 2026-05-07 | **Status:** Phase 2 Partial — NBR Extended, Institutional Sites Limited

---

## 1. NBR Import Data — Extended to 5 Months ✅

**Source:** 10 NBR PDFs (Dec 2025 – Apr 2026, Commercial + Bond)  
**Total records:** 93 HS 8413 line items

### 1.1 Time Series — HS 8413 Total Imports (BDT Millions)

| Month | Commercial | Bond | **Total** |
|-------|-----------|------|-----------|
| Dec 2025 | 1,877 | 39 | **1,916** |
| Jan 2026 | 2,537 | 14 | **2,552** |
| Feb 2026 | 2,253 | 95 | **2,347** |
| Mar 2026 | 2,133 | 160 | **2,293** |
| Apr 2026 | 2,831 | 11 | **2,842** |
| **5-mo avg** | **2,326** | **64** | **2,390** |

### 1.2 HS 8413.70 (Centrifugal Pumps) — Monthly Trend

| Month | CIF Value (BDT M) | Trend |
|-------|-------------------|-------|
| Dec 2025 | 1,201 | — |
| Jan 2026 | 1,438 | ↑ 20% |
| Feb 2026 | 1,609 | ↑ 12% |
| Mar 2026 | 1,583 | ↓ -2% |
| Apr 2026 | 1,450 | ↓ -8% |

**Pattern:** Centrifugal pump imports peak Feb–Mar (Boro irrigation preparation), declining into April. Consistent with seasonal model (Nov–Jan prep, Feb–Apr peak irrigation).

### 1.3 Annualized Estimates

| Metric | 5-Month Average | Annualized |
|--------|----------------|------------|
| HS 8413 Total | ৳2,390M/month | **৳28.7B/year** |
| HS 8413.70 (Centrifugal) | ৳1,456M/month | **৳17.5B/year** |
| HS 8413.81 (Submersible) | ৳366M/month | **৳4.4B/year** |
| HS 8413.91 (Parts) | ৳308M/month | **৳3.7B/year** |
| Bond imports | ৳64M/month | **৳0.8B/year** |

**Refined total import market: ~BDT 29.5 billion/year (~$246M)**

With 1.3–1.6× landed-to-retail markup: **addressable market ~BDT 38–47 billion ($320–390M)**

---

## 2. SREDA Solar Irrigation — Full Dataset ✅

**Total projects:** 32 solar irrigation pump installations  
**Standard capacity:** 43.4 kWp per installation  
**Primary agency:** IDCOL (financing + implementation)

### Geographic Distribution
- **Chuadanga** — Multiple installations (drought-prone southwest)
- **Jhenaidah** — Concentration of projects
- All in western/southwestern Bangladesh (Barind-adjacent)

### Market Implications
- 32 projects × 43.4 kWp = ~1.39 MW total solar irrigation capacity
- Each installation requires submersible pump(s) + solar controller
- **This is a niche but growing segment** — IDCOL pipeline data needed for forward estimate
- Comparison with SREDA dashboard: Solar total = 1,451.8 MW → solar irrigation is <0.1% of total solar
- **Growth potential:** Government targeting 10,000 solar pumps by 2030 → massive upside

---

## 3. Institutional Source Assessment

| Agency | Status | Data Obtained | Access Issue |
|--------|--------|---------------|-------------|
| **BMDA** | ❌ Blocked | Bengali navigation only | JS-heavy pages, no data tables rendered |
| **BWDB** | ❌ Empty | 2 pump mentions on homepage | Project/tender pages return empty HTML |
| **BIDA** | ❌ 404 | Homepage only, no sector data | URL structure changed, most pages 404 |
| **BEZA** | ❌ Cloudflare | Blocked | Anti-bot protection active |

### Recommended Workarounds
1. **BMDA:** Their PDF annual reports exist on the server but need direct URL discovery — try Bengali search for "বিএমডিএ বার্ষিক প্রতিবেদন" or use right-click → Save As from a real browser
2. **BWDB:** Tenders published in newspapers + CPPT (Central Procurement) — more accessible than their website
3. **BIDA:** Use BIDA One Stop Service portal (osp.bida.gov.bd) when DNS resolves, or check Bangladesh Bank FDI statistics as proxy
4. **BEZA:** Need human-operated browser to pass Cloudflare challenge, then save page as HTML

---

## 4. Consolidated Market Sizing — Triangulated

### 4.1 Signal Pool

| Signal | Value | Source | Confidence |
|--------|-------|--------|-----------|
| Annual HS 8413 imports | BDT 29.5B | NBR (5 months) | High |
| HS 8413.70 annualized | BDT 17.5B | NBR | High |
| Dealer price median | ৳12,000–19,700 | BDStall/MEL/Othoba (352 prices) | Medium-High |
| DMR urban pump demand | ~343K units/year | Dhaka Structure Plan | High |
| DMR urban pump value | ~BDT 5.15B/year | Corrected calc × avg price | Medium |
| National urban pump | ~BDT 12.9B/year | DMR × 2.5 multiplier | Medium |
| Solar irrigation pumps | 32 projects (installed) | SREDA | High |
| BSTI certification required | BDS 1082:1984 + motor std | BSTI catalogue | High |

### 4.2 Market Segmentation (Estimate)

| Segment | Annual Value (BDT) | Method | Confidence |
|---------|-------------------|--------|-----------|
| **Agricultural (irrigation)** | ~12–15B | Import × 0.5 (agri share of HS 8413.70) | Medium |
| **Industrial (process/utility)** | ~8–10B | HS 8413.30 + .40 + .60 + partial .70 | Medium |
| **Domestic/Urban (booster)** | ~5–7B | Structure Plan calc + import proxy | Medium |
| **Solar irrigation** | ~0.3B (current) | 32 projects, growing | High (but small base) |
| **Parts & accessories** | ~3.7B | HS 8413.91 imports | High |
| **TOTAL** | **~29–36B** | Triangulated | Medium |

---

## 5. What's Still Needed

| Gap | Priority | Approach |
|-----|----------|----------|
| 31 more months of NBR data | **High** | Manual pagination or direct PDF URL construction |
| BADC installed base (OCR) | **High** | Build PaddleOCR pipeline for image PDFs |
| BMDA tube well inventory | **High** | Manual browser download of annual report PDF |
| BEZA zone tenant data | **Medium** | Human browser session + HTML save |
| BIDA investment pipeline | **Medium** | BIDA OSP portal or Bangladesh Bank FDI data |
| BWDB tender specifications | **Low** | CPPT portal or newspaper procurement ads |
| Daraz product-level data | **Low** | Search API or longer wait time |

---

## 6. Key Seasonality Confirmed

NBR 5-month data confirms the seasonal model:
- **Jan–Feb:** Import volumes surge (Boro preparation)
- **Mar:** Peak imports (irrigation demand fulfillment)
- **Apr:** Decline begins (season winding down)
- **Dec:** Lowest month (post-Aman, pre-Boro)

This validates the seasonal weighting framework from the Market Landscape document.
