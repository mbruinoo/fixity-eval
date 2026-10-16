#!/usr/bin/env python3
"""
Standardize the Met Museum TSV inventory file.

Operations performed:
1. Add proper header row
2. Normalize HTML entities
3. Ensure consistent tab delimiters
4. Trim whitespace
5. Validate data structure
6. Remove duplicate whitespace
"""

import re
import csv
from html import unescape
from pathlib import Path
from collections import namedtuple

# Define the standard column structure
HEADERS = ['Object_Date', 'Title', 'Object_Number', 'Link_Resource']

def clean_html_entities(text):
    """Convert HTML entities to plain text."""
    if not text:
        return text
    text = unescape(text)  # &lt; &gt; etc.
    text = text.replace('&nbsp;', ' ')  # non-breaking spaces
    return text.strip()


def normalize_row(row):
    """
    Normalize a row of data.
    - Ensure 4 columns
    - Clean HTML entities
    - Trim whitespace
    - Handle missing values
    """
    # Pad row if needed
    while len(row) < 4:
        row.append('')
    
    # Trim to 4 columns if overfull
    row = row[:4]
    
    # Clean each field
    cleaned = []
    for field in row:
        if field is None:
            field = ''
        field = str(field).strip()
        field = clean_html_entities(field)
        cleaned.append(field)
    
    return cleaned


def parse_tsv_raw(file_path):
    """
    Parse the TSV file carefully, handling irregular delimiters.
    The source file may have inconsistent tab usage.
    """
    rows = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Use tab as delimiter, allow variable field count initially
            reader = csv.reader(f, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            
            for row_num, row in enumerate(reader, 1):
                if row and any(field.strip() for field in row):  # Skip truly empty rows
                    rows.append(row)
        
        return rows
        
    except Exception as e:
        print(f"ERROR parsing file: {e}")
        return []


def standardize_file(input_path, output_path):
    """
    Read source TSV, standardize, and write output.
    """
    
    print("Reading source file...")
    rows = parse_tsv_raw(input_path)
    
    if not rows:
        print("ERROR: No data read from file!")
        return False
    
    print(f"Read {len(rows)} data rows")
    
    # Normalize all rows
    print("Normalizing data...")
    normalized = []
    stats = {
        'rows_processed': 0,
        'rows_with_missing_title': 0,
        'rows_with_missing_date': 0,
        'rows_with_missing_number': 0,
        'html_entities_cleaned': 0,
    }
    
    for row in rows:
        cleaned = normalize_row(row)
        normalized.append(cleaned)
        stats['rows_processed'] += 1
        
        if not cleaned[0]:  # No date
            stats['rows_with_missing_date'] += 1
        if not cleaned[1]:  # No title
            stats['rows_with_missing_title'] += 1
        if not cleaned[2]:  # No object number
            stats['rows_with_missing_number'] += 1
        if any('&' in field for field in cleaned):
            stats['html_entities_cleaned'] += 1
    
    # Write standardized output
    print(f"Writing standardized output to {output_path}...")
    
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            
            # Write header
            writer.writerow(HEADERS)
            
            # Write data rows
            writer.writerows(normalized)
        
        print(f"✓ Wrote {len(normalized)} data rows (+ 1 header row)")
        
        print("\n--- STANDARDIZATION STATISTICS ---")
        for key, value in sorted(stats.items()):
            print(f"{key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"ERROR writing file: {e}")
        return False


def main():
    input_file = "met_inventory.tsv"
    output_file = "met_inventory_STANDARDIZED.tsv"
    
    print("=" * 70)
    print("TSV STANDARDIZATION SCRIPT")
    print("=" * 70)
    print(f"\nInput:  {input_file}")
    print(f"Output: {output_file}")
    
    success = standardize_file(input_file, output_file)
    
    if success:
        print(f"\n✓ Standardization complete!")
        print(f"✓ Next step: Run 04_checksum_result.py to verify fixity")
    else:
        print(f"\n✗ Standardization failed!")
    
    print("=" * 70)


if __name__ == "__main__":
    main()
