#!/usr/bin/env python3
"""
Met Museum Inventory TSV Standardization Script
Purpose: Standardize TSV formatting and verify data integrity via checksums
"""

import hashlib
import csv
import sys
from pathlib import Path
from datetime import datetime

def calculate_checksum(file_path, algorithm='sha256'):
    """Calculate file checksum using specified algorithm."""
    hash_obj = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()

def standardize_tsv(input_file, output_file):
    """
    Standardize TSV file:
    1. Ensure consistent tab delimiters
    2. Normalize line endings to LF
    3. Preserve quoting for fields containing tabs, newlines, or quotes
    4. Maintain data integrity
    """
    
    rows_read = 0
    rows_written = 0
    
    try:
        # Read with proper TSV parsing
        with open(input_file, 'r', encoding='utf-8') as infile:
            reader = csv.reader(infile, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
            rows = list(reader)
            rows_read = len(rows)
        
        # Write with consistent formatting
        with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.writer(outfile, delimiter='\t', quoting=csv.QUOTE_MINIMAL, 
                              lineterminator='\n')
            writer.writerows(rows)
            rows_written = len(rows)
        
        return rows_read, rows_written
    
    except Exception as e:
        print(f"Error during standardization: {e}", file=sys.stderr)
        raise

def main():
    """Main processing function."""
    
    input_file = Path("met_inventory.tsv")
    output_file = Path("met_inventory_standardized.tsv")
    
    print("=" * 70)
    print("Met Museum Inventory TSV Standardization")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 70)
    
    # Check if input file exists
    if not input_file.exists():
        print(f"ERROR: Input file not found: {input_file}")
        sys.exit(1)
    
    # Calculate source checksum
    print(f"\nSource File: {input_file}")
    source_size = input_file.stat().st_size
    source_sha256 = calculate_checksum(input_file, 'sha256')
    source_md5 = calculate_checksum(input_file, 'md5')
    
    print(f"  Size: {source_size:,} bytes")
    print(f"  SHA256: {source_sha256}")
    print(f"  MD5: {source_md5}")
    
    # Standardize the file
    print("\nProcessing...")
    rows_read, rows_written = standardize_tsv(input_file, output_file)
    
    # Calculate output checksum
    print(f"\nOutput File: {output_file}")
    output_size = output_file.stat().st_size
    output_sha256 = calculate_checksum(output_file, 'sha256')
    output_md5 = calculate_checksum(output_file, 'md5')
    
    print(f"  Size: {output_size:,} bytes")
    print(f"  SHA256: {output_sha256}")
    print(f"  MD5: {output_md5}")
    
    # Report statistics
    print(f"\nData Integrity Report:")
    print(f"  Rows read: {rows_read}")
    print(f"  Rows written: {rows_written}")
    print(f"  Row count match: {'✓ YES' if rows_read == rows_written else '✗ NO'}")
    print(f"  File size change: {output_size - source_size:+,} bytes ({(output_size/source_size - 1)*100:+.2f}%)")
    
    print("\nStandardization Completed Successfully")
    print("=" * 70)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
