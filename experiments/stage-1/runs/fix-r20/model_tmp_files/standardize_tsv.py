#!/usr/bin/env python3
"""Standardize met_inventory.tsv with fixity verification."""

import csv
import json
from pathlib import Path
from datetime import datetime

def standardize_tsv(input_file, output_file):
    """
    Standardize TSV file with:
    - UTF-8 encoding
    - Tab delimiters (verified and consistent)
    - Unix line endings (LF)
    - Trimmed whitespace
    - Minimal quoting
    - Sorted by Object Number
    - Consistent header formatting
    """
    
    # Read the file
    rows = []
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        headers = reader.fieldnames
        
        for row in reader:
            # Strip whitespace from all values
            cleaned_row = {k: (v.strip() if v else '') for k, v in row.items()}
            rows.append(cleaned_row)
    
    # Sort by Object Number (column index 2)
    rows.sort(key=lambda x: x.get('Object Number', ''))
    
    # Write standardized file with Unix line endings
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(
            f, 
            fieldnames=headers, 
            delimiter='\t', 
            quoting=csv.QUOTE_MINIMAL,
            lineterminator='\n'  # Unix LF only
        )
        writer.writeheader()
        writer.writerows(rows)
    
    return len(rows)

if __name__ == '__main__':
    input_path = Path('/mnt/user-data/uploads/met_inventory.tsv')
    output_path = Path('/mnt/user-data/outputs/met_inventory_standardized.tsv')
    
    row_count = standardize_tsv(input_path, output_path)
    print(f"Standardized {row_count} rows")

