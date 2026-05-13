#!/usr/bin/env python3
"""Camoufox Institutional Scraper — Anti-detect browser for BD government sites.
Targets: BMDA, BWDB, BIDA, BEZA (the sites Patchright couldn't crack)
"""
import json, re, time
from pathlib import Path
from camoufox.sync_api import Camoufox

OUTPUT = Path("/Users/lbagent/.openclaw/workspace/leopump/data/raw/institutional")
OUTPUT.mkdir(parents=True, exist_ok=True)

TARGETS = [
    # === BEZA — Cloudflare blocked ===
    {"name": "beza_home", "url": "https://www.beza.gov.bd/", "agency": "BEZA"},
    {"name": "beza_zones", "url": "https://www.beza.gov.bd/economic-zones/", "agency": "BEZA"},
    {"name": "beza_invest", "url": "https://beza.gov.bd/invest-in-beza/", "agency": "BEZA"},
    # === BMDA — JS-heavy, no data rendered ===
    {"name": "bmda_home", "url": "https://www.bmda.gov.bd/", "agency": "BMDA"},
    {"name": "bmda_irrigation", "url": "https://www.bmda.gov.bd/site/page/60c8e22c-8540-4b0d-a56f-5b25e8af9768", "agency": "BMDA"},
    {"name": "bmda_activities", "url": "https://www.bmda.gov.bd/site/page/4e91c8c1-2c14-4c0f-ae3c-c0afdf6d6c11", "agency": "BMDA"},
    # === BIDA — 404 on subpages ===
    {"name": "bida_home", "url": "https://bida.gov.bd/", "agency": "BIDA"},
    {"name": "bida_sectors", "url": "https://bida.gov.bd/sectors", "agency": "BIDA"},
    {"name": "bida_services", "url": "https://bida.gov.bd/one-stop-service", "agency": "BIDA"},
    # === BWDB — empty responses ===
    {"name": "bwdb_home", "url": "https://www.bwdb.gov.bd/", "agency": "BWDB"},
    {"name": "bwdb_annual", "url": "https://www.bwdb.gov.bd/site/page/4a7d7c7b-08f0-4af0-89c4-29c4fc6c91ac", "agency": "BWDB"},
    {"name": "bwdb_tenders", "url": "https://www.bwdb.gov.bd/site/view/tender_list", "agency": "BWDB"},
]

def scrape_page(page, target):
    result = {
        "name": target["name"],
        "url": target["url"],
        "agency": target["agency"],
        "tables": [],
        "text_data": "",
        "pdf_links": [],
        "pump_mentions": [],
        "errors": []
    }
    
    try:
        print(f"[{target['agency']}] {target['name']}: {target['url']}")
        page.goto(target["url"], timeout=30000)
        time.sleep(3)
        
        # Scroll to trigger lazy content
        page.evaluate("""
            async () => {
                for (let i = 0; i < 8; i++) {
                    window.scrollBy(0, 600);
                    await new Promise(r => setTimeout(r, 500));
                }
                window.scrollTo(0, 0);
            }
        """)
        time.sleep(2)
        
        # Check if Cloudflare challenge was bypassed
        title = page.title()
        body_text = page.evaluate("() => document.body.innerText.substring(0, 10000)")
        
        # Extract tables
        tables = page.evaluate("""
            () => {
                const tables = [];
                document.querySelectorAll('table').forEach(table => {
                    const rows = [];
                    table.querySelectorAll('tr').forEach(tr => {
                        const cells = Array.from(tr.querySelectorAll('th, td')).map(c => c.textContent.trim());
                        if (cells.some(c => c)) rows.push(cells);
                    });
                    if (rows.length > 0) tables.push(rows);
                });
                return tables;
            }
        """)
        
        # Extract PDF links
        pdf_links = page.evaluate("""
            () => Array.from(document.querySelectorAll('a[href$=".pdf"], a[href*=".pdf"]'))
                .map(a => ({text: a.textContent.trim().substring(0, 100), href: a.href}))
                .filter(p => p.href.includes('.pdf'))
                .slice(0, 30)
        """)
        
        # Pump-related mentions
        pump_keywords = ['pump', 'পাম্প', 'submersible', 'centrifugal', 'tube well', 
                         'irrigation', 'সেচ', 'booster', 'drainage', 'motor', 'HP',
                         'deep tube', 'shallow tube', 'নলকূপ', 'টিউবওয়েল']
        pump_lines = []
        for line in body_text.split('\n'):
            if any(kw.lower() in line.lower() for kw in pump_keywords):
                pump_lines.append(line.strip()[:200])
        
        result["tables"] = tables
        result["text_data"] = body_text
        result["table_count"] = len(tables)
        result["pdf_links"] = pdf_links
        result["pump_mentions"] = pump_lines[:40]
        result["pump_mention_count"] = len(pump_lines)
        result["page_title"] = title
        
        cf_status = "BLOCKED" if "just a moment" in title.lower() or "cloudflare" in title.lower() else "OK"
        
        print(f"  Title: {title[:60]} | CF: {cf_status}")
        print(f"  Tables: {len(tables)} | PDFs: {len(pdf_links)} | Pump mentions: {len(pump_lines)} | Text: {len(body_text)} chars")
        
        if pdf_links:
            print(f"  PDF links:")
            for pl in pdf_links[:5]:
                print(f"    → {pl['text'][:60]} | {pl['href'][:80]}")
        
        if pump_lines:
            print(f"  Pump mentions:")
            for pl in pump_lines[:5]:
                print(f"    → {pl[:80]}")
        
    except Exception as e:
        result["errors"].append(str(e))
        print(f"  ERROR: {e}")
    
    return result

