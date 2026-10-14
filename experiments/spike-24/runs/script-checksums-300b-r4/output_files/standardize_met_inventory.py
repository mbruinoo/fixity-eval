#!/usr/bin/env python3
"""
Metropolitan Museum Inventory TSV Standardization Script
This script performs data quality transformations on the Met inventory TSV file.
Includes checksums for verification of transformations.
"""

import sys
import hashlib
from pathlib import Path
import csv
from io import StringIO
import re
import html

def calculate_checksum(filepath, algorithm='sha256'):
    """Calculate file checksum."""
    hash_obj = hashlib.new(algorithm)
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()

def calculate_content_checksum(content, algorithm='sha256'):
    """Calculate checksum of string content."""
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(content.encode('utf-8'))
    return hash_obj.hexdigest()

def normalize_html_entities(text):
    """Convert HTML entities to plain text."""
    if not text:
        return text
    # Handle common HTML entities and tags
    text = html.unescape(text)
    text = re.sub(r'<i>(.*?)</i>', r'\1', text)
    text = re.sub(r'<b>(.*?)</b>', r'\1', text)
    text = re.sub(r'</?[^>]+>', '', text)  # Remove any remaining tags
    return text

def clean_title(title):
    """Clean and normalize title field."""
    if not title or title.strip() == '':
        return ''
    
    title = title.strip()
    # Remove leading/trailing brackets used for uncertain data
    title = re.sub(r'^\[|\]$', '', title)
    # Normalize HTML entities
    title = normalize_html_entities(title)
    # Clean up extra quotes
    title = re.sub(r'"{2,}', '"', title)
    
    return title

def clean_field(field):
    """General field cleaning."""
    if field is None:
        return ''
    field = field.strip()
    return field

def standardize_row(row):
    """Standardize a single row."""
    # Ensure we have 4 columns
    while len(row) < 4:
        row.append('')
    
    row = row[:4]  # Take only first 4 columns
    
    # Apply cleaning
    row[0] = clean_field(row[0])  # Object Date
    row[1] = clean_title(row[1])  # Title
    row[2] = clean_field(row[2])  # Object Number
    row[3] = clean_field(row[3])  # Link Resource
    
    return row

def standardize_file(input_path, output_path):
    """Main standardization function."""
    
    # Print header
    print("=" * 80)
    print("Met Inventory TSV Standardization")
    print("=" * 80)
    print()
    
    # Calculate input checksum
    input_checksum = calculate_checksum(input_path)
    print(f"Input file: {input_path}")
    print(f"Input checksum (SHA256): {input_checksum}")
    print()
    
    # Read file with various encodings
    content = None
    for encoding in ['utf-8', 'utf-8-sig', 'latin-1']:
        try:
            with open(input_path, 'r', encoding=encoding) as f:
                content = f.read()
            print(f"Successfully read file with encoding: {encoding}")
            break
        except UnicodeDecodeError:
            continue
    
    if content is None:
        print("ERROR: Could not read file with any encoding")
        sys.exit(1)
    
    print()
    
    # Parse TSV
    input_reader = csv.reader(StringIO(content), delimiter='\t')
    rows = list(input_reader)
    
    print(f"Total rows read: {len(rows)}")
    print(f"  - Header row: 1")
    print(f"  - Data rows: {len(rows) - 1}")
    print()
    
    # Check header
    header = rows[0]
    print(f"Header columns: {len(header)}")
    print(f"Header: {header}")
    print()
    
    # Standardize data rows
    standardized_rows = [header]  # Keep header as-is
    
    transformation_stats = {
        'rows_processed': 0,
        'titles_cleaned': 0,
        'empty_titles_removed': 0,
        'html_entities_removed': 0,
        'fields_trimmed': 0,
    }
    
    for i, row in enumerate(rows[1:], start=1):
        original_row = row.copy()
        standardized_row = standardize_row(row)
        
        # Track transformations
        transformation_stats['rows_processed'] += 1
        
        if clean_title(original_row[1] if len(original_row) > 1 else '') != (standardized_row[1] or ''):
            transformation_stats['titles_cleaned'] += 1
        
        if '<' in str(original_row) and '<' not in str(standardized_row):
            transformation_stats['html_entities_removed'] += 1
        
        for j in range(4):
            if len(original_row) > j and original_row[j] != standardized_row[j]:
                transformation_stats['fields_trimmed'] += 1
        
        standardized_rows.append(standardized_row)
    
    # Write standardized file
    output_content = StringIO()
    writer = csv.writer(output_content, delimiter='\t', lineterminator='\n')
    writer.writerows(standardized_rows)
    output_str = output_content.getvalue()
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output_str)
    
    # Calculate output checksum
    output_checksum = calculate_checksum(output_path)
    output_content_checksum = calculate_content_checksum(output_str)
    
    print("Transformation Statistics:")
    print(f"  - Rows processed: {transformation_stats['rows_processed']}")
    print(f"  - Titles cleaned: {transformation_stats['titles_cleaned']}")
    print(f"  - HTML entities removed: {transformation_stats['html_entities_removed']}")
    print(f"  - Fields trimmed: {transformation_stats['fields_trimmed']}")
    print()
    
    print(f"Output file: {output_path}")
    print(f"Output checksum (SHA256): {output_checksum}")
    print(f"Output content checksum (SHA256): {output_content_checksum}")
    print()
    
    print(f"Input file size: {Path(input_path).stat().st_size} bytes")
    print(f"Output file size: {Path(output_path).stat().st_size} bytes")
    print()
    
    # Generate verification report
    verification_report = {
        'input_file': str(input_path),
        'input_checksum_sha256': input_checksum,
        'output_file': str(output_path),
        'output_checksum_sha256': output_checksum,
        'output_content_checksum_sha256': output_content_checksum,
        'input_file_size': Path(input_path).stat().st_size,
        'output_file_size': Path(output_path).stat().st_size,
        'rows_input': len(rows),
        'rows_output': len(standardized_rows),
        'transformation_stats': transformation_stats,
    }
    
    return verification_report

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 standardize_met_inventory.py <input_file> [output_file]")
        print("Example: python3 standardize_met_inventory.py met_inventory_original.tsv met_inventory_standardized.tsv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'met_inventory_standardized.tsv'
    
    verification = standardize_file(input_file, output_file)
    
    # Write verification report
    report_file = output_file.replace('.tsv', '_verification.txt')
    with open(report_file, 'w') as f:
        f.write("STANDARDIZATION VERIFICATION REPORT\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Input File: {verification['input_file']}\n")
        f.write(f"Input Checksum (SHA256): {verification['input_checksum_sha256']}\n")
        f.write(f"Input File Size: {verification['input_file_size']} bytes\n")
        f.write(f"Input Rows: {verification['rows_input']}\n\n")
        
        f.write(f"Output File: {verification['output_file']}\n")
        f.write(f"Output Checksum (SHA256): {verification['output_checksum_sha256']}\n")
        f.write(f"Output Content Checksum (SHA256): {verification['output_content_checksum_sha256']}\n")
        f.write(f"Output File Size: {verification['output_file_size']} bytes\n")
        f.write(f"Output Rows: {verification['rows_output']}\n\n")
        
        f.write("Transformation Statistics:\n")
        for key, value in verification['transformation_stats'].items():
            f.write(f"  - {key}: {value}\n")
    
    print(f"Verification report written to: {report_file}")
    print("=" * 80)

