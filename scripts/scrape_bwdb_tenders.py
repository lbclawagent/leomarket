#!/usr/bin/env python3
"""BWDB & CPPT Tender Scraper for Pump-Related Procurement.
Scrapes active tenders from BWDB, CPPT, and newspaper procurement sections.
"""
import json, re, time, os
from pathlib import Path
from datetime import datetime
from patchright.sync_api import sync_playwright

OUTPUT_DIR = Path("/Users/lbagent/.openclaw/workspace/leopump/data/raw/bwdb")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def search_cppt_tenders(page):
    """Search CPPT/e-GP portal for pump tenders."""
    tenders = []
    
    # Try the e-GP portal search
    search_urls = [
        "https://www.eprocure.gov.bd/home.jsp",
        "https://cptu.gov.bd/",
    ]
    
    # Alternative: search Prothom Alo procurement notices
    search_terms = [
        "pump tender Bangladesh",
        "irrigation pump procurement Bangladesh",
        "BWDB pump tender",
        "water pump procurement Bangladesh government",
    ]
    
    # Use web_fetch approach - search known tender notice sites
    tender_sources = {
        "cppt": "https://www.eprocure.gov.bd/home.jsp",
        "bwdb": "https://bwdb.gov.bd/",
        "dasg": "https://www.dpp.gov.bd/",  # Development project proposals
    }
    
    for source_name, url in tender_sources.items():
        try:
            print(f"  [{source_name}] Checking {url}")
            resp = page.goto(url, wait_until="domcontentloaded", timeout=20000)
            time.sleep(2)
            
            content = page.content()
            
            # Look for tender-related text
            pump_mentions = re.findall(
                r'(?i)(pump|irrigation|সেচ|পাম্প|নিষ্কাশন|drainage|flood).*?(?:tender|procurement|notice|advertisement)',
                content
            )
            
            if pump_mentions:
                print(f"    Found {len(pump_mentions)} pump-related mentions")
                tenders.append({
                    "source": source_name,
                    "url": url,
                    "mentions": pump_mentions[:5],
                    "status": "found"
                })
            else:
                print(f"    No pump mentions found")
                tenders.append({
                    "source": source_name,
                    "url": url,
                    "status": "no_pump_tenders"
                })
        except Exception as e:
            print(f"    Error: {e}")
            tenders.append({
                "source": source_name,
                "url": url,
                "status": "error",
                "error": str(e)
            })
    
    return tenders

def search_newspaper_procurement(page):
    """Search newspaper procurement sections for pump tenders."""
    tenders = []
    
    # Bengali newspaper tender pages
    sources = {
        "prothomalo_tenders": "https://www.prothomalo.com/tender",
        "dailystar_notices": "https://www.thedailystar.net/tender-notices",
        "jugantor_tender": "https://www.jugantor.com/tender",
    }
    
    for source_name, url in sources.items():
        try:
            print(f"  [{source_name}] Checking {url}")
            resp = page.goto(url, wait_until="domcontentloaded", timeout=15000)
            time.sleep(2)
            
            # Extract tender titles
            titles = page.evaluate("""
                () => {
                    const items = [];
                    document.querySelectorAll('h2, h3, h4, .title, .headline, a').forEach(el => {
                        const text = el.textContent.trim();
                        if (text.length > 20 && text.length < 300) {
                            items.push(text);
                        }
                    });
                    return items.slice(0, 30);
                }
            """)
            
            # Filter for pump-related
            pump_re = re.compile(r'(?i)(pump|পাম্প|সেচ|irrigation|tube.?well|নিষ্কাশন|drainage|flood|বন্যা)')
            pump_tenders = [t for t in titles if pump_re.search(t)]
            
            if pump_tenders:
                print(f"    Found {len(pump_tenders)} pump-related tender headlines")
                tenders.extend([{
                    "source": source_name,
                    "title": t,
                    "url": url,
                    "relevance": "pump"
                } for t in pump_tenders])
            
        except Exception as e:
            print(f"    Error: {e}")
    
    return tenders

