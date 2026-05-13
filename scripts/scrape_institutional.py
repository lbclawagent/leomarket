#!/usr/bin/env python3
"""Institutional Data Scraper — BMDA, BWDB, BIDA, BEZA.
Tier 1: BMDA (Barind irrigation), BWDB (flood/drainage/municipal)
Tier 2: BIDA (investment), BEZA (economic zones)
"""
import json, re, time
from pathlib import Path
from patchright.sync_api import sync_playwright

OUTPUT_DIR = Path("/Users/lbagent/.openclaw/workspace/leopump/data/raw/institutional")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TARGETS = [
    # === BMDA (Tier 1) ===
    {
        "name": "bmda_home",
        "url": "https://www.bmda.gov.bd/",
        "agency": "BMDA",
        "priority": 1
    },
    {
        "name": "bmda_activities",
        "url": "https://www.bmda.gov.bd/site/page/4e91c8c1-2c14-4c0f-ae3c-c0afdf6d6c11",
        "agency": "BMDA",
        "priority": 1
    },
    {
        "name": "bmda_irrigation",
        "url": "https://www.bmda.gov.bd/site/page/60c8e22c-8540-4b0d-a56f-5b25e8af9768",
        "agency": "BMDA",
        "priority": 1
    },
    {
        "name": "bmda_groundwater",
        "url": "https://www.bmda.gov.bd/site/page/a99e6546-9cb7-49d5-82cb-8d42a2c49bbf",
        "agency": "BMDA",
        "priority": 1
    },
    # === BWDB (Tier 1) ===
    {
        "name": "bwdb_home",
        "url": "https://www.bwdb.gov.bd/",
        "agency": "BWDB",
        "priority": 1
    },
    {
        "name": "bwdb_projects",
        "url": "https://www.bwdb.gov.bd/site/page/70e39e9a-c5b3-4e09-8d1b-4ddca3e89d4b",
        "agency": "BWDB",
        "priority": 1
    },
    # === BIDA (Tier 2) ===
    {
        "name": "bida_home",
        "url": "https://bida.gov.bd/",
        "agency": "BIDA",
        "priority": 2
    },
    {
        "name": "bida_investment",
        "url": "https://bida.gov.bd/investment-promotion",
        "agency": "BIDA",
        "priority": 2
    },
    {
        "name": "bida_incentives",
        "url": "https://bida.gov.bd/investment-climate/fiscal-incentives",
        "agency": "BIDA",
        "priority": 2
    },
    # === BEZA (Tier 2) ===
    {
        "name": "beza_home",
        "url": "https://www.beza.gov.bd/",
        "agency": "BEZA",
        "priority": 2
    },
    {
        "name": "beza_zones",
        "url": "https://www.beza.gov.bd/economic-zones/",
        "agency": "BEZA",
        "priority": 2
    },
]

def scrape_page(page, target):
    result = {
        "name": target["name"],
        "url": target["url"],
        "agency": target["agency"],
        "priority": target["priority"],
        "tables": [],
        "text_data": "",
        "pump_mentions": [],
        "numbers": [],
        "errors": []
    }
    
    try:
        print(f"[{target['agency']}] {target['name']}: {target['url']}")
        page.goto(target["url"], wait_until="networkidle", timeout=25000)
        time.sleep(2)
        
        # Extract tables
        tables = page.evaluate("""
            () => {
                const tables = [];
                document.querySelectorAll('table').forEach((table, idx) => {
                    const rows = [];
                    table.querySelectorAll('tr').forEach(tr => {
                        const cells = Array.from(tr.querySelectorAll('th, td'))
                            .map(cell => cell.textContent.trim().substring(0, 200));
                        if (cells.some(c => c)) rows.push(cells);
                    });
                    if (rows.length > 0) tables.push(rows);
                });
                return tables;
            }
        """)
        
        # Extract page text
        text_data = page.evaluate("() => document.body.innerText.substring(0, 8000)")
        
        # Find pump-related mentions
        pump_keywords = ['pump', 'পাম্প', 'submersible', 'centrifugal', 'tube well', 
                         'irrigation', 'সেচ', 'booster', 'drainage', 'flood',
                         'motor', 'HP', 'horsepower', 'water supply']
        pump_lines = []
        for line in text_data.split('\n'):
            if any(kw.lower() in line.lower() for kw in pump_keywords):
                pump_lines.append(line.strip()[:200])
        
        # Extract significant numbers
        numbers = []
        for match in re.finditer(r'[\d,]+(?:\.\d+)?', text_data):
            try:
                val = float(match.group().replace(',', ''))
                if val > 100:
                    numbers.append(val)
            except:
                pass
        
        result["tables"] = tables
        result["text_data"] = text_data
        result["table_count"] = len(tables)
        result["pump_mentions"] = pump_lines[:30]
        result["pump_mention_count"] = len(pump_lines)
        result["numbers"] = numbers[:100]
        result["page_title"] = page.title()
        
        print(f"  Title: {page.title()[:60]}")
        print(f"  Tables: {len(tables)} | Pump mentions: {len(pump_lines)} | Text: {len(text_data)} chars")
        
    except Exception as e:
        result["errors"].append(str(e))
        print(f"  ERROR: {e}")
    
    return result

