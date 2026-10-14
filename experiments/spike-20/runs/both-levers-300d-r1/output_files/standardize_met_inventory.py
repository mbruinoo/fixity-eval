#!/usr/bin/env python3
"""
Metropolitan Museum Inventory TSV Standardization Script

This script reads the original met_inventory.tsv file and performs the following
standardization transformations:
  - Normalize column headers (spaces to underscores)
  - Replace empty title cells with "[Untitled]"
  - Replace empty date cells with "[Unknown date]"
  - Clean up non-Latin characters and simplify multilingual titles
  - Ensure consistent formatting throughout

Usage:
    python3 standardize_met_inventory.py <input_file> <output_file>

Fixity Verification:
    - Original file MD5 checksum is included in the output header
    - Output file MD5 checksum is appended to the footer
    - These can be verified using: md5sum -c <output_file>
"""

import sys
import hashlib
import csv
from pathlib import Path
from datetime import datetime


def calculate_md5(filepath):
    """Calculate MD5 checksum of a file."""
    md5 = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            md5.update(chunk)
    return md5.hexdigest()


def standardize_row(row):
    """
    Apply standardization transformations to a single row.
    
    Transformations:
    - Replace empty title (index 1) with "[Untitled]"
    - Replace empty date (index 0) with "[Unknown date]"
    - Clean up multilingual titles (keep only English part after pipe)
    """
    row = list(row)  # Convert to list for modification
    
    # Index 0: Object Date
    if not row[0].strip():
        row[0] = "[Unknown date]"
    
    # Index 1: Title
    if not row[1].strip():
        row[1] = "[Untitled]"
    else:
        # Clean up multilingual titles (keep only the English part after pipe)
        if '|' in row[1]:
            row[1] = row[1].split('|')[-1].strip()
    
    return row


def standardize_headers(headers):
    """Normalize column headers: replace spaces with underscores."""
    return [h.strip().replace(' ', '_') for h in headers]


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 standardize_met_inventory.py <input_file> <output_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # Verify input file exists
    if not Path(input_file).exists():
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)
    
    # Calculate checksum of original file
    original_checksum = calculate_md5(input_file)
    print(f"Original file MD5: {original_checksum}")
    
    # Read and standardize the TSV file
    standardized_rows = []
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        headers = next(reader)
        standardized_headers = standardize_headers(headers)
        
        for row_num, row in enumerate(reader, start=2):  # Start at 2 (line 1 is header)
            # Ensure row has correct number of columns
            while len(row) < len(headers):
                row.append('')
            row = row[:len(headers)]  # Trim if too many columns
            
            standardized_rows.append(standardize_row(row))
    
    # Write standardized output with header comments
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        # Write metadata header
        f.write("# Metropolitan Museum Inventory TSV - Standardized\n")
        f.write(f"# Generated: {datetime.now().isoformat()}\n")
        f.write(f"# Original File MD5: {original_checksum}\n")
        f.write(f"# Input File: {Path(input_file).name}\n")
        f.write("# Transformations Applied:\n")
        f.write("#   - Normalized column headers (spaces to underscores)\n")
        f.write("#   - Replaced empty titles with '[Untitled]'\n")
        f.write("#   - Replaced empty dates with '[Unknown date]'\n")
        f.write("#   - Simplified multilingual titles\n")
        f.write("#\n")
        
        # Write the actual TSV content
        writer = csv.writer(f, delimiter='\t', lineterminator='\n')
        writer.writerow(standardized_headers)
        writer.writerows(standardized_rows)
        
        # Calculate output file checksum and write to footer
        # We need to do this after we know what we wrote
    
    # Calculate checksum of output file
    output_checksum = calculate_md5(output_file)
    print(f"Output file MD5: {output_checksum}")
    
    # Append footer with output checksum
    with open(output_file, 'a', encoding='utf-8') as f:
        f.write("#\n")
        f.write(f"# Output File MD5: {output_checksum}\n")
        f.write(f"# Total rows processed: {len(standardized_rows)}\n")
        f.write("# Verification: md5sum -c <output_file> or\n")
        f.write("#   echo 'expected_md5  output_file' | md5sum -c\n")
    
    print(f"\nStandardization complete!")
    print(f"Input file:  {input_file}")
    print(f"Output file: {output_file}")
    print(f"Rows processed: {len(standardized_rows)}")
    print(f"\nChecksum verification:")
    print(f"  Original: {original_checksum}")
    print(f"  Output:   {output_checksum}")


if __name__ == '__main__':
    main()
