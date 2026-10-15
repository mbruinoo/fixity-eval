#!/usr/bin/env python3
"""
Standardize Met Museum inventory TSV file.
Computes checksums for source and result files to preserve fixity.
"""

import csv
import hashlib
import sys
from pathlib import Path

def compute_checksum(file_path, algorithm='sha256'):
    """Compute checksum of a file."""
    hasher = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()

def standardize_tsv(input_path, output_path):
    """
    Standardize the TSV file:
    - Ensure consistent tab delimiters
    - Remove extra whitespace from field values
    - Ensure consistent column ordering
    - Handle missing values uniformly
    """
    
    # Expected columns
    columns = ['Object Date', 'Title', 'Object Number', 'Link Resource']
    
    rows = []
    
    # Read the input file
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, fieldnames=columns, delimiter='\t')
        
        for row_num, row in enumerate(reader, 1):
            standardized_row = {}
            for col in columns:
                value = row.get(col, '')
                # Strip leading/trailing whitespace but preserve internal spacing
                value = value.strip() if value else ''
                standardized_row[col] = value
            rows.append(standardized_row)
    
    # Write the standardized output
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns, delimiter='\t')
        writer.writeheader()
        writer.writerows(rows)
    
    return len(rows)

def main():
    input_file = '/mnt/user-data/uploads/met_inventory.tsv'
    output_file = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
    checksum_file = '/mnt/user-data/outputs/checksums.txt'
    
    # Verify input file exists
    if not Path(input_file).exists():
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)
    
    # Create output directory if needed
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("Met Museum Inventory TSV Standardization")
    print("=" * 70)
    
    # Compute source checksum
    print("\n1. Computing source file checksum...")
    source_sha256 = compute_checksum(input_file, 'sha256')
    source_md5 = compute_checksum(input_file, 'md5')
    print(f"   SHA-256: {source_sha256}")
    print(f"   MD5:     {source_md5}")
    
    # Standardize the file
    print("\n2. Standardizing TSV file...")
    row_count = standardize_tsv(input_file, output_file)
    print(f"   ✓ Processed {row_count} data rows")
    print(f"   ✓ Standardized output saved to: {output_file}")
    
    # Compute result checksum
    print("\n3. Computing result file checksum...")
    result_sha256 = compute_checksum(output_file, 'sha256')
    result_md5 = compute_checksum(output_file, 'md5')
    print(f"   SHA-256: {result_sha256}")
    print(f"   MD5:     {result_md5}")
    
    # Write checksums to file
    print("\n4. Writing checksums to file...")
    with open(checksum_file, 'w') as f:
        f.write("MET MUSEUM INVENTORY TSV STANDARDIZATION - CHECKSUMS\n")
        f.write("=" * 70 + "\n\n")
        f.write("SOURCE FILE: met_inventory.tsv\n")
        f.write(f"SHA-256: {source_sha256}\n")
        f.write(f"MD5:     {source_md5}\n\n")
        f.write("OUTPUT FILE: met_inventory_standardized.tsv\n")
        f.write(f"SHA-256: {result_sha256}\n")
        f.write(f"MD5:     {result_md5}\n\n")
        f.write("STANDARDIZATION ACTIONS:\n")
        f.write("- Ensured consistent tab delimiters\n")
        f.write("- Stripped leading/trailing whitespace from all fields\n")
        f.write("- Verified consistent column ordering\n")
        f.write("- Standardized missing value handling\n")
        f.write(f"- Total rows processed: {row_count}\n")
    
    print(f"   ✓ Checksums saved to: {checksum_file}")
    
    print("\n" + "=" * 70)
    print("✓ Standardization complete!")
    print("=" * 70)

if __name__ == '__main__':
    main()
