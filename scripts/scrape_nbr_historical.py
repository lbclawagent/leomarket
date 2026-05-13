#!/usr/bin/env python3
"""NBR Historical PDF Downloader — Extend to 36 months.
Downloads Import Statement IM-4 (Commercial) and IM-7 (Bond) PDFs.
"""
import json, re, time, os
from pathlib import Path
from patchright.sync_api import sync_playwright

OUTPUT_DIR = Path("/Users/lbagent/.openclaw/workspace/leopump/data/raw/nbr")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NBR_URL = "https://nbr.gov.bd/publications/all-publication/eng"

def main():
    results = {"downloaded": [], "skipped": [], "errors": []}
    
    # Check existing files
    existing = {f.name for f in OUTPUT_DIR.glob("*.pdf")}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        
        print("[NBR] Loading publications page...")
        page.goto(NBR_URL, wait_until="networkidle", timeout=30000)
        time.sleep(3)
        
        # Get ALL import statement links by scrolling through the page
        # The page may have pagination or lazy loading
        all_links = []
        
        # Scroll to load all content
        for _ in range(10):
            page.evaluate("window.scrollBy(0, 1000)")
            time.sleep(0.5)
        
        # Extract all links containing "Import Statement"
        links = page.evaluate("""
            () => {
                const results = [];
                const links = Array.from(document.querySelectorAll('a'));
                links.forEach(a => {
                    const text = a.textContent.trim();
                    const href = a.href;
                    if (text.includes('Import Statement') && (text.includes('IM-7') || text.includes('IM-4'))) {
                        results.push({text, href});
                    }
                });
                return results;
            }
        """)
        
        print(f"[NBR] Found {len(links)} import statement links total")
        
        # Check if there's pagination we need to handle
        # Look for "next" or pagination buttons
        pagination_info = page.evaluate("""
            () => {
                const pagination = document.querySelector('[class*="pagination"], [class*="pager"], .page-nav');
                const links = document.querySelectorAll('a[href*="page="], a[href*="publication"]');
                return {
                    hasPagination: !!pagination,
                    paginationHTML: pagination ? pagination.innerHTML.substring(0, 500) : '',
                    totalLinks: links.length
                };
            }
        """)
        
        if pagination_info.get("hasPagination"):
            print(f"[NBR] Pagination detected: {pagination_info['paginationHTML'][:100]}")
            # Try clicking through pages
            page_num = 2
            while page_num <= 10:
                try:
                    next_btn = page.query_selector(f'a[href*="page={page_num}"], [class*="next"], [class*="Next"]')
                    if not next_btn:
                        break
                    next_btn.click()
                    time.sleep(2)
                    more_links = page.evaluate("""
                        () => {
                            const results = [];
                            const links = Array.from(document.querySelectorAll('a'));
                            links.forEach(a => {
                                const text = a.textContent.trim();
                                const href = a.href;
                                if (text.includes('Import Statement') && (text.includes('IM-7') || text.includes('IM-4'))) {
                                    results.push({text, href});
                                }
                            });
                            return results;
                        }
                    """)
                    new_count = 0
                    for link in more_links:
                        if link not in links:
                            links.append(link)
                            new_count += 1
                    print(f"  Page {page_num}: +{new_count} new links")
                    if new_count == 0:
                        break
                    page_num += 1
                except Exception as e:
                    print(f"  Pagination stopped at page {page_num}: {e}")
                    break
        
        # Filter for PDF links only
        pdf_links = [l for l in links if l.get('href', '').endswith('.pdf') or '.pdf' in l.get('href', '')]
        print(f"[NBR] {len(pdf_links)} PDF links found")
        
        # Download all that we don't already have
        downloaded = 0
        for link in pdf_links:
            href = link.get('href', '')
            text = link.get('text', '')
            
            fname = href.split('/')[-1]
            if not fname.endswith('.pdf'):
                fname += '.pdf'
            
            if fname in existing:
                results["skipped"].append(fname)
                continue
            
            try:
                resp = page.request.get(href)
                if resp.ok and len(resp.body()) > 10000:  # Skip tiny/error responses
                    fpath = OUTPUT_DIR / fname
                    with open(fpath, 'wb') as f:
                        f.write(resp.body())
                    size_kb = fpath.stat().st_size / 1024
                    results["downloaded"].append({
                        "filename": fname,
                        "source_text": text[:100],
                        "size_kb": round(size_kb, 0)
                    })
                    downloaded += 1
                    print(f"  [OK] {fname} ({size_kb:.0f} KB) — {text[:60]}")
                else:
                    results["errors"].append(f"HTTP {resp.status} or too small: {fname}")
            except Exception as e:
                results["errors"].append(f"{fname}: {e}")
            
            time.sleep(0.5)  # Be polite
        
        browser.close()
    
    # Save manifest
    manifest_path = OUTPUT_DIR / "nbr_download_manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n[NBR] Downloaded: {downloaded} | Skipped (existing): {len(results['skipped'])} | Errors: {len(results['errors'])}")
    print(f"[NBR] Total PDFs in archive: {len(list(OUTPUT_DIR.glob('*.pdf')))}")

if __name__ == "__main__":
    main()
