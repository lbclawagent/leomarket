# DATA_INVENTORY.md — Bangladesh Water Pump Market Research

**Generated:** 2026-05-13 13:57 GMT+6 | **Total Size:** ~979 MB

---

## Directory Structure

```
data/
├── raw/                          # Raw source data
│   ├── badc/                     # BADC irrigation surveys (928 MB)
│   ├── nbr/                      # NBR import statements (19 MB)
│   ├── bsti/                     # BSTI standards (3.1 MB)
│   ├── institutional/            # BMDA, institutional reports (16 MB)
│   ├── policy/                   # Policy/urban planning (12 MB)
│   ├── idcol/                    # IDCOL/SREDA solar pump (340 KB)
│   ├── pricing/                  # Dealer/e-commerce pricing (156 KB)
│   ├── bwdb/                     # BWDB tenders (4 KB)
│   └── (root-level raw JSONs)
├── outputs/                      # Analysis outputs & reports (80 KB)
├── parsed/                       # Empty — no parsed data yet
├── raw_idcol.json
├── raw_nbr.json
├── raw_govt.json
├── raw_daraz.json
├── raw_daraz_extended.json
└── zai_quota_history.jsonl
```

---

## 1. NBR Import Data (`raw/nbr/`)

### Source: National Board of Revenue (nbr.gov.bd)
### Period: December 2025 — April 2026 (5 months)

| File | Type | Size | Lines |
|------|------|------|-------|
| Import_Statement-IM-4-Commecial(December,2025)_(1).pdf | PDF | 2.0 MB | — |
| Import_Statement-IM-4-Commecial(December,2025)_(1).txt | Text | 228 KB | 3,044 |
| Import_Statement-IM-4-Commecial(January,2026).pdf | PDF | 2.0 MB | — |
| Import_Statement-IM-4-Commecial(January,2026).txt | Text | 231 KB | 3,094 |
| Import_Statement-IM-4-Commecial(February,2026)1.pdf | PDF | 2.4 MB | — |
| Import_Statement-IM-4-Commecial(February,2026)1.txt | Text | 283 KB | 3,344 |
| Import_Statement-IM-4-Commecial(March,2026).pdf | PDF | 2.4 MB | — |
| Import_Statement-IM-4-Commecial(March,2026).txt | Text | 282 KB | 3,343 |
| Import_Statement-IM-4-Commecial(April,2026).pdf | PDF | 2.4 MB | — |
| Import_Statement-IM-4-Commecial(April,2026).txt | Text | 282 KB | 3,343 |
| Import_Statement-IM-7-Bond(December,2025)_(1).pdf | PDF | 1.0 MB | — |
| Import_Statement-IM-7-Bond(December,2025)_(1).txt | Text | 163 KB | 2,153 |
| Import_Statement-IM-7-Bond(January,2026).pdf | PDF | 1.1 MB | — |
| Import_Statement-IM-7-Bond(January,2026).txt | Text | 165 KB | 2,176 |
| Import_Statement-IM-7-Bond(February,2026).pdf | PDF | 1.3 MB | — |
| Import_Statement-IM-7-Bond(February,2026).txt | Text | 175 KB | 2,065 |
| Import_Statement-IM-7-Bond(March,2026).pdf | PDF | 1.3 MB | — |
| Import_Statement-IM-7-Bond(March,2026).txt | Text | 174 KB | 2,060 |
| Import_Statement-IM-7-Bond(April,2026).pdf | PDF | 1.3 MB | — |
| Import_Statement-IM-7-Bond(April,2026).txt | Text | 184 KB | 2,186 |

**Extracted Data:**
| File | Description |
|------|-------------|
| `hs8413_extracted.json` (64 KB) | 93 HS 8413 line items extracted from all 10 PDFs — includes per-file HS code counts |
| `nbr_scrape_results.json` (2.0 KB) | Download manifest with URLs, filenames, and sizes |
| `nbr_download_manifest.json` (607 B) | Shows all 10 PDFs skipped (already downloaded) |
| `nbr_historical_manifest.json` (1.6 KB) | Attempted 2025 historical data — ALL returned HTTP 400 (not available) |
| `nbr_all_links.json` (1.8 KB) | All NBR publication links scraped from website |

