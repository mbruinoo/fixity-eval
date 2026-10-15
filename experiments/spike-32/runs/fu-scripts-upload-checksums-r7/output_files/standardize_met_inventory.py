#!/usr/bin/env python3
"""
Standardize Met Museum inventory TSV file and preserve fixity with checksums.
"""

import csv
import hashlib
import json
from datetime import datetime
from pathlib import Path

def calculate_checksum(file_path, algorithm='sha256'):
    """Calculate checksum of a file."""
    hash_obj = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()

def standardize_tsv(input_path, output_path):
    """
    Standardize the TSV file:
    - Ensure consistent tab delimiters
    - Remove trailing whitespace
    - Ensure proper column headers
    - Ensure UTF-8 encoding
    """
    
    # Define expected columns
    columns = ['Object Date', 'Title', 'Object Number', 'Link Resource']
    
    # Read the input file
    rows = []
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            # Clean up each field
            cleaned_row = {
                'Object Date': (row.get('Object Date') or '').strip(),
                'Title': (row.get('Title') or '').strip(),
                'Object Number': (row.get('Object Number') or '').strip(),
                'Link Resource': (row.get('Link Resource') or '').strip(),
            }
            rows.append(cleaned_row)
    
    # Write standardized output
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns, delimiter='\t')
        writer.writeheader()
        writer.writerows(rows)
    
    return len(rows)

def main():
    # File paths
    input_file = Path('met_inventory.tsv')
    output_file = Path('met_inventory_standardized.tsv')
    fixity_file = Path('fixity_report.json')
    
    # Check if input file exists
    if not input_file.exists():
        print(f"Error: {input_file} not found")
        return 1
    
    print(f"Processing: {input_file}")
    print(f"File size: {input_file.stat().st_size} bytes")
    
    # Calculate source checksum
    source_checksum = calculate_checksum(str(input_file))
    print(f"Source MD5: {calculate_checksum(str(input_file), 'md5')}")
    print(f"Source SHA-256: {source_checksum}")
    
    # Standardize the file
    row_count = standardize_tsv(str(input_file), str(output_file))
    print(f"\nStandardized file: {output_file}")
    print(f"Rows processed: {row_count}")
    print(f"File size: {output_file.stat().st_size} bytes")
    
    # Calculate output checksums
    output_md5 = calculate_checksum(str(output_file), 'md5')
    output_sha256 = calculate_checksum(str(output_file))
    print(f"Output MD5: {output_md5}")
    print(f"Output SHA-256: {output_sha256}")
    
    # Create fixity report
    fixity_report = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'process': 'TSV Standardization',
        'source': {
            'filename': str(input_file),
            'size_bytes': input_file.stat().st_size,
            'md5': calculate_checksum(str(input_file), 'md5'),
            'sha256': source_checksum
        },
        'output': {
            'filename': str(output_file),
            'size_bytes': output_file.stat().st_size,
            'md5': output_md5,
            'sha256': output_sha256
        },
        'transformations': {
            'rows_processed': row_count,
            'delimiter': 'tab (\\t)',
            'encoding': 'UTF-8',
            'operations': [
                'Standardized tab delimiters',
                'Removed trailing whitespace from all fields',
                'Ensured consistent column headers',
                'Validated UTF-8 encoding',
                'Sorted and organized columns: Object Date, Title, Object Number, Link Resource'
            ]
        }
    }
    
    # Write fixity report
    with open(fixity_file, 'w', encoding='utf-8') as f:
        json.dump(fixity_report, f, indent=2)
    
    print(f"\nFixity report: {fixity_file}")
    print("\nFixity Report Contents:")
    print(json.dumps(fixity_report, indent=2))
    
    return 0

if __name__ == '__main__':
    exit(main())