def main():
    results = {}
    
    print("=== CAMOUFOX ANTI-DETECT SCRAPER ===\n")
    
    with Camoufox(headless=True) as browser:
        page = browser.new_page()
        
        for target in TARGETS:
            result = scrape_page(page, target)
            results[target["name"]] = result
            time.sleep(2)
        
        # If BMDA has interesting pages, try navigating deeper
        bmda_deep = []
        for name, r in results.items():
            if r["agency"] == "BMDA" and not r["errors"] and len(r["text_data"]) > 500:
                # Look for links to annual reports or statistics
                deep_links = page.evaluate("""
                    () => {
                        return Array.from(document.querySelectorAll('a'))
                            .filter(a => {
                                const t = (a.textContent + ' ' + a.href).toLowerCase();
                                return t.includes('annual') || t.includes('report') || 
                                       t.includes('statistics') || t.includes('বার্ষিক') ||
                                       t.includes('পরিসংখ্যান') || t.includes('প্রতিবেদন') ||
                                       t.includes('irrigation') || t.includes('সেচ') ||
                                       t.includes('tube well') || t.includes('পাম্প');
                            })
                            .map(a => ({text: a.textContent.trim().substring(0, 80), href: a.href}))
                            .filter(l => l.href.startsWith('http'))
                            .slice(0, 15);
                    }
                """)
                if deep_links:
                    print(f"\n  [BMDA DEEP] Found {len(deep_links)} relevant links:")
                    for dl in deep_links:
                        print(f"    → {dl['text'][:60]} | {dl['href'][:70]}")
                    
                    # Visit most promising links
                    for dl in deep_links[:5]:
                        try:
                            page.goto(dl['href'], timeout=15000)
                            time.sleep(2)
                            text = page.evaluate("() => document.body.innerText.substring(0, 6000)")
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
                            pdfs = page.evaluate("""
                                () => Array.from(document.querySelectorAll('a[href*=".pdf"]'))
                                    .map(a => ({text: a.textContent.trim().substring(0, 80), href: a.href}))
                                    .slice(0, 10)
                            """)
                            
                            key = f"bmda_deep_{dl['text'][:30].replace(' ','_')}"
                            results[key] = {
                                "name": key,
                                "url": dl['href'],
                                "agency": "BMDA",
                                "text_data": text,
                                "tables": tables,
                                "pdf_links": pdfs,
                                "errors": []
                            }
                            print(f"    [{key}] Tables: {len(tables)} | PDFs: {len(pdfs)} | Text: {len(text)}")
                        except Exception as e:
                            print(f"    Deep link error: {e}")
        
        browser.close()
    
    # Save
    out = OUTPUT / "camoufox_institutional.json"
    with open(out, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Summary
    print(f"\n=== SUMMARY ===")
    for agency in ["BEZA", "BMDA", "BIDA", "BWDB"]:
        agency_results = {k: v for k, v in results.items() if v.get("agency") == agency}
        total_tables = sum(r.get("table_count", 0) for r in agency_results.values())
        total_pdfs = sum(len(r.get("pdf_links", [])) for r in agency_results.values())
        total_pump = sum(r.get("pump_mention_count", 0) for r in agency_results.values())
        ok = sum(1 for r in agency_results.values() if not r.get("errors"))
        cf_blocked = sum(1 for r in agency_results.values() if "just a moment" in r.get("page_title", "").lower())
        print(f"  [{agency}] {ok}/{len(agency_results)} OK | CF blocked: {cf_blocked} | Tables: {total_tables} | PDFs: {total_pdfs} | Pump mentions: {total_pump}")
    
    print(f"\nSaved to {out}")

if __name__ == "__main__":
    main()
