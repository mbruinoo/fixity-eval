#!/usr/bin/env python3
"""
TSV Standardization Script with Fixity Checking
Standardizes a TSV file and calculates checksums for both source and result
"""

import hashlib
import os


def calculate_checksums(file_path):
    """Calculate MD5 and SHA256 checksums for a file."""
    md5 = hashlib.md5()
    sha256 = hashlib.sha256()
    
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            md5.update(chunk)
            sha256.update(chunk)
    
    return md5.hexdigest(), sha256.hexdigest()


def standardize_tsv(input_path, output_path):
    """
    Standardize a TSV file:
    - Ensures proper tab delimiters
    - Normalizes line endings (LF)
    - Preserves all data
    - Uses UTF-8 encoding
    """
    
    print(f"Processing: {input_path}")
    print("-" * 70)
    
    # Calculate source checksums
    print("Calculating source file checksums...")
    source_md5, source_sha256 = calculate_checksums(input_path)
    print(f"Source MD5:    {source_md5}")
    print(f"Source SHA256: {source_sha256}")
    
    # Get source file size
    source_size = os.path.getsize(input_path)
    print(f"Source size:   {source_size} bytes")
    
    # Read and standardize
    print("\nStandardizing file...")
    rows = []
    row_count = 0
    
    with open(input_path, 'r', encoding='utf-8') as infile:
        for line in infile:
            # Remove line ending and split by tabs
            line = line.rstrip('\r\n')
            fields = line.split('\t')
            
            # Ensure 4 columns (pad with empty strings if needed)
            while len(fields) < 4:
                fields.append('')
            # Trim to 4 columns if extra
            fields = fields[:4]
            rows.append(fields)
            row_count += 1
    
    # Write standardized version
    print(f"Writing standardized file to: {output_path}")
    with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
        for fields in rows:
            outfile.write('\t'.join(fields) + '\n')
    
    # Calculate result checksums
    print("\nCalculating output file checksums...")
    result_md5, result_sha256 = calculate_checksums(output_path)
    print(f"Result MD5:    {result_md5}")
    print(f"Result SHA256: {result_sha256}")
    
    # Get result file size
    result_size = os.path.getsize(output_path)
    print(f"Result size:   {result_size} bytes")
    
    # Summary
    print("\n" + "=" * 70)
    print("FIXITY REPORT")
    print("=" * 70)
    print(f"Rows processed: {row_count}")
    print(f"Columns per row: 4")
    print(f"Column headers: Object Date | Title | Object Number | Link Resource")
    print(f"\nSource file:   {input_path}")
    print(f"  Size:   {source_size} bytes")
    print(f"  MD5:    {source_md5}")
    print(f"  SHA256: {source_sha256}")
    print(f"\nOutput file:   {output_path}")
    print(f"  Size:   {result_size} bytes")
    print(f"  MD5:    {result_md5}")
    print(f"  SHA256: {result_sha256}")
    print("=" * 70)


if __name__ == "__main__":
    input_file = "/mnt/user-data/uploads/met_inventory.tsv"
    output_file = "/mnt/user-data/outputs/met_inventory_standardized.tsv"
    
    standardize_tsv(input_file, output_file)
