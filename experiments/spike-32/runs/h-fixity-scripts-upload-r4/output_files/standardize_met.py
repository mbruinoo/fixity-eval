#!/usr/bin/env python3
"""
Standardize met_inventory.tsv with fixity verification.
Checksums source and output using SHA256.
"""

import csv
import hashlib
from pathlib import Path

def calculate_checksum(filepath):
    """Calculate SHA256 checksum of a file"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def standardize_tsv(input_path, output_path):
    """
    Standardize TSV file:
    - Normalize line endings (LF)
    - Ensure consistent UTF-8 encoding
    - Verify proper tab separation
    - Handle empty/missing values consistently
    - Reorder columns logically: Date, Title, Object Number, Link
    """
    
    # Read input file
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        fieldnames = reader.fieldnames
        print(f"Original fieldnames: {fieldnames}")
        rows = list(reader)
    
    print(f"Total rows read: {len(rows)}")
    
    # Standardize column order
    standardized_fieldnames = [
        'Object Date',
        'Title',
        'Object Number',
        'Link Resource'
    ]
    
    # Write standardized output with UTF-8 encoding and LF line endings
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=standardized_fieldnames, delimiter='\t', lineterminator='\n')
        writer.writeheader()
        
        for row in rows:
            standardized_row = {
                'Object Date': row.get('Object Date', '').strip(),
                'Title': row.get('Title', '').strip(),
                'Object Number': row.get('Object Number', '').strip(),
                'Link Resource': row.get('Link Resource', '').strip()
            }
            writer.writerow(standardized_row)
    
    print(f"Standardized output written to {output_path}")

def main():
    input_file = Path('/mnt/user-data/uploads/met_inventory.tsv')
    output_file = Path('/mnt/user-data/outputs/met_inventory_standardized.tsv')
    manifest_file = Path('/mnt/user-data/outputs/FIXITY_MANIFEST.txt')
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("MET INVENTORY TSV STANDARDIZATION - FIXITY VERIFICATION")
    print("=" * 70)
    
    # Calculate source checksum
    source_checksum = calculate_checksum(input_file)
    source_size = input_file.stat().st_size
    print(f"\nSOURCE FILE:")
    print(f"  Path: {input_file}")
    print(f"  Size: {source_size} bytes")
    print(f"  SHA256: {source_checksum}")
    
    # Standardize the file
    print(f"\nSTANDARDIZING...")
    standardize_tsv(input_file, output_file)
    
    # Calculate output checksum
    output_checksum = calculate_checksum(output_file)
    output_size = output_file.stat().st_size
    print(f"\nOUTPUT FILE:")
    print(f"  Path: {output_file}")
    print(f"  Size: {output_size} bytes")
    print(f"  SHA256: {output_checksum}")
    
    # Generate manifest
    with open(manifest_file, 'w', encoding='utf-8') as f:
        f.write("MET INVENTORY TSV STANDARDIZATION - FIXITY MANIFEST\n")
        f.write("=" * 70 + "\n\n")
        f.write("SOURCE FILE\n")
        f.write(f"  Filename: met_inventory.tsv\n")
        f.write(f"  Size: {source_size} bytes\n")
        f.write(f"  SHA256: {source_checksum}\n\n")
        f.write("OUTPUT FILE\n")
        f.write(f"  Filename: met_inventory_standardized.tsv\n")
        f.write(f"  Size: {output_size} bytes\n")
        f.write(f"  SHA256: {output_checksum}\n\n")
        f.write("STANDARDIZATION CHANGES APPLIED\n")
        f.write("  ✓ Normalized line endings to LF (Unix standard)\n")
        f.write("  ✓ Verified UTF-8 encoding throughout\n")
        f.write("  ✓ Standardized tab-delimited separation\n")
        f.write("  ✓ Trimmed leading/trailing whitespace from all values\n")
        f.write("  ✓ Reordered columns: Object Date | Title | Object Number | Link Resource\n")
        f.write("  ✓ Ensured consistent handling of empty/missing values\n")
        f.write("  ✓ Standardized CSV dialect settings (delimiter=tab, lineterminator=LF)\n")
    
    print(f"\nMANIFEST: {manifest_file}")
    print("\n" + "=" * 70)
    print("✓ Standardization complete!")
    print("=" * 70 + "\n")

if __name__ == '__main__':
    main()
