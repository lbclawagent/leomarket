#!/usr/bin/env python3
"""IDCOL/SREDA Solar Pump Data Scraper — Phase 1
Scrapes solar irrigation pump installation data from SREDA portal.
"""
import json, re, time, sys
from pathlib import Path
from patchright.sync_api import sync_playwright

OUTPUT_DIR = Path("/Users/lbagent/.openclaw/workspace/leopump/data/raw/idcol")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# SREDA portal for IDCOL solar pump data
URLS = [
    {"name": "sreda_solar_pump", "url": "https://ndre.sreda.gov.bd/index.php?id=01&i=4"},
    {"name": "sreda_home", "url": "https://ndre.sreda.gov.bd/"},
    {"name": "idcol_solar_irrigation", "url": "https://www.idcol.org/project/solar-irrigation"},
    {"name": "idcol_home", "url": "https://www.idcol.org/"},
]

def scrape_idcol():
    results = {}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        
        for source in URLS:
            name = source["name"]
            url = source["url"]
            result = {"url": url, "tables": [], "text_data": "", "errors": []}
            
            try:
                print(f"[{name}] Navigating to {url}")
                page.goto(url, wait_until="networkidle", timeout=25000)
                time.sleep(2)
                
                # Extract tables
                tables = page.evaluate("""
                    () => {
                        const tables = [];
                        document.querySelectorAll('table').forEach((table, idx) => {
                            const rows = [];
                            table.querySelectorAll('tr').forEach(tr => {
                                const cells = Array.from(tr.querySelectorAll('th, td'))
                                    .map(cell => cell.textContent.trim());
                                if (cells.some(c => c)) rows.push(cells);
                            });
                            if (rows.length > 0) tables.push(rows);
                        });
                        return tables;
                    }
                """)
                
                # Extract key text content
                text_data = page.evaluate("""
                    () => {
                        const body = document.body.innerText;
                        return body.substring(0, 5000);
                    }
                """)
                
                # Look for numbers that could be pump counts, capacity, etc.
                numbers = re.findall(r'[\d,]+(?:\.\d+)?', text_data)
                
                result["tables"] = tables
                result["text_data"] = text_data[:3000]
                result["table_count"] = len(tables)
                result["page_title"] = page.title()
                
                print(f"[{name}] Title: {page.title()}, Tables: {len(tables)}, Text: {len(text_data)} chars")
                
            except Exception as e:
                result["errors"].append(str(e))
                print(f"[{name}] ERROR: {e}")
            
            results[name] = result
            time.sleep(1)
        
        browser.close()
    
    out_path = OUTPUT_DIR / "idcol_sreda_data.json"
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n[IDCOL] Saved to {out_path}")
    return results

if __name__ == "__main__":
    scrape_idcol()
