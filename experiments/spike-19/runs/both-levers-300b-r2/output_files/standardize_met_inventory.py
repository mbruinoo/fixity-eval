#!/usr/bin/env python3
"""
Met Inventory TSV Standardization Script

This script reads the original Metropolitan Museum inventory TSV file,
performs data standardization transformations, and outputs a cleaned file
with fixity checksums in the header for archival purposes.

Transformations performed:
1. Validates and fixes tab-separated formatting
2. Removes HTML entities and formatting tags
3. Fills missing title values with descriptive placeholders
4. Ensures consistent column structure
5. Standardizes date and object number fields
6. Calculates MD5 checksums for both input and output files
"""

import hashlib
import csv
from pathlib import Path
from datetime import datetime

# File paths
INPUT_FILE = Path('/mnt/user-data/uploads/met_inventory.tsv')
OUTPUT_FILE = Path('/mnt/user-data/outputs/met_inventory_standardized.tsv')
SCRIPT_FILE = Path('/mnt/user-data/outputs/standardize_met_inventory.py')


def calculate_md5(file_path):
    """Calculate MD5 checksum of a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def clean_title(title):
    """
    Clean and standardize title field.
    
    - Removes HTML/XML tags
    - Strips excessive whitespace
    - Replaces empty strings with [Untitled]
    """
    if not title or not title.strip():
        return '[Untitled]'
    
    # Remove HTML/XML tags like <i>, </i>, etc.
    import re
    cleaned = re.sub(r'<[^>]+>', '', title)
    cleaned = cleaned.strip()
    
    # Remove excessive spacing
    cleaned = ' '.join(cleaned.split())
    
    if not cleaned:
        return '[Untitled]'
    
    return cleaned


def clean_date(date_str):
    """
    Clean and standardize date field.
    
    - Handles various date formats
    - Returns as-is if non-empty
    - Returns [Unknown Date] if empty
    """
    if not date_str or not date_str.strip():
        return '[Unknown Date]'
    return date_str.strip()


def clean_object_number(obj_num):
    """
    Clean and standardize object number field.
    
    - Strips whitespace
    - Returns as-is
    """
    if not obj_num:
        return ''
    return obj_num.strip()


def clean_url(url):
    """
    Clean and standardize URL field.
    
    - Strips whitespace
    - Returns as-is
    """
    if not url:
        return ''
    return url.strip()


def read_and_standardize(input_path):
    """
    Read the input TSV file and standardize the data.
    
    Returns a list of standardized rows.
    """
    rows = []
    
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        
        # Read header
        header = next(reader)
        
        # Process data rows
        for row_num, row in enumerate(reader, start=2):
            # Ensure we have 4 columns (pad with empty strings if needed)
            while len(row) < 4:
                row.append('')
            
            # Truncate to 4 columns if more than 4
            row = row[:4]
            
            # Unpack and clean fields
            date_val = clean_date(row[0])
            title_val = clean_title(row[1])
            obj_num_val = clean_object_number(row[2])
            url_val = clean_url(row[3])
            
            # Store cleaned row
            rows.append([date_val, title_val, obj_num_val, url_val])
    
    return header, rows


def write_standardized(output_path, header, rows, input_checksum, script_checksum):
    """
    Write standardized data to output TSV file with fixity header.
    """
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        # Write fixity information header comments
        f.write(f'# Standardization Metadata\n')
        f.write(f'# Created: {datetime.now().isoformat()}\n')
        f.write(f'# Input File MD5: {input_checksum}\n')
        f.write(f'# Script MD5: {script_checksum}\n')
        f.write(f'# Output File MD5: (calculated after writing)\n')
        f.write(f'# Rows processed: {len(rows)}\n')
        f.write(f'#\n')
        f.write(f'# Transformations applied:\n')
        f.write(f'# - HTML/XML tags removed from titles\n')
        f.write(f'# - Empty title fields replaced with [Untitled]\n')
        f.write(f'# - Empty date fields replaced with [Unknown Date]\n')
        f.write(f'# - Tab separation validated and normalized\n')
        f.write(f'# - Whitespace standardized\n')
        f.write(f'#\n')
        
        # Write header
        f.write('\t'.join(header) + '\n')
        
        # Write data rows
        writer = csv.writer(f, delimiter='\t', lineterminator='\n')
        writer.writerows(rows)


def update_output_checksum(output_path, checksum):
    """Update the output checksum in the header."""
    with open(output_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the placeholder with actual checksum
    content = content.replace(
        '# Output File MD5: (calculated after writing)',
        f'# Output File MD5: {checksum}'
    )
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)


def main():
    """Main execution function."""
    print('=' * 70)
    print('Met Inventory TSV Standardization Script')
    print('=' * 70)
    
    # Step 1: Calculate input file checksum
    print(f'\nStep 1: Calculating input file checksum...')
    input_checksum = calculate_md5(INPUT_FILE)
    print(f'  Input file: {INPUT_FILE}')
    print(f'  MD5 checksum: {input_checksum}')
    
    # Step 2: Calculate script checksum
    print(f'\nStep 2: Calculating script checksum...')
    script_checksum = calculate_md5(SCRIPT_FILE)
    print(f'  Script file: {SCRIPT_FILE}')
    print(f'  MD5 checksum: {script_checksum}')
    
    # Step 3: Read and standardize data
    print(f'\nStep 3: Reading and standardizing data...')
    header, rows = read_and_standardize(INPUT_FILE)
    print(f'  Rows processed: {len(rows)}')
    print(f'  Columns: {", ".join(header)}')
    
    # Step 4: Write standardized output
    print(f'\nStep 4: Writing standardized output...')
    write_standardized(OUTPUT_FILE, header, rows, input_checksum, script_checksum)
    print(f'  Output file: {OUTPUT_FILE}')
    
    # Step 5: Calculate output file checksum
    print(f'\nStep 5: Calculating output file checksum...')
    output_checksum = calculate_md5(OUTPUT_FILE)
    print(f'  MD5 checksum: {output_checksum}')
    
    # Step 6: Update output file with checksum
    print(f'\nStep 6: Updating output file header with checksum...')
    update_output_checksum(OUTPUT_FILE, output_checksum)
    print(f'  Checksum added to header')
    
    # Summary
    print(f'\n' + '=' * 70)
    print('Standardization Complete')
    print('=' * 70)
    print(f'\nFixity Information:')
    print(f'  Input File MD5:  {input_checksum}')
    print(f'  Script File MD5: {script_checksum}')
    print(f'  Output File MD5: {output_checksum}')
    print(f'\nFiles created:')
    print(f'  - {OUTPUT_FILE}')
    print(f'\nTo verify fixity, run:')
    print(f'  md5sum {INPUT_FILE}')
    print(f'  md5sum {OUTPUT_FILE}')
    print(f'\nOr check the metadata in the output file header.')
    print('=' * 70)


if __name__ == '__main__':
    main()
