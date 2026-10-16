#!/usr/bin/env python3
"""
Standardize MET Museum inventory TSV file with fixity verification.
Creates checksums for source and output files to ensure data integrity.
"""

import sys
import csv
import hashlib
from pathlib import Path
from datetime import datetime

def calculate_checksum(filepath, algorithm='sha256'):
    """Calculate checksum of a file."""
    hash_obj = hashlib.new(algorithm)
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()

def standardize_tsv(input_file, output_file):
    """
    Standardize TSV file:
    - Consistent column names (snake_case)
    - Consistent delimiter (tab)
    - Proper escaping and quoting
    - Consistent line endings (LF)
    - UTF-8 encoding
    """
    
    # Read the input file
    rows = []
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        fieldnames = reader.fieldnames
        
        # Standardize field names to snake_case
        standard_fieldnames = []
        for field in fieldnames:
            if field:
                standard_field = field.lower().strip().replace(' ', '_').replace('-', '_')
                standard_fieldnames.append(standard_field)
        
        for row in reader:
            # Create new row with standardized field names
            standard_row = {}
            for old_field, new_field in zip(fieldnames, standard_fieldnames):
                value = row.get(old_field, '')
                # Strip whitespace from values
                standard_row[new_field] = value.strip() if value else ''
            rows.append(standard_row)
    
    # Write standardized output
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(
            f, 
            fieldnames=standard_fieldnames,
            delimiter='\t',
            lineterminator='\n',
            quoting=csv.QUOTE_MINIMAL
        )
        writer.writeheader()
        writer.writerows(rows)

def main():
    if len(sys.argv) < 2:
        print("Usage: python standardize_tsv.py <input_file> [output_file]")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else input_file.parent / f"{input_file.stem}_standardized.tsv"
    
    # Verify input file exists
    if not input_file.exists():
        print(f"Error: Input file '{input_file}' not found", file=sys.stderr)
        sys.exit(1)
    
    print("=" * 80)
    print("MET Museum TSV Standardization with Fixity Verification")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Calculate source checksum
    print(f"Source file: {input_file}")
    source_checksum = calculate_checksum(input_file)
    source_size = input_file.stat().st_size
    print(f"  Size: {source_size:,} bytes")
    print(f"  SHA256: {source_checksum}")
    print()
    
    # Standardize the file
    print("Standardizing file...")
    standardize_tsv(input_file, output_file)
    print(f"✓ Output file created: {output_file}")
    print()
    
    # Calculate output checksum
    output_checksum = calculate_checksum(output_file)
    output_size = output_file.stat().st_size
    print(f"Output file: {output_file}")
    print(f"  Size: {output_size:,} bytes")
    print(f"  SHA256: {output_checksum}")
    print()
    
    # Create fixity report
    report_file = output_file.parent / f"{output_file.stem}_fixity.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("FIXITY VERIFICATION REPORT\n")
        f.write("=" * 80 + "\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write("\n")
        f.write("SOURCE FILE:\n")
        f.write(f"  Path: {input_file}\n")
        f.write(f"  Size: {source_size:,} bytes\n")
        f.write(f"  SHA256: {source_checksum}\n")
        f.write("\n")
        f.write("OUTPUT FILE:\n")
        f.write(f"  Path: {output_file}\n")
        f.write(f"  Size: {output_size:,} bytes\n")
        f.write(f"  SHA256: {output_checksum}\n")
        f.write("\n")
        f.write("STANDARDIZATION APPLIED:\n")
        f.write("  ✓ Column names converted to snake_case\n")
        f.write("  ✓ Consistent tab delimiter\n")
        f.write("  ✓ Minimal quoting applied\n")
        f.write("  ✓ Line endings normalized to LF\n")
        f.write("  ✓ UTF-8 encoding applied\n")
        f.write("  ✓ Whitespace trimmed from values\n")
        f.write("\n")
    
    print(f"✓ Fixity report created: {report_file}")
    print()
    print("=" * 80)
    print("Standardization complete!")
    print("=" * 80)

if __name__ == '__main__':
    main()
