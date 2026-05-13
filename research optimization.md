Here is the **priority-aligned, v2.4-compliant update** for your Leo Pump OpenClaw pipeline. All model routing is shifted to `glm-4.5-air` (flash/fast) and `glm-5.1` (strong reasoning), with research phases restructured around your 4 core priorities: **Zone-Based Market Sizing, Competitor Heatmap, Consumer Insights, and GTM Strategy**.

---

### 🔑 1. Model Routing Update (v2.4 Cloud-Only)

**`.env`** (Update only these lines)
```env
# Fast Extraction / Cleaning / Translation / Price Normalization
FAST_MODEL=glm-4.5-air
FAST_TEMPERATURE=0.2

# Heavy Reasoning / Triangulation / Strategy Synthesis
REASONING_MODEL=glm-5.1
REASONING_TEMPERATURE=0.3
REASONING_MAX_TOKENS=4096

# ZLM/GLM API (single provider for both models)
ZLM_API_KEY=your-zlm-key
ZLM_BASE_URL=https://api.z.ai/api/anthropic
```

**`config/models.yaml`**
```yaml
default_provider: zlm_api

providers:
  zlm_api:
    type: anthropic-compatible
    base_url: ${ZLM_BASE_URL}
    api_key_env: ZLM_API_KEY
    context_length: 8192

models:
  fast_extract:
    provider: zlm_api
    name: ${FAST_MODEL}
    use_for:
      - chunk_cleaning
      - metadata_extraction
      - field_mapping
      - browser_navigation
      - bengali_translation
      - price_normalization
      - dealer_scrape_parsing
    params:
      temperature: ${FAST_TEMPERATURE}
      response_format: { type: "json_object" }

  cloud_reasoning:
    provider: zlm_api
    name: ${REASONING_MODEL}
    use_for:
      - zone_triangulation
      - competitor_heatmap_synthesis
      - consumer_insight_mapping
      - gtm_strategy_generation
      - market_floor_ceiling_calc
    params:
      temperature: ${REASONING_TEMPERATURE}
      max_tokens: ${REASONING_MAX_TOKENS}

routing:
  parser_default: fast_extract
  summary_default: cloud_reasoning
  failover: halt
```

---

### 🎯 2. Priority-Aligned Research Framework (4 Pillars)

| Priority                                 | Core Output                                                                         | Key Data Sources                                                                                                             | Triangulation Logic                                                                                   |
| ---------------------------------------- | ----------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| **1. Zone-Based Market Sizing**          | BDT valuation & unit demand by Barind, Haor, Coastal, Urban                         | BMDA (Barind), BWDB (flood/salinity), RAJUK/CDA permits, BADC installed base, dealer distribution maps                       | `Zone Demand = (Installed Base × Zone Replacement Rate) + (New Construction/Expansion) × ASP`         |
| **2. Competitor Heatmap**                | Market capture %, zone-wise valuation, spec/pricing gaps, white-space opportunities | Daraz/BDStall listings, dealer interviews, trade show catalogs, import shipment HS-8413 breakdowns, service network maps     | `Competitor Share = (Dealer Stock Mix × Street Price × Service Coverage Density) / Total Zone Demand` |
| **3. Consumer Insights** (High Priority) | Buyer personas, decision hierarchy, pain points, WTP, switching triggers            | Bengali farmer forums, dealer feedback logs, IDCOL farmer surveys, municipal tender FAQs, Facebook/YouTube comment sentiment | `Insight Confidence = (Primary Interview Weight) × (Cross-Validation with Trade/Policy Data)`         |
| **4. GTM Strategy**                      | Target sequencing, positioning, channel activation, 90-day roadmap                  | Phases 1-3 outputs, competitor gap matrix, subsidy eligibility windows, dealer margin benchmarks                             | `GTM Priority = (Market Size × Pain Point Severity × Entry Feasibility) / Competitive Saturation`     |

---

