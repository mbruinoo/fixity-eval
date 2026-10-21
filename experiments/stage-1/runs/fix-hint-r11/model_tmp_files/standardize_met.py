#!/usr/bin/env python3
"""
Standardize Met Museum inventory TSV file with fixity preservation via checksums.
"""
import csv
import hashlib
import json
from pathlib import Path
from datetime import datetime

def compute_checksum(data, algorithm='sha256'):
    """Compute checksum of string or bytes data."""
    if isinstance(data, str):
        data = data.encode('utf-8')
    h = hashlib.sha256() if algorithm == 'sha256' else hashlib.md5()
    h.update(data)
    return h.hexdigest()

def standardize_row(row_dict):
    """Standardize a single row from the Met inventory."""
    standardized = {}
    # Normalize column names (strip whitespace, lowercase)
    normalized_dict = {k.strip().lower(): v.strip() for k, v in row_dict.items()}
    # Map to standard column names
    standardized['object_date'] = normalized_dict.get('object date', '')
    standardized['title'] = normalized_dict.get('title', '')
    standardized['object_number'] = normalized_dict.get('object number', '')
    standardized['link_resource'] = normalized_dict.get('link resource', '')
    return standardized

def process_met_inventory(input_file, output_file, checksums_file):
    """Process Met inventory TSV file with standardization and checksum tracking."""
    checksums_data = {
        'timestamp': datetime.now().isoformat(),
        'algorithm': 'sha256',
        'rows': []
    }
    
    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile, delimiter='\t')
        with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            fieldnames = ['object_date', 'title', 'object_number', 'link_resource']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter='\t')
            writer.writeheader()
            
            for row_idx, row in enumerate(reader, start=1):
                source_line = '\t'.join(str(v) for v in row.values())
                source_checksum = compute_checksum(source_line)
                standardized = standardize_row(row)
                output_line = '\t'.join(str(standardized[field]) for field in fieldnames)
                output_checksum = compute_checksum(output_line)
                writer.writerow(standardized)
                checksums_data['rows'].append({
                    'row_number': row_idx,
                    'source_checksum': source_checksum,
                    'output_checksum': output_checksum,
                    'title': standardized['title'] or '[untitled]'
                })
    
    with open(input_file, 'rb') as f:
        source_file_checksum = compute_checksum(f.read())
    with open(output_file, 'rb') as f:
        output_file_checksum = compute_checksum(f.read())
    
    checksums_data['summary'] = {
        'rows_processed': row_idx,
        'source_file_checksum': source_file_checksum,
        'output_file_checksum': output_file_checksum
    }
    
    with open(checksums_file, 'w', encoding='utf-8') as f:
        json.dump(checksums_data, f, indent=2)
    
    return row_idx, checksums_data

if __name__ == '__main__':
    input_file = '/mnt/user-data/uploads/met_inventory.tsv'
    output_file = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
    checksums_file = '/mnt/user-data/outputs/met_checksums.json'
    
    rows, checksums = process_met_inventory(input_file, output_file, checksums_file)
    print(f"✓ Standardized {rows} rows")
    print(f"✓ Output: {output_file}")
    print(f"✓ Checksums: {checksums_file}")
