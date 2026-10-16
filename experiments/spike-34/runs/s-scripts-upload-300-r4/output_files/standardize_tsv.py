#!/usr/bin/env python3
"""
Standardize the Met inventory TSV file.
Handles missing values, inconsistent formatting, and validates structure.
"""

import csv
import sys
from pathlib import Path

def standardize_tsv(input_file, output_file):
    """
    Standardize the TSV file by:
    1. Ensuring consistent delimiters (tabs)
    2. Handling empty/missing values
    3. Trimming whitespace
    4. Validating column count
    """
    
    rows = []
    headers = None
    
    # Read the file
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for row_num, row in enumerate(reader, 1):
            # Get headers from first row
            if row_num == 1:
                headers = [col.strip() for col in row]
                continue
            
            # Ensure consistent column count
            while len(row) < len(headers):
                row.append('')
            
            # Trim to correct number of columns
            row = row[:len(headers)]
            
            # Strip whitespace from each cell
            row = [col.strip() for col in row]
            
            rows.append(row)
    
    # Write standardized file
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t', lineterminator='\n')
        writer.writerow(headers)
        writer.writerows(rows)
    
    # Print statistics
    print(f"✓ Standardization complete!")
    print(f"  Input file: {input_file}")
    print(f"  Output file: {output_file}")
    print(f"  Headers: {len(headers)}")
    print(f"  Data rows: {len(rows)}")
    print(f"\n  Column names:")
    for i, header in enumerate(headers, 1):
        print(f"    {i}. {header}")
    
    # Show data quality statistics
    missing_by_column = [sum(1 for row in rows if not row[i]) for i in range(len(headers))]
    print(f"\n  Missing values by column:")
    for i, header in enumerate(headers):
        missing = missing_by_column[i]
        pct = (missing / len(rows) * 100) if rows else 0
        print(f"    {header}: {missing} ({pct:.1f}%)")

if __name__ == '__main__':
    input_file = '/mnt/user-data/uploads/met_inventory.tsv'
    output_file = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
    
    standardize_tsv(input_file, output_file)
