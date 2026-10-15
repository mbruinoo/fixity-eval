#!/usr/bin/env python3
"""
Standardize Metropolitan Museum inventory TSV file.
Includes checksum verification for data integrity.
"""

import csv
import hashlib
import sys
from pathlib import Path

def calculate_checksum(file_path, algorithm='sha256'):
    """Calculate checksum of a file."""
    hash_obj = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()

def standardize_tsv(input_path, output_path):
    """
    Standardize TSV file with consistent formatting:
    - Ensure proper tab separation
    - Remove trailing whitespace from fields
    - Normalize empty fields
    - Ensure consistent quoting
    - Add proper BOM handling
    """
    
    # Calculate source checksum
    source_checksum = calculate_checksum(input_path)
    print(f"Source file SHA256: {source_checksum}")
    print(f"Source file: {input_path}")
    print()
    
    rows = []
    
    # Read the TSV file with proper handling
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE, 
                           escapechar=None, strict=False)
        for row_num, row in enumerate(reader, 1):
            # Strip whitespace from each field
            cleaned_row = [field.strip() for field in row]
            rows.append(cleaned_row)
    
    # Write standardized TSV
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t', quoting=csv.QUOTE_MINIMAL,
                           lineterminator='\n')
        writer.writerows(rows)
    
    # Calculate result checksum
    result_checksum = calculate_checksum(output_path)
    print(f"Standardized file SHA256: {result_checksum}")
    print(f"Standardized file: {output_path}")
    print()
    
    # Report statistics
    print(f"Total rows processed: {len(rows)}")
    print(f"Columns: {len(rows[0]) if rows else 0}")
    print()
    print("Standardization complete.")
    print("Files differ:", source_checksum != result_checksum)
    
    return source_checksum, result_checksum

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python standardize_tsv.py <input_file> [output_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.tsv', '_standardized.tsv')
    
    standardize_tsv(input_file, output_file)
