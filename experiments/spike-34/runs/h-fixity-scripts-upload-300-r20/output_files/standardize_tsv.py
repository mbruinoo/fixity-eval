#!/usr/bin/env python3
"""
Standardize TSV file and preserve fixity with checksums.
"""
import csv
import hashlib
import sys
from pathlib import Path

def calculate_checksum(file_path, algorithm='sha256'):
    """Calculate checksum of a file."""
    hasher = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()

def standardize_tsv(input_path, output_path):
    """
    Standardize TSV file:
    - Ensure consistent tab delimiters
    - Normalize line endings (LF)
    - Trim whitespace in cells
    - Maintain header row
    - Ensure all rows have 5 columns
    """
    rows = []
    
    # Read the input file
    with open(input_path, 'r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f, delimiter='\t')
        for row_num, row in enumerate(reader, 1):
            # Ensure row has exactly 5 columns (pad with empty strings if needed)
            while len(row) < 5:
                row.append('')
            # Trim to 5 columns if there are extras (shouldn't happen with proper TSV)
            row = row[:5]
            # Strip leading/trailing whitespace from each cell
            row = [cell.strip() for cell in row]
            rows.append(row)
    
    # Write standardized output
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t', lineterminator='\n')
        writer.writerows(rows)
    
    return len(rows)

def main():
    input_file = '/mnt/user-data/uploads/met_inventory.tsv'
    output_file = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
    
    # Calculate source checksum
    source_checksum = calculate_checksum(input_file, 'sha256')
    print(f"Source file: {input_file}")
    print(f"SHA256: {source_checksum}")
    print()
    
    # Standardize the TSV
    row_count = standardize_tsv(input_file, output_file)
    print(f"Standardized TSV created: {output_file}")
    print(f"Total rows processed: {row_count}")
    print()
    
    # Calculate output checksum
    output_checksum = calculate_checksum(output_file, 'sha256')
    print(f"Output file: {output_file}")
    print(f"SHA256: {output_checksum}")
    print()
    
    # Create a manifest file
    manifest_path = '/mnt/user-data/outputs/MANIFEST.txt'
    with open(manifest_path, 'w', encoding='utf-8') as f:
        f.write("TSV STANDARDIZATION MANIFEST\n")
        f.write("=" * 60 + "\n\n")
        f.write("SOURCE FILE\n")
        f.write(f"  Path: {input_file}\n")
        f.write(f"  SHA256: {source_checksum}\n")
        f.write(f"  Size: {Path(input_file).stat().st_size} bytes\n\n")
        f.write("OUTPUT FILE\n")
        f.write(f"  Path: {output_file}\n")
        f.write(f"  SHA256: {output_checksum}\n")
        f.write(f"  Size: {Path(output_file).stat().st_size} bytes\n")
        f.write(f"  Rows: {row_count}\n\n")
        f.write("STANDARDIZATION OPERATIONS\n")
        f.write("  - Normalized tab delimiters\n")
        f.write("  - Standardized line endings (LF)\n")
        f.write("  - Trimmed whitespace from all cells\n")
        f.write("  - Ensured all rows have 5 columns\n")
        f.write("  - Preserved header row\n")
    
    print(f"Manifest created: {manifest_path}")

if __name__ == '__main__':
    main()
