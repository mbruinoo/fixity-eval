#!/usr/bin/env python3
"""
Standardize met_inventory.tsv file with checksums for fixity preservation.

This script:
1. Reads the source TSV file
2. Calculates SHA-256 checksum of source
3. Standardizes the data (consistent formatting, encoding, line endings)
4. Calculates SHA-256 checksum of output
5. Creates a checksums file
6. Logs the standardization process
"""

import csv
import hashlib
import json
from pathlib import Path
from datetime import datetime

def calculate_checksum(file_path, algorithm='sha256'):
    """Calculate checksum of a file."""
    hash_func = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_func.update(chunk)
    return hash_func.hexdigest()

def standardize_tsv(input_file, output_file):
    """
    Standardize TSV file with consistent formatting.
    
    Standardization includes:
    - UTF-8 encoding
    - Unix line endings (LF)
    - Consistent quoting (QUOTE_MINIMAL)
    - Proper escaping
    - Consistent tab delimiters
    - No trailing whitespace
    - Consistent header formatting
    """
    
    # Read source data
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        rows = list(reader)
        fieldnames = reader.fieldnames
    
    # Standardize fieldnames (strip whitespace, consistent naming)
    fieldnames = [name.strip() for name in fieldnames]
    
    # Standardize rows (strip whitespace from all fields)
    standardized_rows = []
    for row in rows:
        standardized_row = {
            key.strip(): (value.strip() if value else '') 
            for key, value in row.items()
        }
        standardized_rows.append(standardized_row)
    
    # Write standardized output
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(
            f, 
            fieldnames=fieldnames,
            delimiter='\t',
            quoting=csv.QUOTE_MINIMAL,
            lineterminator='\n'
        )
        writer.writeheader()
        writer.writerows(standardized_rows)

def main():
    input_file = Path('/mnt/user-data/uploads/met_inventory.tsv')
    output_file = Path('/mnt/user-data/outputs/met_inventory_standardized.tsv')
    checksums_file = Path('/mnt/user-data/outputs/CHECKSUMS.json')
    log_file = Path('/mnt/user-data/outputs/standardization_log.txt')
    
    # Verify input file exists
    if not input_file.exists():
        print(f"Error: Input file not found: {input_file}")
        return False
    
    # Calculate source checksum
    print("Calculating source checksum...")
    source_checksum = calculate_checksum(input_file)
    print(f"Source SHA-256: {source_checksum}")
    
    # Standardize the file
    print("\nStandardizing TSV file...")
    standardize_tsv(input_file, output_file)
    print(f"Standardized file written to: {output_file}")
    
    # Calculate output checksum
    print("Calculating output checksum...")
    output_checksum = calculate_checksum(output_file)
    print(f"Output SHA-256: {output_checksum}")
    
    # Get file sizes
    source_size = input_file.stat().st_size
    output_size = output_file.stat().st_size
    
    # Create checksums file
    checksums_data = {
        "timestamp": datetime.now().isoformat(),
        "source_file": str(input_file),
        "output_file": str(output_file),
        "source_checksum_sha256": source_checksum,
        "output_checksum_sha256": output_checksum,
        "source_size_bytes": source_size,
        "output_size_bytes": output_size,
        "algorithm": "sha256",
        "standardization_applied": [
            "UTF-8 encoding normalized",
            "Unix line endings (LF) applied",
            "Tab delimiters standardized",
            "Whitespace trimmed from all fields",
            "Headers normalized",
            "CSV quoting: QUOTE_MINIMAL",
            "No trailing whitespace"
        ]
    }
    
    with open(checksums_file, 'w') as f:
        json.dump(checksums_data, f, indent=2)
    print(f"\nChecksums written to: {checksums_file}")
    
    # Create detailed log
    with open(log_file, 'w') as f:
        f.write("TSV STANDARDIZATION LOG\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n\n")
        f.write("SOURCE FILE\n")
        f.write(f"  Path: {input_file}\n")
        f.write(f"  Size: {source_size:,} bytes\n")
        f.write(f"  SHA-256: {source_checksum}\n\n")
        f.write("OUTPUT FILE\n")
        f.write(f"  Path: {output_file}\n")
        f.write(f"  Size: {output_size:,} bytes\n")
        f.write(f"  SHA-256: {output_checksum}\n\n")
        f.write("STANDARDIZATION APPLIED\n")
        for item in checksums_data["standardization_applied"]:
            f.write(f"  • {item}\n")
        f.write("\n" + "=" * 60 + "\n")
        f.write("VERIFICATION\n")
        f.write("To verify file integrity, run:\n")
        f.write(f"  sha256sum {output_file}\n")
        f.write("And compare with the checksum above.\n")
    
    print(f"Log written to: {log_file}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("STANDARDIZATION COMPLETE")
    print("=" * 60)
    print(f"Source size:     {source_size:,} bytes")
    print(f"Output size:     {output_size:,} bytes")
    print(f"Size difference: {output_size - source_size:,} bytes")
    print("\nAll files created in: /mnt/user-data/outputs/")
    
    return True

if __name__ == '__main__':
    main()