**Coverage:** 5 months (Dec 2025–Apr 2026), both Commercial (IM-4) and Bond (IM-7)
**Gap:** No data before December 2025. Historical data (2025, 2024) unavailable from NBR website.

---

## 2. BADC Irrigation Survey Data (`raw/badc/`) — 928 MB

### Source: Bangladesh Agricultural Development Corporation
### Period: 2017–18 through 2023–24 (7 survey years)

### PDFs (source documents):

| File | Size |
|------|------|
| `survey_2017_18.pdf` | 2.6 MB |
| `survey_2018_19.pdf` | 9.6 MB |
| `survey_2019_20.pdf` | 14 MB |
| `survey_2020_21.pdf` | 10 MB |
| `survey_2021_22.pdf` | 11 MB |
| `survey_2022_23.pdf` | 11 MB |
| `survey_2023_24.pdf` | 12 MB |

### Extracted Page Images:

| Folder | Pages | Notes |
|--------|-------|-------|
| `irrigation_survey_2017_18_images/` | 17 | Smallest survey — partial |
| `irrigation_survey_2018_19_images/` | 52 | |
| `irrigation_survey_2019_20_images/` | 75 | |
| `irrigation_survey_2020_21_images/` | 50 | |
| `irrigation_survey_2021_22_images/` | 66 | |
| `irrigation_survey_2022_23_images/` | 77 | |
| `irrigation_survey_2023_24_images/` | 112 | |
| `survey_2023_24_images/` | 112 | Duplicate of above |
| `key_pages/` | 77 | Curated key pages from multiple surveys |

### Metadata & Processing:
| File | Description |
|------|-------------|
| `badc_download_manifest.json` | Download status for all 7 surveys |
| `badc_survey_page_links.json` (22 KB) | PDF links from BADC website |
| `badc_ocr_results.json` (52 KB) | OCR processing results & status |
| `*_pump_data.json` (×7, each 98 B) | **ALL EMPTY** — pump_mentions/tube_well_counts/tables_found all `[]` |

**Gap:** Pump data extraction from BADC surveys failed — all 7 pump_data.json files contain empty arrays. OCR was attempted but structured data extraction was not successful. Raw page images exist but need manual/assisted data extraction.

---

## 3. BSTI Standards (`raw/bsti/`) — 3.1 MB

| File | Type | Size | Description |
|------|------|------|-------------|
| `bsti_pump_standards.md` | Markdown | 2.2 KB | Curated list of pump-relevant BDS standards |
| `Bangladesh_Bangladesh Standard and Testing Institution Standards Catalogue_2018-2.pdf` | PDF | 3.1 MB | Full BSTI standards catalogue (2018) |

**Key Standards Identified:**
- BDS 1082:1984 — Horizontal centrifugal pumps (agricultural)
- BDS (three-phase motors) — Motors for centrifugal pumps
- BDS 1145:1986 — Vertical shaft motor dimensions for pumps

---

## 4. IDCOL / SREDA Solar Pump Data (`raw/idcol/`) — 340 KB

| File | Size | Description |
|------|------|-------------|
| `idcol_sreda_data.json` | 326 KB | SREDA solar pump project data — tables with org names, financing details |
| `sreda_full.json` | 8.4 KB | 32 SREDA projects with financing institution details |

**Root-level:**
- `raw_idcol.json` (662 B) — IDCOL homepage scrape (minimal — main solar irrigation page returned 404)

**Coverage:** SREDA solar pump installation data. IDCOL's own project page returned 404.

---

## 5. Dealer / E-Commerce Pricing (`raw/pricing/`) — 156 KB

| File | Size | Description |
|------|------|-------------|
| `othoba_detailed.json` | 117 KB | Othoba.com water pump listings — 200+ prices, range BDT 3,690–100,222 |
| `dealer_pricing.json` | 20 KB | Multi-source: Daraz, BDStall pricing (partial — many empty products) |
| `daraz_othoba_deep.json` | 13 KB | Deep scrape of Daraz + Othoba product pages |

