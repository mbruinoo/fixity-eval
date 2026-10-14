#!/usr/bin/env python3
"""
Met Museum Inventory TSV Standardization Script

Transforms met_inventory.tsv by:
1. Converting en-dashes (–) to hyphens (-) in date ranges
2. Removing quotation marks from titles
3. Removing HTML entity tags (&lt;i&gt;, &lt;/i&gt;)
4. Removing bracket delimiters from titles
5. Generating checksums before and after

Author: Data Standardization Process
Date: 2024
"""

import hashlib
import sys
import re
from pathlib import Path

def calculate_file_checksum(filepath):
    """Calculate MD5 checksum of a file."""
    md5_hash = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()

def transform_line(line):
    """Apply transformations to a single line."""
    # Skip header line
    if line.startswith('Object Date'):
        return line
    
    # Split by tab to process each field
    fields = line.split('\t')
    
    if len(fields) >= 2:
        # Transform the Object Date field (first field)
        # Replace en-dashes with hyphens
        fields[0] = fields[0].replace('–', '-')
        
        # Transform the Title field (second field)
        if len(fields) > 1:
            title = fields[1]
            
            # Remove quotation marks at start and end
            title = re.sub(r'^"(.+)"$', r'\1', title)
            
            # Remove bracket delimiters at start and end
            title = re.sub(r'^\[(.+)\]$', r'\1', title)
            
            # Remove HTML entity tags
            title = title.replace('&lt;i&gt;', '')
            title = title.replace('&lt;/i&gt;', '')
            
            # Clean up multiple spaces
            title = re.sub(r'\s+', ' ', title).strip()
            
            # Replace en-dashes with hyphens in title
            title = title.replace('–', '-')
            
            fields[1] = title
    
    return '\t'.join(fields)

def transform_file(input_path, output_path):
    """Transform the TSV file and generate report."""
    
    # Calculate input checksum
    input_checksum = calculate_file_checksum(input_path)
    print(f"Input file checksum (MD5): {input_checksum}")
    print(f"Input file: {input_path}")
    
    # Read and transform
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"Processing {len(lines)} lines...")
    
    # Track transformations
    transformations = {
        'en_dash_replaced': 0,
        'quotes_removed': 0,
        'brackets_removed': 0,
        'html_tags_removed': 0,
        'lines_processed': 0
    }
    
    transformed_lines = []
    for line_num, line in enumerate(lines, 1):
        original_line = line
        transformed_line = transform_line(line.rstrip('\n\r'))
        
        # Count transformations
        if original_line != transformed_line + '\n' and original_line != transformed_line:
            transformations['lines_processed'] += 1
            
            # Count specific transformations
            if '–' in original_line and '–' not in transformed_line:
                transformations['en_dash_replaced'] += 1
            if '"' in original_line and '"' not in transformed_line:
                transformations['quotes_removed'] += 1
            if '[' in original_line or ']' in original_line:
                if '[' not in transformed_line or ']' not in transformed_line:
                    transformations['brackets_removed'] += 1
            if '&lt;' in original_line and '&lt;' not in transformed_line:
                transformations['html_tags_removed'] += 1
        
        transformed_lines.append(transformed_line + '\n')
    
    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(transformed_lines)
    
    # Calculate output checksum
    output_checksum = calculate_file_checksum(output_path)
    print(f"Output file checksum (MD5): {output_checksum}")
    print(f"Output file: {output_path}")
    
    # Print transformation report
    print("\n" + "="*60)
    print("TRANSFORMATION REPORT")
    print("="*60)
    print(f"Total lines processed: {len(lines)}")
    print(f"Lines with transformations: {transformations['lines_processed']}")
    print(f"En-dashes replaced: {transformations['en_dash_replaced']}")
    print(f"Quotation marks removed: {transformations['quotes_removed']}")
    print(f"Bracket delimiters removed: {transformations['brackets_removed']}")
    print(f"HTML tags removed: {transformations['html_tags_removed']}")
    print("="*60)
    
    return {
        'input_checksum': input_checksum,
        'output_checksum': output_checksum,
        'transformations': transformations,
        'input_file': str(input_path),
        'output_file': str(output_path)
    }

if __name__ == '__main__':
    input_file = '/tmp/met_inventory_original.tsv'
    output_file = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
    
    result = transform_file(input_file, output_file)
    
    # Create a summary file
    summary_path = '/mnt/user-data/outputs/transformation_summary.txt'
    with open(summary_path, 'w') as f:
        f.write("MET MUSEUM INVENTORY STANDARDIZATION\n")
        f.write("="*60 + "\n\n")
        f.write(f"Input File: {result['input_file']}\n")
        f.write(f"Input Checksum (MD5): {result['input_checksum']}\n\n")
        f.write(f"Output File: {result['output_file']}\n")
        f.write(f"Output Checksum (MD5): {result['output_checksum']}\n\n")
        f.write("TRANSFORMATIONS APPLIED:\n")
        f.write("-"*60 + "\n")
        f.write(f"Total lines processed: {result['transformations']['lines_processed']}\n")
        f.write(f"En-dashes (–) replaced with hyphens (-): {result['transformations']['en_dash_replaced']}\n")
        f.write(f"Quotation marks removed: {result['transformations']['quotes_removed']}\n")
        f.write(f"Bracket delimiters removed: {result['transformations']['brackets_removed']}\n")
        f.write(f"HTML entities (&lt;, &gt;) removed: {result['transformations']['html_tags_removed']}\n")
        f.write("="*60 + "\n")
    
    print(f"\nSummary written to: {summary_path}")
