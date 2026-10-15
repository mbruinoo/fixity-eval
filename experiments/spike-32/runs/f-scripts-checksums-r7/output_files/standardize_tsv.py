#!/usr/bin/env python3
"""
Standardize Metropolitan Museum inventory TSV file.
Preserves data integrity with MD5 checksums.
"""

import csv
import hashlib
import sys
from pathlib import Path
from datetime import datetime

def calculate_checksum(file_path):
    """Calculate MD5 checksum of a file."""
    md5_hash = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()

def standardize_tsv(input_file, output_file):
    """
    Standardize the TSV file:
    - Remove extra whitespace
    - Normalize empty fields
    - Ensure consistent formatting
    - Preserve all data integrity
    """
    
    rows_read = 0
    rows_written = 0
    issues_found = []
    
    # Read the input file
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        rows = list(reader)
    
    rows_read = len(rows)
    
    # Process rows
    standardized_rows = []
    
    for idx, row in enumerate(rows, 1):
        # Ensure we have 4 columns (pad with empty strings if needed)
        while len(row) < 4:
            row.append('')
        
        # Trim to 4 columns if more
        if len(row) > 4:
            issues_found.append(f"Row {idx}: Had {len(row)} columns, trimmed to 4")
            row = row[:4]
        
        # Clean whitespace from each field (strip but preserve internal spaces)
        cleaned_row = [field.strip() for field in row]
        
        # Check for issues
        if idx == 1:  # Header row
            if cleaned_row != ['Object Date', 'Title', 'Object Number', 'Link Resource']:
                issues_found.append(f"Row {idx}: Header row mismatch")
        else:
            # Validate Object Number is not empty
            if not cleaned_row[2]:
                issues_found.append(f"Row {idx}: Missing Object Number")
            # Validate Link Resource is not empty
            if not cleaned_row[3]:
                issues_found.append(f"Row {idx}: Missing Link Resource")
        
        standardized_rows.append(cleaned_row)
        rows_written += 1
    
    # Write standardized output
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t', lineterminator='\n')
        writer.writerows(standardized_rows)
    
    return rows_read, rows_written, issues_found

def main():
    input_file = 'met_inventory.tsv'
    output_file = 'met_inventory_standardized.tsv'
    checksum_file = 'met_inventory_checksums.txt'
    
    # Check if input file exists
    if not Path(input_file).exists():
        print(f"Error: {input_file} not found")
        sys.exit(1)
    
    print("=" * 70)
    print("METROPOLITAN MUSEUM INVENTORY TSV STANDARDIZATION")
    print("=" * 70)
    print()
    
    # Calculate source checksum
    print(f"Reading source file: {input_file}")
    source_checksum = calculate_checksum(input_file)
    source_size = Path(input_file).stat().st_size
    print(f"  File size: {source_size:,} bytes")
    print(f"  MD5 checksum: {source_checksum}")
    print()
    
    # Standardize the file
    print("Standardizing file...")
    rows_read, rows_written, issues = standardize_tsv(input_file, output_file)
    print(f"  Rows processed: {rows_read}")
    print(f"  Rows written: {rows_written}")
    print()
    
    # Calculate output checksum
    print(f"Writing standardized file: {output_file}")
    output_checksum = calculate_checksum(output_file)
    output_size = Path(output_file).stat().st_size
    print(f"  File size: {output_size:,} bytes")
    print(f"  MD5 checksum: {output_checksum}")
    print()
    
    # Report issues found
    if issues:
        print("Issues found during standardization:")
        for issue in issues:
            print(f"  - {issue}")
        print()
    else:
        print("No issues found during standardization.")
        print()
    
    # Write checksum file
    with open(checksum_file, 'w') as f:
        f.write("METROPOLITAN MUSEUM INVENTORY TSV STANDARDIZATION\n")
        f.write("=" * 70 + "\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write("\n")
        f.write("SOURCE FILE\n")
        f.write("-" * 70 + "\n")
        f.write(f"Filename: {input_file}\n")
        f.write(f"File size: {source_size:,} bytes\n")
        f.write(f"MD5 checksum: {source_checksum}\n")
        f.write("\n")
        f.write("OUTPUT FILE\n")
        f.write("-" * 70 + "\n")
        f.write(f"Filename: {output_file}\n")
        f.write(f"File size: {output_size:,} bytes\n")
        f.write(f"MD5 checksum: {output_checksum}\n")
        f.write("\n")
        f.write("PROCESSING SUMMARY\n")
        f.write("-" * 70 + "\n")
        f.write(f"Rows read: {rows_read}\n")
        f.write(f"Rows written: {rows_written}\n")
        f.write(f"Issues found: {len(issues)}\n")
        if issues:
            f.write("\nIssues:\n")
            for issue in issues:
                f.write(f"  - {issue}\n")
    
    print(f"Checksum file written: {checksum_file}")
    print()
    print("=" * 70)
    print("STANDARDIZATION COMPLETE")
    print("=" * 70)

if __name__ == '__main__':
    main()
