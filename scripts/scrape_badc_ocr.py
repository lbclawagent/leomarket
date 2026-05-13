#!/usr/bin/env python3
"""BADC Irrigation Report OCR Pipeline.
Downloads BADC irrigation survey reports and extracts pump installed base data using PaddleOCR.
"""
import json, re, time, os, sys
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path("/Users/lbagent/.openclaw/workspace/leopump/data/raw/badc")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

REPORTS_OUTPUT = Path("/Users/lbagent/.openclaw/workspace/leopump/data/outputs")

# BADC irrigation report local files (already downloaded)
# These are scanned image PDFs that need OCR
BADC_REPORTS = {
    "irrigation_survey_2023_24": {
        "local_file": "survey_2023_24.pdf",
        "description": "BADC Irrigation Survey Report 2023-24"
    },
    "irrigation_survey_2022_23": {
        "local_file": "survey_2022_23.pdf",
        "description": "BADC Irrigation Survey Report 2022-23"
    },
    "irrigation_survey_2021_22": {
        "local_file": "survey_2021_22.pdf",
        "description": "BADC Irrigation Survey Report 2021-22"
    },
    "irrigation_survey_2020_21": {
        "local_file": "survey_2020_21.pdf",
        "description": "BADC Irrigation Survey Report 2020-21"
    },
    "irrigation_survey_2019_20": {
        "local_file": "survey_2019_20.pdf",
        "description": "BADC Irrigation Survey Report 2019-20"
    },
    "irrigation_survey_2018_19": {
        "local_file": "survey_2018_19.pdf",
        "description": "BADC Irrigation Survey Report 2018-19"
    },
    "irrigation_survey_2017_18": {
        "local_file": "survey_2017_18.pdf",
        "description": "BADC Irrigation Survey Report 2017-18"
    },
}

def download_with_camoufox(url, output_path, timeout=60):
    """Download PDF using Camoufox (anti-detect Firefox)."""
    try:
        from camoufox.sync_api import Camoufox
        with Camoufox(headless=True) as browser:
            context = browser.new_context(ignore_https_errors=True)
            page = context.new_page()
            print(f"  [Camoufox] Downloading {url[:80]}...")
            
            # Navigate to URL and wait for response
            response = page.goto(url, wait_until="load", timeout=timeout * 1000)
            
            if response and response.ok:
                body = response.body()
                if len(body) > 10000:
                    with open(output_path, 'wb') as f:
                        f.write(body)
                    print(f"  [OK] Downloaded {len(body)/1024:.0f} KB")
                    return True
                else:
                    print(f"  [WARN] Response too small: {len(body)} bytes")
            else:
                print(f"  [FAIL] HTTP {response.status if response else 'no response'}")
            context.close()
    except Exception as e:
        print(f"  [Camoufox error] {e}")
    return False

def download_with_patchright(url, output_path, timeout=60):
    """Fallback: Download PDF using Patchright."""
    try:
        from patchright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(ignore_https_errors=True)
            page = context.new_page()
            
            print(f"  [Patchright] Downloading {url[:80]}...")
            response = page.goto(url, wait_until="load", timeout=timeout * 1000)
            
            if response and response.ok:
                body = response.body()
                if len(body) > 10000:
                    with open(output_path, 'wb') as f:
                        f.write(body)
                    print(f"  [OK] Downloaded {len(body)/1024:.0f} KB")
                    return True
            context.close()
            browser.close()
    except Exception as e:
        print(f"  [Patchright error] {e}")
    return False

def download_with_urllib(url, output_path):
    """Last resort: direct download."""
    try:
        import urllib.request
        import ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        print(f"  [urllib] Downloading {url[:80]}...")
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        with urllib.request.urlopen(req, context=ctx, timeout=120) as resp:
            data = resp.read()
            if len(data) > 10000:
                with open(output_path, 'wb') as f:
                    f.write(data)
                print(f"  [OK] Downloaded {len(data)/1024:.0f} KB")
                return True
            else:
                print(f"  [WARN] Response too small: {len(data)} bytes")
    except Exception as e:
        print(f"  [urllib error] {e}")
    return False

def pdf_to_images(pdf_path, output_dir, dpi=200):
    """Convert PDF pages to images using pypdfium2."""
    import pypdfium2 as pdfium
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    images = []
    pdf = pdfium.PdfDocument(str(pdf_path))
    print(f"  [PDF→Image] {len(pdf)} pages at {dpi} DPI")
    
    for i, page in enumerate(pdf):
        bitmap = page.render(scale=dpi / 72)
        img_path = output_dir / f"page_{i+1:04d}.png"
        bitmap.to_pil().save(str(img_path))
        images.append(str(img_path))
        if (i + 1) % 10 == 0:
            print(f"    Rendered {i+1}/{len(pdf)} pages")
    
    pdf.close()
    return images

