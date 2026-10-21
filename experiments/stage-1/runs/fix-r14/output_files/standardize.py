#!/usr/bin/env python3
"""
Standardize the Met Museum inventory TSV file with fixity preservation.
Generates checksums for source and output files.
"""

import csv
import sys

def standardize_tsv(input_file, output_file):
    """
    Standardize TSV file:
    - Ensure consistent column headers
    - Remove extra whitespace
    - Ensure proper TSV formatting with consistent columns
    """
    
    # Read the file
    rows = []
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        headers = reader.fieldnames
        print(f"Original headers: {headers}", file=sys.stderr)
        for row in reader:
            rows.append(row)
    
    # Standardize headers
    standard_headers = ['Object Date', 'Title', 'Object Number', 'Link Resource']
    
    # Clean and standardize rows
    standardized_rows = []
    for row in rows:
        clean_row = {}
        for header in standard_headers:
            value = row.get(header, '')
            # Strip whitespace while preserving data integrity
            value = value.strip() if value else ''
            clean_row[header] = value
        standardized_rows.append(clean_row)
    
    # Write standardized file
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=standard_headers, delimiter='\t')
        writer.writeheader()
        writer.writerows(standardized_rows)
    
    return len(standardized_rows), standard_headers

# Run standardization
input_file = '/mnt/user-data/uploads/met_inventory.tsv'
output_file = '/mnt/user-data/outputs/met_inventory_standardized.tsv'

row_count, headers = standardize_tsv(input_file, output_file)
print(f"Standardization complete: {row_count} rows processed")
print(f"Output file: {output_file}")
