#!/usr/bin/env python3
"""
TSV Standardizer with Checksum Preservation
Standardizes a Met Museum inventory TSV file and maintains integrity checksums.
"""

import csv
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path


def calculate_checksum(file_path, algorithm='sha256'):
    """Calculate checksum for a file."""
    hash_obj = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()


def log_checksums(source_path, output_path, checksum_log_path):
    """Calculate and log checksums for both files."""
    source_checksum = calculate_checksum(source_path, 'sha256')
    output_checksum = calculate_checksum(output_path, 'sha256')
    
    checksum_data = {
        'timestamp': datetime.now().isoformat(),
        'source_file': source_path,
        'source_checksum_sha256': source_checksum,
        'output_file': output_path,
        'output_checksum_sha256': output_checksum,
        'algorithm': 'SHA-256'
    }
    
    with open(checksum_log_path, 'w') as f:
        json.dump(checksum_data, f, indent=2)
    
    return checksum_data


def standardize_tsv(input_file, output_file):
    """
    Standardize TSV file:
    - Ensure consistent tab delimiters
    - Handle quoted fields properly
    - Normalize whitespace
    - Fix encoding
    - Sort by Object Number (column index 2)
    """
    
    # Read the source file
    rows = []
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE, escapechar=None)
        for row_num, row in enumerate(reader, 1):
            # Strip whitespace from each field
            cleaned_row = [field.strip() for field in row]
            rows.append(cleaned_row)
    
    if not rows:
        print("Error: Empty file or unable to read rows")
        return False
    
    # Extract header
    header = rows[0]
    data_rows = rows[1:]
    
    # Validate and standardize columns
    print(f"Header columns: {len(header)}")
    print(f"Header: {header}")
    print(f"Data rows: {len(data_rows)}")
    
    # Check for inconsistent row lengths
    max_cols = max(len(row) for row in data_rows) if data_rows else len(header)
    print(f"Max columns in data: {max_cols}")
    
    # Normalize all rows to have consistent column count
    standardized_rows = []
    for row in data_rows:
        # Pad rows that are too short
        while len(row) < len(header):
            row.append('')
        # Truncate rows that are too long
        if len(row) > len(header):
            row = row[:len(header)]
        standardized_rows.append(row)
    
    # Sort by Object Number (column 2, 0-indexed)
    try:
        standardized_rows.sort(key=lambda x: x[2] if len(x) > 2 else '')
    except Exception as e:
        print(f"Warning: Could not sort by Object Number: {e}")
    
    # Write standardized output
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(header)
        writer.writerows(standardized_rows)
    
    return True


def main():
    """Main execution function."""
    if len(sys.argv) < 2:
        print("Usage: python standardize_tsv.py <input_file> [output_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'met_inventory_standardized.tsv'
    checksum_log = 'checksums.json'
    
    # Verify input file exists
    if not Path(input_file).exists():
        print(f"Error: Input file '{input_file}' not found")
        sys.exit(1)
    
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    
    # Calculate source checksum before processing
    print("\nCalculating source checksum...")
    source_checksum = calculate_checksum(input_file)
    print(f"Source SHA-256: {source_checksum}")
    
    # Standardize the file
    print("\nStandardizing TSV file...")
    if not standardize_tsv(input_file, output_file):
        sys.exit(1)
    
    print("✓ File standardized successfully")
    
    # Calculate output checksum and log both
    print("\nCalculating output checksum...")
    output_checksum = calculate_checksum(output_file)
    print(f"Output SHA-256: {output_checksum}")
    
    # Log checksums
    print(f"\nLogging checksums to {checksum_log}...")
    checksum_data = log_checksums(input_file, output_file, checksum_log)
    
    print("\n" + "="*60)
    print("STANDARDIZATION COMPLETE")
    print("="*60)
    print(f"Source file: {input_file}")
    print(f"  SHA-256: {checksum_data['source_checksum_sha256']}")
    print(f"\nOutput file: {output_file}")
    print(f"  SHA-256: {checksum_data['output_checksum_sha256']}")
    print(f"\nChecksum log: {checksum_log}")
    print("="*60)


if __name__ == '__main__':
    main()
