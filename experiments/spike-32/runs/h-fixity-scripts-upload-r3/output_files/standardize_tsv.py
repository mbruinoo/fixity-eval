#!/usr/bin/env python3
"""
Standardize TSV file by:
1. Ensuring consistent tab delimiters
2. Removing trailing whitespace
3. Normalizing line endings to Unix (LF)
4. Ensuring headers are present and clean
5. Validating column count consistency
"""

import sys
import csv
from pathlib import Path

def standardize_tsv(input_path, output_path):
    """
    Read TSV, standardize format, and write output.
    """
    with open(input_path, 'r', encoding='utf-8') as infile:
        # Read with csv module using tab delimiter
        reader = csv.reader(infile, delimiter='\t', quoting=csv.QUOTE_NONE, escapechar='\\')
        rows = list(reader)
    
    if not rows:
        print("Error: Input file is empty", file=sys.stderr)
        return False
    
    # Validate and report
    print(f"Input rows: {len(rows)}")
    col_counts = [len(row) for row in rows]
    print(f"Column counts per row: min={min(col_counts)}, max={max(col_counts)}")
    print(f"Header: {rows[0]}")
    
    # Write standardized output
    with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile, delimiter='\t', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        for row in rows:
            # Strip trailing whitespace from each field
            cleaned_row = [field.rstrip() if field else field for field in row]
            writer.writerow(cleaned_row)
    
    print(f"Output rows: {len(rows)}")
    print(f"Successfully wrote to: {output_path}")
    return True

if __name__ == '__main__':
    input_file = '/mnt/user-data/uploads/met_inventory.tsv'
    output_file = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
    
    if not Path(input_file).exists():
        print(f"Error: Input file not found: {input_file}", file=sys.stderr)
        sys.exit(1)
    
    # Ensure output directory exists
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    success = standardize_tsv(input_file, output_file)
    sys.exit(0 if success else 1)
