#!/usr/bin/env python3
"""Phase 2b: Alternative institutional sources.
- BMDA: Try annual report / statistics pages directly
- BIDA: Try service-investment pages
- BEZA: Try alternative URLs (Cloudflare bypass)
- BWDB: Tender / project pages
"""
import json, re, time
from pathlib import Path
from patchright.sync_api import sync_playwright

OUTPUT = Path("/Users/lbagent/.openclaw/workspace/leopump/data/raw/institutional")
OUTPUT.mkdir(parents=True, exist_ok=True)

TARGETS = [
    # BMDA — try English site and annual reports
    {"name": "bmda_en_home", "url": "https://www.bmda.gov.bd/site/page/b4f5ba1b-07c1-4e63-9509-d4c2f0e67e76", "agency": "BMDA"},
    {"name": "bmda_annual_report", "url": "https://www.bmda.gov.bd/site/page/6922e08a-933e-b655-69e2-77be2c4a6a90", "agency": "BMDA"},
    {"name": "bmda_statistics", "url": "https://www.bmda.gov.bd/site/page/6922e142-dbfb-ab28-ce07-92395d4a9c89", "agency": "BMDA"},
    
    # BIDA — alternative pages
    {"name": "bida_sectors", "url": "https://bida.gov.bd/sectors", "agency": "BIDA"},
    {"name": "bida_services", "url": "https://bida.gov.bd/one-stop-service", "agency": "BIDA"},
    {"name": "bida_osp", "url": "https://osp.bida.gov.bd/", "agency": "BIDA"},
    
    # BEZA — alternative
    {"name": "beza_investment", "url": "https://beza.gov.bd/invest-in-beza/", "agency": "BEZA"},
    
    # BWDB — tenders and projects
    {"name": "bwdb_tenders", "url": "https://www.bwdb.gov.bd/site/view/tender_list", "agency": "BWDB"},
    {"name": "bwdb_annual_report", "url": "https://www.bwdb.gov.bd/site/page/4a7d7c7b-08f0-4af0-89c4-29c4fc6c91ac", "agency": "BWDB"},
    
    # Additional: SREDA pump data — try direct API
    {"name": "sreda_api_test", "url": "https://ndre.sreda.gov.bd/api/v1/project?technology=Solar%20Irrigation&limit=500", "agency": "SREDA"},
]

def scrape(page, target):
    result = {
        "name": target["name"],
        "url": target["url"],
        "agency": target["agency"],
        "tables": [],
        "text_data": "",
        "errors": []
    }
    try:
        page.goto(target["url"], wait_until="networkidle", timeout=20000)
        time.sleep(2)
        
        text = page.evaluate("() => document.body.innerText.substring(0, 8000)")
        tables = page.evaluate("""
            () => {
                const tables = [];
                document.querySelectorAll('table').forEach(table => {
                    const rows = [];
                    table.querySelectorAll('tr').forEach(tr => {
                        const cells = Array.from(tr.querySelectorAll('th, td')).map(c => c.textContent.trim());
                        if (cells.some(c => c)) rows.push(cells);
                    });
                    if (rows.length) tables.push(rows);
                });
                return tables;
            }
        """)
        
        result["text_data"] = text
        result["tables"] = tables
        result["table_count"] = len(tables)
        result["page_title"] = page.title()
        
        # Check for PDF links
        pdf_links = page.evaluate("""
            () => Array.from(document.querySelectorAll('a[href$=".pdf"]'))
                .map(a => ({text: a.textContent.trim().substring(0, 80), href: a.href}))
                .slice(0, 20)
        """)
        result["pdf_links"] = pdf_links
        
        print(f"  [{target['agency']}] {target['name']}: {len(tables)} tables, {len(text)} chars, {len(pdf_links)} PDFs")
        
        # If BMDA has PDF annual reports, download them
        if target['agency'] == 'BMDA' and pdf_links:
            import urllib.request
            for pl in pdf_links[:5]:
                fname = pl['href'].split('/')[-1]
                if not fname.endswith('.pdf'):
                    fname += '.pdf'
                fpath = OUTPUT / fname
                if not fpath.exists():
                    try:
                        urllib.request.urlretrieve(pl['href'], fpath)
                        print(f"    [PDF] {fname} ({fpath.stat().st_size / 1024:.0f} KB)")
                        result.setdefault("downloaded_pdfs", []).append(fname)
                    except Exception as e:
                        print(f"    [PDF FAIL] {fname}: {e}")
        
    except Exception as e:
        result["errors"].append(str(e))
        print(f"  [{target['agency']}] {target['name']}: ERROR {e}")
    
    return result

def main():
    results = {}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            ignore_https_errors=True,
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        for t in TARGETS:
            r = scrape(page, t)
            results[t["name"]] = r
            time.sleep(1.5)
        
        browser.close()
    
    out = OUTPUT / "institutional_phase2b.json"
    with open(out, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nSaved to {out}")

if __name__ == "__main__":
    main()
