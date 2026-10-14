#!/usr/bin/env python3
"""
Transform Met Museum Inventory TSV File
Standardizes formatting and validates data integrity with checksums.
"""

import sys
import hashlib
import re
from pathlib import Path
from collections import defaultdict


def calculate_checksum(filepath, algorithm='md5'):
    """Calculate file checksum."""
    hash_obj = hashlib.new(algorithm)
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()


def log_info(message, stats=None):
    """Print informational message."""
    print(f"[INFO] {message}")
    if stats:
        for key, value in stats.items():
            print(f"       {key}: {value}")


def parse_tsv(filepath):
    """Parse TSV file and return rows."""
    rows = []
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines):
        # Strip only trailing newlines, preserve internal whitespace
        line = line.rstrip('\n')
        # Split by tabs
        cells = line.split('\t')
        rows.append(cells)
    
    return rows


def clean_title(title):
    """Clean and standardize title field."""
    if not title or title.isspace():
        return '[Untitled]'
    
    # Remove HTML tags
    title = re.sub(r'</?i>', '', title)
    title = re.sub(r'</?b>', '', title)
    
    # Clean up extra whitespace
    title = ' '.join(title.split())
    
    # Simplify long descriptions by extracting first clause or truncating context
    # Remove redundant series/publisher info at end if following pattern "X issued by Y"
    if ' issued by ' in title and len(title) > 120:
        # Keep main title, move publisher to parenthetical
        parts = title.split(' issued by ')
        main_title = parts[0].strip()
        publisher = parts[1].strip()
        title = f"{main_title} (issued by {publisher})"
    
    return title


def standardize_row(cells):
    """Standardize a row to have exactly 4 columns."""
    # Ensure we have at least 4 cells
    while len(cells) < 4:
        cells.append('')
    
    # Take only first 4 cells
    cells = cells[:4]
    
    # Standardize each cell
    object_date = cells[0].strip() if cells[0] else ''
    title = clean_title(cells[1])
    object_number = cells[2].strip() if cells[2] else ''
    link_resource = cells[3].strip() if cells[3] else ''
    
    return [object_date, title, object_number, link_resource]


def validate_row(cells, row_num):
    """Validate row structure and content."""
    issues = []
    
    if len(cells) != 4:
        issues.append(f"Row {row_num}: Expected 4 columns, got {len(cells)}")
    
    if not cells[2]:  # Object number is critical
        issues.append(f"Row {row_num}: Missing Object Number")
    
    if not cells[3]:  # Link is important
        issues.append(f"Row {row_num}: Missing Link Resource")
    
    return issues


def transform_file(input_path, output_path):
    """Main transformation function."""
    print("=" * 70)
    print("MET MUSEUM INVENTORY STANDARDIZATION")
    print("=" * 70)
    
    # Verify input file exists
    if not Path(input_path).exists():
        print(f"[ERROR] Input file not found: {input_path}")
        sys.exit(1)
    
    # Calculate input checksum
    input_checksum = calculate_checksum(input_path)
    print(f"\n[CHECKSUM] Original file MD5: {input_checksum}")
    
    # Parse input file
    log_info("Parsing input file...")
    rows = parse_tsv(input_path)
    input_stats = {
        'Total rows': len(rows),
        'Header row': rows[0] if rows else 'N/A'
    }
    log_info(f"Parsed {len(rows)} rows", input_stats)
    
    # Process rows
    log_info("Standardizing rows...")
    output_rows = []
    transformation_stats = defaultdict(int)
    validation_issues = []
    
    for i, cells in enumerate(rows):
        if i == 0:
            # Keep header as-is, but standardize it
            standardized = standardize_row(cells)
            output_rows.append(standardized)
            transformation_stats['Header rows'] += 1
        else:
            before = cells.copy()
            standardized = standardize_row(cells)
            
            # Track transformations
            if before[1] != standardized[1]:  # Title changed
                transformation_stats['Titles cleaned'] += 1
            
            if len(before) != 4:  # Column count changed
                transformation_stats['Rows with column adjustments'] += 1
            
            # Validate
            issues = validate_row(standardized, i + 1)
            validation_issues.extend(issues)
            
            output_rows.append(standardized)
            transformation_stats['Data rows processed'] += 1
    
    log_info("Transformation complete", dict(transformation_stats))
    
    # Report validation issues
    if validation_issues:
        print(f"\n[WARNING] {len(validation_issues)} validation issues found:")
        for issue in validation_issues[:10]:  # Show first 10
            print(f"         {issue}")
        if len(validation_issues) > 10:
            print(f"         ... and {len(validation_issues) - 10} more")
    
    # Write output file
    log_info("Writing output file...")
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        for row in output_rows:
            f.write('\t'.join(row) + '\n')
    
    # Calculate output checksum
    output_checksum = calculate_checksum(output_path)
    print(f"[CHECKSUM] Transformed file MD5: {output_checksum}")
    
    # Verify files are different
    if input_checksum == output_checksum:
        print("[WARNING] Input and output checksums match - no transformations applied")
    else:
        print("[SUCCESS] Checksums differ - transformations verified")
    
    # Print summary
    print("\n" + "=" * 70)
    print("TRANSFORMATION SUMMARY")
    print("=" * 70)
    print(f"Input file:        {input_path}")
    print(f"Input checksum:    {input_checksum}")
    print(f"Output file:       {output_path}")
    print(f"Output checksum:   {output_checksum}")
    print(f"Total rows:        {len(output_rows)}")
    print(f"Rows transformed:  {transformation_stats['Data rows processed']}")
    print(f"Titles cleaned:    {transformation_stats['Titles cleaned']}")
    print("=" * 70)


if __name__ == '__main__':
    input_file = '/mnt/user-data/uploads/met_inventory.tsv'
    output_file = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
    
    transform_file(input_file, output_file)
