#!/usr/bin/env python3
"""NBR Import Data Scraper — Phase 1 Data Collection
Downloads HS 8413 import statement PDFs from NBR (Bond + Commercial).
"""
import json, os, re, sys, time
from pathlib import Path

# Patchright for anti-detection browsing
from patchright.sync_api import sync_playwright

OUTPUT_DIR = Path("/Users/lbagent/.openclaw/workspace/leopump/data/raw/nbr")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NBR_URL = "https://nbr.gov.bd/publications/all-publication/eng"

def scrape_nbr():
    results = {"pdfs_downloaded": [], "page_links": [], "errors": []}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        
        try:
            print(f"[NBR] Navigating to {NBR_URL}")
            page.goto(NBR_URL, wait_until="networkidle", timeout=30000)
            time.sleep(2)
            
            # Get page content
            content = page.content()
            results["page_title"] = page.title()
            print(f"[NBR] Page title: {page.title()}")
            
            # Find all links containing "Import Statement" 
            import_links = page.evaluate("""
                () => {
                    const links = Array.from(document.querySelectorAll('a'));
                    return links
                        .filter(a => a.textContent.includes('Import Statement'))
                        .map(a => ({
                            text: a.textContent.trim(),
                            href: a.href
                        }))
                        .slice(0, 30);
                }
            """)
            
            print(f"[NBR] Found {len(import_links)} import statement links")
            
            # Filter for IM-7-Bond and IM-4-Commercial with recent months
            target_links = []
            for link in import_links:
                text = link.get('text', '')
                href = link.get('href', '')
                # We want Bond (IM-7) and Commercial (IM-4) statements
                if any(kw in text for kw in ['IM-7', 'IM-4', 'Bond', 'Commercial']):
                    target_links.append(link)
                    print(f"  [MATCH] {text[:80]} → {href[:80]}")
            
            results["page_links"] = target_links
            
            # Try to download the most recent PDFs (up to 6 of each type)
            downloaded = 0
            for link in target_links[:12]:
                href = link.get('href', '')
                text = link.get('text', '')
                if not href or not href.startswith('http'):
                    continue
                if not href.lower().endswith('.pdf'):
                    # Try to follow the link and see if it redirects to a PDF
                    continue
                    
                try:
                    fname = href.split('/')[-1]
                    fpath = OUTPUT_DIR / fname
                    print(f"  [DOWNLOAD] {fname}")
                    
                    # Download via page request
                    resp = page.request.get(href)
                    if resp.ok:
                        with open(fpath, 'wb') as f:
                            f.write(resp.body())
                        results["pdfs_downloaded"].append({
                            "filename": fname,
                            "source_text": text,
                            "url": href,
                            "size_bytes": fpath.stat().st_size
                        })
                        downloaded += 1
                        print(f"  [OK] {fname} ({fpath.stat().st_size} bytes)")
                    else:
                        results["errors"].append(f"HTTP {resp.status} for {href}")
                except Exception as e:
                    results["errors"].append(f"Download error: {e}")
                    
            print(f"\n[NBR] Downloaded {downloaded} PDFs, {len(results['errors'])} errors")
            
        except Exception as e:
            results["errors"].append(f"Navigation error: {e}")
            print(f"[NBR ERROR] {e}")
        finally:
            browser.close()
    
    # Save results
    out_path = OUTPUT_DIR / "nbr_scrape_results.json"
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"[NBR] Results saved to {out_path}")
    return results

if __name__ == "__main__":
    scrape_nbr()
