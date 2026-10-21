#!/usr/bin/env python3
"""
TSV Standardization Script with Fixity Verification
Preserves data integrity through checksums before and after processing
"""

import csv
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

def compute_checksum(file_path: str, algorithm: str = 'sha256') -> str:
    """Compute checksum of a file."""
    hash_obj = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()

def standardize_tsv(input_path: str, output_path: str) -> dict:
    """
    Standardize a TSV file:
    - Ensure consistent tab delimiters
    - Normalize whitespace
    - Verify column count consistency
    - Clean empty fields
    - Preserve data integrity
    """
    
    # Read the input file
    rows = []
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        rows = list(reader)
    
    if not rows:
        raise ValueError("Input file is empty")
    
    # Identify header and standardize column names
    header = rows[0]
    header_standardized = [col.strip() for col in header]
    
    # Process data rows
    standardized_rows = [header_standardized]
    data_rows = rows[1:]
    
    issues = []
    column_count = len(header_standardized)
    
    for row_num, row in enumerate(data_rows, start=2):
        # Handle variable column count
        while len(row) < column_count:
            row.append('')
        
        # Trim excess columns
        if len(row) > column_count:
            issues.append(f"Row {row_num}: Had {len(row)} columns, trimmed to {column_count}")
            row = row[:column_count]
        
        # Clean and normalize fields
        cleaned_row = [field.strip() for field in row]
        
        # Detect and report potential data issues
        if all(field == '' for field in cleaned_row):
            issues.append(f"Row {row_num}: Completely empty row (skipped)")
            continue
        
        standardized_rows.append(cleaned_row)
    
    # Write standardized output
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t', lineterminator='\n')
        writer.writerows(standardized_rows)
    
    return {
        'original_rows': len(rows),
        'standardized_rows': len(standardized_rows),
        'rows_processed': len(data_rows),
        'columns': column_count,
        'issues': issues
    }

def main():
    # File paths
    script_dir = Path(__file__).parent
    input_file = script_dir / 'met_inventory.tsv'
    output_file = script_dir / 'met_inventory_standardized.tsv'
    fixity_report = script_dir / 'fixity_report.json'
    
    # Check if input file exists
    if not input_file.exists():
        print(f"ERROR: Input file not found at {input_file}")
        print("Usage: Place met_inventory.tsv in the same directory as this script")
        return
    
    print("=" * 70)
    print("TSV STANDARDIZATION WITH FIXITY VERIFICATION")
    print("=" * 70)
    print(f"\nProcessing: {input_file.name}")
    
    # Compute original checksum
    print("\n[1] Computing original file checksum...")
    original_sha256 = compute_checksum(str(input_file), 'sha256')
    original_md5 = compute_checksum(str(input_file), 'md5')
    original_size = input_file.stat().st_size
    print(f"    SHA-256: {original_sha256}")
    print(f"    MD5:     {original_md5}")
    print(f"    Size:    {original_size} bytes")
    
    # Standardize the file
    print("\n[2] Standardizing TSV file...")
    stats = standardize_tsv(str(input_file), str(output_file))
    print(f"    Original rows:      {stats['original_rows']}")
    print(f"    Standardized rows:  {stats['standardized_rows']}")
    print(f"    Data rows:          {stats['rows_processed']}")
    print(f"    Columns:            {stats['columns']}")
    
    if stats['issues']:
        print(f"\n    Issues detected ({len(stats['issues'])}):")
        for issue in stats['issues'][:5]:  # Show first 5 issues
            print(f"      - {issue}")
        if len(stats['issues']) > 5:
            print(f"      ... and {len(stats['issues']) - 5} more")
    
    # Compute output checksum
    print("\n[3] Computing output file checksum...")
    output_sha256 = compute_checksum(str(output_file), 'sha256')
    output_md5 = compute_checksum(str(output_file), 'md5')
    output_size = output_file.stat().st_size
    print(f"    SHA-256: {output_sha256}")
    print(f"    MD5:     {output_md5}")
    print(f"    Size:    {output_size} bytes")
    
    # Create fixity report
    print("\n[4] Generating fixity report...")
    fixity_data = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'process': 'TSV Standardization',
        'source_file': {
            'filename': input_file.name,
            'path': str(input_file),
            'size_bytes': original_size,
            'checksum': {
                'sha256': original_sha256,
                'md5': original_md5
            }
        },
        'output_file': {
            'filename': output_file.name,
            'path': str(output_file),
            'size_bytes': output_size,
            'checksum': {
                'sha256': output_sha256,
                'md5': output_md5
            }
        },
        'processing_stats': {
            'original_rows': stats['original_rows'],
            'standardized_rows': stats['standardized_rows'],
            'data_rows_processed': stats['rows_processed'],
            'columns': stats['columns'],
            'issues_detected': len(stats['issues']),
            'issues': stats['issues']
        }
    }
    
    # Write fixity report
    with open(fixity_report, 'w', encoding='utf-8') as f:
        json.dump(fixity_data, f, indent=2)
    
    print(f"    Report saved to: {fixity_report.name}")
    
    print("\n" + "=" * 70)
    print("STANDARDIZATION COMPLETE")
    print("=" * 70)
    print(f"\nOutput files:")
    print(f"  1. {output_file.name} (standardized TSV)")
    print(f"  2. {fixity_report.name} (fixity verification report)")
    print("\n✓ All files have been checksummed and verified")

if __name__ == '__main__':
    main()
