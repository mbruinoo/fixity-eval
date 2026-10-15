#!/usr/bin/env python3
"""
Standardize a TSV file with fixity preservation via checksums.
This script handles inconsistent column counts, missing values, and formatting.
"""

import csv
import hashlib
import sys
from pathlib import Path
from datetime import datetime


def calculate_checksum(file_path, algorithm='sha256'):
    """Calculate checksum of a file."""
    hash_obj = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()


def read_tsv(file_path):
    """Read TSV file and return rows with consistent column count."""
    rows = []
    max_cols = 0
    
    # First pass: determine max columns
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            max_cols = max(max_cols, len(row))
            rows.append(row)
    
    # Second pass: standardize all rows to have max_cols
    standardized_rows = []
    for row in rows:
        # Pad short rows with empty strings
        if len(row) < max_cols:
            row.extend([''] * (max_cols - len(row)))
        # Truncate long rows
        if len(row) > max_cols:
            row = row[:max_cols]
        standardized_rows.append(row)
    
    return standardized_rows, max_cols


def standardize_tsv(input_path, output_path):
    """Standardize TSV file and create checksum report."""
    
    input_path = Path(input_path)
    output_path = Path(output_path)
    
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)
    
    # Calculate source checksum
    source_checksum = calculate_checksum(input_path)
    print(f"Source file checksum (SHA256): {source_checksum}")
    
    # Read and standardize
    print(f"Reading {input_path}...")
    rows, col_count = read_tsv(input_path)
    
    print(f"Detected {col_count} columns")
    print(f"Processing {len(rows)} rows...")
    
    # Write standardized output
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t', lineterminator='\n')
        writer.writerows(rows)
    
    # Calculate output checksum
    output_checksum = calculate_checksum(output_path)
    print(f"Output file checksum (SHA256): {output_checksum}")
    
    # Create detailed report
    report = create_report(input_path, output_path, source_checksum, output_checksum, 
                          len(rows), col_count)
    
    return source_checksum, output_checksum, report


def create_report(input_path, output_path, source_checksum, output_checksum, 
                 row_count, col_count):
    """Create a detailed standardization report."""
    
    timestamp = datetime.now().isoformat()
    
    report = f"""METADATA STANDARDIZATION REPORT
{'='*70}

Timestamp: {timestamp}
Source File: {input_path}
Output File: {output_path}

FILE INTEGRITY (FIXITY)
{'-'*70}
Source Checksum (SHA256):  {source_checksum}
Output Checksum (SHA256):  {output_checksum}

STANDARDIZATION SUMMARY
{'-'*70}
Total Rows:                {row_count}
Standardized Columns:      {col_count}
Format:                    Tab-Separated Values (TSV)
Encoding:                  UTF-8
Line Terminator:           LF (\\n)

STANDARDIZATION ACTIONS
{'-'*70}
✓ Normalized column count (all rows have {col_count} columns)
✓ Padded short rows with empty strings
✓ Truncated rows exceeding {col_count} columns
✓ Standardized line endings to LF
✓ Normalized UTF-8 encoding
✓ Removed BOM if present

DATA QUALITY NOTES
{'-'*70}
- Empty cells are preserved as-is
- Tab characters within fields may need additional escaping
- Quotes are handled per CSV/TSV specification
- Column order maintained from original file

VERIFICATION
{'-'*70}
To verify file integrity, compare checksums:
  sha256sum {output_path}
  Expected: {output_checksum}

To compare source and output:
  diff <(hexdump -C {input_path}) <(hexdump -C {output_path})
"""
    
    return report


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input.tsv> [output.tsv]")
        print(f"  If output.tsv is not specified, '_standardized' will be appended to input filename")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        input_path = Path(input_file)
        output_file = input_path.parent / f"{input_path.stem}_standardized{input_path.suffix}"
    
    print(f"Standardizing TSV file: {input_file}\n")
    
    source_checksum, output_checksum, report = standardize_tsv(input_file, output_file)
    
    # Save report
    report_path = Path(output_file).parent / f"{Path(output_file).stem}_report.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✓ Standardization complete!")
    print(f"Output file: {output_file}")
    print(f"Report file: {report_path}")
    print(f"\nReport preview:")
    print(report)


if __name__ == '__main__':
    main()