**Root-level pricing files:**
- `raw_daraz.json` (1.5 KB) — Daraz water pump prices + 1HP submersible prices (BDT 3,080–15,800)
- `raw_daraz_extended.json` (177 B) — Daraz 2HP (BDT 6,000–40,000) and 3HP (BDT 14,200–19,857) prices

**Coverage:** Daraz, Othoba, BDStall pricing data. Othoba is richest (200+ prices). BDStall has 41 products.

---

## 6. Institutional Data (`raw/institutional/`) — 16 MB

| File | Size | Description |
|------|------|-------------|
| `institutional_data.json` | 191 KB | BMDA homepage + other institutional site scrapes |
| `institutional_phase2b.json` | 72 KB | Phase 2b institutional data collection |
| `bmda_v2.json` | 6.9 KB | BMDA achievements page data |
| `bmda_camoufox.json` | 1.3 KB | BMDA data via Camoufox browser |
| `bmda_annual_reports_parsed.json` | 2.3 KB | Parsed BMDA annual report metadata |
| `annual_report_7e983f8140984c118d0ca59c6c8da18b.pdf` | 7.1 MB | BMDA annual report |
| `annual_report_7e983f8140984c118d0ca59c6c8da18b.txt` | 66 KB | Text extraction of above |
| `annual_report_164c35deafc8462dbf748e6629057cc8.pdf` | 3.2 MB | BMDA annual report |
| `annual_report_164c35deafc8462dbf748e6629057cc8.txt` | 72 KB | Text extraction of above |
| `annual_report_868cc0189d1246a1a26222b45350aee4.pdf` | 5.2 MB | BMDA annual report |
| `annual_report_868cc0189d1246a1a26222b45350aee4.txt` | 104 KB | Text extraction of above |

**Coverage:** 3 BMDA annual reports with text extractions. Homepage and achievements page data.

---

## 7. Policy / Urban Data (`raw/policy/`) — 12 MB

| File | Size | Description |
|------|------|-------------|
| `dhaka_structure_plan.pdf` | 12 MB | Dhaka Structure Plan (full PDF) |
| `dhaka_structure_plan.housing.txt` | 46 KB | Extracted housing-relevant sections |
| `policy_urban_data.json` | 44 KB | RAJUK and urban planning data |

---

## 8. BWDB Tenders (`raw/bwdb/`) — 4 KB

| File | Size | Description |
|------|------|-------------|
| `bwdb_tenders.json` | 783 B | Tender search — 3 sources checked, **0 pump tenders found** |

**Gap:** CPPT site timed out. BWDB and DASG returned no pump tenders.

---

## 9. Root-Level Raw JSON Files

| File | Size | Description |
|------|------|-------------|
| `raw_nbr.json` | 3.3 KB | NBR homepage scrape (navigation/menu text) |
| `raw_govt.json` | 7.9 KB | Government site scrapes (IDCOL 404, BADC homepage in Bengali) |
| `raw_idcol.json` | 662 B | IDCOL homepage (minimal content) |
| `raw_daraz.json` | 1.5 KB | Daraz pricing data (see §5) |
| `raw_daraz_extended.json` | 177 B | Extended Daraz 2HP/3HP pricing |
| `zai_quota_history.jsonl` | 39 KB | ZAI API quota usage log (internal, not market data) |

---

## 10. Analysis Outputs (`outputs/`) — 80 KB

### Reports (Markdown):
| File | Size | Title/Description |
|------|------|-------------------|
| `Phase_1_Report_2026-05-07.md` | 9.2 KB | Phase 1 Data Collection Report — NBR import data, dealer pricing, IDCOL/SREDA |
| `Phase_1_Supplement_2026-05-07.md` | 7.2 KB | Dealer Pricing Deep Dive + Urban Housing Data |
| `Phase_2_Progress_2026-05-07.md` | 6.0 KB | Phase 2 Progress — NBR extended to 5 months, institutional sites limited |
| `Scraping_Arsenal_Research.md` | 6.8 KB | Scraping tools research (Camoufox, anti-detection browsers) |
| `gtm_strategy.md` | 7.1 KB | GTM Strategy: Leo Pump Bangladesh Market Entry |
| `pilot_submersible.md` | 7.8 KB | Pilot Market Assessment: Submersible Pumps (HS 8413.70) |

