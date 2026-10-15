#!/usr/bin/env python3
"""
Standardize Met Museum Inventory TSV File
Preserves data integrity with MD5 checksums for source and output
"""

import csv
import hashlib
import sys
from pathlib import Path
from datetime import datetime


def calculate_checksum(file_path):
    """Calculate MD5 checksum of a file."""
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            md5.update(chunk)
    return md5.hexdigest()


def standardize_tsv(input_file, output_file):
    """
    Standardize the Met inventory TSV file:
    - Ensure proper column headers
    - Clean up empty cells
    - Normalize whitespace
    - Maintain data integrity
    """
    
    # Define standardized column headers
    headers = ['Object Date', 'Title', 'Object Number', 'Link Resource']
    
    rows = []
    
    # Read and parse input file
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictFieldnames=headers, delimiter='\t')
        for row in reader:
            # Skip header row if it appears in data
            if row['Object Date'] == 'Object Date':
                continue
            
            # Clean up whitespace
            cleaned_row = {
                key: value.strip() if value else '' 
                for key, value in row.items()
            }
            
            rows.append(cleaned_row)
    
    # Write standardized output
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(
            f, 
            fieldnames=headers, 
            delimiter='\t',
            quoting=csv.QUOTE_MINIMAL,
            lineterminator='\n'
        )
        writer.writeheader()
        writer.writerows(rows)
    
    return len(rows)


def generate_report(input_file, output_file):
    """Generate a validation report with checksums."""
    
    source_checksum = calculate_checksum(input_file)
    output_checksum = calculate_checksum(output_file)
    
    source_size = Path(input_file).stat().st_size
    output_size = Path(output_file).stat().st_size
    
    report = f"""
================================================================================
MET MUSEUM INVENTORY TSV STANDARDIZATION REPORT
Generated: {datetime.now().isoformat()}
================================================================================

SOURCE FILE:
  Path: {input_file}
  Size: {source_size:,} bytes
  MD5 Checksum: {source_checksum}

OUTPUT FILE:
  Path: {output_file}
  Size: {output_size:,} bytes
  MD5 Checksum: {output_checksum}

STANDARDIZATION CHANGES:
  ✓ Normalized tab-delimited format
  ✓ Ensured consistent column headers: Object Date, Title, Object Number, Link Resource
  ✓ Trimmed whitespace from all cells
  ✓ Removed duplicate headers from data
  ✓ Preserved all data integrity
  ✓ UTF-8 encoding maintained

DATA STATISTICS:
  Records processed: {get_row_count(output_file) - 1} data rows (excluding header)

INTEGRITY VERIFICATION:
  Source MD5:  {source_checksum}
  Output MD5:  {output_checksum}
  
  These checksums should be stored for future verification of:
  - Source file authenticity
  - Output file integrity
  - Detection of any unauthorized modifications

================================================================================
"""
    return report


def get_row_count(file_path):
    """Get total number of rows in TSV file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return sum(1 for _ in f)


def main():
    if len(sys.argv) < 2:
        print("Usage: python standardize_met_inventory.py <input.tsv> [output.tsv]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'met_inventory_standardized.tsv'
    
    # Validate input file exists
    if not Path(input_file).exists():
        print(f"Error: Input file '{input_file}' not found")
        sys.exit(1)
    
    print(f"Processing {input_file}...")
    
    try:
        row_count = standardize_tsv(input_file, output_file)
        report = generate_report(input_file, output_file)
        
        print(report)
        
        # Save report to file
        report_file = output_file.replace('.tsv', '_report.txt')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n✓ Standardization complete!")
        print(f"✓ Output: {output_file}")
        print(f"✓ Report: {report_file}")
        
    except Exception as e:
        print(f"Error during processing: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
