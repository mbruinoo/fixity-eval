#!/usr/bin/env python3
"""
Verify Met Museum inventory TSV file integrity using stored checksums.
"""

import csv
import hashlib
import json
from pathlib import Path


def compute_checksum(data, algorithm='sha256'):
    """Compute checksum for string data."""
    if isinstance(data, str):
        data = data.encode('utf-8')
    h = hashlib.sha256() if algorithm == 'sha256' else hashlib.md5()
    h.update(data)
    return h.hexdigest()


def verify_file():
    """Verify the standardized file against stored checksums."""
    
    output_file = Path('/mnt/user-data/outputs/met_inventory_standardized.tsv')
    checksum_log = Path('/mnt/user-data/outputs/met_inventory_checksums.json')
    
    # Load stored checksums
    with open(checksum_log, 'r', encoding='utf-8') as f:
        stored = json.load(f)
    
    # Read and verify output file
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    current_checksum = compute_checksum(content)
    
    print("=" * 70)
    print("MET MUSEUM INVENTORY TSV - FIXITY VERIFICATION")
    print("=" * 70)
    print()
    
    # File-level verification
    print("FILE-LEVEL VERIFICATION")
    print("-" * 70)
    print(f"File: {output_file.name}")
    print(f"Stored checksum:  {stored['output_file_checksum']}")
    print(f"Current checksum: {current_checksum}")
    
    if stored['output_file_checksum'] == current_checksum:
        print("✓ FILE INTEGRITY VERIFIED - Checksums match")
        file_ok = True
    else:
        print("✗ FILE CORRUPTION DETECTED - Checksums do not match!")
        file_ok = False
    
    print()
    
    # Row-level verification
    print("ROW-LEVEL VERIFICATION (Sample)")
    print("-" * 70)
    
    with open(output_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        headers = next(reader)
        rows = list(reader)
    
    rows_verified = 0
    rows_corrupted = 0
    sample_rows = [0, len(rows)//2, len(rows)-1]  # First, middle, last
    
    for row_idx in sample_rows:
        if row_idx >= len(rows):
            continue
            
        row = rows[row_idx]
        stored_hash = stored['row_checksums']['standardized'].get(str(row_idx), {}).get('full_row')
        
        if stored_hash:
            current_hash = compute_checksum('|'.join(str(v) for v in row))
            match = stored_hash == current_hash
            
            status = "✓" if match else "✗"
            print(f"{status} Row {row_idx}: {stored_hash[:16]}... ", end="")
            if match:
                print("[OK]")
                rows_verified += 1
            else:
                print(f"[MISMATCH] Got: {current_hash[:16]}...")
                rows_corrupted += 1
    
    print()
    print(f"Sample rows verified: {rows_verified}/{len(sample_rows)}")
    
    # Cell-level verification (example)
    print()
    print("CELL-LEVEL VERIFICATION (First Row, Column 0)")
    print("-" * 70)
    
    row_idx = 0
    col_idx = 0
    row = rows[row_idx]
    cell_value = row[col_idx] if col_idx < len(row) else ''
    
    stored_cell_hash = stored['row_checksums']['standardized'].get(str(row_idx), {}).get('cells', {}).get(str(col_idx))
    current_cell_hash = compute_checksum(cell_value)
    
    print(f"Row: {row_idx}, Column: {col_idx} (Object Date)")
    print(f"Cell value: '{cell_value}'")
    print(f"Stored hash:  {stored_cell_hash}")
    print(f"Current hash: {current_cell_hash}")
    
    if stored_cell_hash == current_cell_hash:
        print("✓ CELL INTEGRITY VERIFIED")
    else:
        print("✗ CELL CORRUPTION DETECTED")
    
    # Summary
    print()
    print("=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    
    if file_ok and rows_verified == len(sample_rows):
        print("✓ All checks passed - File integrity confirmed")
        return True
    else:
        print("✗ Some checks failed - File may be corrupted")
        return False


if __name__ == '__main__':
    verify_file()