### Analysis Data (JSON):
| File | Size | Description |
|------|------|-------------|
| `zone_market_sizing.json` | 3.9 KB | Zone-level market sizing (Barind, etc.) — unit demand & value |
| `competitor_heatmap.json` | 5.8 KB | Bangladesh water pump market competitive heatmap |
| `consumer_persona_map.json` | 7.7 KB | Consumer personas & switching triggers by segment |
| `gtm_strategy.json` | 7.2 KB | GTM strategy structured data (mirrors .md version) |

---

## 11. Parsed Data (`parsed/`)

**Empty directory.** No structured/transformed data has been written here yet.

---

## Data Sources Coverage Summary

| Source | Status | Period | Completeness |
|--------|--------|--------|-------------|
| **NBR Import (HS 8413)** | ✅ Good | Dec 2025–Apr 2026 | 5 months, 93 line items. No historical. |
| **BADC Irrigation Surveys** | ⚠️ Partial | 2017–18 to 2023–24 | 7 PDFs + images downloaded, but pump data extraction failed |
| **BSTI Standards** | ✅ Complete | 2018 catalogue | Pump-relevant standards identified |
| **IDCOL/SREDA** | ✅ Partial | Current | 32 solar projects + SREDA tables. IDCOL main page 404. |
| **Daraz Pricing** | ✅ Good | Current | 1HP/2HP/3HP pricing collected |
| **Othoba Pricing** | ✅ Good | Current | 200+ product prices, richest source |
| **BDStall Pricing** | ✅ Partial | Current | 41 products |
| **BMDA Institutional** | ✅ Partial | Current | 3 annual reports + homepage data |
| **BWDB Tenders** | ❌ Empty | — | 0 tenders found |
| **Policy/Urban** | ⚠️ Partial | Current | Dhaka Structure Plan, RAJUK data |
| **BADC Key Pages** | ⚠️ Images only | 2021–24 | 77 curated page images, not OCR'd to structured data |

---

## Key Gaps & Risks

1. **BADC pump data extraction failed** — All 7 `_pump_data.json` files are empty. The PDFs were converted to images but structured data (pump counts, tube well numbers, irrigation areas) was not successfully extracted. This is a significant gap for installed-base analysis.

2. **NBR historical data unavailable** — 2025 and earlier import statements returned HTTP 400 from NBR website. Only 5 months available (Dec 2025–Apr 2026).

3. **IDCOL solar irrigation page 404** — The main IDCOL solar irrigation project page returned 404. Data was obtained from SREDA instead.

4. **BWDB tenders empty** — No pump-related tenders found from BWDB/CPPT/DASG.

5. **BADC `survey_2023_24_images/` duplicated** — Same 112 pages exist in both `irrigation_survey_2023_24_images/` and `survey_2023_24_images/`.

6. **Parsed directory empty** — No final structured/normalized data has been produced yet.

7. **Root-level raw scrapes limited** — `raw_nbr.json`, `raw_govt.json`, `raw_idcol.json` contain mostly navigation text, not structured data.

---

## File Count Summary

| Category | Files | Total Size |
|----------|-------|------------|
| BADC survey PDFs | 7 | ~70 MB |
| BADC page images | 573 | ~840 MB |
| BADC key pages | 77 | ~90 MB |
| BADC metadata JSON | 12 | ~76 KB |
| NBR PDFs | 10 | ~15 MB |
| NBR extracted text | 10 | ~2.2 MB |
| NBR metadata JSON | 5 | ~70 KB |
| BSTI files | 2 | 3.1 MB |
| IDCOL/SREDA | 2 | 334 KB |
| Pricing files | 5 | 152 KB |
| Institutional | 11 | ~16 MB |
| Policy files | 3 | ~12 MB |
| BWDB | 1 | 783 B |
| Root-level JSON | 6 | ~51 KB |
| Output reports | 12 | ~80 KB |
| **TOTAL** | **~733** | **~979 MB** |
