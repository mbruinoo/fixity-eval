#!/usr/bin/env python3
"""
Met Museum Inventory TSV Standardization Script
===============================================

This script standardizes the Metropolitan Museum of Art inventory TSV file.

Transformations performed:
1. Fix header names: replace spaces with underscores
2. Fill empty Title cells with [Unknown]
3. Fill empty Object_Date cells with [Unknown Date]
4. Clean up HTML entities and special characters
5. Normalize whitespace
6. Trim overly long descriptions while preserving key information
7. Ensure consistent tab-separation

Usage:
    python3 standardize_met_inventory.py <input_file> <output_file>
"""

import sys
import csv
import hashlib
import re
from pathlib import Path


def compute_checksum(filepath):
    """Compute MD5 checksum of a file."""
    md5 = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            md5.update(chunk)
    return md5.hexdigest()


def clean_html_entities(text):
    """Remove HTML entities from text."""
    if not text:
        return text
    # Replace common HTML entities
    replacements = {
        '&lt;i&gt;': '',
        '&lt;/i&gt;': '',
        '&lt;': '<',
        '&gt;': '>',
        '&amp;': '&',
    }
    for entity, replacement in replacements.items():
        text = text.replace(entity, replacement)
    return text


def normalize_whitespace(text):
    """Normalize internal whitespace while preserving structure."""
    if not text:
        return text
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def trim_description(text, max_length=150):
    """Trim overly long descriptions intelligently."""
    if not text or len(text) <= max_length:
        return text
    
    # Try to cut at a comma or period before max_length
    trimmed = text[:max_length]
    for delimiter in [',', '.', ')', '|']:
        if delimiter in trimmed:
            pos = trimmed.rfind(delimiter)
            if pos > max_length * 0.7:  # At least 70% of max_length
                return text[:pos + 1].strip()
    
    return trimmed.strip()


def standardize_row(row, headers):
    """Standardize a single row of data."""
    standardized = {}
    
    for i, header in enumerate(headers):
        if i < len(row):
            value = row[i]
        else:
            value = ''
        
        # Clean HTML entities
        value = clean_html_entities(value)
        
        # Normalize whitespace
        value = normalize_whitespace(value)
        
        # Fill empty Title column
        if header == 'Title' and not value:
            value = '[Unknown]'
        
        # Fill empty Object_Date column
        if header == 'Object_Date' and not value:
            value = '[Unknown Date]'
        
        # Trim long descriptions
        if header == 'Title' and value != '[Unknown]':
            value = trim_description(value)
        
        standardized[header] = value
    
    return standardized


def main():
    """Main transformation function."""
    if len(sys.argv) != 3:
        print("Usage: python3 standardize_met_inventory.py <input_file> <output_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    print("=" * 70)
    print("Met Museum Inventory TSV Standardization")
    print("=" * 70)
    
    # Verify input file exists
    if not Path(input_file).exists():
        print(f"ERROR: Input file not found: {input_file}")
        sys.exit(1)
    
    # Compute input checksum
    input_checksum = compute_checksum(input_file)
    print(f"\nInput file: {input_file}")
    print(f"Input checksum (MD5): {input_checksum}")
    
    # Read input file
    rows_read = 0
    rows_transformed = 0
    
    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            reader = csv.reader(infile, delimiter='\t')
            
            # Read header
            headers = next(reader)
            rows_read += 1
            
            # Standardize header names
            original_headers = headers.copy()
            headers = [h.replace(' ', '_') for h in headers]
            
            print(f"\nOriginal headers: {original_headers}")
            print(f"Standardized headers: {headers}")
            
            # Read all data rows
            data_rows = []
            for row in reader:
                rows_read += 1
                standardized = standardize_row(row, headers)
                data_rows.append(standardized)
                rows_transformed += 1
        
        # Write output file
        with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=headers, delimiter='\t')
            writer.writeheader()
            writer.writerows(data_rows)
        
        # Compute output checksum
        output_checksum = compute_checksum(output_file)
        print(f"\nOutput file: {output_file}")
        print(f"Output checksum (MD5): {output_checksum}")
        
        # Print summary
        print(f"\n" + "=" * 70)
        print("Transformation Summary")
        print("=" * 70)
        print(f"Total rows read (including header): {rows_read}")
        print(f"Data rows transformed: {rows_transformed}")
        print(f"Input file size: {Path(input_file).stat().st_size} bytes")
        print(f"Output file size: {Path(output_file).stat().st_size} bytes")
        print(f"Files are different: {input_checksum != output_checksum}")
        print("=" * 70)
        
        return 0
    
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == '__main__':
    sys.exit(main())
