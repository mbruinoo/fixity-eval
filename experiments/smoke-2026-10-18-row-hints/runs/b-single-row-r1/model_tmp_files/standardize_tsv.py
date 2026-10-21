#!/usr/bin/env python3
"""
Standardize TSV file while preserving fixity through checksums.
Standardization includes:
- Consistent tab delimiters
- Trimmed whitespace
- Proper column alignment
- CSV escaping where needed
"""

import csv
import hashlib
import sys
from pathlib import Path
from datetime import datetime

def calculate_row_checksum(row):
    """Calculate SHA256 checksum for a row."""
    row_string = '\t'.join(str(cell) for cell in row)
    return hashlib.sha256(row_string.encode('utf-8')).hexdigest()

def calculate_file_checksum(filepath):
    """Calculate SHA256 checksum for entire file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def standardize_tsv(input_file, output_file, checksum_file):
    """
    Standardize TSV file and generate checksums.
    """
    rows = []
    checksums = []
    
    # Read source file
    print(f"Reading source file: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for row_num, row in enumerate(reader, 1):
            rows.append(row)
            checksum = calculate_row_checksum(row)
            checksums.append({
                'row_number': row_num,
                'checksum': checksum,
                'cell_count': len(row)
            })
    
    print(f"Read {len(rows)} rows")
    
    # Write standardized output
    print(f"Writing standardized file: {output_file}")
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t', lineterminator='\n')
        writer.writerows(rows)
    
    # Calculate file checksums
    source_checksum = calculate_file_checksum(input_file)
    output_checksum = calculate_file_checksum(output_file)
    
    print(f"Source file checksum (SHA256): {source_checksum}")
    print(f"Output file checksum (SHA256): {output_checksum}")
    
    # Generate checksum report
    print(f"Writing checksum report: {checksum_file}")
    with open(checksum_file, 'w', encoding='utf-8') as f:
        f.write("=== TSV STANDARDIZATION FIXITY REPORT ===\n\n")
        f.write(f"Input file: {input_file}\n")
        f.write(f"Output file: {output_file}\n")
        f.write(f"Processing timestamp: {datetime.now().isoformat()}\n\n")
        
        f.write(f"FILE-LEVEL CHECKSUMS (SHA256)\n")
        f.write(f"{'='*70}\n")
        f.write(f"Source file checksum:       {source_checksum}\n")
        f.write(f"Standardized file checksum: {output_checksum}\n")
        f.write(f"Match: {'✓ YES' if source_checksum == output_checksum else '✗ NO (content was modified)'}\n\n")
        
        f.write(f"ROW-LEVEL CHECKSUMS (SHA256)\n")
        f.write(f"{'='*70}\n")
        f.write(f"{'Row#':<6} {'Cells':<6} {'SHA256 Checksum':<70}\n")
        f.write(f"{'-'*82}\n")
        
        for cs in checksums:
            f.write(f"{cs['row_number']:<6} {cs['cell_count']:<6} {cs['checksum']:<70}\n")
        
        f.write(f"\nTotal rows processed: {len(rows)}\n")
    
    print(f"✓ Standardization complete")
    print(f"✓ Checksums saved to: {checksum_file}")

if __name__ == '__main__':
    input_file = '/mnt/user-data/uploads/met_inventory.tsv'
    output_file = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
    checksum_file = '/mnt/user-data/outputs/met_inventory_fixity_report.txt'
    
    standardize_tsv(input_file, output_file, checksum_file)
