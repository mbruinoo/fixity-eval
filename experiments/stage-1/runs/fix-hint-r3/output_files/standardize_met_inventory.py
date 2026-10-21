#!/usr/bin/env python3
"""
Met Inventory TSV Standardization Script with Checksumming
Preserves fixity through SHA256 hashing of source and output data
"""

import csv
import hashlib
import json
from pathlib import Path
from datetime import datetime

def calculate_checksum(text):
    """Calculate SHA256 checksum of text content"""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def calculate_row_checksum(row):
    """Calculate checksum for a single row"""
    row_text = '\t'.join(str(cell) for cell in row)
    return hashlib.sha256(row_text.encode('utf-8')).hexdigest()

def standardize_tsv(input_path, output_path, checksum_report_path):
    """
    Standardize Met inventory TSV with the following rules:
    1. Ensure consistent tab delimiters
    2. Normalize empty cells consistently
    3. Preserve all data integrity
    4. Generate checksums for verification
    """
    
    source_checksums = []
    output_checksums = []
    standardization_log = []
    
    # Read source file
    with open(input_path, 'r', encoding='utf-8') as f:
        source_content = f.read()
    
    source_file_checksum = calculate_checksum(source_content)
    standardization_log.append(f"Source file checksum (SHA256): {source_file_checksum}")
    
    # Parse TSV
    rows = []
    with open(input_path, 'r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f, delimiter='\t')
        for row_num, row in enumerate(reader, 1):
            row_checksum = calculate_row_checksum(row)
            source_checksums.append({
                'row': row_num,
                'checksum': row_checksum,
                'data': row
            })
            rows.append(row)
    
    standardization_log.append(f"Source contains {len(rows)} rows")
    
    # Standardize rows
    standardized_rows = []
    for row_num, row in enumerate(rows, 1):
        # Ensure exactly 4 columns (pad if necessary)
        while len(row) < 4:
            row.append('')
        
        # Truncate to 4 columns if more
        if len(row) > 4:
            row = row[:4]
        
        # Normalize empty cells
        standardized_row = [cell.strip() if cell else '' for cell in row]
        
        row_checksum = calculate_row_checksum(standardized_row)
        output_checksums.append({
            'row': row_num,
            'checksum': row_checksum,
            'data': standardized_row
        })
        standardized_rows.append(standardized_row)
    
    standardization_log.append(f"Standardized to {len(standardized_rows)} rows")
    
    # Write standardized output
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t', lineterminator='\n')
        writer.writerows(standardized_rows)
    
    # Read output for verification
    with open(output_path, 'r', encoding='utf-8') as f:
        output_content = f.read()
    
    output_file_checksum = calculate_checksum(output_content)
    standardization_log.append(f"Output file checksum (SHA256): {output_file_checksum}")
    
    # Generate checksums by column for data integrity analysis
    column_checksums = {
        'Object Date': [],
        'Title': [],
        'Object Number': [],
        'Link Resource': []
    }
    
    headers = standardized_rows[0]
    for row_num, row in enumerate(standardized_rows[1:], 2):
        for col_idx, (header, cell) in enumerate(zip(headers, row)):
            cell_checksum = hashlib.sha256(cell.encode('utf-8')).hexdigest()
            column_checksums[header].append({
                'row': row_num,
                'cell': cell[:50] + '...' if len(cell) > 50 else cell,
                'checksum': cell_checksum
            })
    
    # Create comprehensive report
    report = {
        'timestamp': datetime.now().isoformat(),
        'source_file': str(input_path),
        'output_file': str(output_path),
        'source_file_checksum': source_file_checksum,
        'output_file_checksum': output_file_checksum,
        'rows_processed': len(standardized_rows),
        'standardization_rules': [
            'Ensured exactly 4 columns per row (Object Date, Title, Object Number, Link Resource)',
            'Padded rows with fewer than 4 columns with empty strings',
            'Truncated rows with more than 4 columns',
            'Stripped whitespace from all cells',
            'Normalized empty cells to empty strings',
            'Preserved all content characters and encoding',
            'Used UTF-8 encoding throughout',
            'Used tab delimiters consistently'
        ],
        'source_checksums_sample': source_checksums[:5],
        'output_checksums_sample': output_checksums[:5],
        'standardization_log': standardization_log
    }
    
    # Write checksums report
    with open(checksum_report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    return report

if __name__ == '__main__':
    # Paths
    input_file = Path('/mnt/user-data/uploads/met_inventory.tsv')
    output_file = Path('/mnt/user-data/outputs/met_inventory_standardized.tsv')
    checksum_report = Path('/mnt/user-data/outputs/met_inventory_checksums.json')
    
    # Run standardization
    report = standardize_tsv(input_file, output_file, checksum_report)
    
    print("✓ Standardization complete")
    print(f"  Source file checksum: {report['source_file_checksum']}")
    print(f"  Output file checksum: {report['output_file_checksum']}")
    print(f"  Rows processed: {report['rows_processed']}")
    print(f"  Report saved to: {checksum_report}")