def main():
    all_results = {}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            ignore_https_errors=True,
            viewport={"width": 1366, "height": 768},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        for target in TARGETS:
            result = scrape_page(page, target)
            all_results[target["name"]] = result
            time.sleep(1.5)
        
        # Try BMDA deep links — look for pump/tube well data pages
        print("\n[BMDA] Trying to find deep tube well / pump inventory pages...")
        bmda_deep_urls = [
            "https://www.bmda.gov.bd/site/page/60c8e22c-8540-4b0d-a56f-5b25e8af9768",  # irrigation
            "https://www.bmda.gov.bd/site/notices",
        ]
        for url in bmda_deep_urls:
            try:
                page.goto(url, wait_until="networkidle", timeout=15000)
                time.sleep(2)
                links = page.evaluate("""
                    () => {
                        return Array.from(document.querySelectorAll('a')).filter(a => {
                            const t = (a.textContent + ' ' + a.href).toLowerCase();
                            return t.includes('tube well') || t.includes('pump') || t.includes('irrigation') || t.includes('পাম্প') || t.includes('সেচ');
                        }).map(a => ({text: a.textContent.trim().substring(0, 100), href: a.href})).slice(0, 20);
                    }
                """)
                if links:
                    print(f"  Found {len(links)} pump-related links on {url}")
                    # Visit first few
                    for link in links[:3]:
                        try:
                            page.goto(link['href'], wait_until="networkidle", timeout=15000)
                            time.sleep(2)
                            text = page.evaluate("() => document.body.innerText.substring(0, 5000)")
                            result = {
                                "name": f"bmda_deep_{link['text'][:30]}",
                                "url": link['href'],
                                "agency": "BMDA",
                                "text_data": text,
                                "tables": page.evaluate("""
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
                                """),
                                "errors": []
                            }
                            result["table_count"] = len(result["tables"])
                            all_results[f"bmda_deep_{len(all_results)}"] = result
                            print(f"    → {link['text'][:50]}: {result['table_count']} tables, {len(text)} chars")
                        except:
                            pass
            except Exception as e:
                print(f"  Deep link error: {e}")
        
        browser.close()
    
    # Save
    out_path = OUTPUT_DIR / "institutional_data.json"
    with open(out_path, 'w') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    # Summary
    for agency in ["BMDA", "BWDB", "BIDA", "BEZA"]:
        agency_results = {k: v for k, v in all_results.items() if v.get("agency") == agency}
        total_tables = sum(r.get("table_count", 0) for r in agency_results.values())
        total_pump = sum(r.get("pump_mention_count", 0) for r in agency_results.values())
        ok = sum(1 for r in agency_results.values() if not r.get("errors"))
        print(f"\n[{agency}] {ok}/{len(agency_results)} pages OK | {total_tables} tables | {total_pump} pump mentions")
    
    print(f"\nSaved to {out_path}")

if __name__ == "__main__":
    main()
