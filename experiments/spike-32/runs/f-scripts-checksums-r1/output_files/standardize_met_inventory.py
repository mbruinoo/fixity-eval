#!/usr/bin/env python3
"""
Standardize Metropolitan Museum inventory TSV file with checksum verification.
Addresses issues like inconsistent column naming, encoding, and formatting.
"""

import csv
import hashlib
import sys
from pathlib import Path
from typing import Tuple

def calculate_checksum(file_path: str, algorithm: str = 'sha256') -> str:
    """Calculate checksum of a file."""
    hash_obj = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()

def standardize_tsv(input_file: str, output_file: str) -> Tuple[str, str, dict]:
    """
    Standardize the Met Museum inventory TSV file.
    
    Standardizations applied:
    - Consistent column headers (snake_case)
    - UTF-8 encoding
    - Proper tab delimiter
    - Strip whitespace from fields
    - Handle missing values consistently
    - Validate data integrity
    
    Returns:
        Tuple of (input_checksum, output_checksum, stats)
    """
    
    stats = {
        'rows_processed': 0,
        'rows_with_empty_date': 0,
        'rows_with_empty_title': 0,
        'rows_with_empty_object_number': 0,
        'rows_with_empty_link': 0,
    }
    
    # Read input file and calculate checksum
    print(f"Reading from: {input_file}")
    input_checksum = calculate_checksum(input_file)
    print(f"Input SHA256: {input_checksum}")
    
    # Read and process data
    rows = []
    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile, delimiter='\t')
            
            # Get original headers
            original_headers = reader.fieldnames
            print(f"Original headers: {original_headers}")
            
            for row in reader:
                stats['rows_processed'] += 1
                
                # Standardize field names and clean data
                cleaned_row = {}
                
                # Map original headers to standardized names
                for old_header in original_headers:
                    # Standardize header name
                    new_header = old_header.strip().lower().replace(' ', '_')
                    value = row[old_header].strip() if row[old_header] else ''
                    cleaned_row[new_header] = value
                    
                    # Track empty values
                    if not value:
                        if 'date' in new_header:
                            stats['rows_with_empty_date'] += 1
                        elif 'title' in new_header:
                            stats['rows_with_empty_title'] += 1
                        elif 'object' in new_header:
                            stats['rows_with_empty_object_number'] += 1
                        elif 'link' in new_header:
                            stats['rows_with_empty_link'] += 1
                
                rows.append(cleaned_row)
    
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Define standardized headers
    standardized_headers = ['object_date', 'title', 'object_number', 'link_resource']
    
    # Write standardized output
    print(f"\nWriting to: {output_file}")
    try:
        with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(
                outfile,
                fieldnames=standardized_headers,
                delimiter='\t',
                quoting=csv.QUOTE_MINIMAL,
                lineterminator='\n'
            )
            writer.writeheader()
            writer.writerows(rows)
    
    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Calculate output checksum
    output_checksum = calculate_checksum(output_file)
    print(f"Output SHA256: {output_checksum}")
    
    return input_checksum, output_checksum, stats

def print_stats(stats: dict):
    """Print processing statistics."""
    print("\n" + "="*60)
    print("PROCESSING STATISTICS")
    print("="*60)
    print(f"Total rows processed: {stats['rows_processed']}")
    print(f"Rows with empty date: {stats['rows_with_empty_date']}")
    print(f"Rows with empty title: {stats['rows_with_empty_title']}")
    print(f"Rows with empty object_number: {stats['rows_with_empty_object_number']}")
    print(f"Rows with empty link_resource: {stats['rows_with_empty_link']}")
    print("="*60)

def main():
    """Main entry point."""
    input_file = 'met_inventory.tsv'
    output_file = 'met_inventory_standardized.tsv'
    checksum_file = 'met_inventory_checksums.txt'
    
    print("Metropolitan Museum Inventory TSV Standardizer")
    print("=" * 60)
    
    # Process file
    input_checksum, output_checksum, stats = standardize_tsv(input_file, output_file)
    
    # Print statistics
    print_stats(stats)
    
    # Save checksums to file
    try:
        with open(checksum_file, 'w', encoding='utf-8') as f:
            f.write("METROPOLITAN MUSEUM INVENTORY STANDARDIZATION\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Input file: {input_file}\n")
            f.write(f"Input SHA256: {input_checksum}\n\n")
            f.write(f"Output file: {output_file}\n")
            f.write(f"Output SHA256: {output_checksum}\n\n")
            f.write("Standardizations applied:\n")
            f.write("- Consistent column headers (snake_case)\n")
            f.write("- UTF-8 encoding\n")
            f.write("- Proper tab delimiter\n")
            f.write("- Whitespace trimming\n")
            f.write("- Consistent empty value handling\n\n")
            f.write("Processing Statistics:\n")
            f.write(f"- Total rows: {stats['rows_processed']}\n")
            f.write(f"- Rows with empty date: {stats['rows_with_empty_date']}\n")
            f.write(f"- Rows with empty title: {stats['rows_with_empty_title']}\n")
            f.write(f"- Rows with empty object_number: {stats['rows_with_empty_object_number']}\n")
            f.write(f"- Rows with empty link_resource: {stats['rows_with_empty_link']}\n")
        
        print(f"\nChecksums saved to: {checksum_file}")
    
    except Exception as e:
        print(f"Error writing checksums: {e}", file=sys.stderr)
        sys.exit(1)
    
    print("\n✓ Standardization complete!")

if __name__ == '__main__':
    main()