def search_ogd_tenders(page):
    """Search Open Government Data portal for procurement data."""
    tenders = []
    
    # Try CPTU e-Procurement
    try:
        url = "https://www.eprocure.gov.bd/tendersearch.jsp"
        print(f"  [eGP] Searching tenders...")
        resp = page.goto(url, wait_until="domcontentloaded", timeout=20000)
        time.sleep(3)
        
        # Try to use the search form
        search_input = page.query_selector('input[name="search"], input[type="text"], #searchTender')
        if search_input:
            search_input.fill("pump")
            time.sleep(1)
            
            # Look for submit button
            submit = page.query_selector('button[type="submit"], input[type="submit"], .search-btn')
            if submit:
                submit.click()
                time.sleep(3)
                
                # Extract results
                results = page.evaluate("""
                    () => {
                        const rows = document.querySelectorAll('table tr, .tender-item, .result-item');
                        return Array.from(rows).slice(0, 20).map(row => row.textContent.trim());
                    }
                """)
                
                pump_results = [r for r in results if re.search(r'(?i)(pump|পাম্প|সেচ)', r)]
                print(f"    Found {len(pump_results)} pump tenders from search")
                tenders.extend([{
                    "source": "eprocure_search",
                    "text": r[:300],
                    "relevance": "pump_search"
                } for r in pump_results])
        else:
            print("    No search form found, scraping page content")
            content = page.content()
            pump_mentions = re.findall(r'(?i)[^\n]{0,100}(pump|পাম্প|সেচ)[^\n]{0,100}', content)
            if pump_mentions:
                tenders.extend([{
                    "source": "eprocure_content",
                    "text": m.strip()[:200],
                } for m in pump_mentions[:10]])
                
    except Exception as e:
        print(f"  [eGP] Error: {e}")
    
    return tenders

def scrape_with_fallbacks():
    """Main scraping with multiple fallback approaches."""
    all_tenders = {
        "started": datetime.now().isoformat(),
        "cppt_tenders": [],
        "newspaper_tenders": [],
        "egp_tenders": [],
        "summary": {}
    }
    
    try:
        from patchright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                ignore_https_errors=True,
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            print("[BWDB] Phase 1: CPPT/Government tender portals...")
            all_tenders["cppt_tenders"] = search_cppt_tenders(page)
            
            print("\n[BWDB] Phase 2: e-Procurement search...")
            all_tenders["egp_tenders"] = search_ogd_tenders(page)
            
            print("\n[BWDB] Phase 3: Newspaper procurement sections...")
            all_tenders["newspaper_tenders"] = search_newspaper_procurement(page)
            
            context.close()
            browser.close()
    except Exception as e:
        print(f"[FATAL] Patchright failed: {e}")
        all_tenders["error"] = str(e)
    
    # Summary
    total_cppt = len(all_tenders["cppt_tenders"])
    total_news = len(all_tenders["newspaper_tenders"])
    total_egp = len(all_tenders["egp_tenders"])
    
    all_tenders["summary"] = {
        "cppt_sources_checked": total_cppt,
        "newspaper_tenders": total_news,
        "egp_tenders": total_egp,
        "total_found": total_news + total_egp,
        "completed": datetime.now().isoformat()
    }
    
    return all_tenders

def main():
    print("=" * 60)
    print("BWDB/CPPT Pump Tender Scraper")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 60)
    
    results = scrape_with_fallbacks()
    
    # Save results
    output_path = OUTPUT_DIR / "bwdb_tenders.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n[SAVE] Results → {output_path}")
    
    # Summary
    s = results.get("summary", {})
    print(f"\n{'=' * 60}")
    print(f"SUMMARY")
    print(f"{'=' * 60}")
    print(f"  CPPT sources checked: {s.get('cppt_sources_checked', 0)}")
    print(f"  e-GP pump tenders: {s.get('egp_tenders', 0)}")
    print(f"  Newspaper pump tenders: {s.get('newspaper_tenders', 0)}")
    print(f"  Total pump tenders found: {s.get('total_found', 0)}")
    
    return results

if __name__ == "__main__":
    main()
