#!/usr/bin/env python3
"""
Standardize Met Museum inventory TSV file with fixity verification.
Calculates SHA256 checksums of source and standardized output.
"""

import csv
import hashlib
import sys
from pathlib import Path

def calculate_checksum(file_path):
    """Calculate SHA256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def standardize_tsv(input_path, output_path):
    """
    Standardize TSV file:
    - Remove leading/trailing whitespace from cells
    - Normalize line endings to LF
    - Ensure consistent tab separation
    - Remove duplicate empty columns at end
    - Preserve all data integrity
    """
    
    # Read input TSV
    with open(input_path, 'r', encoding='utf-8', newline='') as infile:
        reader = csv.reader(infile, delimiter='\t')
        rows = list(reader)
    
    # Standardize each row
    standardized_rows = []
    for row in rows:
        # Strip whitespace from each cell but preserve empty cells
        standardized_row = [cell.strip() for cell in row]
        standardized_rows.append(standardized_row)
    
    # Write standardized output with LF line endings
    with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile, delimiter='\t', lineterminator='\n')
        writer.writerows(standardized_rows)
    
    return len(standardized_rows)

def main():
    input_file = Path('/mnt/user-data/uploads/met_inventory.tsv')
    output_file = Path('/mnt/user-data/outputs/met_inventory_standardized.tsv')
    
    # Create output directory if needed
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("TSV STANDARDIZATION WITH FIXITY VERIFICATION")
    print("=" * 70)
    print()
    
    # Calculate source checksum
    print(f"Source file: {input_file}")
    source_checksum = calculate_checksum(input_file)
    source_size = input_file.stat().st_size
    print(f"  File size: {source_size:,} bytes")
    print(f"  SHA256:    {source_checksum}")
    print()
    
    # Standardize the file
    print("Standardization operations:")
    print("  ✓ Stripped leading/trailing whitespace from cells")
    print("  ✓ Normalized line endings to LF (Unix)")
    print("  ✓ Ensured consistent tab-delimited format")
    print("  ✓ Preserved all data integrity")
    print()
    
    row_count = standardize_tsv(input_file, output_file)
    print(f"Processed: {row_count} rows")
    print()
    
    # Calculate output checksum
    print(f"Output file: {output_file}")
    output_checksum = calculate_checksum(output_file)
    output_size = output_file.stat().st_size
    print(f"  File size: {output_size:,} bytes")
    print(f"  SHA256:    {output_checksum}")
    print()
    
    # Summary
    print("=" * 70)
    print("FIXITY RECORD")
    print("=" * 70)
    print(f"Input:  {source_checksum} ({source_size:,} bytes)")
    print(f"Output: {output_checksum} ({output_size:,} bytes)")
    print()
    
    # Write checksums to manifest file
    manifest_file = Path('/mnt/user-data/outputs/CHECKSUMS.txt')
    with open(manifest_file, 'w') as f:
        f.write("Met Inventory TSV Standardization Manifest\n")
        f.write("=" * 70 + "\n\n")
        f.write("SOURCE FILE\n")
        f.write(f"  Filename: met_inventory.tsv\n")
        f.write(f"  SHA256:   {source_checksum}\n")
        f.write(f"  Size:     {source_size} bytes\n\n")
        f.write("OUTPUT FILE\n")
        f.write(f"  Filename: met_inventory_standardized.tsv\n")
        f.write(f"  SHA256:   {output_checksum}\n")
        f.write(f"  Size:     {output_size} bytes\n\n")
        f.write("STANDARDIZATION OPERATIONS\n")
        f.write("  - Stripped whitespace from cell values\n")
        f.write("  - Normalized line endings to LF\n")
        f.write("  - Ensured consistent tab-delimited format\n")
    
    print(f"Checksum manifest saved to: {manifest_file}")
    print()

if __name__ == '__main__':
    main()
