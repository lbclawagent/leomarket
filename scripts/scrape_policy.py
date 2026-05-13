#!/usr/bin/env python3
"""Policy & Urban Data Collector — BSTI standards + RAJUK housing data.
"""
import json, re, time, sys
from pathlib import Path
import pypdfium2 as pdfium
from patchright.sync_api import sync_playwright

OUTPUT_DIR = Path("/Users/lbagent/.openclaw/workspace/leopump/data/raw/policy")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def download_pdf(url, fname):
    """Download a PDF via requests."""
    import urllib.request
    fpath = OUTPUT_DIR / fname
    try:
        urllib.request.urlretrieve(url, fpath)
        print(f"  [DOWNLOAD] {fname} ({fpath.stat().st_size / 1024:.0f} KB)")
        return fpath
    except Exception as e:
        print(f"  [ERROR] {fname}: {e}")
        return None

def extract_pdf_text(pdf_path, max_pages=20):
    """Extract text from PDF."""
    text = ""
    try:
        pdf = pdfium.PdfDocument(str(pdf_path))
        for i in range(min(len(pdf), max_pages)):
            page = pdf[i]
            textpage = page.get_textpage()
            text += textpage.get_text_range() + "\n"
        pdf.close()
    except Exception as e:
        print(f"  [PDF ERROR] {e}")
    return text

def scrape_rajuk_portal():
    """Scrape RAJUK developer registration data."""
    result = {"developers": [], "errors": [], "page_text": ""}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        
        try:
            print("[RAJUK] Navigating to portal...")
            page.goto("https://rajuk.gov.bd/pages/static-pages/6922dbda933eb65569e0d00c",
                      wait_until="networkidle", timeout=25000)
            time.sleep(3)
            
            body_text = page.inner_text("body")
            result["page_text"] = body_text[:5000]
            
            # Extract any tables
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
            result["tables"] = tables
            result["table_count"] = len(tables)
            
            # Look for developer-related numbers
            dev_numbers = re.findall(r'[\d,]+', body_text)
            result["numbers_found"] = dev_numbers[:50]
            
            print(f"[RAJUK] Tables: {len(tables)}, Text: {len(body_text)} chars")
            
        except Exception as e:
            result["errors"].append(str(e))
            print(f"[RAJUK ERROR] {e}")
        finally:
            browser.close()
    
    return result

def parse_dhaka_structure_plan(pdf_path):
    """Extract housing need estimation from Dhaka Structure Plan.
    Target: Section 6.2.1, page 120, table 6.1
    """
    result = {"housing_data": [], "errors": [], "target_section": ""}
    
    print(f"[DHAKA PLAN] Parsing {pdf_path.name}")
    
    # Extract pages around page 120 (0-indexed: ~119-125)
    try:
        pdf = pdfium.PdfDocument(str(pdf_path))
        total_pages = len(pdf)
        print(f"  Total pages: {total_pages}")
        
        # Extract pages 115-130 to capture the table and context
        target_pages = range(max(0, 115), min(total_pages, 135))
        all_text = ""
        
        for i in target_pages:
            page = pdf[i]
            textpage = page.get_textpage()
            page_text = textpage.get_text_range()
            all_text += f"\n--- PAGE {i+1} ---\n{page_text}"
            
            # Check if this page has housing need content
            if any(kw in page_text.lower() for kw in ['housing need', '6.2.1', 'table 6.1', 'dwelling', 'household']):
                result["target_section"] += page_text + "\n"
        
        pdf.close()
        
        # Extract numbers from housing section
        housing_numbers = re.findall(r'[\d,]+(?:\.\d+)?', result.get("target_section", ""))
        result["housing_numbers"] = housing_numbers[:100]
        
        # Save full extracted text
        txt_path = pdf_path.with_suffix('.housing.txt')
        txt_path.write_text(all_text)
        
        print(f"  Housing section: {len(result['target_section'])} chars")
        print(f"  Numbers found: {len(housing_numbers)}")
        
    except Exception as e:
        result["errors"].append(str(e))
        print(f"  [ERROR] {e}")
    
    return result

def main():
    all_results = {}
    
    # 1. BSTI Standards Catalogue
    print("\n=== BSTI STANDARDS ===")
    bsti_path = download_pdf(
        "https://rise.esmap.org/sites/default/files/library/bangladesh/Clean%20Cooking/Bangladesh_Bangladesh%20Standard%20and%20Testing%20Institution%20Standards%20Catalogue_2018.pdf",
        "bsti_standards_catalogue_2018.pdf"
    )
    if bsti_path:
        text = extract_pdf_text(bsti_path, max_pages=50)
        # Search for pump-related standards
        pump_standards = []
        for line in text.split('\n'):
            if any(kw in line.lower() for kw in ['pump', '8413', 'water pump', 'centrifugal', 'submersible', 'motor']):
                pump_standards.append(line.strip())
        
        all_results["bsti"] = {
            "text_length": len(text),
            "pump_standards": pump_standards[:50],
            "pump_standard_count": len(pump_standards)
        }
        print(f"  [BSTI] {len(pump_standards)} pump-related standard entries found")
        
        # Save pump standards
        (OUTPUT_DIR / "bsti_pump_standards.txt").write_text('\n'.join(pump_standards))
    
    # 2. RAJUK Portal
    print("\n=== RAJUK ===")
    all_results["rajuk"] = scrape_rajuk_portal()
    
    # 3. Dhaka Structure Plan
    print("\n=== DHAKA STRUCTURE PLAN ===")
    plan_path = download_pdf(
        "https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-rajuk/2024/12/aa7155f471ce403f80aef4771f4c87aa.pdf",
        "dhaka_structure_plan.pdf"
    )
    if plan_path:
        all_results["dhaka_plan"] = parse_dhaka_structure_plan(plan_path)
    
    # Save all
    out_path = OUTPUT_DIR / "policy_urban_data.json"
    with open(out_path, 'w') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\n[POLICY] Saved to {out_path}")

if __name__ == "__main__":
    main()
