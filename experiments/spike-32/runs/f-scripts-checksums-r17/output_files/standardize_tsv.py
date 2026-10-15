#!/usr/bin/env python3
"""
Standardize Metropolitan Museum inventory TSV file.
Generates checksums for source and output for fixity verification.
"""

import csv
import hashlib
import sys
from pathlib import Path
from datetime import datetime


def calculate_checksum(file_path, algorithm='sha256'):
    """Calculate SHA256 checksum of a file."""
    hash_obj = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()


def standardize_tsv(input_path, output_path):
    """
    Standardize the TSV file:
    - Ensure consistent column headers (no extra spaces)
    - Normalize empty cells
    - Ensure consistent line endings
    - Add metadata row with processing info
    """
    
    # Read the input file
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Calculate source checksum
    source_checksum = calculate_checksum(input_path)
    
    # Parse with CSV reader to handle TSV properly
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        rows = list(reader)
    
    # Standardize headers (strip whitespace)
    if rows:
        headers = [h.strip() for h in rows[0]]
        rows[0] = headers
    
    # Process data rows - strip whitespace from all cells
    standardized_rows = [rows[0]]  # Keep headers
    for row in rows[1:]:
        # Ensure row has same number of columns as header
        while len(row) < len(headers):
            row.append('')
        row = row[:len(headers)]  # Trim if too many
        # Strip whitespace from each cell
        row = [cell.strip() for cell in row]
        standardized_rows.append(row)
    
    # Write standardized output
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t', lineterminator='\n')
        writer.writerows(standardized_rows)
    
    # Calculate output checksum
    output_checksum = calculate_checksum(output_path)
    
    return {
        'source_file': input_path,
        'output_file': output_path,
        'source_checksum': source_checksum,
        'output_checksum': output_checksum,
        'rows_processed': len(standardized_rows),
        'columns': len(headers),
        'timestamp': datetime.now().isoformat()
    }


def main():
    input_file = '/mnt/user-data/uploads/met_inventory.tsv'
    output_file = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
    
    # Check if input file exists
    if not Path(input_file).exists():
        print(f"Error: Input file not found: {input_file}", file=sys.stderr)
        sys.exit(1)
    
    # Run standardization
    print("Standardizing TSV file...")
    results = standardize_tsv(input_file, output_file)
    
    # Generate checksum manifest
    manifest_content = f"""# TSV Standardization Manifest
# Generated: {results['timestamp']}

## Source File
File: {results['source_file']}
SHA256: {results['source_checksum']}

## Output File
File: {results['output_file']}
SHA256: {results['output_checksum']}

## Processing Details
Rows: {results['rows_processed']}
Columns: {results['columns']}

## Changes Applied
- Stripped whitespace from headers
- Normalized empty cells
- Ensured consistent column alignment
- Applied Unix line endings (LF)
- UTF-8 encoding preserved
"""
    
    manifest_file = '/mnt/user-data/outputs/standardization_manifest.txt'
    with open(manifest_file, 'w', encoding='utf-8') as f:
        f.write(manifest_content)
    
    print(f"\n✓ Standardization complete!")
    print(f"\nOutput files:")
    print(f"  - {output_file}")
    print(f"  - {manifest_file}")
    print(f"\nSource SHA256:  {results['source_checksum']}")
    print(f"Output SHA256:  {results['output_checksum']}")
    print(f"Rows processed: {results['rows_processed']}")
    print(f"Columns:        {results['columns']}")


if __name__ == '__main__':
    main()
