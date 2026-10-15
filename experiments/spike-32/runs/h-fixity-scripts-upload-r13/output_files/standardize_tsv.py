#!/usr/bin/env python3
"""
TSV Standardization Script
Standardizes met_inventory.tsv with the following rules:
1. Ensure consistent tab delimiters
2. Remove trailing whitespace from fields
3. Normalize empty cells (use explicit empty string)
4. UTF-8 encoding
5. Unix line endings (LF)
"""

import csv
import sys
import hashlib

def calculate_checksum(filepath, algorithm='sha256'):
    """Calculate file checksum"""
    hasher = hashlib.new(algorithm)
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()

def standardize_tsv(input_file, output_file):
    """Standardize TSV file"""
    try:
        # Read input file
        with open(input_file, 'r', encoding='utf-8') as infile:
            reader = csv.reader(infile, delimiter='\t', quoting=csv.QUOTE_NONE, 
                              escapechar=None, lineterminator='')
            rows = list(reader)
        
        # Standardize rows: strip whitespace from all fields
        standardized_rows = []
        for row in rows:
            standardized_row = [field.strip() if field else '' for field in row]
            standardized_rows.append(standardized_row)
        
        # Write output file with consistent formatting
        with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.writer(outfile, delimiter='\t', quoting=csv.QUOTE_MINIMAL,
                              lineterminator='\n', escapechar='\\')
            writer.writerows(standardized_rows)
        
        return True
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return False

if __name__ == '__main__':
    input_path = '/mnt/user-data/uploads/met_inventory.tsv'
    output_path = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
    
    # Calculate source checksum
    print("Calculating source file checksum...")
    source_checksum = calculate_checksum(input_path)
    print(f"Source SHA256: {source_checksum}")
    
    # Standardize file
    print("\nStandardizing TSV file...")
    if standardize_tsv(input_path, output_path):
        print(f"✓ Standardized file created: {output_path}")
    else:
        print("✗ Standardization failed")
        sys.exit(1)
    
    # Calculate output checksum
    print("\nCalculating output file checksum...")
    output_checksum = calculate_checksum(output_path)
    print(f"Output SHA256: {output_checksum}")
    
    # Generate checksum report
    report_path = '/mnt/user-data/outputs/CHECKSUMS.txt'
    with open(report_path, 'w', encoding='utf-8') as report:
        report.write("TSV Standardization - Fixity Report\n")
        report.write("=" * 50 + "\n\n")
        report.write(f"Source file: met_inventory.tsv\n")
        report.write(f"Source SHA256: {source_checksum}\n\n")
        report.write(f"Output file: met_inventory_standardized.tsv\n")
        report.write(f"Output SHA256: {output_checksum}\n\n")
        report.write("Standardization operations performed:\n")
        report.write("1. Consistent tab delimiters\n")
        report.write("2. Removed trailing whitespace from all fields\n")
        report.write("3. Normalized empty cells\n")
        report.write("4. UTF-8 encoding\n")
        report.write("5. Unix line endings (LF)\n")
    
    print(f"\n✓ Checksum report saved: {report_path}")
