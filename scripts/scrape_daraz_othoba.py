#!/usr/bin/env python3
"""Daraz + Othoba Deep Scrape — Fixed selectors + longer waits.
Othoba uses search endpoint; Daraz needs extended wait for JS rendering.
"""
import json, re, time, sys
from pathlib import Path
from patchright.sync_api import sync_playwright

OUTPUT_DIR = Path("/Users/lbagent/.openclaw/workspace/leopump/data/raw/pricing")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TARGETS = [
    {
        "name": "othoba_search",
        "url": "https://othoba.com/ts/search/water%20pump?t=t&q=water%20pump",
        "wait": "networkidle",
        "sleep": 5,
        "scroll": True
    },
    {
        "name": "daraz_water_pump",
        "url": "https://www.daraz.com.bd/water-pump/",
        "wait": "networkidle",
        "sleep": 5,
        "scroll": True
    },
    {
        "name": "daraz_submersible",
        "url": "https://www.daraz.com.bd/submersible-pump/",
        "wait": "networkidle",
        "sleep": 5,
        "scroll": True
    },
    {
        "name": "daraz_centrifugal",
        "url": "https://www.daraz.com.bd/centrifugal-pump/",
        "wait": "networkidle",
        "sleep": 5,
        "scroll": True
    },
    {
        "name": "daraz_1hp",
        "url": "https://www.daraz.com.bd/water-pump-1hp/",
        "wait": "networkidle",
        "sleep": 5,
        "scroll": True
    },
    {
        "name": "daraz_2hp",
        "url": "https://www.daraz.com.bd/catalog/?q=2hp+water+pump",
        "wait": "networkidle",
        "sleep": 5,
        "scroll": True
    },
    {
        "name": "daraz_booster",
        "url": "https://www.daraz.com.bd/catalog/?q=booster+pump",
        "wait": "networkidle",
        "sleep": 5,
        "scroll": True
    },
]

def extract_products(page, site_name):
    """Multiple extraction strategies to handle different site layouts."""
    products = []
    
    # Strategy 1: Daraz-specific selectors
    daraz_data = page.evaluate("""
        () => {
            const products = [];
            // Daraz uses [data-tracking="product_card"] or .gridItem or [class*="Card"]
            const cards = document.querySelectorAll(
                '[class*="gridItem"], [class*="GridItem"], [data-tracking="product_card"], [class*="product-card"]'
            );
            cards.forEach(card => {
                const nameEl = card.querySelector('[class*="title"], [class*="name"], a[class*="link"], R2OzRQ');
                const priceEl = card.querySelector('[class*="price"], [class*="Price"], span[class*="ooOxS"]');
                const img = card.querySelector('img');
                products.push({
                    name: nameEl ? nameEl.textContent.trim().substring(0, 200) : (img ? img.alt || '' : ''),
                    price: priceEl ? priceEl.textContent.trim().substring(0, 100) : '',
                    href: nameEl && nameEl.tagName === 'A' ? nameEl.href : (card.querySelector('a') ? card.querySelector('a').href : '')
                });
            });
            return products;
        }
    """)
    if daraz_data:
        products.extend(daraz_data)
    
    # Strategy 2: Generic product card extraction
    generic_data = page.evaluate("""
        () => {
            const products = [];
            const cards = document.querySelectorAll(
                '[class*="product"], [class*="item"], [class*="card"], [class*="Card"], article'
            );
            cards.forEach(card => {
                if (card.offsetWidth < 50 || card.offsetHeight < 50) return; // skip hidden
                const nameEl = card.querySelector(
                    '[class*="title"], [class*="name"], [class*="Title"], h2, h3, h4, a[title], img[alt]'
                );
                const priceEl = card.querySelector(
                    '[class*="price"], [class*="Price"], [class*="amount"], [class*="Amount"]'
                );
                const name = nameEl ? (nameEl.textContent || nameEl.alt || '').trim().substring(0, 200) : '';
                const price = priceEl ? priceEl.textContent.trim().substring(0, 100) : '';
                if (name || price) {
                    products.push({
                        name: name,
                        price: price,
                        href: (nameEl && nameEl.tagName === 'A') ? nameEl.href : ''
                    });
                }
            });
            return products;
        }
    """)
    if generic_data:
        products.extend(generic_data)
    
    # Deduplicate by name
    seen = set()
    unique = []
    for p in products:
        key = (p.get('name', '')[:50], p.get('price', '')[:20])
        if key not in seen and (p.get('name') or p.get('price')):
            seen.add(key)
            unique.append(p)
    
    return unique

def scrape_site(page, site):
    result = {"site": site["name"], "url": site["url"], "products": [], "errors": [], "raw_text_len": 0}
    try:
        print(f"[{site['name']}] Navigating...")
        page.goto(site["url"], wait_until=site["wait"], timeout=30000)
        time.sleep(site.get("sleep", 3))
        
        # Scroll to load lazy content
        if site.get("scroll"):
            page.evaluate("""
                async () => {
                    for (let i = 0; i < 5; i++) {
                        window.scrollBy(0, 500);
                        await new Promise(r => setTimeout(r, 800));
                    }
                    window.scrollTo(0, 0);
                    await new Promise(r => setTimeout(r, 500));
                }
            """)
            time.sleep(1)
        
        products = extract_products(page, site["name"])
        
        # Also extract raw prices from page text
        body_text = page.inner_text("body")
        result["raw_text_len"] = len(body_text)
        
        # Parse ৳ prices
        price_matches = re.findall(r'৳\s*([\d,]+)', body_text)
        raw_prices = []
        for p in price_matches:
            try:
                val = int(p.replace(',', ''))
                if 500 <= val <= 500000:
                    raw_prices.append(val)
            except:
                pass
        
        result["products"] = products
        result["raw_taka_prices"] = sorted(set(raw_prices))
        result["price_count"] = len(raw_prices)
        if raw_prices:
            result["price_range"] = f"৳{min(raw_prices):,} - ৳{max(raw_prices):,}"
            result["price_mean"] = round(sum(raw_prices) / len(raw_prices))
        
        print(f"[{site['name']}] {len(products)} products, {len(raw_prices)} raw prices, range: {result.get('price_range', 'N/A')}")
        
    except Exception as e:
        result["errors"].append(str(e))
        print(f"[{site['name']}] ERROR: {e}")
    
    return result

def main():
    results = {}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            ignore_https_errors=True,
            viewport={"width": 1366, "height": 768},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        for site in TARGETS:
            result = scrape_site(page, site)
            results[site["name"]] = result
            time.sleep(2)
        
        browser.close()
    
    # Save
    out_path = OUTPUT_DIR / "daraz_othoba_deep.json"
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Summary
    total = sum(len(r["products"]) for r in results.values())
    total_prices = sum(r.get("price_count", 0) for r in results.values())
    sites_ok = sum(1 for r in results.values() if not r.get("errors"))
    print(f"\n[SUMMARY] {sites_ok}/{len(TARGETS)} sites OK | {total} products | {total_prices} raw prices")
    print(f"Saved to {out_path}")

if __name__ == "__main__":
    main()
