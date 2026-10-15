#!/usr/bin/env python3
"""
Standardize TSV file from Met Museum inventory.
Computes checksums for source and output files to preserve fixity.
"""

import hashlib
import sys
from pathlib import Path

def compute_checksum(file_path, algorithm='sha256'):
    """Compute SHA256 checksum of a file."""
    hash_obj = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()

def standardize_tsv(input_path, output_path):
    """
    Standardize TSV file:
    - Ensure consistent tab separation
    - Remove trailing whitespace from lines
    - Ensure proper line endings (LF)
    - Preserve all data including empty cells
    """
    rows = []
    
    with open(input_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            # Remove line ending
            line = line.rstrip('\r\n')
            
            # Split by tabs
            cells = line.split('\t')
            
            # Strip trailing whitespace from each cell but preserve content
            cells = [cell.rstrip() for cell in cells]
            
            rows.append(cells)
    
    # Write standardized output
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        for row in rows:
            f.write('\t'.join(row) + '\n')
    
    return len(rows)

def main():
    input_file = Path('/mnt/user-data/uploads/met_inventory.tsv')
    output_file = Path('/mnt/user-data/outputs/met_inventory_standardized.tsv')
    checksum_file = Path('/mnt/user-data/outputs/checksums.txt')
    
    if not input_file.exists():
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)
    
    # Compute source checksum
    print("Computing checksums...")
    source_sha256 = compute_checksum(input_file, 'sha256')
    source_md5 = compute_checksum(input_file, 'md5')
    
    print(f"Source file: {input_file.name}")
    print(f"  SHA256: {source_sha256}")
    print(f"  MD5:    {source_md5}")
    
    # Standardize the file
    print(f"\nStandardizing TSV file...")
    row_count = standardize_tsv(input_file, output_file)
    print(f"  Rows processed: {row_count}")
    
    # Compute output checksums
    output_sha256 = compute_checksum(output_file, 'sha256')
    output_md5 = compute_checksum(output_file, 'md5')
    
    print(f"\nOutput file: {output_file.name}")
    print(f"  SHA256: {output_sha256}")
    print(f"  MD5:    {output_md5}")
    
    # Write checksum report
    report = f"""Met Museum Inventory TSV Standardization Report
================================================

Source File: met_inventory.tsv
  SHA256: {source_sha256}
  MD5:    {source_md5}
  
Output File: met_inventory_standardized.tsv
  SHA256: {output_sha256}
  MD5:    {output_md5}

Standardization Applied:
  - Consistent tab separation
  - Removed trailing whitespace from cells
  - Normalized line endings (LF)
  - Preserved all data including empty cells
  - Total rows processed: {row_count}
  - Header row: 1
  - Data rows: {row_count - 1}

Validation:
  - Source file readable: ✓
  - Output file created: ✓
  - Checksums computed: ✓
"""
    
    print("\n" + report)
    
    with open(checksum_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"Checksum report written to: {checksum_file.name}")

if __name__ == '__main__':
    main()
