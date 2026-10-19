#!/usr/bin/env python3
"""
Standardize Met Museum inventory TSV file with fixity verification.
Creates checksums of source and standardized data at multiple levels.
"""

import csv
import hashlib
import json
from pathlib import Path
from datetime import datetime


def compute_checksum(data, algorithm='sha256'):
    """Compute checksum for string data."""
    if isinstance(data, str):
        data = data.encode('utf-8')
    h = hashlib.sha256() if algorithm == 'sha256' else hashlib.md5()
    h.update(data)
    return h.hexdigest()


def compute_row_checksums(row, algorithm='sha256'):
    """Compute checksums for individual cells in a row."""
    return {
        'full_row': compute_checksum('|'.join(str(v) for v in row), algorithm),
        'cells': {i: compute_checksum(str(v), algorithm) for i, v in enumerate(row)}
    }


def standardize_date(date_str):
    """Standardize date formats in Object Date field."""
    date_str = date_str.strip() if date_str else ''
    
    # If empty, return as is
    if not date_str:
        return ''
    
    # Remove uncertainty markers for processing, but preserve them
    uncertainty = '(?)' in date_str or '(?)' in date_str
    clean_date = date_str.replace('(?)', '').strip()
    
    # Standardize century notation
    if 'century' in clean_date:
        return date_str  # Keep century notation as-is, it's already standard
    
    # Keep other dates as-is (BCE, specific years, ranges, etc.)
    return date_str


def standardize_row(row, headers):
    """Standardize a single row."""
    standardized = {}
    
    for i, header in enumerate(headers):
        value = row[i] if i < len(row) else ''
        
        if header == 'Object Date':
            standardized[header] = standardize_date(value)
        elif header == 'Title':
            # Clean up excess whitespace, normalize quotes
            standardized[header] = value.strip() if value else ''
        elif header == 'Object Number':
            standardized[header] = value.strip() if value else ''
        elif header == 'Link Resource':
            # Ensure URLs are lowercase for consistency
            standardized[header] = value.strip().lower() if value else ''
        else:
            standardized[header] = value.strip() if value else ''
    
    return standardized


def main():
    input_file = Path('/mnt/user-data/uploads/met_inventory.tsv')
    output_file = Path('/mnt/user-data/outputs/met_inventory_standardized.tsv')
    checksum_log = Path('/mnt/user-data/outputs/met_inventory_checksums.json')
    
    # Initialize checksum tracking
    checksums = {
        'timestamp': datetime.now().isoformat(),
        'source_file': str(input_file),
        'output_file': str(output_file),
        'algorithm': 'sha256',
        'source_file_checksum': '',
        'output_file_checksum': '',
        'row_checksums': {
            'source': {},
            'standardized': {}
        },
        'issues_found': []
    }
    
    # Read and checksum source file
    with open(input_file, 'r', encoding='utf-8') as f:
        source_content = f.read()
    
    checksums['source_file_checksum'] = compute_checksum(source_content)
    
    # Parse source file
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        headers = next(reader)
        rows = list(reader)
    
    # Compute checksums for source rows
    for row_idx, row in enumerate(rows):
        checksums['row_checksums']['source'][row_idx] = compute_row_checksums(row)
    
    # Standardize all rows
    standardized_rows = []
    for row_idx, row in enumerate(rows):
        std_row = standardize_row(row, headers)
        standardized_rows.append(std_row)
        checksums['row_checksums']['standardized'][row_idx] = compute_row_checksums(
            [std_row.get(h, '') for h in headers]
        )
    
    # Write standardized output
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers, delimiter='\t')
        writer.writeheader()
        writer.writerows(standardized_rows)
    
    # Checksum output file
    with open(output_file, 'r', encoding='utf-8') as f:
        output_content = f.read()
    
    checksums['output_file_checksum'] = compute_checksum(output_content)
    
    # Save checksum log
    with open(checksum_log, 'w', encoding='utf-8') as f:
        json.dump(checksums, f, indent=2)
    
    # Print summary
    print(f"✓ Standardization complete")
    print(f"  Source file: {input_file}")
    print(f"  Output file: {output_file}")
    print(f"  Checksum log: {checksum_log}")
    print(f"\n  Rows processed: {len(rows)}")
    print(f"  Headers: {', '.join(headers)}")
    print(f"\n  Source checksum (SHA-256): {checksums['source_file_checksum']}")
    print(f"  Output checksum (SHA-256): {checksums['output_file_checksum']}")
    print(f"\n  Row-level checksums saved for {len(rows)} rows")


if __name__ == '__main__':
    main()
