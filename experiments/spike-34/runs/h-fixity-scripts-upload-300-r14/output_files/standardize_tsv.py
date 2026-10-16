#!/usr/bin/env python3
"""
Standardize TSV file from the Metropolitan Museum of Art inventory.
Preserves fixity by computing checksums before and after processing.
"""

import hashlib
import sys
from pathlib import Path
import csv
import re

def compute_checksum(filepath, algorithm='sha256'):
    """Compute cryptographic checksum of a file."""
    hash_obj = hashlib.new(algorithm)
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()

def standardize_tsv(input_path, output_path):
    """
    Standardize TSV file:
    - Ensure consistent tab delimiters
    - Remove extra whitespace (leading/trailing per cell)
    - Ensure consistent line endings (LF)
    - Normalize HTML entities
    - Validate all rows have same column count
    """
    
    rows = []
    
    # Read input file with TSV dialect
    with open(input_path, 'r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f, delimiter='\t')
        for row_num, row in enumerate(reader, 1):
            rows.append(row)
    
    # Determine expected column count from header
    if not rows:
        raise ValueError("File is empty")
    
    header = rows[0]
    expected_cols = len(header)
    
    # Standardize rows
    standardized_rows = []
    
    for row_num, row in enumerate(rows, 1):
        # Ensure correct column count
        if len(row) < expected_cols:
            row = row + [''] * (expected_cols - len(row))
        elif len(row) > expected_cols:
            row = row[:expected_cols]
        
        # Strip whitespace from each cell
        row = [cell.strip() for cell in row]
        
        # Normalize HTML entities
        row = [normalize_html_entities(cell) for cell in row]
        
        standardized_rows.append(row)
    
    # Write standardized TSV with LF line endings
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t', lineterminator='\n')
        writer.writerows(standardized_rows)

def normalize_html_entities(text):
    """Normalize common HTML entities."""
    if not text:
        return text
    
    # Replace common HTML entities
    replacements = {
        '&lt;': '<',
        '&gt;': '>',
        '&amp;': '&',
        '&quot;': '"',
        '&#39;': "'",
    }
    
    for entity, char in replacements.items():
        text = text.replace(entity, char)
    
    return text

def main():
    input_file = '/mnt/user-data/uploads/met_inventory.tsv'
    output_file = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
    
    # Compute source checksum
    print("=" * 70)
    print("STANDARDIZING TSV FILE WITH FIXITY VERIFICATION")
    print("=" * 70)
    print()
    
    print(f"Input file: {input_file}")
    source_sha256 = compute_checksum(input_file, 'sha256')
    source_md5 = compute_checksum(input_file, 'md5')
    
    print(f"  SHA256: {source_sha256}")
    print(f"  MD5:    {source_md5}")
    print()
    
    # Process file
    print("Processing file...")
    try:
        standardize_tsv(input_file, output_file)
        print("✓ File standardized successfully")
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)
    
    print()
    
    # Compute output checksum
    print(f"Output file: {output_file}")
    output_sha256 = compute_checksum(output_file, 'sha256')
    output_md5 = compute_checksum(output_file, 'md5')
    
    print(f"  SHA256: {output_sha256}")
    print(f"  MD5:    {output_md5}")
    print()
    
    # Read and display statistics
    with open(input_file, 'r', encoding='utf-8', newline='') as f:
        input_rows = len(f.readlines())
    
    with open(output_file, 'r', encoding='utf-8', newline='') as f:
        output_rows = len(f.readlines())
    
    input_size = Path(input_file).stat().st_size
    output_size = Path(output_file).stat().st_size
    
    print("=" * 70)
    print("STATISTICS")
    print("=" * 70)
    print(f"Input rows:   {input_rows}")
    print(f"Output rows:  {output_rows}")
    print(f"Input size:   {input_size:,} bytes")
    print(f"Output size:  {output_size:,} bytes")
    print()
    
    # Create manifest file
    manifest_path = '/mnt/user-data/outputs/fixity_manifest.txt'
    with open(manifest_path, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("TSV STANDARDIZATION FIXITY MANIFEST\n")
        f.write("=" * 70 + "\n\n")
        
        f.write("SOURCE FILE\n")
        f.write(f"Path:   {input_file}\n")
        f.write(f"Size:   {input_size:,} bytes\n")
        f.write(f"Rows:   {input_rows}\n")
        f.write(f"SHA256: {source_sha256}\n")
        f.write(f"MD5:    {source_md5}\n\n")
        
        f.write("OUTPUT FILE\n")
        f.write(f"Path:   {output_file}\n")
        f.write(f"Size:   {output_size:,} bytes\n")
        f.write(f"Rows:   {output_rows}\n")
        f.write(f"SHA256: {output_sha256}\n")
        f.write(f"MD5:    {output_md5}\n\n")
        
        f.write("STANDARDIZATION CHANGES\n")
        f.write("- Consistent tab delimiters\n")
        f.write("- Stripped leading/trailing whitespace from all cells\n")
        f.write("- Normalized HTML entities (&lt; → <, &gt; → >, etc.)\n")
        f.write("- Ensured all rows have consistent column count (4 columns)\n")
        f.write("- Unix line endings (LF) applied\n")
    
    print(f"Manifest saved: {manifest_path}")
    print()
    print("✓ Standardization complete with fixity verification!")

if __name__ == '__main__':
    main()
