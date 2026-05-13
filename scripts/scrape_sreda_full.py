#!/usr/bin/env python3
"""SREDA Full Pagination Extractor — All solar irrigation pump projects.
"""
import json, re, time
from pathlib import Path
from patchright.sync_api import sync_playwright

OUTPUT = Path("/Users/lbagent/.openclaw/workspace/leopump/data/raw/idcol/sreda_full.json")
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://ndre.sreda.gov.bd/index.php?id=01&i=4"

def main():
    all_projects = []
    page_num = 1
    has_more = True
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        
        print(f"[SREDA] Loading solar irrigation page...")
        page.goto(BASE_URL, wait_until="networkidle", timeout=25000)
        time.sleep(3)
        
        # First pass: extract initial table data
        initial_data = page.evaluate("""
            () => {
                const tables = document.querySelectorAll('table');
                const result = {tableCount: tables.length, tableData: []};
                
                tables.forEach((table, idx) => {
                    const rows = [];
                    table.querySelectorAll('tr').forEach(tr => {
                        const cells = Array.from(tr.querySelectorAll('th, td'))
                            .map(cell => cell.textContent.trim());
                        if (cells.some(c => c)) rows.push(cells);
                    });
                    if (rows.length > 1) {
                        result.tableData.push(rows);
                    }
                });
                
                // Check for pagination
                const pagination = document.querySelector('[class*="pagination"], [class*="pager"], .dataTables_paginate');
                result.hasPagination = !!pagination;
                result.paginationHTML = pagination ? pagination.innerHTML.substring(0, 500) : '';
                
                // Look for "showing X of Y" text
                const infoEl = document.querySelector('[class*="info"], .dataTables_info');
                result.infoText = infoEl ? infoEl.textContent.trim() : '';
                
                return result;
            }
        """)
        
        print(f"  Tables: {initial_data['tableCount']}")
        print(f"  Pagination: {initial_data['hasPagination']}")
        print(f"  Info: {initial_data.get('infoText', 'N/A')}")
        print(f"  Pagination HTML: {initial_data.get('paginationHTML', 'N/A')[:200]}")
        
        # Extract what we have from the main table
        main_table = initial_data.get('tableData', [])
        if main_table:
            # Find the project data table (should have SL, Project Name, SID, etc.)
            for table in main_table:
                for row in table[:3]:
                    print(f"  Header: {row}")
                if len(table) > 3:
                    print(f"  ... ({len(table)} rows total)")
                    all_projects.extend(table[1:])  # Skip header
        
        # Try DataTables pagination (most common for this type of site)
        # Try clicking "Next" or increasing page length to show all
        try:
            # First try to set display to show all entries
            length_select = page.query_selector('select[name*="length"], select[name*="Display"], select')
            if length_select:
                # Try to select "All" or maximum
                options = page.evaluate("""
                    () => {
                        const select = document.querySelector('select[name*="length"], select');
                        if (!select) return [];
                        return Array.from(select.options).map(o => ({value: o.value, text: o.textContent}));
                    }
                """)
                print(f"\n  Display options: {options}")
                
                # Try selecting max or -1 (all)
                for opt in options:
                    if opt['value'] in ['-1', '100', '500', 'All']:
                        page.evaluate(f"() => {{ document.querySelector('select').value = '{opt['value']}'; document.querySelector('select').dispatchEvent(new Event('change')); }}")
                        time.sleep(3)
                        print(f"  Selected display: {opt['text']}")
                        break
        
        except Exception as e:
            print(f"  Pagination adjust error: {e}")
        
        # Re-extract after display change
        time.sleep(2)
        final_data = page.evaluate("""
            () => {
                const tables = document.querySelectorAll('table');
                const result = [];
                
                tables.forEach(table => {
                    const rows = [];
                    table.querySelectorAll('tr').forEach(tr => {
                        const cells = Array.from(tr.querySelectorAll('th, td'))
                            .map(cell => cell.textContent.trim());
                        if (cells.some(c => c)) rows.push(cells);
                    });
                    if (rows.length > 3) result.push(rows);
                });
                
                const infoEl = document.querySelector('[class*="info"], .dataTables_info');
                const info = infoEl ? infoEl.textContent.trim() : '';
                
                return {tables: result, info: info};
            }
        """)
        
        print(f"\n  After pagination adjust: {final_data.get('info', 'N/A')}")
        
        for table in final_data.get('tables', []):
            if len(table) > 3:
                all_projects = table[1:]  # Skip header
                print(f"  Final table: {len(table)} rows ({len(table)-1} projects)")
        
        # If still only getting ~30 rows, try AJAX pagination
        if len(all_projects) < 50:
            print(f"\n[SREDA] Trying AJAX pagination for full dataset...")
            
            # Intercept network requests to find the data API
            api_responses = []
            
            def handle_response(response):
                if 'sreda' in response.url and ('json' in response.url or 'data' in response.url or 'api' in response.url):
                    try:
                        api_responses.append({"url": response.url, "status": response.status})
                    except:
                        pass
            
            page.on("response", handle_response)
            
            # Try clicking through pages
            for p_num in range(2, 20):
                try:
                    next_btn = page.query_selector('[class*="next"]:not(.disabled), a.next, .paginate_button.next:not(.disabled)')
                    if not next_btn:
                        print(f"  No more pages at page {p_num}")
                        break
                    
                    next_btn.click()
                    time.sleep(2)
                    
                    # Extract new rows
                    new_rows = page.evaluate("""
                        () => {
                            const table = document.querySelector('table');
                            if (!table) return [];
                            const rows = [];
                            table.querySelectorAll('tr').forEach(tr => {
                                const cells = Array.from(tr.querySelectorAll('td'))
                                    .map(cell => cell.textContent.trim());
                                if (cells.length > 3 && cells[0]) rows.push(cells);
                            });
                            return rows;
                        }
                    """)
                    
                    if new_rows:
                        all_projects.extend(new_rows)
                        print(f"  Page {p_num}: +{len(new_rows)} projects (total: {len(all_projects)})")
                    else:
                        break
                    
                except Exception as e:
                    print(f"  Page {p_num} error: {e}")
                    break
        
        browser.close()
    
    # Deduplicate by project name or SID
    seen = set()
    unique_projects = []
    for row in all_projects:
        # Use first few cells as key
        key = str(row[:3])
        if key not in seen:
            seen.add(key)
            unique_projects.append(row)
    
    result = {
        "total_projects": len(unique_projects),
        "projects": unique_projects,
        "api_responses": api_responses if 'api_responses' in dir() else []
    }
    
    with open(OUTPUT, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n[SREDA] Total unique projects: {len(unique_projects)}")
    print(f"Saved to {OUTPUT}")

if __name__ == "__main__":
    main()
