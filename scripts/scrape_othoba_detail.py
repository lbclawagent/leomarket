#!/usr/bin/env python3
"""Othoba price fix — extract prices from product detail pages."""
import json, re, time
from pathlib import Path
from patchright.sync_api import sync_playwright

OUT = Path("/Users/lbagent/.openclaw/workspace/leopump/data/raw/pricing/othoba_detailed.json")

# Load existing data to get product URLs
existing = json.load(open(Path("/Users/lbagent/.openclaw/workspace/leopump/data/raw/pricing/daraz_othoba_deep.json")))
othoba = existing.get("othoba_search", {})

# Also re-scrape the search page with better price extraction
SEARCH_URL = "https://othoba.com/ts/search/water%20pump?t=t&q=water%20pump"

def main():
    results = {"products": [], "errors": []}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            ignore_https_errors=True,
            viewport={"width": 1366, "height": 768},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        print("[OTHOBA] Re-scraping search page with price extraction...")
        page.goto(SEARCH_URL, wait_until="networkidle", timeout=30000)
        time.sleep(4)
        
        # Scroll
        page.evaluate("""
            async () => {
                for (let i = 0; i < 8; i++) {
                    window.scrollBy(0, 600);
                    await new Promise(r => setTimeout(r, 1000));
                }
                window.scrollTo(0, 0);
            }
        """)
        time.sleep(2)
        
        # Strategy: get ALL text content that looks like prices
        # Othoba uses Bengali taka or numeric prices
        body = page.inner_text("body")
        
        # Extract product cards with all their text
        products = page.evaluate("""
            () => {
                const results = [];
                // Try multiple selectors
                const selectors = [
                    '[class*="product"]', '[class*="Product"]',
                    '[class*="item"]', '[class*="Item"]',
                    '[class*="card"]', '[class*="Card"]',
                    '.product-card', '.product-item'
                ];
                
                for (const sel of selectors) {
                    const cards = document.querySelectorAll(sel);
                    if (cards.length > 5) {
                        cards.forEach(card => {
                            const allText = card.textContent;
                            const links = Array.from(card.querySelectorAll('a')).map(a => a.href);
                            const href = links.find(l => l.includes('/product/')) || links[0] || '';
                            
                            // Get all text, split and clean
                            const parts = allText.split(/\\n/).map(s => s.trim()).filter(s => s.length > 1);
                            
                            if (parts.length > 2) {
                                results.push({
                                    raw_parts: parts.slice(0, 10),
                                    href: href,
                                    all_text: allText.substring(0, 300)
                                });
                            }
                        });
                        break;  // Use first selector that returns results
                    }
                }
                return results;
            }
        """)
        
        # Try alternative: direct HTML scraping for price elements
        price_elements = page.evaluate("""
            () => {
                const prices = [];
                // Look for elements with price-related classes or content
                const allElements = document.querySelectorAll('[class*="price"], [class*="Price"], [class*="amount"], [class*="Amount"], [class*="mrp"], [class*="MRP"], [class*="offer"], [class*="selling"]');
                allElements.forEach(el => {
                    const text = el.textContent.trim();
                    if (text && text.length < 50) {
                        prices.push({
                            class: el.className,
                            text: text
                        });
                    }
                });
                return prices;
            }
        """)
        
        # Also try to find product links and visit first few for detail prices
        product_links = page.evaluate("""
            () => {
                return Array.from(document.querySelectorAll('a[href*="/product/"]'))
                    .map(a => ({ name: a.textContent.trim().substring(0, 80), href: a.href }))
                    .filter(p => p.name.length > 5)
                    .slice(0, 20);
            }
        """)
        
        print(f"  Products via selector: {len(products)}")
        print(f"  Price elements found: {len(price_elements)}")
        print(f"  Product links: {len(product_links)}")
        
        if price_elements:
            print(f"\n  Sample price elements:")
            for pe in price_elements[:10]:
                print(f"    class='{pe['class'][:40]}' text='{pe['text']}'")
        
        # Visit product detail pages for exact prices
        detailed = []
        for link in product_links[:10]:
            try:
                print(f"  [DETAIL] {link['name'][:40]}...")
                page.goto(link['href'], wait_until="networkidle", timeout=15000)
                time.sleep(2)
                
                detail = page.evaluate("""
                    () => {
                        const body = document.body.innerText;
                        const priceEls = document.querySelectorAll('[class*="price"], [class*="Price"], [class*="selling"], [class*="amount"]');
                        const prices = Array.from(priceEls).map(el => el.textContent.trim()).filter(t => t.length < 50);
                        
                        // Find product title
                        const title = document.querySelector('h1, [class*="title"], [class*="Title"]');
                        
                        return {
                            title: title ? title.textContent.trim() : '',
                            prices: prices,
                            body_snippet: body.substring(0, 2000)
                        };
                    }
                """)
                
                # Extract numeric prices from detail page
                all_nums = re.findall(r'[\d,]+(?:\.\d{2})?', detail.get('body_snippet', ''))
                bdt_prices = []
                for n in all_nums:
                    try:
                        val = float(n.replace(',', ''))
                        if 500 <= val <= 200000:
                            bdt_prices.append(int(val))
                    except:
                        pass
                
                detailed.append({
                    "name": link['name'],
                    "href": link['href'],
                    "title": detail.get('title', ''),
                    "price_elements": detail.get('prices', []),
                    "numeric_prices": sorted(set(bdt_prices))[:5]
                })
                
                print(f"    Title: {detail.get('title', 'N/A')[:60]}")
                print(f"    Price elements: {detail.get('prices', [])[:5]}")
                print(f"    Numeric: {sorted(set(bdt_prices))[:5]}")
                
                time.sleep(1)
            except Exception as e:
                print(f"    ERROR: {e}")
        
        results["products"] = products
        results["price_elements"] = price_elements
        results["product_links"] = product_links
        results["detail_pages"] = detailed
        
        browser.close()
    
    with open(OUT, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n[OTHOBA] Saved {len(detailed)} detail pages to {OUT}")

if __name__ == "__main__":
    main()
