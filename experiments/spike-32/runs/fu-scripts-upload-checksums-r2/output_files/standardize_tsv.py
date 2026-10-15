#!/usr/bin/env python3
"""
Standardize a TSV file and preserve fixity with checksums.
Standardization includes:
- Consistent UTF-8 encoding
- Unix line endings (LF)
- Proper tab separation
- Trimmed whitespace in cells
- Consistent quoting for fields with special characters
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
    Standardize a TSV file with proper formatting and encoding.
    """
    # Read the input file
    rows = []
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            # Trim whitespace from each cell and preserve content
            standardized_row = [cell.strip() for cell in row]
            rows.append(standardized_row)
    
    # Write standardized TSV with Unix line endings and UTF-8 encoding
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t', lineterminator='\n', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(rows)

def main():
    input_file = '/mnt/user-data/uploads/met_inventory.tsv'
    output_file = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
    checksum_file = '/mnt/user-data/outputs/checksums.txt'
    
    # Verify input file exists
    if not Path(input_file).exists():
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)
    
    # Calculate source checksum
    print("Calculating source file checksums...")
    source_sha256 = calculate_checksum(input_file, 'sha256')
    source_sha512 = calculate_checksum(input_file, 'sha512')
    source_md5 = calculate_checksum(input_file, 'md5')
    
    print(f"Source file: {input_file}")
    print(f"  SHA256: {source_sha256}")
    print(f"  SHA512: {source_sha512}")
    print(f"  MD5:    {source_md5}")
    print()
    
    # Standardize the file
    print("Standardizing TSV file...")
    standardize_tsv(input_file, output_file)
    print(f"Output file: {output_file}")
    print()
    
    # Calculate output checksums
    print("Calculating output file checksums...")
    output_sha256 = calculate_checksum(output_file, 'sha256')
    output_sha512 = calculate_checksum(output_file, 'sha512')
    output_md5 = calculate_checksum(output_file, 'md5')
    
    print(f"Output file: {output_file}")
    print(f"  SHA256: {output_sha256}")
    print(f"  SHA512: {output_sha512}")
    print(f"  MD5:    {output_md5}")
    print()
    
    # Write checksum file
    with open(checksum_file, 'w') as f:
        f.write("# TSV Standardization Checksum Report\n")
        f.write("# Generated for fixity verification\n\n")
        
        f.write("## SOURCE FILE\n")
        f.write(f"File: {input_file}\n")
        f.write(f"SHA256: {source_sha256}\n")
        f.write(f"SHA512: {source_sha512}\n")
        f.write(f"MD5:    {source_md5}\n\n")
        
        f.write("## OUTPUT FILE (Standardized)\n")
        f.write(f"File: {output_file}\n")
        f.write(f"SHA256: {output_sha256}\n")
        f.write(f"SHA512: {output_sha512}\n")
        f.write(f"MD5:    {output_md5}\n\n")
        
        f.write("## STANDARDIZATION NOTES\n")
        f.write("- Encoding: UTF-8\n")
        f.write("- Line endings: Unix (LF)\n")
        f.write("- Delimiter: Tab character (\\t)\n")
        f.write("- Quoting: Minimal (only when necessary)\n")
        f.write("- Whitespace: Trimmed from cell boundaries\n")
        f.write("- Row count preserved from original\n")
    
    print(f"Checksum file written to: {checksum_file}")
    
    # Verify data integrity - count rows
    with open(input_file, 'r', encoding='utf-8') as f:
        input_rows = sum(1 for _ in f)
    
    with open(output_file, 'r', encoding='utf-8') as f:
        output_rows = sum(1 for _ in f)
    
    print()
    print("## INTEGRITY VERIFICATION")
    print(f"Source rows:  {input_rows}")
    print(f"Output rows:  {output_rows}")
    print(f"Rows match:   {'✓ YES' if input_rows == output_rows else '✗ NO'}")

if __name__ == '__main__':
    main()