def ocr_extract(images, output_json):
    """Run PaddleOCR on images and extract text."""
    from paddleocr import PaddleOCR
    
    ocr = PaddleOCR(
        use_textline_orientation=True,
        lang='en',  # English primary, BADC reports use English tables
    )
    
    all_results = []
    for i, img_path in enumerate(images):
        try:
            result = ocr.ocr(img_path)
            page_text = []
            if result and result[0]:
                for line in result[0]:
                    text = line[1][0]
                    conf = line[1][1]
                    bbox = line[0]
                    page_text.append({
                        "text": text,
                        "confidence": round(conf, 3),
                        "bbox": [[round(x, 1) for x in point] for point in bbox]
                    })
            
            all_results.append({
                "page": i + 1,
                "image": os.path.basename(img_path),
                "lines": page_text
            })
            
            if (i + 1) % 5 == 0:
                print(f"    OCR'd {i+1}/{len(images)} pages")
        except Exception as e:
            print(f"    [OCR error] Page {i+1}: {e}")
            all_results.append({
                "page": i + 1,
                "image": os.path.basename(img_path),
                "error": str(e)
            })
    
    # Save raw OCR output
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    return all_results

def extract_pump_data(ocr_results):
    """Extract pump/irrigation installed base data from OCR text."""
    pump_data = {
        "pump_mentions": [],
        "tube_well_counts": [],
        "irrigation_area": [],
        "tables_found": []
    }
    
    # Keywords to look for
    pump_keywords = [
        'pump', 'tube well', 'deep tube well', 'shallow tube well',
        'dtw', 'stw', 'llp', 'low lift pump', 'hand tube well',
        'submersible', 'centrifugal', 'motor', 'engine',
        'irrigated', 'irrigation', 'hectare', 'acre', 'command area',
        'electric', 'diesel', 'solar', 'bmda', 'badc', 'bwb',
        'installed', 'operable', 'inoperable', 'beneficiary', 'farmer'
    ]
    
    for page_result in ocr_results:
        if 'error' in page_result:
            continue
            
        page_num = page_result['page']
        page_lines = page_result.get('lines', [])
        
        # Combine all text on page for keyword search
        full_page_text = ' '.join([l['text'] for l in page_lines]).lower()
        
        # Check if page has relevant content
        keyword_hits = [kw for kw in pump_keywords if kw in full_page_text]
        
        if len(keyword_hits) >= 2:  # At least 2 keywords = relevant page
            # Look for numbers near keywords
            relevant_lines = []
            for line in page_lines:
                text_lower = line['text'].lower()
                if any(kw in text_lower for kw in pump_keywords):
                    relevant_lines.append({
                        "text": line['text'],
                        "confidence": line['confidence']
                    })
            
            # Also extract lines with numbers (potential table data)
            number_lines = []
            for line in page_lines:
                if re.search(r'\d{2,}', line['text']):  # 2+ digit numbers
                    number_lines.append(line['text'])
            
            if relevant_lines or (number_lines and len(keyword_hits) >= 3):
                pump_data['pump_mentions'].append({
                    "page": page_num,
                    "keyword_hits": keyword_hits,
                    "relevant_lines": relevant_lines[:30],  # Cap output
                    "number_lines": number_lines[:20],
                    "total_lines_on_page": len(page_lines)
                })
        
        # Detect table structures (rows of aligned text)
        if len(page_lines) > 10:
            # Check for table-like alignment
            x_positions = [l['bbox'][0][0] for l in page_lines]
            # Group by x-position (columns)
            from collections import Counter
            x_rounded = [round(x / 10) * 10 for x in x_positions]
            col_counts = Counter(x_rounded)
            main_cols = [x for x, c in col_counts.items() if c > 3]
            
            if len(main_cols) >= 3:  # At least 3 columns = likely a table
                pump_data['tables_found'].append({
                    "page": page_num,
                    "num_columns": len(main_cols),
                    "num_rows": len(page_lines),
                    "column_x_positions": sorted(main_cols)
                })
    
    return pump_data

