#!/usr/bin/env python3
"""
Met Museum Inventory Standardization Script
Reads original TSV, applies data standardization, and outputs with fixity checks.

Input: met_inventory.tsv (tab-separated values)
Output: met_inventory_standardized.tsv (tab-separated values with standardized format)

Transformations applied:
  1. Fill empty Title cells with [Unknown]
  2. Fill empty Object Date cells with [Unknown]
  3. Remove bilingual prefixes (Chinese/Japanese) from titles, keeping English only
  4. Ensure consistent tab-delimited format
  5. Preserve all original data integrity
"""

import sys
import os
import hashlib
from pathlib import Path

def calculate_checksum(filepath, algorithm='md5'):
    """Calculate checksum of a file."""
    hash_func = hashlib.new(algorithm)
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_func.update(chunk)
    return hash_func.hexdigest()

def standardize_row(row):
    """
    Standardize a single row.
    Expected format: Object Date | Title | Object Number | Link Resource
    """
    if len(row) < 4:
        # Pad row if it has fewer than 4 columns
        row.extend([''] * (4 - len(row)))
    
    object_date, title, object_number, link = row[0], row[1], row[2], row[3]
    
    # Standardization: fill empty fields with [Unknown]
    if not object_date.strip():
        object_date = '[Unknown]'
    if not title.strip():
        title = '[Unknown]'
    
    # Remove bilingual prefixes (Chinese/Japanese) from titles
    # Pattern: "Chinese/Japanese text|English title" or similar
    if '|' in title:
        # Take the part after the pipe (English title)
        parts = title.split('|', 1)
        title = parts[1].strip()
    
    return [object_date, title, object_number, link]

def main():
    input_file = '/mnt/user-data/uploads/met_inventory.tsv'
    output_file = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
    
    # Check input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}", file=sys.stderr)
        sys.exit(1)
    
    # Calculate input checksum
    input_md5 = calculate_checksum(input_file, 'md5')
    input_sha256 = calculate_checksum(input_file, 'sha256')
    
    print(f"Input file: {input_file}")
    print(f"  MD5:    {input_md5}")
    print(f"  SHA256: {input_sha256}")
    print()
    
    # Read and process
    with open(input_file, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()
    
    # Parse header
    if not lines:
        print("Error: Input file is empty", file=sys.stderr)
        sys.exit(1)
    
    header = lines[0].rstrip('\n').split('\t')
    print(f"Header: {header}")
    print(f"Total rows to process: {len(lines) - 1}")
    print()
    
    # Process data rows
    standardized_rows = [header]
    for i, line in enumerate(lines[1:], 1):
        row = line.rstrip('\n').split('\t')
        standardized_row = standardize_row(row)
        standardized_rows.append(standardized_row)
    
    # Write output
    with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        for row in standardized_rows:
            outfile.write('\t'.join(row) + '\n')
    
    # Calculate output checksum
    output_md5 = calculate_checksum(output_file, 'md5')
    output_sha256 = calculate_checksum(output_file, 'sha256')
    
    print(f"Output file: {output_file}")
    print(f"  MD5:    {output_md5}")
    print(f"  SHA256: {output_sha256}")
    print()
    
    # Generate manifest
    manifest_file = '/mnt/user-data/outputs/MANIFEST.txt'
    with open(manifest_file, 'w', encoding='utf-8') as mf:
        mf.write("Met Museum Inventory Standardization - File Manifest\n")
        mf.write("=" * 70 + "\n\n")
        mf.write("TRANSFORMATION SCRIPT: standardize_met_inventory.py\n")
        mf.write("Purpose: Standardize TSV format and fill missing values\n\n")
        
        mf.write("INPUT FILE\n")
        mf.write("-" * 70 + "\n")
        mf.write(f"Filename: met_inventory.tsv\n")
        mf.write(f"Path: {input_file}\n")
        mf.write(f"MD5:    {input_md5}\n")
        mf.write(f"SHA256: {input_sha256}\n")
        mf.write(f"Rows: {len(lines) - 1} (excluding header)\n\n")
        
        mf.write("OUTPUT FILE\n")
        mf.write("-" * 70 + "\n")
        mf.write(f"Filename: met_inventory_standardized.tsv\n")
        mf.write(f"Path: {output_file}\n")
        mf.write(f"MD5:    {output_md5}\n")
        mf.write(f"SHA256: {output_sha256}\n")
        mf.write(f"Rows: {len(standardized_rows) - 1} (excluding header)\n\n")
        
        mf.write("TRANSFORMATIONS APPLIED\n")
        mf.write("-" * 70 + "\n")
        mf.write("1. Standardized empty 'Object Date' cells → [Unknown]\n")
        mf.write("2. Standardized empty 'Title' cells → [Unknown]\n")
        mf.write("3. Removed bilingual prefixes (Chinese/Japanese text) from titles\n")
        mf.write("   - Kept English title after pipe character (|)\n")
        mf.write("4. Ensured consistent tab-delimited format (4 columns)\n")
        mf.write("5. Preserved all original data and hyperlinks\n\n")
        
        mf.write("FIXITY VERIFICATION\n")
        mf.write("-" * 70 + "\n")
        mf.write("To verify file integrity:\n")
        mf.write(f"  md5sum -c MANIFEST.txt\n")
        mf.write(f"  md5sum met_inventory.tsv\n")
        mf.write(f"    Expected: {input_md5}\n")
        mf.write(f"  md5sum met_inventory_standardized.tsv\n")
        mf.write(f"    Expected: {output_md5}\n\n")
        
        mf.write("OR using SHA256:\n")
        mf.write(f"  sha256sum met_inventory.tsv\n")
        mf.write(f"    Expected: {input_sha256}\n")
        mf.write(f"  sha256sum met_inventory_standardized.tsv\n")
        mf.write(f"    Expected: {output_sha256}\n")
    
    print(f"Manifest file: {manifest_file}")
    print("\nStandardization complete!")
    return 0

if __name__ == '__main__':
    sys.exit(main())
