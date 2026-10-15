#!/usr/bin/env python3
"""
Standardize TSV file with integrity verification via checksums.
Handles the Metropolitan Museum inventory file with proper column alignment.
"""

import csv
import hashlib
import sys
from pathlib import Path

def calculate_checksum(file_path, algorithm='sha256'):
    """Calculate SHA256 checksum of a file."""
    hash_func = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_func.update(chunk)
    return hash_func.hexdigest()

def standardize_tsv(input_file, output_file):
    """
    Standardize TSV file:
    - Ensure consistent tab delimiters
    - Normalize line endings (LF)
    - Remove trailing whitespace
    - Ensure proper column count
    - Validate data integrity
    """
    
    # Read the input file
    rows = []
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        rows = list(reader)
    
    if not rows:
        print("Error: Empty input file")
        sys.exit(1)
    
    # Identify header and expected column count
    header = rows[0]
    expected_cols = len(header)
    
    print(f"Input file: {input_file}")
    print(f"Header columns: {expected_cols}")
    print(f"Header: {header}")
    print(f"Total rows (including header): {len(rows)}")
    
    # Standardize rows
    standardized_rows = [header]  # Keep header as-is
    issues = []
    
    for i, row in enumerate(rows[1:], start=2):  # Start from row 2
        # Strip whitespace from each cell
        cleaned_row = [cell.strip() for cell in row]
        
        # Pad or trim to expected column count
        if len(cleaned_row) < expected_cols:
            cleaned_row.extend([''] * (expected_cols - len(cleaned_row)))
            issues.append(f"Row {i}: Missing columns (had {len(row)}, expected {expected_cols})")
        elif len(cleaned_row) > expected_cols:
            cleaned_row = cleaned_row[:expected_cols]
            issues.append(f"Row {i}: Extra columns (had {len(row)}, expected {expected_cols})")
        
        standardized_rows.append(cleaned_row)
    
    # Write standardized output with explicit LF line endings
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t', lineterminator='\n')
        writer.writerows(standardized_rows)
    
    return issues

def main():
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'met_inventory.tsv'
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'met_inventory_standardized.tsv'
    
    # Check input file exists
    if not Path(input_file).exists():
        print(f"Error: Input file '{input_file}' not found")
        sys.exit(1)
    
    # Calculate source checksum
    print("\n" + "="*70)
    print("STANDARDIZATION PROCESS")
    print("="*70 + "\n")
    
    source_checksum = calculate_checksum(input_file)
    print(f"Source file checksum (SHA256):")
    print(f"  {source_checksum}\n")
    
    # Standardize the file
    issues = standardize_tsv(input_file, output_file)
    
    # Calculate output checksum
    output_checksum = calculate_checksum(output_file)
    print(f"\nStandardized file checksum (SHA256):")
    print(f"  {output_checksum}\n")
    
    # Report issues
    if issues:
        print(f"Issues found during standardization ({len(issues)}):")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("No issues found during standardization.")
    
    # Generate integrity report
    print("\n" + "="*70)
    print("INTEGRITY REPORT")
    print("="*70)
    
    report = f"""
Source File: {input_file}
  Checksum (SHA256): {source_checksum}

Output File: {output_file}
  Checksum (SHA256): {output_checksum}

Status: {'✓ Successfully standardized' if not issues else '⚠ Standardized with corrections'}
"""
    
    print(report)
    
    # Write integrity report to file
    report_file = output_file.replace('.tsv', '_integrity.txt')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("TSV STANDARDIZATION INTEGRITY REPORT\n")
        f.write("="*70 + "\n\n")
        f.write(report)
        if issues:
            f.write("\nDetailed Issues:\n")
            for issue in issues:
                f.write(f"  {issue}\n")
    
    print(f"Integrity report saved to: {report_file}")
    print("\n" + "="*70 + "\n")

if __name__ == '__main__':
    main()
