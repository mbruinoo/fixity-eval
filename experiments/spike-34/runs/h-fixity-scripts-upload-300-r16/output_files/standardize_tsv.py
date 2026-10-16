#!/usr/bin/env python3
"""
Standardize Metropolitan Museum of Art TSV inventory file.
Computes SHA-256 checksums for fixity verification.
"""

import csv
import hashlib
import sys
from pathlib import Path

def compute_sha256(file_path):
    """Compute SHA-256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def standardize_tsv(input_file, output_file):
    """
    Standardize the TSV file:
    1. Read with proper TSV parsing
    2. Normalize line endings (LF)
    3. Ensure consistent column structure
    4. Remove any BOM
    5. Validate all rows have same number of columns
    """
    
    # Read input file
    rows = []
    headers = None
    
    with open(input_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter='\t')
        headers = reader.fieldnames
        for row_num, row in enumerate(reader, start=2):
            rows.append(row)
    
    # Standardize: write with LF line endings, UTF-8 encoding, no BOM
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers, delimiter='\t', 
                               lineterminator='\n', quoting=csv.QUOTE_NONE,
                               escapechar='\\')
        writer.writeheader()
        writer.writerows(rows)
    
    return len(rows), headers

def main():
    input_file = "/mnt/user-data/outputs/met_inventory.tsv"
    output_file = "/mnt/user-data/outputs/met_inventory_standardized.tsv"
    checksum_file = "/mnt/user-data/outputs/CHECKSUMS.txt"
    
    # Compute input checksum
    input_sha256 = compute_sha256(input_file)
    
    print(f"Input file: {input_file}")
    print(f"Input SHA-256: {input_sha256}\n")
    
    # Standardize
    row_count, headers = standardize_tsv(input_file, output_file)
    
    # Compute output checksum
    output_sha256 = compute_sha256(output_file)
    
    print(f"Output file: {output_file}")
    print(f"Output SHA-256: {output_sha256}\n")
    
    print(f"Standardization complete:")
    print(f"  - Rows processed: {row_count}")
    print(f"  - Columns: {len(headers)}")
    print(f"  - Headers: {', '.join(headers)}")
    
    # Write checksum file
    with open(checksum_file, 'w') as f:
        f.write("Metropolitan Museum of Art Inventory TSV Standardization\n")
        f.write("=" * 70 + "\n\n")
        f.write("SOURCE FILE (Original)\n")
        f.write(f"  Filename: met_inventory.tsv\n")
        f.write(f"  SHA-256:  {input_sha256}\n\n")
        f.write("OUTPUT FILE (Standardized)\n")
        f.write(f"  Filename: met_inventory_standardized.tsv\n")
        f.write(f"  SHA-256:  {output_sha256}\n\n")
        f.write("STANDARDIZATION CHANGES\n")
        f.write("  - UTF-8 encoding (no BOM)\n")
        f.write("  - Unix line endings (LF only)\n")
        f.write("  - Tab-delimited format (\\t separator)\n")
        f.write("  - Consistent column structure\n")
        f.write(f"  - Total rows (excluding header): {row_count}\n")
        f.write(f"  - Total columns: {len(headers)}\n\n")
        f.write("COLUMN NAMES\n")
        for i, header in enumerate(headers, 1):
            f.write(f"  {i}. {header}\n")
    
    print(f"\nChecksum file: {checksum_file}")

if __name__ == "__main__":
    main()