### ⚙️ 3. OpenClaw Pipeline Adjustments

**`config/agents.yaml`**
```yaml
agents:
  - id: zone_sizer
    purpose: Extract zone-specific installed base, ASP, and replacement rates
    model: fast_extract

  - id: competitor_scanner
    purpose: Scrape dealer listings, price bands, service coverage, and spec matrices
    model: fast_extract

  - id: consumer_insight_parser
    purpose: Extract pain points, decision hierarchy, WTP, and switching triggers from interviews/forums
    model: fast_extract

  - id: gtm_strategist
    purpose: Triangulate zone sizing + competitor gaps + consumer insights into actionable GTM plan
    model: cloud_reasoning

  - id: report_compiler
    purpose: Generate confidence-tagged markdown/JSON outputs for stakeholder review
    model: cloud_reasoning
```

**`SKILL_market_landscape.md`** (Append these execution routines)
```markdown
## ZONE-BASED SIZING ROUTINE
1. Pull BMDA/BWDB/BADC installed base by upazila/division
2. Apply zone-specific replacement rates: Barind 0.20-0.25, Haor 0.17-0.20, Coastal 0.25-0.33, Urban 0.11-0.14
3. Multiply by weighted ASP (fast_extract output)
4. Output: Zone Demand (units & BDT), Confidence, Data Gap Flags

## COMPETITOR HEATMAP ROUTINE
1. Map brand presence per zone via dealer inventory scans + e-commerce listings
2. Calculate street price bands (list - 8-15% dealer discount)
3. Overlay service coverage (technician count, spare parts lead time)
4. Flag zones with: >60% Chinese imports, >30% service complaints, or spec mismatch (salinity/voltage)

## CONSUMER INSIGHT ROUTINE
1. Extract decision hierarchy per persona (Farmer, Fish Farmer, Urban Homeowner, Municipal/Industrial)
2. Map pain points to operating conditions (voltage spikes, salinity corrosion, diesel cost, spare delay)
3. Identify switching triggers (warranty extension, technician certification, financing, hybrid solar)
4. Weight WTP by segment; tag as High/Medium/Low elasticity

## GTM SYNTHESIS ROUTINE
1. Cross-reference zone demand size × competitor weakness × consumer pain severity
2. Rank target zones: Attack First, Build Presence, Monitor, Defer
3. Define positioning pillar per zone (e.g., Barind = Voltage-Protected Deep Well; Coastal = Salinity-Resistant)
4. Generate 90-day activation checklist with channel, pricing, and messaging triggers
```

**`AGENTS.md`** (Add validation gates)
```markdown
## ZONE & CONSUMER VALIDATION RULES
- Zone estimates require ≥2 independent signals (govt data + dealer/e-commerce)
- Consumer insights must distinguish stated preference vs. revealed behavior (purchase history)
- Competitor market capture ≤70% without service network proof → label "Projected"
- GTM sequencing must include risk flag (policy shift, currency, competitor retaliation)
```

---

### 📊 4. Phased Execution & Token Budget (Optimized)

| Phase | Focus | Model Mix | Max Tokens | Deliverable |
|-------|-------|-----------|------------|-------------|
| **Phase 1** | Zone Sizing + Competitor Baseline | 70% `glm-4.5-air` / 30% `glm-5.1` | 8,000 | `zone_market_sizing.json`, `competitor_heatmap.json` |
| **Phase 2** | Consumer Insights + Pain Mapping | 60% `glm-4.5-air` / 40% `glm-5.1` | 7,000 | `consumer_persona_map.json`, `switching_triggers.md` |
| **Phase 3** | GTM Strategy + 90-Day Activation | 100% `glm-5.1` | 9,000 | `gtm_strategy.md`, `activation_checklist.json` |
| **Total** | **Priority-Aligned Baseline** | **Hybrid** | **24,000** | **Investor-Ready, Execution-Ready** |

---

