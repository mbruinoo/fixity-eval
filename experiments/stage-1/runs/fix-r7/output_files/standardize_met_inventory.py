#!/usr/bin/env python3
"""
Standardize the Met Museum inventory TSV file with fixity verification.
Generates checksums for source and output files.
"""

import hashlib
import csv
import sys
from pathlib import Path
from datetime import datetime

def calculate_checksum(filepath, algorithm='sha256'):
    """Calculate SHA256 checksum of a file."""
    hash_obj = hashlib.new(algorithm)
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()

def standardize_tsv(input_path, output_path, checksum_log_path):
    """
    Standardize the Met inventory TSV file:
    - Ensure consistent column ordering
    - Handle missing values uniformly (use empty string)
    - Remove trailing whitespace
    - Ensure proper escaping
    - Sort by object date, then by object number
    """
    
    # Calculate source checksum
    source_checksum = calculate_checksum(input_path)
    print(f"Source file checksum (SHA256): {source_checksum}")
    
    # Define standardized column order
    standard_columns = ['Object Date', 'Title', 'Object Number', 'Link Resource']
    
    rows = []
    
    # Read input file
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            
            if reader.fieldnames is None:
                raise ValueError("Input file has no header row")
            
            print(f"Input columns: {reader.fieldnames}")
            
            for row_num, row in enumerate(reader, start=2):
                # Create standardized row with consistent column order
                std_row = {}
                for col in standard_columns:
                    value = row.get(col, '')
                    # Strip whitespace and standardize empty values
                    std_row[col] = value.strip() if value else ''
                rows.append(std_row)
    
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        raise
    
    print(f"Read {len(rows)} data rows")
    
    # Sort rows: by Object Date (handling complex date strings), then by Object Number
    def sort_key(row):
        date_str = row['Object Date']
        obj_num = row['Object Number']
        # Simple natural sort for dates (may need customization for complex date formats)
        return (date_str, obj_num)
    
    rows.sort(key=sort_key)
    
    # Write standardized output file
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=standard_columns, delimiter='\t', lineterminator='\n')
            writer.writeheader()
            writer.writerows(rows)
        print(f"Wrote {len(rows)} data rows to output")
    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        raise
    
    # Calculate output checksum
    output_checksum = calculate_checksum(output_path)
    print(f"Output file checksum (SHA256): {output_checksum}")
    
    # Write checksum log
    timestamp = datetime.now().isoformat()
    log_entries = [
        f"Standardization Log - {timestamp}",
        f"",
        f"Input File: {input_path}",
        f"Input SHA256: {source_checksum}",
        f"Input row count: {len(rows)} data rows (plus header)",
        f"",
        f"Output File: {output_path}",
        f"Output SHA256: {output_checksum}",
        f"Output row count: {len(rows)} data rows (plus header)",
        f"",
        f"Standardization Operations:",
        f"  - Normalized column order to: {', '.join(standard_columns)}",
        f"  - Stripped trailing/leading whitespace from all fields",
        f"  - Standardized empty values to empty strings",
        f"  - Sorted by Object Date, then Object Number",
        f"",
        f"Integrity: Source and output files can be verified using SHA256 checksums above.",
    ]
    
    try:
        with open(checksum_log_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(log_entries))
        print(f"Checksum log written to {checksum_log_path}")
    except Exception as e:
        print(f"Error writing checksum log: {e}", file=sys.stderr)
        raise
    
    return source_checksum, output_checksum

if __name__ == '__main__':
    input_file = '/mnt/user-data/uploads/met_inventory.tsv'
    output_file = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
    checksum_log = '/mnt/user-data/outputs/CHECKSUM_LOG.txt'
    
    print("=== Met Inventory TSV Standardization with Fixity Verification ===\n")
    
    try:
        source_cs, output_cs = standardize_tsv(input_file, output_file, checksum_log)
        print(f"\n✓ Standardization complete")
        print(f"✓ Files: {output_file}")
        print(f"✓ Log: {checksum_log}")
    except Exception as e:
        print(f"\n✗ Standardization failed: {e}", file=sys.stderr)
        sys.exit(1)
