#!/usr/bin/env python3
"""
Met Inventory TSV Standardizer with Fixity Verification
Preserves data integrity through checksums of source and standardized rows
"""

import csv
import hashlib
import json
from pathlib import Path
from datetime import datetime

def calculate_hash(text, algorithm='sha256'):
    """Calculate hash of text content."""
    h = hashlib.new(algorithm)
    h.update(text.encode('utf-8'))
    return h.hexdigest()

def standardize_tsv(input_path, output_path, checksums_path):
    """
    Standardize TSV file and generate checksums for fixity verification.
    
    Standardization includes:
    - Consistent tab delimiters
    - Empty cells represented as empty strings
    - Consistent line endings (LF)
    - UTF-8 encoding
    - No trailing spaces
    """
    
    source_checksums = []
    standardized_checksums = []
    
    with open(input_path, 'r', encoding='utf-8') as infile:
        reader = csv.reader(infile, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
        
        # Read all rows
        rows = list(reader)
        
        # Generate source checksums (row-level)
        for row_num, row in enumerate(rows, 1):
            row_text = '\t'.join(row)
            source_hash = calculate_hash(row_text)
            source_checksums.append({
                'row_number': row_num,
                'row_content': row_text[:100] + '...' if len(row_text) > 100 else row_text,
                'sha256': source_hash
            })
    
    # Standardize and write output
    with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile, delimiter='\t', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        
        for row_num, row in enumerate(rows, 1):
            # Standardize: strip trailing spaces from each cell
            standardized_row = [cell.strip() for cell in row]
            writer.writerow(standardized_row)
            
            # Generate standardized checksums (row-level)
            row_text = '\t'.join(standardized_row)
            std_hash = calculate_hash(row_text)
            standardized_checksums.append({
                'row_number': row_num,
                'row_content': row_text[:100] + '...' if len(row_text) > 100 else row_text,
                'sha256': std_hash
            })
    
    # Calculate file-level checksums
    with open(input_path, 'rb') as f:
        source_file_hash = hashlib.sha256(f.read()).hexdigest()
    
    with open(output_path, 'rb') as f:
        output_file_hash = hashlib.sha256(f.read()).hexdigest()
    
    # Create comprehensive checksum report
    checksum_report = {
        'timestamp': datetime.now().isoformat(),
        'source_file': str(input_path),
        'output_file': str(output_path),
        'statistics': {
            'total_rows': len(rows),
            'total_columns': max(len(row) for row in rows) if rows else 0,
        },
        'file_level_checksums': {
            'source_file_sha256': source_file_hash,
            'output_file_sha256': output_file_hash,
        },
        'standardization_changes': {
            'whitespace_normalized': True,
            'encoding': 'UTF-8',
            'line_terminator': 'LF (\\n)',
            'delimiter': 'TAB',
            'quoting': 'Minimal (QUOTE_MINIMAL)'
        },
        'row_level_checksums': {
            'source_rows': source_checksums,
            'standardized_rows': standardized_checksums
        }
    }
    
    # Write checksum report
    with open(checksums_path, 'w', encoding='utf-8') as f:
        json.dump(checksum_report, f, indent=2, ensure_ascii=False)
    
    print("✓ Standardization complete")
    print(f"\nFile Statistics:")
    print(f"  Total rows: {checksum_report['statistics']['total_rows']}")
    print(f"  Max columns: {checksum_report['statistics']['total_columns']}")
    print(f"\nFile-Level Checksums (SHA-256):")
    print(f"  Source:       {source_file_hash}")
    print(f"  Standardized: {output_file_hash}")
    print(f"\nRow-Level Checksums: {len(source_checksums)} rows documented")
    print(f"  First row hash (source):       {source_checksums[0]['sha256']}")
    print(f"  First row hash (standardized): {standardized_checksums[0]['sha256']}")
    print(f"  Last row hash (source):        {source_checksums[-1]['sha256']}")
    print(f"  Last row hash (standardized):  {standardized_checksums[-1]['sha256']}")
    print(f"\n✓ Checksum report saved to: {checksums_path}")
    
    return checksum_report

if __name__ == '__main__':
    input_file = '/mnt/user-data/uploads/met_inventory.tsv'
    output_file = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
    checksums_file = '/mnt/user-data/outputs/met_inventory_checksums.json'
    
    standardize_tsv(input_file, output_file, checksums_file)