def generate_plain_text(ocr_results, output_path):
    """Generate readable plain text from OCR results."""
    lines = []
    for page_result in ocr_results:
        if 'error' in page_result:
            lines.append(f"\n--- PAGE {page_result['page']} (ERROR: {page_result['error']}) ---\n")
            continue
        
        lines.append(f"\n--- PAGE {page_result['page']} ---\n")
        for line in page_result.get('lines', []):
            lines.append(line['text'])
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

def main():
    print("=" * 60)
    print("BADC Irrigation Report OCR Pipeline")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 60)
    
    results = {
        "started": datetime.now().isoformat(),
        "reports": {}
    }
    
    # Step 1: Check local files
    print("\n[1/4] Checking local BADC reports...")
    for report_id, report_info in BADC_REPORTS.items():
        print(f"\n  Report: {report_info['description']}")
        pdf_path = OUTPUT_DIR / report_info['local_file']
        
        if pdf_path.exists() and pdf_path.stat().st_size > 10000:
            print(f"  [OK] Local file exists ({pdf_path.stat().st_size/1024:.0f} KB)")
            results["reports"][report_id] = {"status": "exists", "pdf": str(pdf_path)}
        else:
            results["reports"][report_id] = {"status": "missing", "expected_file": report_info['local_file']}
            print(f"  [FAIL] Local file missing: {report_info['local_file']}")
    
    # Step 2: Convert PDFs to images
    print("\n[2/4] Converting PDFs to images...")
    for report_id in results["reports"]:
        report = results["reports"][report_id]
        if report.get("status") in ("exists", "downloaded"):
            pdf_path = Path(report["pdf"])
            img_dir = OUTPUT_DIR / f"{report_id}_images"
            
            if img_dir.exists() and len(list(img_dir.glob("*.png"))) > 0:
                existing_images = sorted(str(p) for p in img_dir.glob("*.png"))
                print(f"  [SKIP] {report_id}: {len(existing_images)} images already exist")
                report["images"] = existing_images
                continue
            
            try:
                images = pdf_to_images(pdf_path, img_dir, dpi=200)
                report["images"] = images
                print(f"  [OK] {report_id}: {len(images)} pages rendered")
            except Exception as e:
                print(f"  [FAIL] {report_id}: {e}")
                report["status"] = "pdf_convert_failed"
    
    # Step 3: Run OCR
    print("\n[3/4] Running PaddleOCR...")
    for report_id in results["reports"]:
        report = results["reports"][report_id]
        images = report.get("images", [])
        
        if not images:
            continue
        
        ocr_json = OUTPUT_DIR / f"{report_id}_ocr.json"
        
        if ocr_json.exists():
            print(f"  [SKIP] {report_id}: OCR already done")
            with open(ocr_json, 'r') as f:
                ocr_results = json.load(f)
        else:
            try:
                ocr_results = ocr_extract(images, str(ocr_json))
                print(f"  [OK] {report_id}: {len(ocr_results)} pages OCR'd")
            except Exception as e:
                print(f"  [FAIL] {report_id}: {e}")
                report["status"] = "ocr_failed"
                continue
        
        # Step 4: Extract pump data
        print(f"\n[4/4] Extracting pump data from {report_id}...")
        pump_data = extract_pump_data(ocr_results)
        
        # Save pump extraction
        pump_json = OUTPUT_DIR / f"{report_id}_pump_data.json"
        with open(pump_json, 'w', encoding='utf-8') as f:
            json.dump(pump_data, f, indent=2, ensure_ascii=False)
        
        # Generate plain text
        txt_path = OUTPUT_DIR / f"{report_id}.txt"
        generate_plain_text(ocr_results, str(txt_path))
        
        # Summary
        relevant_pages = len(pump_data['pump_mentions'])
        tables = len(pump_data['tables_found'])
        print(f"  Pump-relevant pages: {relevant_pages}")
        print(f"  Tables detected: {tables}")
        
        report["ocr_pages"] = len(ocr_results)
        report["pump_pages"] = relevant_pages
        report["tables"] = tables
        
    # Save overall results
    results["completed"] = datetime.now().isoformat()
    results_path = OUTPUT_DIR / "badc_ocr_results.json"
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for rid, rdata in results["reports"].items():
        status = rdata.get("status", "unknown")
        pages = rdata.get("ocr_pages", 0)
        pump_pages = rdata.get("pump_pages", 0)
        tables = rdata.get("tables", 0)
        print(f"  {rid}: {status} | {pages} pages | {pump_pages} pump-relevant | {tables} tables")
    
    print(f"\nResults saved to {results_path}")
    return results

if __name__ == "__main__":
    main()
