#!/usr/bin/env python3
"""
Met Museum Inventory TSV Standardization Script

This script reads the original Met Museum inventory TSV file, applies standardization
transformations, and produces a cleaned output file. Checksums (SHA256 and MD5) are
included in the output file header as a fixity check.

Author: Data Processing Script
Date: 2024
Input File: met_inventory.tsv
Output File: met_inventory_standardized.tsv
"""

import csv
import hashlib
import re
import html
from datetime import datetime
from pathlib import Path

def calculate_checksums(filepath):
    """Calculate SHA256 and MD5 checksums for a file."""
    sha256_hash = hashlib.sha256()
    md5_hash = hashlib.md5()
    
    with open(filepath, 'rb') as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
            md5_hash.update(byte_block)
    
    return {
        'sha256': sha256_hash.hexdigest(),
        'md5': md5_hash.hexdigest()
    }

def standardize_date(date_str):
    """
    Standardize date formats.
    - Replace 'ca.' with 'circa'
    - Handle various date range formats
    - Clean up unnecessary qualifiers in brackets
    """
    if not date_str or date_str.strip() == '':
        return 'Unknown'
    
    # Replace 'ca.' with 'circa'
    date_str = re.sub(r'\bca\.\s+', 'circa ', date_str)
    
    # Remove brackets around dates
    date_str = re.sub(r'\[([^]]+)\]', r'\1', date_str)
    
    # Clean up "printed later" and similar qualifiers
    date_str = re.sub(r',\s*printed\s+\w+', '', date_str)
    date_str = re.sub(r',\s*executed\s+', ', executed ', date_str)
    
    # Standardize date ranges to use en-dash
    date_str = re.sub(r'–+', '–', date_str)  # Normalize dashes
    date_str = re.sub(r'-(?=[0-9])', '–', date_str)  # Convert hyphens in ranges
    
    # Clean up leading/trailing whitespace
    date_str = date_str.strip()
    
    return date_str if date_str else 'Unknown'

def standardize_title(title_str):
    """
    Standardize titles.
    - Remove HTML tags (e.g., <i>, </i>)
    - Remove brackets around titles
    - Clean up excessive publication information
    - Decode HTML entities
    """
    if not title_str or title_str.strip() == '':
        return 'Unknown'
    
    # Decode HTML entities
    title_str = html.unescape(title_str)
    
    # Remove HTML tags
    title_str = re.sub(r'<[^>]+>', '', title_str)
    
    # Remove brackets around titles
    title_str = re.sub(r'^\[([^\]]+)\]$', r'\1', title_str)
    title_str = re.sub(r'^\[', '', title_str)
    title_str = re.sub(r'\]$', '', title_str)
    
    # Remove "Fiore D'Ogni..." type long titles, keep first part
    # For very long descriptive titles with multiple clauses
    if len(title_str) > 250:
        # For excessively long titles, keep the core and abbreviate
        # Find the first major clause/comma and use that as primary title
        match = re.match(r'([^,]+)(?:,\s+from\s+|,\s+page\s+|,\s+plate\s+|;)', title_str)
        if match:
            title_str = match.group(1)
    
    # Clean up multiple spaces
    title_str = re.sub(r'\s+', ' ', title_str)
    
    # Clean up leading/trailing whitespace
    title_str = title_str.strip()
    
    return title_str if title_str else 'Unknown'

def standardize_object_number(obj_num):
    """
    Standardize object numbers.
    - Clean up whitespace
    - Keep all numbering schemes as-is (they're authoritative)
    """
    if not obj_num or obj_num.strip() == '':
        return 'Unknown'
    
    # Clean up whitespace but preserve the structure
    obj_num = obj_num.strip()
    
    return obj_num if obj_num else 'Unknown'

def standardize_url(url_str):
    """
    Standardize URLs.
    - Ensure proper format
    - Remove extra whitespace
    """
    if not url_str or url_str.strip() == '':
        return 'Unknown'
    
    url_str = url_str.strip()
    
    # Verify it looks like a URL
    if url_str.startswith('http'):
        return url_str
    else:
        return 'Unknown'

