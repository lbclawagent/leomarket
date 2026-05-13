#!/usr/bin/env python3
"""BADC Irrigation Survey PDF Data Extraction Pipeline v3.

Extracts pump/irrigation data from BADC Minor Irrigation Survey Reports.
Uses pypdfium2/pymupdf to extract embedded text from PDFs with text layers.
For scanned/image-only PDFs, outputs a note that OCR is needed.

Key tables extracted:
  - Table 2.1: Equipment trend (DTW, STW, LLP counts by year)
  - Table 2.2: Irrigated area trend by mode
  - Table 5.2: Division-wise equipment counts
  - Table 5.3: Division-wise irrigated area
  - Table 5.5: Area irrigated by DTWs and STWs by division

Usage:
    uv run --directory /Users/lbagent/.openclaw/workspace scripts/ocr_badc.py
    uv run --directory /Users/lbagent/.openclaw/workspace scripts/ocr_badc.py --year 2023_24
"""

import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("/Users/lbagent/.openclaw/workspace/data/raw/badc")
OUTPUT_DIR = DATA_DIR

REPORTS = {
    "2023_24": {"pdf": "survey_2023_24.pdf", "label": "2023-24"},
    "2022_23": {"pdf": "survey_2022_23.pdf", "label": "2022-23"},
    "2021_22": {"pdf": "survey_2021_22.pdf", "label": "2021-22"},
    "2020_21": {"pdf": "survey_2020_21.pdf", "label": "2020-21"},
    "2019_20": {"pdf": "survey_2019_20.pdf", "label": "2019-20"},
    "2018_19": {"pdf": "survey_2018_19.pdf", "label": "2018-19"},
    "2017_18": {"pdf": "survey_2017_18.pdf", "label": "2017-18"},
}

# Known divisions in Bangladesh (with OCR variant mappings)
DIVISIONS = ['dhaka', 'mymensingh', 'rajshahi', 'rangpur', 'chattogram', 'khulna', 'sylhet', 'barishal']
DIVISION_ALIASES = {
    'dhaka': 'Dhaka',
    'mymensingh': 'Mymensingh',
    'rajshahi': 'Rajshahi',
    'rangpur': 'Rangpur',
    'chattogram': 'Chattogram', 'chittagong': 'Chattogram',
    'khulna': 'Khulna',
    'sylhet': 'Sylhet',
    'barishal': 'Barishal', 'barisal': 'Barishal',
    'total': 'Total',
}

def match_division(line_lower: str) -> str | None:
    """Match a line start to a division name (handling OCR errors)."""
    for alias, name in DIVISION_ALIASES.items():
        if line_lower.startswith(alias):
            return name
    # Handle OCR garbled names like [t/lymensingh, [/lymensingh
    if line_lower.startswith('[/') or line_lower.startswith('[t/'):
        if 'ymensingh' in line_lower:
            return 'Mymensingh'
    return None

def strip_division_name(line: str) -> str:
    """Remove the leading division name from a line."""
    # Remove all known aliases
    for alias in list(DIVISION_ALIASES.keys()) + ['[/', '[t/', 'i raka']:
        if line.lower().startswith(alias):
            return line[len(alias):].lstrip()
    # Handle garbled starts
    if line.lower().startswith('['):
        rest = re.sub(r'^\[.?/?\w*\s*', '', line)
        return rest
    return line


def extract_all_pages(pdf_path: Path) -> list[dict]:
    """Extract text from all pages using pypdfium2."""
    import pypdfium2 as pdfium
    pdf = pdfium.PdfDocument(str(pdf_path))
    pages = []
    for i in range(len(pdf)):
        page = pdf[i]
        text = page.get_textpage().get_text_range()
        pages.append({"page": i + 1, "text": text, "chars": len(text.strip())})
    pdf.close()
    return pages


def has_embedded_text(pages: list[dict]) -> bool:
    pages_with_text = sum(1 for p in pages if p["chars"] > 50)
    return pages_with_text > len(pages) * 0.3


