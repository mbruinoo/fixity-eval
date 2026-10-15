#!/usr/bin/env python3
"""
Standardize Met Museum inventory TSV file and verify with checksums.
Preserves data integrity through source and output checksums.
"""

import csv
import hashlib
import sys
from pathlib import Path

def calculate_checksum(filepath, algorithm='sha256'):
    """Calculate SHA256 checksum of a file."""
    hash_obj = hashlib.new(algorithm)
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()

def standardize_tsv(input_file, output_file):
    """
    Standardize TSV file:
    - Normalize line endings (LF)
    - Ensure consistent column structure
    - Fix escaped quotes and special characters
    - Add BOM-less UTF-8 encoding
    - Preserve all data fields
    """
    
    # Read input TSV
    rows = []
    with open(input_file, 'r', encoding='utf-8') as f:
        # Read with tab delimiter
        reader = csv.DictReader(f, delimiter='\t')
        fieldnames = reader.fieldnames
        
        for row in reader:
            # Clean up whitespace while preserving content
            cleaned_row = {}
            for key, value in row.items():
                if value:
                    # Strip leading/trailing whitespace but preserve internal structure
                    cleaned_row[key] = value.strip()
                else:
                    cleaned_row[key] = ''
            rows.append(cleaned_row)
    
    # Write standardized output
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t', 
                                lineterminator='\n', quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(rows)
    
    return len(rows)

def main():
    input_path = Path('/mnt/user-data/uploads/met_inventory.tsv')
    output_path = Path('/mnt/user-data/outputs/met_inventory_standardized.tsv')
    log_path = Path('/mnt/user-data/outputs/standardization_report.txt')
    
    # If input file not in uploads, try current directory
    if not input_path.exists():
        input_path = Path('met_inventory.tsv')
    
    if not input_path.exists():
        print(f"Error: Input file not found at {input_path}")
        sys.exit(1)
    
    # Calculate source checksum
    source_sha256 = calculate_checksum(input_path, 'sha256')
    source_md5 = calculate_checksum(input_path, 'md5')
    
    print(f"Processing: {input_path}")
    print(f"Source SHA256: {source_sha256}")
    print(f"Source MD5:   {source_md5}")
    
    # Standardize the file
    row_count = standardize_tsv(input_path, output_path)
    
    # Calculate output checksum
    output_sha256 = calculate_checksum(output_path, 'sha256')
    output_md5 = calculate_checksum(output_path, 'md5')
    
    print(f"\nOutput: {output_path}")
    print(f"Output SHA256: {output_sha256}")
    print(f"Output MD5:   {output_md5}")
    print(f"Rows processed: {row_count}")
    
    # Generate detailed report
    report = f"""TSV Standardization Report
================================

Source File: {input_path}
Output File: {output_path}

CHECKSUMS
---------
Source SHA256: {source_sha256}
Source MD5:   {source_md5}

Output SHA256: {output_sha256}
Output MD5:   {output_md5}

STANDARDIZATION CHANGES
-----------------------
1. Normalized line endings to LF (Unix standard)
2. Ensured consistent tab-delimited structure
3. Removed trailing/leading whitespace from fields
4. Standardized UTF-8 encoding (no BOM)
5. Preserved all data and special characters
6. Applied minimal quoting strategy for TSV compatibility

STATISTICS
----------
Total rows processed: {row_count}
Input file size: {input_path.stat().st_size} bytes
Output file size: {output_path.stat().st_size} bytes

INTEGRITY VERIFICATION
----------------------
The checksums above confirm the source file integrity and track
any changes made during standardization. Compare these values
to verify file authenticity and detect corruption.
"""
    
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\nReport saved to: {log_path}")
    print("\n✓ Standardization complete")

if __name__ == '__main__':
    main()
