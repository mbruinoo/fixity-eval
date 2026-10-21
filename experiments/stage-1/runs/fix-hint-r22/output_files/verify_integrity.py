#!/usr/bin/env python3
"""
Integrity verification script for standardized TSV file.
Demonstrates how to verify checksums for individual cells and rows.
"""

import json
import hashlib
import csv
from pathlib import Path


def load_checksums(checksum_file: str) -> dict:
    """Load checksums from JSON file."""
    with open(checksum_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def read_standardized_file(tsv_file: str) -> list:
    """Read the standardized TSV file."""
    rows = []
    with open(tsv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        rows = list(reader)
    return rows


def verify_cell(row_num: int, col_num: int, cell_value: str, checksums: dict) -> bool:
    """Verify a single cell's integrity."""
    calculated = hashlib.sha256(cell_value.encode('utf-8')).hexdigest()
    
    # Get column name
    header = ['Object Date', 'Title', 'Object Number', 'Link Resource']
    col_name = header[col_num]
    
    # Try both string and int keys
    row_key = str(row_num) if str(row_num) in checksums['cell_checksums'] else row_num
    expected = checksums['cell_checksums'][row_key][col_name]['checksum']
    return calculated == expected


def verify_row(row_num: int, row: list, checksums: dict) -> bool:
    """Verify an entire row's integrity."""
    row_str = '\t'.join(row)
    calculated = hashlib.sha256(row_str.encode('utf-8')).hexdigest()
    
    # Try both string and int keys
    row_key = str(row_num) if str(row_num) in checksums['source_rows'] else row_num
    expected = checksums['source_rows'][row_key]['checksum']
    return calculated == expected


def main():
    checksums_file = '/mnt/user-data/outputs/checksums.json'
    tsv_file = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
    
    print("=" * 70)
    print("INTEGRITY VERIFICATION REPORT")
    print("=" * 70)
    
    # Load data
    print("\nLoading checksums and file...")
    checksums = load_checksums(checksums_file)
    rows = read_standardized_file(tsv_file)
    
    # Overall statistics
    total_rows = len(rows)
    total_cells = total_rows * 4  # 4 columns
    
    print(f"\nFile Statistics:")
    print(f"  Total rows (including header): {total_rows}")
    print(f"  Data rows: {total_rows - 1}")
    print(f"  Total cells: {total_cells}")
    print(f"  Columns: 4 (Object Date, Title, Object Number, Link Resource)")
    
    # Verify all rows
    print("\n" + "=" * 70)
    print("VERIFYING ALL ROWS")
    print("=" * 70)
    
    all_valid = True
    failed_rows = []
    
    for row_num in range(1, total_rows + 1):
        row = rows[row_num - 1]
        is_valid = verify_row(row_num, row, checksums)
        
        if not is_valid:
            all_valid = False
            failed_rows.append(row_num)
            print(f"\n✗ Row {row_num} FAILED verification")
            print(f"  Content preview: {row[0][:40] if row[0] else '(empty)'}...")
        elif row_num == 1 or row_num % 20 == 0 or row_num == total_rows:
            print(f"✓ Row {row_num}: OK")
    
    # Verify sample cells
    print("\n" + "=" * 70)
    print("VERIFYING SAMPLE CELLS")
    print("=" * 70)
    
    header = ['Object Date', 'Title', 'Object Number', 'Link Resource']
    
    # Sample from different parts of file
    sample_rows = [2, 10, 50, 100, total_rows]
    all_cells_valid = True
    
    for row_num in sample_rows:
        if row_num > total_rows:
            continue
        
        row = rows[row_num - 1]
        print(f"\nRow {row_num}:")
        
        for col_num, (col_name, cell_value) in enumerate(zip(header, row)):
            is_valid = verify_cell(row_num, col_num, cell_value, checksums)
            
            # Display value preview
            preview = cell_value[:50] + "..." if len(cell_value) > 50 else cell_value
            preview = preview if preview else "(empty)"
            
            status = "✓" if is_valid else "✗"
            print(f"  {status} {col_name}: {preview}")
            
            if not is_valid:
                all_cells_valid = False
                print(f"     ERROR: Checksum mismatch!")
    
    # Summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    
    if all_valid and all_cells_valid:
        print("\n✓ ALL INTEGRITY CHECKS PASSED")
        print("  - All row checksums verified")
        print("  - All sample cell checksums verified")
        print("  - File integrity confirmed")
        return 0
    else:
        print("\n✗ INTEGRITY CHECKS FAILED")
        if failed_rows:
            print(f"  - {len(failed_rows)} rows failed verification")
            print(f"    Failed rows: {failed_rows}")
        if not all_cells_valid:
            print("  - Some cell checksums did not match")
        return 1


if __name__ == '__main__':
    exit(main())
