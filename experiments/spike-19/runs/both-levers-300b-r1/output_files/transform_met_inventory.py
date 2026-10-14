#!/usr/bin/env python3
"""
Met Museum Inventory TSV Standardization Script
Reads met_inventory.tsv and produces a standardized, cleaned version
with fixity checks via SHA256 checksums.

Script: transform_met_inventory.py
Input: met_inventory.tsv
Output: met_inventory_standardized.tsv
"""

import csv
import hashlib
import sys
from pathlib import Path
from datetime import datetime

def calculate_sha256(file_path):
    """Calculate SHA256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def clean_title(title):
    """Clean and standardize title field."""
    if not title or title.strip() == "":
        return "[Untitled]"
    
    # Remove HTML entities and extra markup
    title = title.replace('&lt;i&gt;', '').replace('&lt;/i&gt;', '')
    title = title.replace('&lt;b&gt;', '').replace('&lt;/b&gt;', '')
    
    # Clean up common patterns
    title = title.strip()
    
    # Handle bracketed descriptions - remove brackets but keep content
    if title.startswith('[') and title.endswith(']'):
        title = title[1:-1]
    
    # Handle quoted titles with descriptions
    if title.startswith('"') and '" ' in title:
        # Extract title and make description part of it
        parts = title.split('" ', 1)
        title = parts[0].lstrip('"') + ' (' + parts[1].rstrip(')') + ')'
    elif title.startswith('"') and title.endswith('"'):
        title = title.strip('"')
    
    return title if title else "[Untitled]"

def clean_date(date):
    """Clean and standardize date field."""
    if not date or date.strip() == "":
        return "[Unknown]"
    return date.strip()

def clean_object_number(obj_num):
    """Clean and standardize object number field."""
    return obj_num.strip() if obj_num else ""

def clean_url(url):
    """Clean and standardize URL field."""
    return url.strip() if url else ""

def standardize_tsv(input_file, output_file):
    """
    Read TSV file, standardize all fields, and write to output file.
    Returns a dict with processing statistics.
    """
    stats = {
        'total_rows': 0,
        'rows_with_missing_titles': 0,
        'rows_with_missing_dates': 0,
        'input_file': input_file,
        'output_file': output_file,
        'input_checksum': calculate_sha256(input_file),
        'timestamp': datetime.now().isoformat()
    }
    
    rows = []
    
    # Read input TSV
    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile, delimiter='\t')
        
        for row in reader:
            stats['total_rows'] += 1
            
            # Extract fields (handle column name variations)
            date_val = row.get('Object Date', row.get('Date', ''))
            title_val = row.get('Title', '')
            obj_num = row.get('Object Number', '')
            url = row.get('Link Resource', '')
            
            # Check for missing data
            if not title_val or title_val.strip() == "":
                stats['rows_with_missing_titles'] += 1
            if not date_val or date_val.strip() == "":
                stats['rows_with_missing_dates'] += 1
            
            # Clean and standardize
            cleaned_row = {
                'Date': clean_date(date_val),
                'Title': clean_title(title_val),
                'Object Number': clean_object_number(obj_num),
                'Link Resource': clean_url(url)
            }
            
            rows.append(cleaned_row)
    
    # Write standardized TSV with header comment containing checksums
    with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        # Write fixity information as commented header
        outfile.write("# TSV Standardization Report\n")
        outfile.write(f"# Generated: {stats['timestamp']}\n")
        outfile.write(f"# Script: transform_met_inventory.py\n")
        outfile.write(f"# Input File: {input_file}\n")
        outfile.write(f"# Input SHA256: {stats['input_checksum']}\n")
        outfile.write(f"# Total Rows Processed: {stats['total_rows']}\n")
        outfile.write(f"# Rows with Missing Titles: {stats['rows_with_missing_titles']}\n")
        outfile.write(f"# Rows with Missing Dates: {stats['rows_with_missing_dates']}\n")
        outfile.write("#\n")
        
        # Write actual TSV data
        writer = csv.DictWriter(
            outfile,
            fieldnames=['Date', 'Title', 'Object Number', 'Link Resource'],
            delimiter='\t'
        )
        writer.writeheader()
        writer.writerows(rows)
    
    # Calculate output checksum
    stats['output_checksum'] = calculate_sha256(output_file)
    
    return stats

def main():
    """Main entry point."""
    # Set file paths
    script_dir = Path(__file__).parent
    input_file = Path('/mnt/user-data/uploads/met_inventory.tsv')
    output_file = Path('/mnt/user-data/outputs/met_inventory_standardized.tsv')
    
    # Verify input file exists
    if not input_file.exists():
        print(f"ERROR: Input file not found: {input_file}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Processing: {input_file}")
    print("=" * 70)
    
    # Perform standardization
    stats = standardize_tsv(input_file, output_file)
    
    # Print report
    print(f"\nInput File Checksum (SHA256):")
    print(f"  {stats['input_checksum']}")
    print(f"\nOutput File Checksum (SHA256):")
    print(f"  {stats['output_checksum']}")
    print(f"\nProcessing Statistics:")
    print(f"  Total Rows Processed: {stats['total_rows']}")
    print(f"  Rows with Missing Titles: {stats['rows_with_missing_titles']}")
    print(f"  Rows with Missing Dates: {stats['rows_with_missing_dates']}")
    print(f"\nOutput File: {output_file}")
    print("=" * 70)
    
    # Append checksum information to output file header (already done above)
    print("\n✓ Standardization complete!")
    print(f"  Input:  {input_file}")
    print(f"  Output: {output_file}")

if __name__ == "__main__":
    main()
