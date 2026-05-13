#!/usr/bin/env python3
"""NBR PDF Parser — Extract HS 8413 pump import data from NBR PDFs.
Uses pypdfium2 for text extraction (no poppler needed).
"""
import json, re, sys, os
from pathlib import Path
import pypdfium2 as pdfium

NBR_DIR = Path("/Users/lbagent/.openclaw/workspace/leopump/data/raw/nbr")
OUTPUT = NBR_DIR / "hs8413_extracted.json"

# HS 8413 sub-codes to extract
HS_CODES = [
    "8413.11", "8413.19", "8413.20", "8413.30", 
    "8413.40", "8413.50", "8413.60", "8413.70",
    "8413.70.10", "8413.70.20", "8413.70.90",
    "8413.81", "8413.82", "8413.91", "8413.92"
]

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using pypdfium2."""
    text = ""
    try:
        pdf = pdfium.PdfDocument(str(pdf_path))
        for page_idx in range(min(len(pdf), 50)):  # Limit pages
            page = pdf[page_idx]
            textpage = page.get_textpage()
            text += textpage.get_text_range() + "\n"
        pdf.close()
    except Exception as e:
        print(f"  [ERROR] {pdf_path.name}: {e}")
    return text

def parse_hs8413(text, filename):
    """Extract HS 8413 line items from NBR import statement text."""
    results = []
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        # Look for HS code patterns
        if '8413' in line:
            # Try to capture the full context (line + surrounding lines)
            context_start = max(0, i - 1)
            context_end = min(len(lines), i + 3)
            context = '\n'.join(lines[context_start:context_end])
            
            # Extract numbers that look like monetary values
            # NBR format typically: HS code, description, quantity, CIF value (BDT)
            numbers = re.findall(r'[\d,]+(?:\.\d{2})?', line)
            
            # Extract CIF value (usually last large number)
            cif_values = []
            for n in numbers:
                try:
                    val = float(n.replace(',', ''))
                    if val > 100:  # Filter tiny numbers
                        cif_values.append(val)
                except:
                    pass
            
            results.append({
                "source_file": filename,
                "line_number": i + 1,
                "line_text": line.strip()[:300],
                "context": context[:500],
                "extracted_values": cif_values,
                "matched_hs": [code for code in HS_CODES if code.replace('.', '') in line.replace('.', '')]
            })
    
    return results

def main():
    all_results = {"extraction_date": "2026-05-07", "files_processed": [], "hs8413_records": []}
    
    pdf_files = sorted(NBR_DIR.glob("*.pdf"))
    print(f"[NBR PARSE] Found {len(pdf_files)} PDFs")
    
    for pdf_path in pdf_files:
        print(f"\n[PARSING] {pdf_path.name} ({pdf_path.stat().st_size / 1024:.0f} KB)")
        
        text = extract_text_from_pdf(pdf_path)
        print(f"  Extracted {len(text)} chars from {pdf_path.name}")
        
        # Check if text extraction worked
        if len(text.strip()) < 100:
            print(f"  [WARN] Very little text extracted — PDF may be scanned/image-based")
            all_results["files_processed"].append({
                "file": pdf_path.name,
                "text_length": len(text),
                "status": "possibly_scanned"
            })
            # Save raw text anyway for inspection
            txt_path = pdf_path.with_suffix('.txt')
            txt_path.write_text(text)
            continue
        
        records = parse_hs8413(text, pdf_path.name)
        print(f"  Found {len(records)} HS 8413 references")
        all_results["hs8413_records"].extend(records)
        
        all_results["files_processed"].append({
            "file": pdf_path.name,
            "text_length": len(text),
            "hs8413_count": len(records),
            "status": "ok"
        })
        
        # Save extracted text for reference
        txt_path = pdf_path.with_suffix('.txt')
        txt_path.write_text(text)
    
    # Save results
    with open(OUTPUT, 'w') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\n[NBR PARSE] Results saved to {OUTPUT}")
    print(f"[NBR PARSE] Total HS 8413 records: {len(all_results['hs8413_records'])}")
    
    # Print summary
    for fp in all_results["files_processed"]:
        print(f"  {fp['file']}: {fp.get('hs8413_count', '?')} records ({fp['status']})")

if __name__ == "__main__":
    main()