def parse_num(s: str) -> int | float | None:
    """Parse a number string, handling commas and decimals."""
    s = s.strip().replace(',', '')
    if not s or s == '-':
        return 0
    try:
        if '.' in s:
            return float(s)
        return int(s)
    except ValueError:
        return None


# ─── Table Parsers ──────────────────────────────────────────────

def parse_equipment_trend(pages: list[dict]) -> list[dict]:
    """Parse Table 2.1: Trend of Minor Irrigation Equipment.
    Format: SEASON  DTW  STW  LLP  DTW%  STW%  LLP%
    """
    rows = []
    in_table = False
    
    for page_info in pages:
        text = page_info["text"]
        text_lower = text.lower()
        
        if "trend of minor irrigation equipment" in text_lower:
            in_table = True
        
        if not in_table:
            continue
        
        for line in text.split('\n'):
            line = line.strip()
            # Stop conditions
            if line.startswith('Note:') or line.startswith('Figure'):
                in_table = False
                break
            
            # Match year pattern: 2023-24, 2009- 10, 201 1-12, etc.
            m = re.match(r'^(\d{4}\s*[-–]\s*\d{2,4})\s+(.+)', line)
            if not m:
                continue
            
            season = m.group(1).replace(' ', '').replace('–', '-')
            rest = m.group(2)
            
            # Parse numbers from the rest
            num_strs = re.findall(r'-?[\d,.]+', rest)
            nums = []
            for ns in num_strs:
                v = parse_num(ns)
                if v is not None:
                    nums.append(v)
            
            if len(nums) < 2:
                continue
            
            row = {"season": season}
            
            # Separate counts (large integers) from percentages (small decimals or negatives)
            counts = [n for n in nums if isinstance(n, int) and n >= 0]
            pcts = [n for n in nums if isinstance(n, float) or (isinstance(n, int) and n < 0)]
            
            # If all nums look like integers, first N are counts, rest are pcts
            all_int = all(isinstance(n, int) and n >= 0 for n in nums)
            if all_int:
                # Determine split: if >3 large nums, first 3 are counts
                large = [n for n in nums if n > 100]
                if len(large) >= 3:
                    counts = large[:3]
                    pcts = [n for n in nums if n not in counts]
                elif len(large) == 2:
                    counts = large[:2]
                    pcts = []
                elif len(large) == 1:
                    counts = large[:1]
                    pcts = []
                else:
                    # Very early years with small counts
                    counts = [int(n) for n in nums[:3] if isinstance(n, int)]
            
            if len(counts) >= 1:
                row["dtw"] = counts[0]
            if len(counts) >= 2:
                row["stw"] = counts[1]
            if len(counts) >= 3:
                row["llp"] = counts[2]
            
            if pcts:
                row["pct_changes"] = pcts[:3]
            
            rows.append(row)
    
    return rows


def parse_irrigated_area(pages: list[dict]) -> list[dict]:
    """Parse Table 2.2: Trend of Irrigated Area by Mode.
    Format: SEASON  DTW  STW  LLP  Manual  Traditional  Gravity  Solar  DugWell  Total
    """
    rows = []
    in_table = False
    keys = ["dtw", "stw", "llp", "manual_artesian", "traditional", "gravity", "solar", "dug_well", "total"]
    
    for page_info in pages:
        text = page_info["text"]
        text_lower = text.lower()
        
        # Start on the page that has this specific table header
        if "trend of irrigated area" in text_lower and \
           ("minor irrigation mode" in text_lower or "different minor irrigation" in text_lower):
            in_table = True
            # Data may start on this very page - process remaining lines
        
        if not in_table:
            continue
        
        for line in text.split('\n'):
            line = line.strip()
            # Skip header/label lines
            if 'trend of irrigated area' in line.lower():
                continue
            if line.lower().startswith('irrigation season') or line.lower().startswith('irrigation'):
                continue
                
            # Stop conditions
            if line.startswith('Note:') or '2.3.2' in line or 'comparative study' in line.lower():
                in_table = False
                break
            
            m = re.match(r'^(\d{4}\s*[-–]\s*\d{2,4})\s+(.+)', line)
            if not m:
                continue
            
            season = m.group(1).replace(' ', '').replace('–', '-')
            rest = m.group(2)
            num_strs = re.findall(r'[\d,.]+', rest)
            
            if len(num_strs) < 2:
                continue
            
            row = {"season": season}
            for i, ns in enumerate(num_strs):
                v = parse_num(ns)
                if v is not None and i < len(keys):
                    row[keys[i]] = v
            
            rows.append(row)
    
    return rows


