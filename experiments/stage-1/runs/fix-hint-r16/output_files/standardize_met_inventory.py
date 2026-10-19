#!/usr/bin/env python3
"""
Metropolitan Museum Inventory TSV Standardization Script
Standardizes the met_inventory.tsv file and generates checksums for fixity verification.
"""

import csv
import hashlib
import json
from pathlib import Path
from datetime import datetime

def compute_hash(text, algorithm='sha256'):
    """Compute hash of text content."""
    h = hashlib.new(algorithm)
    h.update(text.encode('utf-8'))
    return h.hexdigest()

def compute_row_hash(row_dict, algorithm='sha256'):
    """Compute hash of a normalized row."""
    # Create a canonical representation of the row
    normalized = json.dumps(row_dict, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
    h = hashlib.new(algorithm)
    h.update(normalized.encode('utf-8'))
    return h.hexdigest()

def standardize_tsv(input_path, output_path, checksums_path):
    """
    Standardize the TSV file with the following improvements:
    1. Consistent field delimiter (tab)
    2. Proper header standardization
    3. Empty cell handling
    4. Character encoding validation (UTF-8)
    5. Row integrity verification
    """
    
    # Source file checksums
    source_checksums = {}
    
    # Read original file
    with open(input_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    source_checksums['original_file_sha256'] = compute_hash(original_content)
    source_checksums['original_file_sha512'] = compute_hash(original_content, 'sha512')
    source_checksums['original_line_count'] = len(original_content.splitlines())
    
    # Parse the TSV
    rows = []
    row_checksums = []
    
    with open(input_path, 'r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f, delimiter='\t')
        headers = reader.fieldnames
        
        for row_num, row in enumerate(reader, start=2):  # Start at 2 because row 1 is header
            # Standardize row structure
            standardized_row = {}
            for header in headers:
                # Normalize empty strings and whitespace
                value = row.get(header, '')
                standardized_row[header] = value.strip() if value else ''
            
            rows.append(standardized_row)
            
            # Create row hash for fixity tracking
            row_hash = compute_row_hash(standardized_row)
            row_checksums.append({
                'row_number': row_num,
                'object_number': standardized_row.get('Object Number', ''),
                'sha256': row_hash
            })
    
    # Standardize headers
    standard_headers = [
        'Object Date',
        'Title',
        'Object Number',
        'Link Resource'
    ]
    
    # Write standardized TSV
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=standard_headers, delimiter='\t', 
                               quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, '') for k in standard_headers})
    
    # Read standardized file for its checksum
    with open(output_path, 'r', encoding='utf-8') as f:
        standardized_content = f.read()
    
    standardized_checksums = {
        'standardized_file_sha256': compute_hash(standardized_content),
        'standardized_file_sha512': compute_hash(standardized_content, 'sha512'),
        'standardized_line_count': len(standardized_content.splitlines()),
        'row_count': len(rows)
    }
    
    # Compile complete checksums document
    checksums = {
        'metadata': {
            'standardization_date': datetime.now().isoformat(),
            'script_version': '1.0',
            'input_file': str(input_path),
            'output_file': str(output_path),
            'encoding': 'UTF-8',
            'field_delimiter': 'TAB',
            'line_terminator': 'LF (\\n)'
        },
        'source_file': source_checksums,
        'standardized_file': standardized_checksums,
        'field_definitions': {
            'Object Date': 'Date or date range of the object',
            'Title': 'Title or description of the object',
            'Object Number': 'Museum catalog/accession number',
            'Link Resource': 'URL to object in museum collection'
        },
        'row_integrity': row_checksums,
        'standardization_notes': [
            'Removed inconsistent whitespace from cell values',
            'Ensured consistent tab delimiters between fields',
            'Normalized empty cells',
            'Applied UTF-8 encoding throughout',
            'Preserved original data values (no content modification)',
            'Maintained column order and structure',
            'Header row standardized to match field names'
        ]
    }
    
    # Write checksums to JSON
    with open(checksums_path, 'w', encoding='utf-8') as f:
        json.dump(checksums, f, indent=2, ensure_ascii=False)
    
    return checksums, len(rows)

def main():
    input_file = Path('/mnt/user-data/uploads/met_inventory.tsv')
    output_file = Path('/mnt/user-data/outputs/met_inventory_standardized.tsv')
    checksums_file = Path('/mnt/user-data/outputs/met_inventory_checksums.json')
    
    if not input_file.exists():
        print(f"Error: Input file {input_file} not found")
        return
    
    print("Starting Metropolitan Museum Inventory Standardization...")
    print(f"Input: {input_file}")
    print(f"Output: {output_file}")
    print(f"Checksums: {checksums_file}")
    print()
    
    checksums, row_count = standardize_tsv(input_file, output_file, checksums_file)
    
    print("✓ Standardization completed successfully!")
    print()
    print(f"Processed {row_count} data rows")
    print()
    print("Source File Hash (SHA256):")
    print(f"  {checksums['source_file']['original_file_sha256']}")
    print()
    print("Standardized File Hash (SHA256):")
    print(f"  {checksums['standardized_file']['standardized_file_sha256']}")
    print()
    print("Sample Row Checksums (first 5 rows):")
    for row_info in checksums['row_integrity'][:5]:
        print(f"  Row {row_info['row_number']} ({row_info['object_number']}): {row_info['sha256'][:16]}...")
    print()
    print("All checksums saved to met_inventory_checksums.json")

if __name__ == '__main__':
    main()
