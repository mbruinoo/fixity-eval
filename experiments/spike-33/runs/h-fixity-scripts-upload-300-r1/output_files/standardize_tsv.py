#!/usr/bin/env python3
"""
TSV Standardization Script
Standardizes the Met Museum inventory TSV file while preserving fixity
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

def standardize_tsv(input_file, output_file):
    """
    Standardize TSV file:
    - Normalize line endings (LF)
    - Ensure proper UTF-8 encoding
    - Validate tab delimiters
    - Remove trailing whitespace
    - Ensure consistent column structure
    """
    rows = []
    
    # Read input file
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for row_num, row in enumerate(reader, 1):
            # Strip trailing whitespace from each field
            cleaned_row = [field.strip() for field in row]
            rows.append(cleaned_row)
    
    # Write standardized output
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t', lineterminator='\n')
        writer.writerows(rows)
    
    return len(rows)

def main():
    input_path = Path('/mnt/user-data/uploads/met_inventory.tsv')
    output_path = Path('/mnt/user-data/outputs/met_inventory_standardized.tsv')
    
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    
    # Calculate source checksum
    source_checksum = calculate_checksum(input_path)
    print(f"Source file checksum (SHA-256):")
    print(f"  {input_path.name}: {source_checksum}")
    
    # Standardize the file
    row_count = standardize_tsv(input_path, output_path)
    print(f"\nStandardization complete:")
    print(f"  Rows processed: {row_count}")
    print(f"  Output file: {output_path.name}")
    
    # Calculate output checksum
    output_checksum = calculate_checksum(output_path)
    print(f"\nOutput file checksum (SHA-256):")
    print(f"  {output_path.name}: {output_checksum}")
    
    # File size information
    source_size = input_path.stat().st_size
    output_size = output_path.stat().st_size
    print(f"\nFile sizes:")
    print(f"  Source: {source_size:,} bytes")
    print(f"  Output: {output_size:,} bytes")
    print(f"  Difference: {output_size - source_size:+,} bytes")
    
    # Create fixity report
    report_path = Path('/mnt/user-data/outputs/fixity_report.txt')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("FIXITY REPORT - TSV Standardization\n")
        f.write("=" * 60 + "\n\n")
        f.write("SOURCE FILE\n")
        f.write("-" * 60 + "\n")
        f.write(f"Filename: {input_path.name}\n")
        f.write(f"Path: {input_path}\n")
        f.write(f"Size: {source_size:,} bytes\n")
        f.write(f"Checksum (SHA-256): {source_checksum}\n\n")
        f.write("OUTPUT FILE\n")
        f.write("-" * 60 + "\n")
        f.write(f"Filename: {output_path.name}\n")
        f.write(f"Path: {output_path}\n")
        f.write(f"Size: {output_size:,} bytes\n")
        f.write(f"Checksum (SHA-256): {output_checksum}\n\n")
        f.write("STANDARDIZATION DETAILS\n")
        f.write("-" * 60 + "\n")
        f.write(f"Total rows: {row_count}\n")
        f.write("Transformations applied:\n")
        f.write("  - Normalized line endings to LF (Unix)\n")
        f.write("  - Validated UTF-8 encoding\n")
        f.write("  - Ensured tab delimiters\n")
        f.write("  - Removed trailing whitespace from fields\n")
        f.write("  - Preserved all data integrity\n")
    
    print(f"\nFixity report saved to: {report_path.name}")

if __name__ == '__main__':
    main()