def parse_division_equipment(pages: list[dict]) -> list[dict]:
    """Parse Table 5.2: Division-wise irrigation equipment.
    Format: Division  DTW  STW  LLP  FloatPump  SolarPump  Total
    """
    rows = []
    
    for page_info in pages:
        text = page_info["text"]
        text_lower = text.lower()
        
        if "division-wise irrigation equipment" not in text_lower and \
           "division wise" not in text_lower:
            continue
        
        for line in text.split('\n'):
            line = line.strip()
            line_lower = line.lower()
            
            # Check if line starts with a division name
            found_div = None
            for div in DIVISIONS:
                if line_lower.startswith(div):
                    found_div = div.title()
                    break
            
            if line_lower.startswith('total'):
                found_div = "Total"
            
            if not found_div:
                continue
            
            # Parse numbers after the division name
            # Remove the division name and parse remaining
            rest = re.sub(r'^(dhaka|mymensingh|rajshahi|rangpur|chattogram|khulna|sylhet|barishal|total)\s*', '', line_lower, flags=re.IGNORECASE)
            num_strs = re.findall(r'[\d,.]+', rest)
            
            if len(num_strs) < 3:
                continue
            
            nums = [parse_num(ns) for ns in num_strs]
            nums = [n for n in nums if n is not None]
            
            keys = ["dtw", "stw", "llp", "floating_pump", "solar_pump", "total"]
            row = {"division": found_div}
            for i, n in enumerate(nums):
                if i < len(keys):
                    row[keys[i]] = n
            
            rows.append(row)
    
    return rows


def parse_division_area(pages: list[dict]) -> list[dict]:
    """Parse Table 5.3: Division-wise irrigated area.
    Format: Division  Area(ha)  %ofTotal
    """
    rows = []
    
    for page_info in pages:
        text = page_info["text"]
        text_lower = text.lower()
        
        if "division wise irrigated area" not in text_lower and \
           "division-wise irrigated area" not in text_lower:
            continue
        
        for line in text.split('\n'):
            line = line.strip()
            line_lower = line.lower()
            
            found_div = None
            for div in DIVISIONS:
                if line_lower.startswith(div):
                    found_div = div.title()
                    break
            if line_lower.startswith('total') and 'division' not in line_lower:
                found_div = "Total"
            
            if not found_div:
                continue
            
            rest = re.sub(r'^(dhaka|mymensingh|rajshahi|rangpur|chattogram|chittagong|khulna|sylhet|barishal|barisal|total)\s*', '', line_lower, flags=re.IGNORECASE)
            num_strs = re.findall(r'[\d,.]+', rest)
            
            if len(num_strs) < 1:
                continue
            
            nums = [parse_num(ns) for ns in num_strs]
            nums = [n for n in nums if n is not None]
            
            row = {"division": found_div}
            if len(nums) >= 1:
                row["irrigated_area_ha"] = nums[0]
            if len(nums) >= 2:
                row["pct_of_total"] = nums[1]
            
            rows.append(row)
            # Stop after getting the full table (8 divisions + total)
            if len(rows) >= 9:
                break
        
        if len(rows) >= 9:
            break
    
    return rows


