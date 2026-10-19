#!/usr/bin/env python3
"""
Integrity Verification Script
Independently verifies checksums against source and output files
"""

import csv
import hashlib
import json
import sys
from pathlib import Path

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

def verify_file(filepath, expected_checksums):
    """Verify a TSV file against expected checksums"""
    if not Path(filepath).exists():
        print(f"ERROR: File not found: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    file_hash = calculate_checksum(content)
    expected_file_hash = expected_checksums.get('file_full')
    
    print(f"\nVerifying: {filepath}")
    print("-" * 80)
    print(f"Calculated SHA256: {file_hash}")
    print(f"Expected SHA256:   {expected_file_hash}")
    
    if file_hash == expected_file_hash:
        print("✓ FILE INTEGRITY: VERIFIED")
    else:
        print("✗ FILE INTEGRITY: FAILED")
        return False
    
    # Verify row-by-row
    lines = content.split('\n')
    reader = csv.DictReader(
        lines,
        fieldnames=['Object Date', 'Title', 'Object Number', 'Link Resource'],
        delimiter='\t'
    )
    
    rows = []
    for row in reader:
        if row['Object Date'] is None:
            break
        rows.append(row)
    
    print(f"\nRow-by-row verification ({len(rows)} rows):")
    failed_rows = []
    
    for idx, row in enumerate(rows, 1):
        row_hash = calculate_row_checksum(row)
        expected_row_hash = expected_checksums['rows'].get(str(idx), {}).get('full_row')
        
        if row_hash != expected_row_hash:
            failed_rows.append(idx)
            print(f"  Row {idx}: ✗ MISMATCH")
        elif idx <= 5 or idx > len(rows) - 2:  # Show first 5 and last 2
            print(f"  Row {idx}: ✓ OK")
        elif idx == 6:
            print(f"  ... ({len(rows) - 7} more rows) ...")
    
    if failed_rows:
        print(f"\n✗ FAILED ROWS: {failed_rows}")
        return False
    else:
        print(f"\n✓ ALL {len(rows)} ROWS VERIFIED")
        return True

def main():
    print("=" * 80)
    print("INTEGRITY VERIFICATION UTILITY")
    print("=" * 80)
    
    # Load verification report
    report_path = '/mnt/user-data/outputs/fixity_verification_report.json'
    
    if not Path(report_path).exists():
        print(f"ERROR: Verification report not found: {report_path}")
        print("Please run standardize_met_inventory.py first")
        sys.exit(1)
    
    with open(report_path, 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    print(f"\nVerification Report: {report_path}")
    print(f"Report Timestamp: {report['metadata']['timestamp']}")
    print(f"Rows Processed: {report['metadata']['rows_processed']}")
    
    # Verify output file
    output_path = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
    output_checksums = report['output']
    
    output_ok = verify_file(output_path, output_checksums)
    
    # Summary
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    
    if output_ok:
        print("✓ All integrity checks PASSED")
        print("✓ Output file is valid and matches expected checksums")
        print("✓ All rows verified")
        sys.exit(0)
    else:
        print("✗ Some integrity checks FAILED")
        print("✗ Please check the output above for details")
        sys.exit(1)

if __name__ == '__main__':
    main()
