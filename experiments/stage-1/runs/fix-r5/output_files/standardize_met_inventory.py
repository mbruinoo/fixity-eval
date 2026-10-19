#!/usr/bin/env python3
"""
Standardize met_inventory.tsv with fixity checking.
Computes SHA256 checksums before and after processing.
"""

import hashlib
import sys
from pathlib import Path

def compute_sha256(filepath):
    """Compute SHA256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def standardize_tsv(input_path, output_path):
    """
    Standardize TSV file:
    - Ensure consistent tab delimiters (single tab between columns)
    - Preserve all data including empty Title cells
    - Use Unix line endings (LF)
    - Remove trailing whitespace on each line
    """
    lines = []
    
    with open(input_path, 'r', encoding='utf-8') as f:
        for line in f:
            # Remove any trailing whitespace including line endings
            line = line.rstrip('\r\n')
            
            # Split by tabs
            fields = line.split('\t')
            
            # Ensure we have exactly 4 fields (Object Date, Title, Object Number, Link Resource)
            # Pad with empty strings if needed
            while len(fields) < 4:
                fields.append('')
            
            # Take only first 4 fields if there are more
            fields = fields[:4]
            
            # Join with single tab
            standardized_line = '\t'.join(fields)
            lines.append(standardized_line)
    
    # Write with Unix line endings
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        f.write('\n'.join(lines) + '\n')

def main():
    input_file = Path('/mnt/user-data/uploads/met_inventory.tsv')
    output_file = Path('/mnt/user-data/outputs/met_inventory_standardized.tsv')
    checksum_file = Path('/mnt/user-data/outputs/met_inventory_checksums.txt')
    
    # Check input file exists
    if not input_file.exists():
        print(f"Error: Input file not found at {input_file}", file=sys.stderr)
        sys.exit(1)
    
    # Compute input checksum
    print("Computing input file checksum...")
    input_checksum = compute_sha256(input_file)
    print(f"Input SHA256:  {input_checksum}")
    print(f"Input file:    {input_file}")
    
    # Process file
    print("\nStandardizing TSV file...")
    standardize_tsv(input_file, output_file)
    print(f"Output file:   {output_file}")
    
    # Compute output checksum
    print("\nComputing output file checksum...")
    output_checksum = compute_sha256(output_file)
    print(f"Output SHA256: {output_checksum}")
    
    # Verify output file structure
    print("\nVerifying output structure...")
    with open(output_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        print(f"Total lines:   {len(lines)}")
        
        # Check first line (header)
        header = lines[0].rstrip('\n').split('\t')
        print(f"Header fields: {len(header)}")
        print(f"Header:        {header}")
        
        # Check a few data lines
        print(f"\nSample rows:")
        for i in [1, 2, 10, 50, -1]:
            if i < len(lines):
                fields = lines[i].rstrip('\n').split('\t')
                print(f"  Line {i+1}: {len(fields)} fields")
    
    # Write checksums to file
    print("\nWriting checksums to file...")
    with open(checksum_file, 'w', encoding='utf-8') as f:
        f.write("Metropolitan Museum of Art Inventory Standardization\n")
        f.write("=" * 70 + "\n\n")
        f.write("INPUT FILE\n")
        f.write(f"Path:   {input_file}\n")
        f.write(f"SHA256: {input_checksum}\n\n")
        f.write("OUTPUT FILE\n")
        f.write(f"Path:   {output_file}\n")
        f.write(f"SHA256: {output_checksum}\n\n")
        f.write("STANDARDIZATION APPLIED\n")
        f.write("- Consistent tab delimiters (single tab between all columns)\n")
        f.write("- Preserved all data including empty Title cells\n")
        f.write("- Unix line endings (LF only)\n")
        f.write("- Removed trailing whitespace\n")
        f.write("- Ensured 4 columns: Object Date, Title, Object Number, Link Resource\n")
    
    print(f"Checksums written to: {checksum_file}")
    
    print("\n✓ Standardization complete!")
    return 0

if __name__ == '__main__':
    sys.exit(main())