def parse_dtw_stw_area_by_division(pages: list[dict]) -> list[dict]:
    """Parse Table 5.5: Area irrigated by DTWs and STWs by division."""
    rows = []
    
    for page_info in pages:
        text = page_info["text"]
        text_lower = text.lower()
        
        if "area irrigated by dtw" not in text_lower:
            continue
        
        for line in text.split('\n'):
            line = line.strip()
            line_lower = line.lower()
            
            found_div = None
            for div in DIVISIONS:
                if line_lower.startswith(div):
                    found_div = div.title()
                    break
            if line_lower.startswith('total'):
                found_div = "Total"
            
            if not found_div:
                continue
            
            rest = re.sub(r'^(dhaka|mymensingh|rajshahi|rangpur|chattogram|khulna|sylhet|barishal|total)\s*', '', line_lower, flags=re.IGNORECASE)
            num_strs = re.findall(r'[\d,.]+', rest)
            
            if len(num_strs) < 3:
                continue
            
            nums = [parse_num(ns) for ns in num_strs]
            nums = [n for n in nums if n is not None]
            
            row = {"division": found_div, "values": nums}
            rows.append(row)
    
    return rows


def extract_key_metrics(pages: list[dict], year_label: str) -> dict:
    """Extract key summary metrics from executive summary and overview pages."""
    metrics = {"year_label": year_label}
    
    # Combine text from first 70 pages for key metrics
    full_text = '\n'.join(p["text"] for p in pages[:70])
    
    # Total irrigated area
    m = re.search(r'irrigated\s+area\s+was\s+([\d.]+)\s*million\s*ha', full_text, re.IGNORECASE)
    if m:
        metrics["total_irrigated_area_million_ha"] = float(m.group(1))
    
    # Total equipment
    m = re.search(r'([\d,]+)\s*nos?\.?\s*of\s*irrigation\s*equipment', full_text, re.IGNORECASE)
    if m:
        metrics["total_equipment"] = parse_num(m.group(1))
    
    # Farmers benefited
    m = re.search(r'([\d,.]+)\s*million\s*farmers?', full_text, re.IGNORECASE)
    if m:
        metrics["farmers_benefited_million"] = float(m.group(1))
    
    # Groundwater percentage
    m = re.search(r'([\d.]+)\s*%\s*(?:of\s+total\s+)?(?:irrigated\s+area|irrigation)', full_text, re.IGNORECASE)
    if m and "groundwater" in full_text[max(0, m.start()-200):m.start()].lower():
        metrics["groundwater_pct"] = float(m.group(1))
    
    # Latest year equipment from parsed trend table
    eq_data = parse_equipment_trend(pages)
    if eq_data:
        latest = eq_data[-1]
        metrics["latest_season"] = latest.get("season")
        metrics["latest_dtw"] = latest.get("dtw")
        metrics["latest_stw"] = latest.get("stw")
        metrics["latest_llp"] = latest.get("llp")
    
    return metrics


def extract_full_text(pages: list[dict], output_path: Path):
    """Save full extracted text to a file."""
    lines = []
    for p in pages:
        lines.append(f"\n{'='*60}")
        lines.append(f"PAGE {p['page']} ({p['chars']} chars)")
        lines.append(f"{'='*60}")
        lines.append(p["text"])
    output_path.write_text('\n'.join(lines), encoding='utf-8')


