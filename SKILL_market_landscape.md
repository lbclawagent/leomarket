## HYBRID EXECUTION MODE
Pipeline: Search → Parse → Translate → Normalize → Triangulate → Output

## HS-CODE-FIRST SEARCH
- site:nbr.gov.bd "8413" tariff
- site:volza.com "Bangladesh" "8413" import shipments
- "Bangladesh Customs" "pumps for liquids"

## BENGALI SEARCH LOOP
- পানির পাম্প দাম বাংলাদেশ
- সেচ পাম্প বাজার বাংলাদেশ
- সাবমারসিবল পাম্প দাম
Convert কোটি/লাখ to BDT automatically.

## PRICE NORMALIZATION
Weighted Avg Price = (mode × 0.6) + (midpoint × 0.4)

## MULTI-ENGINE TRIANGULATION
1. Installed Base Model: Annual Demand = Installed Base × Replacement Rate
2. Trade Model: Market = Import Value × (1.2 – 1.8)
3. Policy Model: Estimate = Govt target × avg cost
If 2 models agree → high confidence. If not → output range.

## OUTPUT FORMAT
Each section: Data, Source, Method, Confidence

## TEMPORAL INTELLIGENCE LAYER (added 2026-05-06)

### Temporal Normalization Routine
When parsing any source:
1. Extract explicit date fields: publication_date, data_as_of, fiscal_year_reference
2. If missing → infer from context (e.g., "Boro 2025" → data_as_of = 2024-11 to 2025-04)
3. Convert all dates to Asia/Dhaka timezone + ISO 8601 format
4. Flag records where data_as_of > 12 months from current_date

### Seasonal Tagging Logic
Auto-assign seasonal_tag to each record:
- month in [11,12,1] → "boro_prep"
- month in [2,3,4] → "peak_irrigation"
- month in [5,6,7] → "monsoon_transition"
- month in [8,9,10] → "aman_harvest"
- urban_source AND month in [3,4,5,6] → "urban_summer"

### Seasonal Weighting Rules
- Boro Prep (Nov–Jan): Dealer pricing ×1.5, Import data ×1.2, IDCOL pipeline ×1.3
- Peak Irrigation (Feb–Apr): Replacement signals ×2.0, Voltage failure reports ×1.8
- Monsoon (May–Jul): Drainage pump listings ×1.7, Haor dealer activity ×1.5
- Aman Harvest (Oct–Nov): Cooperative bulk orders ×1.6, Post-harvest financing ×1.4
- Urban Summer (Mar–Jun): Booster listings ×1.5, Apartment permits ×1.3

### Confidence Degradation Schedule
| Data Age | Adjustment |
|----------|------------|
| 0–3 months | No change |
| 4–6 months | ×0.9 |
| 7–12 months | ×0.7 |
| 13–18 months | ×0.5 + "Stale" flag |
| >18 months | ×0.3 + "Historical Reference Only" |
Exception: BADC census / NBR annual reports retain base confidence for 24 months.

### Data Collection Time Windows
| Source | Range |
|--------|-------|
| NBR HS 8413 | 36 months rolling + current YTD |
| BADC Irrigation Census | Last 3 FYs (July–June) + latest quarterly |
| IDCOL Solar | Last 24 months + active pipeline (6 months) |
| Dealer Pricing | 90-day rolling + seasonal peak snapshots |
| Bengali News/Interviews | 180-day rolling, 0.95^days decay |
| BSTI/Policy | All from 2020 onward |
| RAJUK/CDA/KDA Permits | 24 months rolling + current quarter |
| Industrial Expansion | 36 months backward + forward registry |

## AGRO-ECOLOGICAL ZONE SEGMENTATION (added 2026-05-06)
1. **Barind Tract** (Rajshahi, Naogaon, Chapainawabganj): Deep submersible 10-30 HP, drought-prone, subsidy-sensitive
2. **Haor Basin** (Sunamganj, Kishoreganj, Netrokona): Portable centrifugal, seasonal flooding, community bulk buy
3. **Coastal Salinity Belt** (Khulna, Satkhira, Cox's Bazar): Stainless/polymer pumps, institutional tenders
4. **Urban Corridors** (Dhaka, Chattogram, Gazipur): Booster systems, brand + service focus

## PRODUCT-TYPE DEMAND ANALYSIS (added 2026-05-06)
- **Jet Pumps**: 0.5-2 HP, domestic/small farm, high fragmentation, price-sensitive
- **Submersible**: 3-30 HP, deep groundwater, mid-tier consolidation (RFL, Walton)
- **Centrifugal**: 1-15 HP, surface irrigation/drainage, import-dominant (Chinese)
- **Solar/Hybrid**: 1-5 HP equiv, policy-driven (IDCOL), emerging segment

## IMPORT vs LOCAL ASSEMBLY HS-CODE FILTER (added 2026-05-06)
1. Identify HS 8413 subcodes with highest import volume growth
2. Cross-reference with local assembly feasibility (motor 8501, impeller, casing, seal)
3. If finished goods duty ≥30% AND components duty ≤15% → local assembly compelling
4. Validate with dealer feedback
Phased approach: Import premium → Local assembly volume → Hybrid models

## ZONE-BASED SIZING ROUTINE (v2.4)
1. Pull BMDA/BWDB/BADC installed base by upazila/division
2. Apply zone-specific replacement rates: Barind 0.20-0.25, Haor 0.17-0.20, Coastal 0.25-0.33, Urban 0.11-0.14
3. Multiply by weighted ASP (fast_extract output)
4. Output: Zone Demand (units & BDT), Confidence, Data Gap Flags
5. If data unavailable → use estimation, educated guesses; flag clearly

## COMPETITOR HEATMAP ROUTINE (v2.4)
1. Map brand presence per zone via dealer inventory scans + e-commerce listings
2. Calculate street price bands (list - 8-15% dealer discount)
3. Overlay service coverage (technician count, spare parts lead time)
4. Flag zones with: >60% Chinese imports, >30% service complaints, or spec mismatch (salinity/voltage)
5. Identify Leo Pump white space opportunities per zone

## CONSUMER INSIGHT ROUTINE (v2.4)
1. Extract decision hierarchy per persona (Farmer, Fish Farmer, Urban Homeowner, Municipal/Industrial)
2. Map pain points to operating conditions (voltage spikes, salinity corrosion, diesel cost, spare delay)
3. Identify switching triggers (warranty extension, technician certification, financing, hybrid solar)
4. Weight WTP by segment; tag as High/Medium/Low elasticity
5. If primary research unavailable → estimate from market structure, dealer feedback, policy signals

## GTM SYNTHESIS ROUTINE (v2.4)
1. Cross-reference zone demand size × competitor weakness × consumer pain severity
2. Rank target zones: Attack First, Build Presence, Monitor, Defer
3. Define positioning pillar per zone (e.g., Barind = Voltage-Protected Deep Well; Coastal = Salinity-Resistant)
4. Generate 90-day activation checklist with channel, pricing, and messaging triggers
5. Include risk flags: policy shift, currency volatility, competitor retaliation

## MODEL ROUTING (v2.4)
- Fast extraction (glm-4.5-air): chunk_cleaning, metadata_extraction, price_normalization, bengali_translation, dealer_scrape_parsing
- Heavy reasoning (glm-5.1): zone_triangulation, competitor_heatmap_synthesis, consumer_insight_mapping, gtm_strategy_generation
- Failover: halt (no fallback, flag and stop)