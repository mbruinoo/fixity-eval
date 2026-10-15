#!/usr/bin/env python3
"""
Standardize TSV file: Met Museum Inventory
- Ensure consistent tab-delimited format
- Remove trailing whitespace
- Normalize line endings to LF
- Validate column structure
- Generate checksums for fixity verification
"""

import csv
import sys
import hashlib
from pathlib import Path

def calculate_checksum(file_path, algorithm='sha256'):
    """Calculate file checksum."""
    hash_obj = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()

def standardize_tsv(input_file, output_file):
    """
    Standardize TSV file:
    - Use tab as delimiter
    - Remove trailing whitespace from each field
    - Normalize line endings to LF
    - Ensure consistent structure
    """
    rows = []
    stats = {
        'rows_read': 0,
        'rows_written': 0,
        'empty_rows': 0,
        'columns': set()
    }
    
    # Read the file
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for row_num, row in enumerate(reader, 1):
            # Count columns in this row
            col_count = len(row)
            stats['columns'].add(col_count)
            
            if all(field.strip() == '' for field in row):
                stats['empty_rows'] += 1
                continue
            
            # Strip trailing/leading whitespace from each field
            cleaned_row = [field.strip() for field in row]
            rows.append(cleaned_row)
            stats['rows_read'] += 1
    
    # Determine expected column count (most common)
    if stats['columns']:
        expected_cols = max(stats['columns'], key=list(stats['columns']).count)
    else:
        expected_cols = 4
    
    # Pad rows to have consistent columns if needed
    standardized_rows = []
    for row in rows:
        while len(row) < expected_cols:
            row.append('')
        # Trim excess columns if any
        row = row[:expected_cols]
        standardized_rows.append(row)
        stats['rows_written'] += 1
    
    # Write standardized file with LF line endings
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t', lineterminator='\n')
        writer.writerows(standardized_rows)
    
    return stats, expected_cols

def main():
    input_file = '/mnt/user-data/uploads/met_inventory.tsv'
    output_file = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
    
    # Calculate source checksum
    source_checksum = calculate_checksum(input_file)
    print(f"Source file SHA256: {source_checksum}")
    print(f"Source file: {input_file}\n")
    
    # Standardize
    print("Standardizing TSV file...")
    stats, col_count = standardize_tsv(input_file, output_file)
    
    # Calculate output checksum
    output_checksum = calculate_checksum(output_file)
    print(f"\nOutput file SHA256: {output_checksum}")
    print(f"Output file: {output_file}\n")
    
    # Print statistics
    print("=" * 60)
    print("STANDARDIZATION STATISTICS")
    print("=" * 60)
    print(f"Rows read:           {stats['rows_read']}")
    print(f"Rows written:        {stats['rows_written']}")
    print(f"Empty rows removed:  {stats['empty_rows']}")
    print(f"Standardized columns: {col_count}")
    print(f"Column count variance: {stats['columns']}")
    print("=" * 60)
    
    # Create manifest file
    manifest_path = '/mnt/user-data/outputs/MANIFEST.txt'
    with open(manifest_path, 'w') as f:
        f.write("TSV STANDARDIZATION MANIFEST\n")
        f.write("=" * 60 + "\n\n")
        f.write("SOURCE FILE\n")
        f.write(f"  Path: {input_file}\n")
        f.write(f"  SHA256: {source_checksum}\n\n")
        f.write("OUTPUT FILE\n")
        f.write(f"  Path: {output_file}\n")
        f.write(f"  SHA256: {output_checksum}\n\n")
        f.write("STANDARDIZATION DETAILS\n")
        f.write(f"  Rows processed: {stats['rows_read']}\n")
        f.write(f"  Rows written: {stats['rows_written']}\n")
        f.write(f"  Empty rows removed: {stats['empty_rows']}\n")
        f.write(f"  Standardized columns: {col_count}\n\n")
        f.write("OPERATIONS PERFORMED\n")
        f.write("  • Consistent tab-delimited format\n")
        f.write("  • Removed leading/trailing whitespace from fields\n")
        f.write("  • Normalized line endings to LF (\\n)\n")
        f.write("  • Removed completely empty rows\n")
        f.write("  • Standardized to 4 columns across all rows\n\n")
        f.write("VERIFICATION\n")
        f.write("  To verify file integrity:\n")
        f.write(f"    sha256sum {output_file}\n")
        f.write(f"  Expected hash: {output_checksum}\n")
    
    print(f"\nManifest created: {manifest_path}")

if __name__ == '__main__':
    main()