def process_report(year_key: str, report_info: dict) -> dict:
    """Process a single BADC survey report."""
    pdf_path = DATA_DIR / report_info["pdf"]
    year_label = report_info["label"]
    
    print(f"\n{'='*60}")
    print(f"Processing: BADC Survey {year_label}")
    print(f"{'='*60}")
    
    if not pdf_path.exists():
        print(f"  [FAIL] PDF not found")
        return {"status": "pdf_missing", "year": year_label}
    
    # Extract text
    print(f"  Extracting text...")
    pages = extract_all_pages(pdf_path)
    total_pages = len(pages)
    pages_with_text = sum(1 for p in pages if p["chars"] > 50)
    has_text = has_embedded_text(pages)
    
    print(f"  → {total_pages} pages, {pages_with_text} with text, has_embedded={has_text}")
    
    if not has_text:
        print(f"  ⚠ Scanned PDF - needs OCR (not available)")
        result = {
            "status": "scanned_needs_ocr",
            "year": year_label,
            "has_embedded_text": False,
            "total_pages": total_pages,
            "pages_with_text": pages_with_text,
            "processed_at": datetime.now().isoformat(),
        }
        # Save minimal result
        json_path = OUTPUT_DIR / f"irrigation_survey_{year_key}_pump_data.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        return result
    
    # Parse tables
    print(f"  Parsing tables...")
    equipment_trend = parse_equipment_trend(pages)
    irrigated_area = parse_irrigated_area(pages)
    division_equipment = parse_division_equipment(pages)
    division_area = parse_division_area(pages)
    dtw_stw_area = parse_dtw_stw_area_by_division(pages)
    key_metrics = extract_key_metrics(pages, year_label)
    
    print(f"  → Equipment trend: {len(equipment_trend)} rows")
    print(f"  → Irrigated area: {len(irrigated_area)} rows")
    print(f"  → Division equipment: {len(division_equipment)} rows")
    print(f"  → Division area: {len(division_area)} rows")
    print(f"  → DTW/STW area by div: {len(dtw_stw_area)} rows")
    
    # Save full text
    txt_path = OUTPUT_DIR / f"irrigation_survey_{year_key}_full_text.txt"
    extract_full_text(pages, txt_path)
    
    # Save structured data
    result = {
        "status": "completed",
        "year": year_label,
        "has_embedded_text": True,
        "total_pages": total_pages,
        "pages_with_text": pages_with_text,
        "equipment_trend": equipment_trend,
        "irrigated_area": irrigated_area,
        "division_equipment": division_equipment,
        "division_area": division_area,
        "dtw_stw_area_by_division": dtw_stw_area,
        "key_metrics": key_metrics,
        "processed_at": datetime.now().isoformat(),
    }
    
    json_path = OUTPUT_DIR / f"irrigation_survey_{year_key}_pump_data.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"  → Saved {json_path.name} ({json_path.stat().st_size:,} bytes)")
    
    return result


def main():
    import argparse
    parser = argparse.ArgumentParser(description='BADC Irrigation Survey Data Extraction')
    parser.add_argument('--year', type=str, help='Specific year (e.g., 2023_24)')
    args = parser.parse_args()
    
    print("="*60)
    print("BADC Irrigation Survey Data Extraction Pipeline v3")
    print(f"Started: {datetime.now().isoformat()}")
    print("="*60)
    
    years = {args.year: REPORTS[args.year]} if args.year else REPORTS
    results = {"started": datetime.now().isoformat(), "pipeline_version": "3.0", "reports": {}}
    
    for year_key, info in years.items():
        try:
            results["reports"][year_key] = process_report(year_key, info)
        except Exception as e:
            import traceback
            traceback.print_exc()
            results["reports"][year_key] = {"status": "error", "error": str(e)}
    
    # Summary
    results["completed"] = datetime.now().isoformat()
    results_path = OUTPUT_DIR / "badc_extraction_results.json"
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    for yk, r in results["reports"].items():
        status = r.get("status", "?")
        if status == "completed":
            eq = len(r.get("equipment_trend", []))
            ia = len(r.get("irrigated_area", []))
            de = len(r.get("division_equipment", []))
            da = len(r.get("division_area", []))
            km = r.get("key_metrics", {})
            latest = km.get("latest_season", "?")
            dtw = km.get("latest_dtw", "?")
            stw = km.get("latest_stw", "?")
            llp = km.get("latest_llp", "?")
            print(f"  {yk}: ✅ {r['total_pages']}p | Equip:{eq} rows | Area:{ia} rows | Div.Eq:{de} | Div.Area:{da}")
            print(f"         Latest ({latest}): DTW={dtw}, STW={stw}, LLP={llp}")
        elif status == "scanned_needs_ocr":
            print(f"  {yk}: ⚠️  Scanned PDF ({r['total_pages']}p) - needs OCR")
        else:
            print(f"  {yk}: ❌ {status}")
    
    print(f"\nResults: {results_path}")
    return results


if __name__ == "__main__":
    main()
