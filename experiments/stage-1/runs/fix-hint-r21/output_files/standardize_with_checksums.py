#!/usr/bin/env python3
"""
Met Museum Inventory TSV Standardization with Fixity Preservation
Generates checksums before and after standardization to verify data integrity
"""

import csv
import hashlib
import json
from pathlib import Path
from datetime import datetime

def calculate_checksum(data, algorithm='sha256'):
    """Calculate checksum of data (string or bytes)"""
    if isinstance(data, str):
        data = data.encode('utf-8')
    h = hashlib.new(algorithm)
    h.update(data)
    return h.hexdigest()

def calculate_row_checksum(row_dict, algorithm='sha256'):
    """Calculate checksum of a single row"""
    canonical = json.dumps(row_dict, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
    return calculate_checksum(canonical, algorithm)

def calculate_cell_checksum(cell_value, algorithm='sha256'):
    """Calculate checksum of a single cell"""
    if cell_value is None:
        cell_value = ""
    return calculate_checksum(str(cell_value), algorithm)

def standardize_date(date_str):
    """Standardize date field"""
    if not date_str or not date_str.strip():
        return ""
    return date_str.strip()

def standardize_title(title_str):
    """Standardize title field"""
    if not title_str or not title_str.strip():
        return "[Untitled]"
    return title_str.strip()

def standardize_object_number(obj_num):
    """Standardize object number"""
    if not obj_num or not obj_num.strip():
        return ""
    return obj_num.strip()

def standardize_url(url):
    """Standardize URL field"""
    if not url or not url.strip():
        return ""
    url = url.strip()
    if url and not url.startswith('http'):
        return ""
    return url

def read_and_checksum_source(source_file):
    """Read TSV content and generate source checksums"""
    with open(source_file, 'r', encoding='utf-8') as f:
        file_content = f.read()
    
    source_checksums = {
        'file_full': calculate_checksum(file_content),
        'rows': {}
    }
    
    lines = file_content.split('\n')
    reader = csv.DictReader(
        lines,
        fieldnames=['Object Date', 'Title', 'Object Number', 'Link Resource'],
        delimiter='\t'
    )
    
    rows = []
    for idx, row in enumerate(reader, 1):
        if not row.get('Object Date'):
            break
        rows.append(row)
        
        row_checksum = calculate_row_checksum(row)
        source_checksums['rows'][idx] = {
            'full_row': row_checksum,
            'cells': {
                'date': calculate_cell_checksum(row.get('Object Date', '')),
                'title': calculate_cell_checksum(row.get('Title', '')),
                'object_number': calculate_cell_checksum(row.get('Object Number', '')),
                'url': calculate_cell_checksum(row.get('Link Resource', ''))
            }
        }
    
    return rows, source_checksums, file_content

def standardize_rows(rows):
    """Apply standardization rules to all rows"""
    standardized = []
    
    for row in rows:
        standardized_row = {
            'Object Date': standardize_date(row.get('Object Date', '')),
            'Title': standardize_title(row.get('Title', '')),
            'Object Number': standardize_object_number(row.get('Object Number', '')),
            'Link Resource': standardize_url(row.get('Link Resource', ''))
        }
        standardized.append(standardized_row)
    
    return standardized

def generate_output_checksums(standardized_rows, output_content):
    """Generate checksums for standardized output"""
    output_checksums = {
        'file_full': calculate_checksum(output_content),
        'rows': {}
    }
    
    for idx, row in enumerate(standardized_rows, 1):
        row_checksum = calculate_row_checksum(row)
        output_checksums['rows'][idx] = {
            'full_row': row_checksum,
            'cells': {
                'date': calculate_cell_checksum(row.get('Object Date', '')),
                'title': calculate_cell_checksum(row.get('Title', '')),
                'object_number': calculate_cell_checksum(row.get('Object Number', '')),
                'url': calculate_cell_checksum(row.get('Link Resource', ''))
            }
        }
    
    return output_checksums

def write_tsv(rows, filepath):
    """Write standardized TSV file"""
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(
            f,
            fieldnames=['Object Date', 'Title', 'Object Number', 'Link Resource'],
            delimiter='\t',
            lineterminator='\n'
        )
        writer.writeheader()
        writer.writerows(rows)

def main():
    source_file = '/mnt/user-data/outputs/met_inventory_source.tsv'
    output_file = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
    report_file = '/mnt/user-data/outputs/fixity_verification_report.json'
    summary_file = '/mnt/user-data/outputs/standardization_summary.txt'
    
    print("=" * 80)
    print("MET MUSEUM INVENTORY TSV STANDARDIZATION WITH FIXITY PRESERVATION")
    print("=" * 80)
    print(f"Process started: {datetime.now().isoformat()}\n")
    
    # Step 1: Read source and generate source checksums
    print("STEP 1: READING SOURCE FILE AND GENERATING SOURCE CHECKSUMS")
    print("-" * 80)
    rows, source_checksums, source_content = read_and_checksum_source(source_file)
    print(f"Total rows read: {len(rows)}")
    print(f"Source file full SHA256: {source_checksums['file_full']}")
    print(f"Generated checksums for {len(source_checksums['rows'])} rows\n")
    
    # Step 2: Standardize
    print("STEP 2: STANDARDIZING DATA")
    print("-" * 80)
    standardized_rows = standardize_rows(rows)
    print(f"Standardization complete: {len(standardized_rows)} rows")
    
    # Count changes by field
    changes = {'date': 0, 'title': 0, 'object_number': 0, 'url': 0}
    for orig, std in zip(rows, standardized_rows):
        if orig.get('Object Date', '') != std.get('Object Date', ''):
            changes['date'] += 1
        if orig.get('Title', '') != std.get('Title', ''):
            changes['title'] += 1
        if orig.get('Object Number', '') != std.get('Object Number', ''):
            changes['object_number'] += 1
        if orig.get('Link Resource', '') != std.get('Link Resource', ''):
            changes['url'] += 1
    
    print(f"  - Date field changes: {changes['date']}")
    print(f"  - Title field changes: {changes['title']}")
    print(f"  - Object Number field changes: {changes['object_number']}")
    print(f"  - URL field changes: {changes['url']}\n")
    
    # Step 3: Write standardized TSV
    print("STEP 3: WRITING STANDARDIZED TSV FILE")
    print("-" * 80)
    write_tsv(standardized_rows, output_file)
    print(f"Wrote to: {output_file}\n")
    
    # Step 4: Read output and generate checksums
    print("STEP 4: GENERATING OUTPUT CHECKSUMS")
    print("-" * 80)
    with open(output_file, 'r', encoding='utf-8') as f:
        output_content = f.read()
    
    output_checksums = generate_output_checksums(standardized_rows, output_content)
    print(f"Output file full SHA256: {output_checksums['file_full']}")
    print(f"Generated checksums for {len(output_checksums['rows'])} rows\n")
    
    # Step 5: Create detailed verification report
    print("STEP 5: CREATING VERIFICATION REPORT")
    print("-" * 80)
    
    verification_report = {
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'source_file': source_file,
            'output_file': output_file,
            'script': 'standardize_with_checksums.py',
            'source_algorithm': 'SHA256',
            'rows_processed': len(rows)
        },
        'source': source_checksums,
        'standardization': {
            'rules_applied': [
                'Trimmed whitespace from all fields',
                'Replaced empty titles with "[Untitled]"',
                'Preserved date format integrity',
                'Validated URL format (must start with http)',
                'Stripped leading/trailing whitespace from object numbers'
            ],
            'changes_by_field': changes
        },
        'output': output_checksums,
        'row_by_row_verification': {}
    }
    
    # Add row-by-row detail
    for idx, (src, std, src_check, out_check) in enumerate(zip(
        rows, standardized_rows,
        source_checksums['rows'].values(),
        output_checksums['rows'].values()
    ), 1):
        verification_report['row_by_row_verification'][idx] = {
            'source_row_hash': src_check['full_row'],
            'output_row_hash': out_check['full_row'],
            'modified': src_check['full_row'] != out_check['full_row'],
            'field_changes': {
                'date': src.get('Object Date', '') != std.get('Object Date', ''),
                'title': src.get('Title', '') != std.get('Title', ''),
                'object_number': src.get('Object Number', '') != std.get('Object Number', ''),
                'url': src.get('Link Resource', '') != std.get('Link Resource', '')
            }
        }
    
    # Write verification report as JSON
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(verification_report, f, indent=2, ensure_ascii=False)
    print(f"Verification report written to: {report_file}\n")
    
    # Step 6: Create human-readable summary
    print("STEP 6: CREATING SUMMARY REPORT")
    print("-" * 80)
    
    summary_lines = [
        "MET MUSEUM INVENTORY STANDARDIZATION - SUMMARY REPORT",
        "=" * 80,
        f"Process Timestamp: {datetime.now().isoformat()}",
        "",
        "FILE INFORMATION",
        "-" * 80,
        f"Source file:  {source_file}",
        f"Output file:  {output_file}",
        f"Source SHA256:  {source_checksums['file_full']}",
        f"Output SHA256:  {output_checksums['file_full']}",
        f"Total rows: {len(rows)}",
        "",
        "STANDARDIZATION CHANGES",
        "-" * 80,
        f"Rows with title changes:         {changes['title']}",
        f"Rows with date changes:          {changes['date']}",
        f"Rows with object number changes: {changes['object_number']}",
        f"Rows with URL changes:           {changes['url']}",
        "",
        "STANDARDIZATION RULES APPLIED",
        "-" * 80,
        "1. Whitespace: Trimmed leading and trailing whitespace from all fields",
        "2. Titles: Empty title cells replaced with '[Untitled]'",
        "3. Dates: Preserved as-is after whitespace trim (maintains historical accuracy)",
        "4. URLs: Validated format (must start with 'http')",
        "5. Object Numbers: Stripped whitespace, preserved original format",
        "",
        "CHECKSUM COVERAGE",
        "-" * 80,
        f"✓ Full source file: SHA256",
        f"✓ Full output file: SHA256",
        f"✓ Each row in source: SHA256 (canonical JSON representation)",
        f"✓ Each cell in source: SHA256 (by field)",
        f"✓ Each row in output: SHA256 (canonical JSON representation)",
        f"✓ Each cell in output: SHA256 (by field)",
        f"✓ Total data points checksummed: {2 * (1 + len(rows) * 5)} hashes",
        "",
        "OUTPUT FILES",
        "-" * 80,
        f"1. met_inventory_standardized.tsv - Standardized tab-separated values file",
        f"2. fixity_verification_report.json - Detailed verification with all checksums",
        f"3. standardization_summary.txt - This human-readable summary",
        "",
        "HOW TO VERIFY INTEGRITY",
        "-" * 80,
        "1. Compare file checksums in the JSON report to recalculate checksums",
        "2. Examine row-by-row-verification to see which rows were modified",
        "3. Use the cell-level checksums to verify individual data elements",
        "4. The canonical JSON representation ensures field order doesn't affect hashes",
    ]
    
    summary_text = "\n".join(summary_lines)
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary_text)
    print(f"Summary written to: {summary_file}\n")
    
    print(summary_text)
    print("\n" + "=" * 80)
    print("STANDARDIZATION COMPLETE")
    print("=" * 80)

if __name__ == '__main__':
    main()
