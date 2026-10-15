#!/usr/bin/env python3
"""
Standardize the Met Museum inventory TSV file.

This script:
1. Ensures proper tab-delimited format
2. Removes extra whitespace and inconsistencies
3. Validates data integrity
4. Creates output with consistent formatting
"""

import csv
import sys
from pathlib import Path

def standardize_tsv(input_file, output_file):
    """
    Standardize the TSV file by:
    - Ensuring proper tab delimiters
    - Trimming whitespace from all fields
    - Removing empty lines
    - Maintaining consistent structure
    """
    
    rows_read = 0
    rows_written = 0
    issues_found = []
    
    try:
        # Read the input file
        with open(input_file, 'r', encoding='utf-8') as infile:
            reader = csv.reader(infile, delimiter='\t', quoting=csv.QUOTE_ALL)
            rows = list(reader)
            rows_read = len(rows)
        
        # Standardize the data
        standardized_rows = []
        for i, row in enumerate(rows, 1):
            # Skip completely empty rows
            if not any(row):
                issues_found.append(f"Row {i}: Empty row skipped")
                continue
            
            # Strip whitespace from all fields
            cleaned_row = [field.strip() for field in row]
            
            # Validate column count (should be 4)
            if len(cleaned_row) != 4:
                issues_found.append(f"Row {i}: Expected 4 columns, got {len(cleaned_row)}")
            
            standardized_rows.append(cleaned_row)
            rows_written += 1
        
        # Write the standardized file
        with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.writer(outfile, delimiter='\t', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
            writer.writerows(standardized_rows)
        
        return {
            'success': True,
            'rows_read': rows_read,
            'rows_written': rows_written,
            'issues': issues_found
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

if __name__ == '__main__':
    input_path = '/mnt/user-data/uploads/met_inventory.tsv'
    output_path = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
    
    result = standardize_tsv(input_path, output_path)
    
    print("=" * 70)
    print("TSV STANDARDIZATION REPORT")
    print("=" * 70)
    print(f"Input file:  {input_path}")
    print(f"Output file: {output_path}")
    print(f"\nRows read:    {result.get('rows_read', 'N/A')}")
    print(f"Rows written: {result.get('rows_written', 'N/A')}")
    
    if result.get('issues'):
        print(f"\nIssues found ({len(result['issues'])}):")
        for issue in result['issues'][:10]:  # Show first 10 issues
            print(f"  - {issue}")
        if len(result['issues']) > 10:
            print(f"  ... and {len(result['issues']) - 10} more")
    else:
        print("\nNo issues found!")
    
    print("\n" + "=" * 70)