### 📤 5. Output Schemas (Pipeline-Ready)

**`zone_market_sizing.json`**
```json
{
  "barind": {"demand_units": "45000-52000", "valuation_bdt": "120-140 Cr", "confidence": "Medium-High", "key_drivers": ["BADC deep well expansion", "groundwater decline"]},
  "haor": {"demand_units": "28000-34000", "valuation_bdt": "65-80 Cr", "confidence": "Medium", "key_drivers": ["seasonal drainage demand", "post-Aman cash flow"]},
  "coastal": {"demand_units": "31000-38000", "valuation_bdt": "85-105 Cr", "confidence": "Medium", "key_drivers": ["salinity corrosion replacement", "NGO/municipal tenders"]},
  "urban": {"demand_units": "55000-68000", "valuation_bdt": "110-135 Cr", "confidence": "High", "key_drivers": ["apartment construction", "municipal pressure deficit"]}
}
```

**`competitor_heatmap.json`**
```json
{
  "rfl": {"zone_presence": "All", "market_capture_pct": "32-38", "weakness": "Urban service density, coastal spec fit"},
  "kirloskar": {"zone_presence": "Industrial/Urban", "market_capture_pct": "12-15", "weakness": "Rural dealer coverage, price sensitivity"},
  "walton": {"zone_presence": "Domestic/Urban", "market_capture_pct": "18-22", "weakness": "Agricultural durability, spare lead time"},
  "chinese_imports": {"zone_presence": "Coastal/Haor", "market_capture_pct": "25-30", "weakness": "Counterfeit risk, zero after-sales, voltage burnout"},
  "leo_white_space": ["Barind voltage-protected bundles", "Coastal salinity-rated SKUs", "Haor seasonal financing partnerships"]
}
```

**`gtm_strategy.md`** (Structure)
```markdown
# Leo Pump GTM Activation Blueprint
## Target Sequencing (Priority 1-3)
1. Barind Agricultural (High demand, subsidy alignment, voltage protection gap)
2. Urban Domestic (High ASP, brand trust potential, municipal pressure deficit)
3. Coastal Aquaculture/Municipal (Corrosion gap, tender-driven, lower volume but premium margin)

## Positioning Pillars by Zone
- Barind: "Built for Deep Wells & Grid Instability"
- Urban: "Quiet, Efficient, Apartment-Ready"
- Coastal: "Salt-Resistant. Zero Downtime."

## 90-Day Quick Wins
- [ ] Pre-certify 3HP submersible for IDCOL/BMDA eligibility
- [ ] Launch dealer technician certification in Rajshahi (20 technicians)
- [ ] Deploy voltage-protection + 18-month warranty bundle for Barind dealers
- [ ] Optimize Daraz/BDStall listings with Bengali spec sheets & warranty QR codes
```

---

### ✅ 6. Deployment Checklist (v2.4)

- [ ] Update `.env` with `FAST_MODEL=glm-4.5-air` and `REASONING_MODEL=glm-5.1`
- [ ] Replace `config/models.yaml` with the ZLM/GLM routing block above
- [ ] Overwrite `config/agents.yaml` with the 4-priority agent map
- [ ] Append zone/competitor/consumer/GTM routines to `SKILL_market_landscape.md`
- [ ] Add validation gates to `AGENTS.md`
- [ ] Run `bash scripts/run_pipeline.sh` → Phase 1 executes first
- [ ] Verify `data/outputs/` contains JSON/Markdown with confidence tags
- [ ] No `sudo`, no local models, pure cloud routing, `failover: halt` enforced

This configuration delivers **zone-granular sizing, competitor heatmaps, high-fidelity consumer insights, and actionable GTM strategy** within ~24K tokens, fully aligned with your v2.4 architecture and `glm-4.5-air` / `glm-5.1` routing. Execute Phase 1 first, then proceed sequentially.



`Last but not least: if data is not available then estimation, educated guesses are the option.`