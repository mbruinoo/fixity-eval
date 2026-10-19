#!/usr/bin/env python3
"""
Verify the integrity of the standardized Met inventory file against checksums.
"""
import csv
import hashlib
import json
import sys

def compute_checksum(data):
    if isinstance(data, str):
        data = data.encode('utf-8')
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()

def verify_output(output_file, checksums_file):
    """Verify standardized output against recorded checksums."""
    
    # Load checksums
    with open(checksums_file, 'r') as f:
        checksums_data = json.load(f)
    
    # Verify file-level checksum
    with open(output_file, 'rb') as f:
        current_checksum = compute_checksum(f.read())
    
    recorded_checksum = checksums_data['summary']['output_file_checksum']
    file_match = current_checksum == recorded_checksum
    
    print("=" * 70)
    print("FILE-LEVEL VERIFICATION")
    print("=" * 70)
    print(f"File: {output_file}")
    print(f"Status: {'✓ VERIFIED' if file_match else '✗ MODIFIED'}")
    print(f"Expected: {recorded_checksum}")
    print(f"Got:      {current_checksum}")
    print(f"Rows processed: {checksums_data['summary']['rows_processed']}")
    
    # Verify row-level checksums
    print("\n" + "=" * 70)
    print("ROW-LEVEL VERIFICATION (sample)")
    print("=" * 70)
    
    with open(output_file, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        fieldnames = reader.fieldnames
        
        mismatches = 0
        for row_idx, row in enumerate(reader, start=1):
            output_line = '\t'.join(str(row[field]) for field in fieldnames)
            current_row_checksum = compute_checksum(output_line)
            recorded_row_checksum = checksums_data['rows'][row_idx-1]['output_checksum']
            
            if current_row_checksum != recorded_row_checksum:
                mismatches += 1
                print(f"Row {row_idx} ('{checksums_data['rows'][row_idx-1]['title']}'): MISMATCH")
    
    print(f"\nTotal rows verified: {checksums_data['summary']['rows_processed']}")
    print(f"Mismatches: {mismatches}")
    print(f"Status: {'✓ ALL ROWS VERIFIED' if mismatches == 0 else f'✗ {mismatches} ROWS MODIFIED'}")
    
    return file_match and mismatches == 0

if __name__ == '__main__':
    output_file = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
    checksums_file = '/mnt/user-data/outputs/met_checksums.json'
    
    result = verify_output(output_file, checksums_file)
    sys.exit(0 if result else 1)