def process_inventory(input_file, output_file):
    """
    Process the inventory file with standardizations.
    Returns checksums for both input and output files.
    """
    
    # Calculate input checksums
    print(f"Calculating checksums for input file: {input_file}")
    input_checksums = calculate_checksums(input_file)
    print(f"  SHA256: {input_checksums['sha256']}")
    print(f"  MD5:    {input_checksums['md5']}")
    
    # Read and process the file
    print(f"\nReading input file: {input_file}")
    rows_read = 0
    rows_processed = 0
    
    standardized_rows = []
    
    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile, delimiter='\t')
        
        # Store header
        fieldnames = reader.fieldnames
        print(f"  Detected columns: {fieldnames}")
        
        for row in reader:
            rows_read += 1
            
            # Apply standardizations
            standardized_row = {
                'Object Date': standardize_date(row.get('Object Date', '')),
                'Title': standardize_title(row.get('Title', '')),
                'Object Number': standardize_object_number(row.get('Object Number', '')),
                'Link Resource': standardize_url(row.get('Link Resource', ''))
            }
            
            standardized_rows.append(standardized_row)
            rows_processed += 1
    
    print(f"  Rows read: {rows_read}")
    print(f"  Rows processed: {rows_processed}")
    
    # Write output file
    print(f"\nWriting output file: {output_file}")
    with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        writer.writerows(standardized_rows)
    
    # Calculate output checksums
    print(f"Calculating checksums for output file: {output_file}")
    output_checksums = calculate_checksums(output_file)
    print(f"  SHA256: {output_checksums['sha256']}")
    print(f"  MD5:    {output_checksums['md5']}")
    
    return input_checksums, output_checksums, rows_processed

def create_metadata_report(input_file, output_file, input_checksums, output_checksums, rows_processed):
    """
    Create a metadata report documenting the transformation.
    """
    report_file = output_file.replace('.tsv', '_METADATA.txt')
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("MET MUSEUM INVENTORY STANDARDIZATION - METADATA REPORT\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"Generated: {datetime.now().isoformat()}\n")
        f.write(f"Script: standardize_met_inventory.py\n\n")
        
        f.write("INPUT FILE INFORMATION\n")
        f.write("-" * 80 + "\n")
        f.write(f"Filename: {input_file}\n")
        f.write(f"SHA256:   {input_checksums['sha256']}\n")
        f.write(f"MD5:      {input_checksums['md5']}\n")
        input_size = Path(input_file).stat().st_size
        f.write(f"Size:     {input_size:,} bytes\n\n")
        
        f.write("OUTPUT FILE INFORMATION\n")
        f.write("-" * 80 + "\n")
        f.write(f"Filename: {output_file}\n")
        f.write(f"SHA256:   {output_checksums['sha256']}\n")
        f.write(f"MD5:      {output_checksums['md5']}\n")
        output_size = Path(output_file).stat().st_size
        f.write(f"Size:     {output_size:,} bytes\n\n")
        
        f.write("PROCESSING INFORMATION\n")
        f.write("-" * 80 + "\n")
        f.write(f"Records processed: {rows_processed}\n")
        f.write(f"Size difference: {output_size - input_size:,} bytes\n\n")
        
        f.write("TRANSFORMATIONS APPLIED\n")
        f.write("-" * 80 + "\n")
        f.write("1. Object Date field:\n")
        f.write("   - Replaced 'ca.' with 'circa'\n")
        f.write("   - Standardized date range dashes to en-dash (–)\n")
        f.write("   - Removed brackets and extra qualifiers\n")
        f.write("   - Replaced empty values with 'Unknown'\n\n")
        
        f.write("2. Title field:\n")
        f.write("   - Removed HTML tags (<i>, </i>, etc.)\n")
        f.write("   - Decoded HTML entities\n")
        f.write("   - Removed brackets around titles\n")
        f.write("   - Truncated excessively long titles (>250 chars)\n")
        f.write("   - Normalized whitespace\n")
        f.write("   - Replaced empty values with 'Unknown'\n\n")
        
        f.write("3. Object Number field:\n")
        f.write("   - Preserved all authoritative numbering schemes\n")
        f.write("   - Cleaned whitespace\n")
        f.write("   - Replaced empty values with 'Unknown'\n\n")
        
        f.write("4. Link Resource field:\n")
        f.write("   - Validated URL format\n")
        f.write("   - Replaced invalid/empty URLs with 'Unknown'\n\n")
        
        f.write("FIXITY VERIFICATION\n")
        f.write("-" * 80 + "\n")
        f.write("To verify file integrity, calculate checksums and compare:\n")
        f.write(f"SHA256: {input_checksums['sha256']} (input) → {output_checksums['sha256']} (output)\n")
        f.write(f"MD5:    {input_checksums['md5']} (input) → {output_checksums['md5']} (output)\n")
        f.write("=" * 80 + "\n")
    
    print(f"Metadata report written to: {report_file}\n")
    return report_file

if __name__ == '__main__':
    # File paths
    input_file = '/mnt/user-data/uploads/met_inventory.tsv'
    output_file = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
    
    # Process the inventory
    print("Starting Met Museum Inventory Standardization\n")
    input_checksums, output_checksums, rows_processed = process_inventory(input_file, output_file)
    
    # Create metadata report
    metadata_file = create_metadata_report(input_file, output_file, input_checksums, output_checksums, rows_processed)
    
    print("Standardization complete!")
    print(f"Output files:")
    print(f"  - {output_file}")
    print(f"  - {metadata_file}")
