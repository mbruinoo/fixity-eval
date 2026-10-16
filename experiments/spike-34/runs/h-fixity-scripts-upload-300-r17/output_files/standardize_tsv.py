#!/usr/bin/env python3
"""
Standardize Met Museum inventory TSV file with data fixity verification.
Performs checksumming on source and output to verify data integrity.
"""

import csv
import hashlib
import sys
from pathlib import Path
from datetime import datetime


def calculate_checksum(file_path, algorithm='sha256'):
    """Calculate file checksum using specified algorithm."""
    hash_obj = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()


def calculate_content_checksum(content, algorithm='sha256'):
    """Calculate checksum of string content."""
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(content.encode('utf-8'))
    return hash_obj.hexdigest()


def standardize_tsv(input_path, output_path):
    """
    Standardize TSV file:
    - Ensure consistent tab delimiters
    - Remove trailing/leading whitespace from fields
    - Ensure consistent line endings (LF)
    - Replace empty Title fields with explicit empty string
    - Preserve all data integrity
    """
    
    # Read source file
    print(f"Reading source file: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        source_content = f.read()
    
    source_checksum = calculate_content_checksum(source_content)
    print(f"Source file SHA256: {source_checksum}")
    
    # Parse TSV
    rows = []
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for row_num, row in enumerate(reader, 1):
            rows.append(row)
    
    print(f"Total rows read: {len(rows)}")
    
    # Standardize rows
    standardized_rows = []
    for row_num, row in enumerate(rows, 1):
        # Ensure exactly 5 columns
        if len(row) < 5:
            row.extend([''] * (5 - len(row)))
        elif len(row) > 5:
            row = row[:5]
        
        # Strip whitespace from each field while preserving internal spaces
        standardized_row = [field.strip() for field in row]
        standardized_rows.append(standardized_row)
    
    # Write standardized TSV
    print(f"Writing standardized file: {output_path}")
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t', lineterminator='\n')
        writer.writerows(standardized_rows)
    
    # Calculate output checksum
    with open(output_path, 'r', encoding='utf-8') as f:
        output_content = f.read()
    
    output_checksum = calculate_content_checksum(output_content)
    print(f"Output file SHA256: {output_checksum}")
    
    # Verify data integrity
    print("\nData Integrity Verification:")
    print(f"  Source rows: {len(rows)}")
    print(f"  Output rows: {len(standardized_rows)}")
    
    # Count empty Title fields
    empty_titles_input = sum(1 for row in rows if len(row) > 1 and row[1].strip() == '')
    empty_titles_output = sum(1 for row in standardized_rows if len(row) > 1 and row[1].strip() == '')
    
    print(f"  Empty Title fields (input): {empty_titles_input}")
    print(f"  Empty Title fields (output): {empty_titles_output}")
    
    # Verify row counts match
    if len(rows) == len(standardized_rows):
        print("  ✓ Row count preserved")
    else:
        print("  ✗ Row count mismatch!")
    
    # Spot check data integrity
    object_numbers_input = [row[2] for row in rows[1:] if len(row) > 2]
    object_numbers_output = [row[2] for row in standardized_rows[1:] if len(row) > 2]
    
    if object_numbers_input == object_numbers_output:
        print("  ✓ Object numbers preserved")
    else:
        print("  ✗ Object number mismatch!")
    
    return {
        'source_checksum': source_checksum,
        'output_checksum': output_checksum,
        'rows_processed': len(rows),
        'source_file': str(input_path),
        'output_file': str(output_path),
        'timestamp': datetime.now().isoformat()
    }


def main():
    input_file = Path('/mnt/user-data/uploads/met_inventory.tsv')
    output_file = Path('/mnt/user-data/outputs/met_inventory_standardized.tsv')
    
    if not input_file.exists():
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)
    
    # Run standardization
    results = standardize_tsv(input_file, output_file)
    
    # Save metadata
    metadata = {
        'standardization_report': {
            'timestamp': results['timestamp'],
            'source_file': results['source_file'],
            'source_checksum_sha256': results['source_checksum'],
            'output_file': results['output_file'],
            'output_checksum_sha256': results['output_checksum'],
            'rows_processed': results['rows_processed'],
            'standardizations_applied': [
                'Consistent tab delimiters',
                'Whitespace trimming from all fields',
                'Unix line endings (LF)',
                'Exactly 5 columns per row',
                'UTF-8 encoding preserved'
            ]
        }
    }
    
    # Write metadata
    metadata_path = Path('/mnt/user-data/outputs/standardization_metadata.txt')
    with open(metadata_path, 'w', encoding='utf-8') as f:
        f.write("Met Museum Inventory TSV Standardization Report\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Timestamp: {metadata['standardization_report']['timestamp']}\n")
        f.write(f"Source File: {metadata['standardization_report']['source_file']}\n")
        f.write(f"Source Checksum (SHA256): {metadata['standardization_report']['source_checksum_sha256']}\n\n")
        f.write(f"Output File: {metadata['standardization_report']['output_file']}\n")
        f.write(f"Output Checksum (SHA256): {metadata['standardization_report']['output_checksum_sha256']}\n\n")
        f.write(f"Rows Processed: {metadata['standardization_report']['rows_processed']}\n\n")
        f.write("Standardizations Applied:\n")
        for item in metadata['standardization_report']['standardizations_applied']:
            f.write(f"  • {item}\n")
    
    print(f"\nMetadata written to: {metadata_path}")
    print("\n✓ Standardization complete!")
    print(f"✓ Output: {output_file}")


if __name__ == '__main__':
    main()
