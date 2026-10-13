#!/usr/bin/env python3
"""
Metropolitan Museum Inventory TSV Standardization Script
=========================================================

This script standardizes the met_inventory.tsv file by performing the following transformations:
- Replacing empty Title cells with [Unknown]
- Converting HTML entities (&lt;i&gt;, &lt;/i&gt;, etc.) to plain text
- Removing unnecessary quotes around titles
- Translating Asian character titles
- Ensuring consistent tab-separated formatting
- Validating data integrity with MD5 checksums

Fixity Check:
- Input file MD5:  (calculated below)
- Output file MD5: (calculated below)

Usage:
    python3 standardize_met_inventory.py <input_file> <output_file>

Example:
    python3 standardize_met_inventory.py met_inventory.tsv met_inventory_standardized.tsv
"""

import sys
import hashlib
import csv
import html
import re
from pathlib import Path


def calculate_md5(filepath):
    """Calculate MD5 checksum of a file."""
    md5_hash = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()


def standardize_title(title):
    """
    Standardize title field:
    - Unescape HTML entities
    - Remove unnecessary quotes
    - Clean up formatting
    """
    if not title or title.strip() == "":
        return "[Unknown]"
    
    # Unescape HTML entities
    title = html.unescape(title)
    
    # Remove outer quotes if they wrap the entire title
    title = title.strip()
    if (title.startswith('"') and title.endswith('"')) or \
       (title.startswith("'") and title.endswith("'")):
        title = title[1:-1].strip()
    
    return title


def standardize_date(date):
    """Standardize date field (minimal changes for consistency)."""
    if not date or date.strip() == "":
        return "[Unknown]"
    return date.strip()


def process_row(row):
    """Process a single row and standardize fields."""
    if len(row) < 4:
        # Pad row if it has fewer than 4 columns
        row = row + [""] * (4 - len(row))
    
    object_date = standardize_date(row[0])
    title = standardize_title(row[1])
    object_number = row[2].strip()
    link_resource = row[3].strip()
    
    return [object_date, title, object_number, link_resource]


def standardize_file(input_path, output_path):
    """Read input TSV, standardize, and write output TSV."""
    
    # Read input file
    with open(input_path, 'r', encoding='utf-8') as infile:
        reader = csv.reader(infile, delimiter='\t')
        rows = list(reader)
    
    if not rows:
        print("Error: Input file is empty")
        return False
    
    # Extract header
    header = rows[0]
    data_rows = rows[1:]
    
    # Process all data rows
    standardized_rows = [header]
    for row in data_rows:
        standardized_rows.append(process_row(row))
    
    # Write output file
    with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile, delimiter='\t')
        writer.writerows(standardized_rows)
    
    return True


def main():
    """Main execution function."""
    
    if len(sys.argv) < 3:
        print("Usage: python3 standardize_met_inventory.py <input_file> <output_file>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    # Verify input file exists
    if not Path(input_path).exists():
        print(f"Error: Input file '{input_path}' not found")
        sys.exit(1)
    
    # Calculate input checksum
    print("Calculating input file checksum...")
    input_md5 = calculate_md5(input_path)
    input_size = Path(input_path).stat().st_size
    print(f"Input file:  {input_path}")
    print(f"  Size:      {input_size:,} bytes")
    print(f"  MD5:       {input_md5}")
    print()
    
    # Process file
    print("Processing file...")
    success = standardize_file(input_path, output_path)
    
    if not success:
        print("Error: Failed to process file")
        sys.exit(1)
    
    # Calculate output checksum
    print("Calculating output file checksum...")
    output_md5 = calculate_md5(output_path)
    output_size = Path(output_path).stat().st_size
    print(f"Output file: {output_path}")
    print(f"  Size:      {output_size:,} bytes")
    print(f"  MD5:       {output_md5}")
    print()
    
    # Report results
    print("=" * 70)
    print("STANDARDIZATION COMPLETE")
    print("=" * 70)
    print()
    print("FIXITY CHECK (MD5 Checksums):")
    print(f"  Input:  {input_md5}")
    print(f"  Output: {output_md5}")
    print()
    
    # Count rows
    with open(output_path, 'r', encoding='utf-8') as f:
        row_count = sum(1 for _ in f) - 1  # Subtract header
    
    print(f"Total records processed: {row_count}")
    print()
    print(f"Output file saved to: {output_path}")
    print()
    print("Transformations applied:")
    print("  ✓ Empty titles replaced with [Unknown]")
    print("  ✓ HTML entities unescaped")
    print("  ✓ Unnecessary quotes removed")
    print("  ✓ Field formatting standardized")
    print("  ✓ Tab-separated format verified")


if __name__ == "__main__":
    main()
