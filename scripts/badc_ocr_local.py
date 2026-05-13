#!/usr/bin/env python3
"""BADC Irrigation Report OCR Pipeline v2 - Use Local PDFs.
Uses existing local PDFs and PaddleOCR to extract pump installed base trends.
"""
import json, os, re, sys
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path("/Users/lbagent/.openclaw/workspace/leopump/data/raw/badc")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

import pypdfium2 as pdfium
from paddleocr import PaddleOCR

print('Initializing PaddleOCR 3.5...')
ocr = PaddleOCR(lang='en', use_textline_orientation=True)
print('PaddleOCR ready')

# Use local PDFs we already have
LOCAL_REPORTS = {
    'survey_2023_24': {
        'pdf': OUTPUT_DIR / 'survey_2023_24.pdf',
        'description': 'BADC Irrigation Survey Report 2023-24'
    },
    'survey_2022_23': {
        'pdf': OUTPUT_DIR / 'survey_2022_23.pdf',
        'description': 'BADC Irrigation Survey Report 2022-23'
    },
    'survey_2021_22': {
        'pdf': OUTPUT_DIR / 'survey_2021_22.pdf',
        'description': 'BADC Irrigation Survey Report 2021-22'
    },
    'survey_2020_21': {
        'pdf': OUTPUT_DIR / 'survey_2020_21.pdf',
        'description': 'BADC Irrigation Survey Report 2020-21'
    },
    'survey_2019_20': {
        'pdf': OUTPUT_DIR / 'survey_2019_20.pdf',
        'description': 'BADC Irrigation Survey Report 2019-20'
    },
    'survey_2018_19': {
        'pdf': OUTPUT_DIR / 'survey_2018_19.pdf',
        'description': 'BADC Irrigation Survey Report 2018-19'
    },
    'survey_2017_18': {
        'pdf': OUTPUT_DIR / 'survey_2017_18.pdf',
        'description': 'BADC Irrigation Survey Report 2017-18'
    },
}

def pdf_to_images(pdf_path, output_dir, dpi=200):
    """Convert PDF pages to images."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    images = []
    pdf = pdfium.PdfDocument(str(pdf_path))
    print(f"  PDF→Image: {len(pdf)} pages at {dpi} DPI")
    
    for i, page in enumerate(pdf):
        bitmap = page.render(scale=dpi / 72)
        img_path = output_dir / f"page_{i+1:04d}.png"
        bitmap.to_pil().save(str(img_path))
        images.append(str(img_path))
        if (i + 1) % 20 == 0:
            print(f"    Rendered {i+1}/{len(pdf)} pages")
    
    pdf.close()
    return images

def ocr_extract(images, output_json):
    """Run PaddleOCR on images and extract text."""
    all_results = []
    for i, img_path in enumerate(images):
        try:
            result = ocr.ocr(img_path)
            page_lines = []
            if result:
                for res in result:
                    if isinstance(res, list):
                        for line in res:
                            if isinstance(line, (list, tuple)) and len(line) >= 2:
                                bbox_data = line[0] if len(line) > 0 else None
                                text_data = line[1] if len(line) > 1 else None
                                if text_data and isinstance(text_data, (list, tuple)) and len(text_data) >= 2:
                                    page_lines.append({
                                        'text': str(text_data[0]),
                                        'confidence': round(float(text_data[1]), 3),
                                        'bbox': [[round(x) for x in pt] for pt in bbox_data] if bbox_data else None
                                    })
                                elif text_data:
                                    page_lines.append({'text': str(text_data), 'confidence': 1.0, 'bbox': None})
            
            all_results.append({
                'page': i + 1,
                'image': os.path.basename(img_path),
                'lines': page_lines
            })
            if (i + 1) % 10 == 0:
                print(f"    OCR {i+1}/{len(images)} ({datetime.now().strftime('%H:%M:%S')})")
        except Exception as e:
            all_results.append({'page': i + 1, 'error': str(e)})
            print(f"    [OCR error] Page {i+1}: {e}")
    
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    return all_results

def extract_pump_data(ocr_results, report_name):
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
                    "relevant_lines": [l['text'] for l in relevant_lines[:30]],
                    "number_lines": number_lines[:20],
                    "total_lines_on_page": len(page_lines)
                })
        
        # Detect table structures (rows of aligned text)
        if len(page_lines) > 10:
            # Check for table-like alignment
            x_positions = [l['bbox'][0][0] for l in page_lines if l['bbox']]
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
    print("BADC Irrigation Report OCR Pipeline v2 (Local PDFs)")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 60)
    
    results = {
        "started": datetime.now().isoformat(),
        "reports": {}
    }
    
    # Process reports in order (most recent first)
    for report_name, report_info in LOCAL_REPORTS.items():
        print(f"\n[1/3] Processing {report_info['description']}")
        
        pdf_path = report_info['pdf']
        if not pdf_path.exists():
            print(f"  [FAIL] PDF not found: {pdf_path}")
            results["reports"][report_name] = {"status": "pdf_missing"}
            continue
        
        # Check if already processed
        ocr_json = OUTPUT_DIR / f"{report_name}_ocr.json"
        pump_json = OUTPUT_DIR / f"{report_name}_pump_data.json"
        
        if ocr_json.exists() and pump_json.exists():
            print(f"  [SKIP] Already processed")
            results["reports"][report_name] = {"status": "exists"}
            continue
        
        # Step 1: Convert PDF to images
        img_dir = OUTPUT_DIR / f"{report_name}_images"
        existing_imgs = sorted(img_dir.glob("*.png"))
        
        if existing_imgs:
            images = [str(p) for p in existing_imgs]
            print(f"  [OK] Using {len(images)} pre-rendered images")
        else:
            print(f"  [OK] Rendering PDF pages...")
            images = pdf_to_images(pdf_path, img_dir, dpi=200)
        
        # Step 2: Run OCR
        print(f"  [OK] Running OCR on {len(images)} pages...")
        ocr_results = ocr_extract(images, str(ocr_json))
        
        # Step 3: Extract pump data
        print(f"  [OK] Extracting pump data...")
        pump_data = extract_pump_data(ocr_results, report_name)
        
        # Save pump extraction
        with open(pump_json, 'w', encoding='utf-8') as f:
            json.dump(pump_data, f, indent=2, ensure_ascii=False)
        
        # Generate plain text
        txt_path = OUTPUT_DIR / f"{report_name}.txt"
        generate_plain_text(ocr_results, str(txt_path))
        
        # Summary
        relevant_pages = len(pump_data['pump_mentions'])
        tables = len(pump_data['tables_found'])
        print(f"  [DONE] {len(ocr_results)} pages | {relevant_pages} pump-relevant | {tables} tables")
        
        results["reports"][report_name] = {
            "status": "completed",
            "pages": len(ocr_results),
            "pump_pages": relevant_pages,
            "tables": tables
        }
    
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
        if isinstance(rdata, dict):
            status = rdata.get("status", "unknown")
            pages = rdata.get("pages", 0)
            pump_pages = rdata.get("pump_pages", 0)
            tables = rdata.get("tables", 0)
            print(f"  {rid}: {status} | {pages} pages | {pump_pages} pump-relevant | {tables} tables")
    
    print(f"\nResults saved to {results_path}")
    return results

if __name__ == "__main__":
    main()