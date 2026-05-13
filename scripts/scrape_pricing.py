#!/usr/bin/env python3
"""Dealer Pricing Scraper — Phase 1 Data Collection
Scrapes water pump prices from BD e-commerce sites.
"""
import json, os, re, sys, time
from pathlib import Path
from patchright.sync_api import sync_playwright

OUTPUT_DIR = Path("/Users/lbagent/.openclaw/workspace/leopump/data/raw/pricing")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SITES = [
    {
        "name": "daraz_submersible",
        "url": "https://www.daraz.com.bd/submersible-pump/",
        "price_regex": r'৳\s*[\d,]+',
        "wait": "networkidle",
        "sleep": 2
    },
    {
        "name": "daraz_centrifugal",
        "url": "https://www.daraz.com.bd/centrifugal-pump/",
        "price_regex": r'৳\s*[\d,]+',
        "wait": "networkidle",
        "sleep": 2
    },
    {
        "name": "daraz_water_pump_1hp",
        "url": "https://www.daraz.com.bd/water-pump-1hp/",
        "price_regex": r'৳\s*[\d,]+',
        "wait": "networkidle",
        "sleep": 2
    },
    {
        "name": "bdstall",
        "url": "https://www.bdstall.com/water-pump/",
        "price_regex": r'(?:৳|Tk\.?)\s*[\d,]+',
        "wait": "domcontentloaded",
        "sleep": 3
    },
    {
        "name": "othoba",
        "url": "https://www.othoba.com/water-pump",
        "price_regex": r'(?:৳|Tk\.?)\s*[\d,]+',
        "wait": "domcontentloaded",
        "sleep": 3
    },
    {
        "name": "melmart",
        "url": "https://www.melmartbd.com/product-category/water-pump/",
        "price_regex": r'(?:৳|Tk\.?)\s*[\d,]+',
        "wait": "domcontentloaded",
        "sleep": 3
    },
    {
        "name": "pedrollo",
        "url": "https://pedrollo.com.bd/brand/pedrollo/",
        "price_regex": r'(?:৳|Tk\.?)\s*[\d,]+',
        "wait": "domcontentloaded",
        "sleep": 3
    },
]

def scrape_site(page, site):
    """Scrape a single site for product names and prices."""
    result = {"site": site["name"], "url": site["url"], "products": [], "errors": []}
    
    try:
        print(f"[{site['name']}] Navigating to {site['url']}")
        page.goto(site["url"], wait_until=site["wait"], timeout=20000)
        time.sleep(site.get("sleep", 2))
        
        # Extract product data
        products = page.evaluate("""
            (pricePattern) => {
                const products = [];
                // Try common e-commerce selectors
                const cards = document.querySelectorAll(
                    '[class*="product"], [class*="item"], [class*="card"], [data-product]'
                );
                
                cards.forEach(card => {
                    const nameEl = card.querySelector(
                        '[class*="title"], [class*="name"], h2, h3, h4, a[title]'
                    );
                    const priceEl = card.querySelector(
                        '[class*="price"], [class*="Price"]'
                    );
                    
                    if (nameEl || priceEl) {
                        products.push({
                            name: nameEl ? nameEl.textContent.trim().substring(0, 150) : '',
                            price: priceEl ? priceEl.textContent.trim().substring(0, 50) : '',
                            href: (nameEl && nameEl.tagName === 'A') ? nameEl.href : ''
                        });
                    }
                });
                
                return products.slice(0, 50);
            }
        """, site.get("price_regex", ""))
        
        # Also get raw page text for regex-based price extraction
        page_text = page.inner_text("body")
        prices = re.findall(r'[\d,]+', page_text) if page_text else []
        
        # Filter to reasonable pump prices (500 - 500,000 BDT)
        filtered_prices = []
        for p in prices:
            try:
                val = int(p.replace(',', ''))
                if 500 <= val <= 500000:
                    filtered_prices.append(val)
            except:
                pass
        
        result["products"] = products
        result["raw_price_count"] = len(filtered_prices)
        result["price_range"] = f"{min(filtered_prices)}-{max(filtered_prices)}" if filtered_prices else "N/A"
        
        print(f"[{site['name']}] {len(products)} products, {len(filtered_prices)} prices in range, range: {result['price_range']}")
        
    except Exception as e:
        result["errors"].append(str(e))
        print(f"[{site['name']}] ERROR: {e}")
    
    return result

def main():
    all_results = {}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            ignore_https_errors=True,
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        for site in SITES:
            result = scrape_site(page, site)
            all_results[site["name"]] = result
            time.sleep(1)
        
        browser.close()
    
    # Save
    out_path = OUTPUT_DIR / "dealer_pricing.json"
    with open(out_path, 'w') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\n[PRICING] Saved to {out_path}")
    
    # Summary
    total_products = sum(len(r.get("products", [])) for r in all_results.values())
    sites_ok = sum(1 for r in all_results.values() if not r.get("errors"))
    print(f"[PRICING] {sites_ok}/{len(SITES)} sites OK, {total_products} total products extracted")
    
    return all_results

if __name__ == "__main__":
    main()
