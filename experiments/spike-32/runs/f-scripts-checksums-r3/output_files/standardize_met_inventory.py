#!/usr/bin/env python3
"""
Standardize Met Museum inventory TSV file with fixity preservation.
Handles:
- Consistent column naming and ordering
- Proper TSV formatting with escaped characters
- UTF-8 encoding
- Checksum generation for source and output files
"""

import csv
import hashlib
import sys
from pathlib import Path
from datetime import datetime

def calculate_sha256(file_path):
    """Calculate SHA256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def standardize_tsv(input_file, output_file, checksum_file):
    """
    Standardize TSV file with proper formatting.
    
    Standardization includes:
    - Consistent column headers
    - Proper delimiter handling
    - Normalized whitespace
    - UTF-8 encoding
    - Escaped special characters
    """
    
    # Read the source file
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    source_checksum = calculate_sha256(input_file)
    
    # Parse TSV with proper handling of quoted fields
    reader = csv.DictReader(content.splitlines(), delimiter='\t')
    
    # Normalize column names
    fieldnames = ['Object Date', 'Title', 'Object Number', 'Link Resource']
    
    rows = []
    for row in reader:
        standardized_row = {
            'Object Date': row.get('Object Date', '').strip(),
            'Title': row.get('Title', '').strip(),
            'Object Number': row.get('Object Number', '').strip(),
            'Link Resource': row.get('Link Resource', '').strip()
        }
        rows.append(standardized_row)
    
    # Write standardized TSV
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t', 
                               lineterminator='\n', quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(rows)
    
    output_checksum = calculate_sha256(output_file)
    
    # Write checksum report
    with open(checksum_file, 'w', encoding='utf-8') as f:
        f.write("FIXITY PRESERVATION REPORT\n")
        f.write("=" * 60 + "\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n\n")
        
        f.write("SOURCE FILE\n")
        f.write("-" * 60 + "\n")
        f.write(f"File: {input_file}\n")
        f.write(f"Size: {Path(input_file).stat().st_size} bytes\n")
        f.write(f"SHA256: {source_checksum}\n\n")
        
        f.write("OUTPUT FILE\n")
        f.write("-" * 60 + "\n")
        f.write(f"File: {output_file}\n")
        f.write(f"Size: {Path(output_file).stat().st_size} bytes\n")
        f.write(f"SHA256: {output_checksum}\n\n")
        
        f.write("STANDARDIZATION APPLIED\n")
        f.write("-" * 60 + "\n")
        f.write(f"Total records processed: {len(rows)}\n")
        f.write(f"Encoding: UTF-8\n")
        f.write(f"Delimiter: Tab (\\t)\n")
        f.write(f"Line terminator: LF (\\n)\n")
        f.write(f"Quoting: Minimal (as needed)\n")
        f.write(f"Field order: Object Date | Title | Object Number | Link Resource\n")
        f.write(f"Whitespace: Trimmed\n")

    return source_checksum, output_checksum, len(rows)

if __name__ == "__main__":
    input_path = Path("met_inventory.tsv")
    output_path = Path("met_inventory_standardized.tsv")
    checksum_path = Path("met_inventory_fixity.txt")
    
    if not input_path.exists():
        print(f"Error: {input_path} not found")
        sys.exit(1)
    
    print(f"Standardizing {input_path}...")
    source_sum, output_sum, record_count = standardize_tsv(input_path, output_path, checksum_path)
    
    print(f"\nSuccess!")
    print(f"Records processed: {record_count}")
    print(f"Source checksum (SHA256): {source_sum}")
    print(f"Output checksum (SHA256): {output_sum}")
    print(f"\nFiles created:")
    print(f"  - {output_path}")
    print(f"  - {checksum_path}")
