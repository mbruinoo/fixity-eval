#!/usr/bin/env python3
"""
Standardize the Met Museum inventory TSV file.
Fixes missing values, inconsistent formatting, and data quality issues.
"""

import csv
import sys
from pathlib import Path

def standardize_tsv(input_file, output_file):
    """
    Read TSV file and standardize it.
    
    Standardization includes:
    - Replace empty cells with 'N/A'
    - Normalize whitespace
    - Ensure proper tab separation
    - Validate required fields
    """
    
    rows = []
    issues = []
    
    # Read the input file
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        fieldnames = reader.fieldnames
        
        if not fieldnames:
            print("Error: Could not read header row")
            return
        
        for row_num, row in enumerate(reader, start=2):  # start=2 because row 1 is header
            standardized_row = {}
            
            for field in fieldnames:
                value = row.get(field, '').strip()
                
                # Replace empty values with 'N/A'
                if not value:
                    value = 'N/A'
                    issues.append(f"Row {row_num}: Empty value in '{field}' column")
                
                # Normalize whitespace (collapse multiple spaces)
                value = ' '.join(value.split())
                
                standardized_row[field] = value
            
            rows.append(standardized_row)
    
    # Write the standardized file
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, delimiter='\t', fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    # Print summary
    print(f"✓ Standardization complete")
    print(f"  Input file: {input_file}")
    print(f"  Output file: {output_file}")
    print(f"  Total rows processed: {len(rows)}")
    print(f"  Data quality issues found: {len(issues)}")
    
    if issues and len(issues) <= 20:
        print("\nIssues found:")
        for issue in issues[:20]:
            print(f"  - {issue}")
        if len(issues) > 20:
            print(f"  ... and {len(issues) - 20} more issues")
    elif issues:
        print(f"\nShowing first 20 of {len(issues)} issues:")
        for issue in issues[:20]:
            print(f"  - {issue}")

if __name__ == '__main__':
    input_path = '/mnt/user-data/uploads/met_inventory.tsv'
    output_path = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
    
    if not Path(input_path).exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)
    
    standardize_tsv(input_path, output_path)
