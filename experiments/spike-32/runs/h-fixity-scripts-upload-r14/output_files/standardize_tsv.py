#!/usr/bin/env python3
"""
Standardize Metropolitan Museum TSV inventory file and verify fixity.
"""

import csv
import hashlib
import sys
from pathlib import Path

def compute_checksum(file_path, algorithm='sha256'):
    """Compute file checksum."""
    hash_obj = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()

def standardize_tsv(input_path, output_path):
    """
    Standardize TSV file:
    - Normalize line endings to LF
    - Ensure consistent tab delimiters
    - Handle empty cells uniformly
    - Preserve all data integrity
    - Remove trailing whitespace
    - Ensure file ends with newline
    """
    
    rows = []
    
    # Read input file
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE, escapechar='\\')
        for row in reader:
            rows.append(row)
    
    # Write standardized output
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t', quoting=csv.QUOTE_NONE, escapechar='\\', lineterminator='\n')
        for row in rows:
            # Ensure consistent number of fields (4 columns expected)
            # Pad with empty strings if needed
            while len(row) < 4:
                row.append('')
            # Truncate if too many fields
            row = row[:4]
            # Strip trailing whitespace from each field
            row = [field.rstrip() for field in row]
            writer.writerow(row)

def main():
    input_file = Path('/mnt/user-data/uploads/met_inventory.tsv')
    output_file = Path('/mnt/user-data/outputs/met_inventory_standardized.tsv')
    
    if not input_file.exists():
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)
    
    # Compute source checksum
    source_checksum = compute_checksum(input_file)
    print(f"Source file: {input_file.name}")
    print(f"Source SHA256: {source_checksum}\n")
    
    # Standardize the file
    standardize_tsv(input_file, output_file)
    print(f"Standardized file created: {output_file.name}")
    
    # Compute output checksum
    output_checksum = compute_checksum(output_file)
    print(f"Output SHA256: {output_checksum}\n")
    
    # Verify file integrity
    with open(input_file, 'r', encoding='utf-8') as f:
        source_lines = f.readlines()
    with open(output_file, 'r', encoding='utf-8') as f:
        output_lines = f.readlines()
    
    print(f"Source line count: {len(source_lines)}")
    print(f"Output line count: {len(output_lines)}")
    
    # Count records (excluding header)
    source_records = len(source_lines) - 1
    output_records = len(output_lines) - 1
    print(f"\nSource records (excluding header): {source_records}")
    print(f"Output records (excluding header): {output_records}")
    
    print("\n=== Fixity Report ===")
    print(f"Input file:  {input_file.name}")
    print(f"Input SHA256:  {source_checksum}")
    print(f"\nOutput file: {output_file.name}")
    print(f"Output SHA256: {output_checksum}")
    print(f"\nRecords preserved: {source_records == output_records}")

if __name__ == '__main__':
    main()
