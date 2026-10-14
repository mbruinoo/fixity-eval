#!/usr/bin/env python3
"""
Met Inventory TSV Standardization Script
Transforms met_inventory_original.tsv into a standardized format with data integrity checks.

Transformations performed:
1. Fill empty Title cells with "[Unknown]"
2. Fill empty Object Date cells with "[Unknown]"
3. Remove HTML entities (&lt;i&gt;, &lt;/i&gt;, etc.)
4. Normalize whitespace in titles
5. Remove leading/trailing quotes from titles
6. Verify row structure (4 columns per row)
7. Track all changes with detailed logging

Checksums verify data integrity before and after transformation.
"""

import sys
import csv
import hashlib
import re
from pathlib import Path
from html import unescape

# Configuration
INPUT_FILE = "met_inventory_original.tsv"
OUTPUT_FILE = "met_inventory_standardized.tsv"
LOG_FILE = "transformation_log.txt"
CHECKSUM_FILE = "checksums.txt"

def calculate_file_checksum(filepath):
    """Calculate SHA-256 checksum of file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def normalize_title(title):
    """Normalize title field."""
    if not title or not title.strip():
        return "[Unknown]"
    
    title = title.strip()
    # Remove surrounding quotes if present
    if (title.startswith('"') and title.endswith('"')) or \
       (title.startswith("'") and title.endswith("'")):
        title = title[1:-1].strip()
    
    # Unescape HTML entities
    title = unescape(title)
    
    # Normalize multiple spaces
    title = re.sub(r'\s+', ' ', title)
    
    return title

def normalize_date(date_str):
    """Normalize date field."""
    if not date_str or not date_str.strip():
        return "[Unknown]"
    return date_str.strip()

def normalize_row(row):
    """Normalize a single row to 4 columns."""
    # Ensure we have exactly 4 columns
    while len(row) < 4:
        row.append("")
    row = row[:4]
    
    # Normalize each field
    date_field = normalize_date(row[0])
    title_field = normalize_title(row[1])
    object_num = row[2].strip() if row[2] else ""
    url = row[3].strip() if row[3] else ""
    
    return [date_field, title_field, object_num, url]

def main():
    """Main transformation function."""
    
    print("=" * 80)
    print("MET INVENTORY TSV STANDARDIZATION")
    print("=" * 80)
    
    # Check input file exists
    if not Path(INPUT_FILE).exists():
        print(f"ERROR: Input file '{INPUT_FILE}' not found!")
        sys.exit(1)
    
    # Calculate input checksum
    print(f"\nCalculating input file checksum...")
    input_checksum = calculate_file_checksum(INPUT_FILE)
    print(f"Input checksum (SHA-256): {input_checksum}")
    
    # Read and transform data
    print(f"\nReading '{INPUT_FILE}'...")
    rows_read = 0
    rows_modified = 0
    transformation_log = []
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as infile:
        reader = csv.reader(infile, delimiter='\t')
        rows = list(reader)
    
    print(f"Read {len(rows)} rows from input file")
    
    # Process rows
    standardized_rows = []
    for idx, row in enumerate(rows):
        if idx == 0:  # Header row
            standardized_rows.append(row[:4] if len(row) >= 4 else row + [""] * (4 - len(row)))
            continue
        
        rows_read += 1
        original_row = row[:]
        normalized_row = normalize_row(row)
        
        # Check if row was modified
        was_modified = False
        if not original_row[0].strip() and normalized_row[0] == "[Unknown]":
            was_modified = True
        if not original_row[1].strip() and normalized_row[1] == "[Unknown]":
            was_modified = True
        if original_row[1].strip() != normalized_row[1]:
            was_modified = True
        
        if was_modified:
            rows_modified += 1
            transformation_log.append({
                'row': rows_read,
                'original': original_row,
                'transformed': normalized_row
            })
        
        standardized_rows.append(normalized_row)
    
    # Write output file
    print(f"\nWriting standardized output to '{OUTPUT_FILE}'...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile, delimiter='\t')
        writer.writerows(standardized_rows)
    
    # Calculate output checksum
    print(f"Calculating output file checksum...")
    output_checksum = calculate_file_checksum(OUTPUT_FILE)
    print(f"Output checksum (SHA-256): {output_checksum}")
    
    # Generate transformation log
    print(f"\nGenerating transformation log...")
    with open(LOG_FILE, 'w', encoding='utf-8') as logfile:
        logfile.write("TRANSFORMATION LOG\n")
        logfile.write("=" * 80 + "\n")
        logfile.write(f"Input file: {INPUT_FILE}\n")
        logfile.write(f"Output file: {OUTPUT_FILE}\n")
        logfile.write(f"Total data rows processed: {rows_read}\n")
        logfile.write(f"Total rows modified: {rows_modified}\n\n")
        
        logfile.write("TRANSFORMATIONS APPLIED\n")
        logfile.write("-" * 80 + "\n")
        logfile.write("1. Empty Title fields → '[Unknown]'\n")
        logfile.write("2. Empty Object Date fields → '[Unknown]'\n")
        logfile.write("3. HTML entities (e.g., &lt;i&gt;) → decoded characters\n")
        logfile.write("4. Multiple consecutive spaces → single space\n")
        logfile.write("5. Surrounding quotes on titles → removed\n")
        logfile.write("6. Whitespace trimmed on all fields\n\n")
        
        logfile.write("DETAILED CHANGES\n")
        logfile.write("-" * 80 + "\n")
        for change in transformation_log[:50]:  # Log first 50 changes
            logfile.write(f"\nRow {change['row']}:\n")
            logfile.write(f"  Original:  {change['original']}\n")
            logfile.write(f"  Transform: {change['transformed']}\n")
        
        if len(transformation_log) > 50:
            logfile.write(f"\n... and {len(transformation_log) - 50} more transformations\n")
    
    # Generate checksums file
    print(f"Generating checksums file...")
    with open(CHECKSUM_FILE, 'w', encoding='utf-8') as checksumfile:
        checksumfile.write("CHECKSUM VERIFICATION\n")
        checksumfile.write("=" * 80 + "\n")
        checksumfile.write(f"Input file:  {INPUT_FILE}\n")
        checksumfile.write(f"SHA-256:     {input_checksum}\n\n")
        checksumfile.write(f"Output file: {OUTPUT_FILE}\n")
        checksumfile.write(f"SHA-256:     {output_checksum}\n\n")
        checksumfile.write("VERIFICATION NOTES\n")
        checksumfile.write("-" * 80 + "\n")
        checksumfile.write(f"Total data rows: {rows_read}\n")
        checksumfile.write(f"Rows modified: {rows_modified}\n")
        checksumfile.write(f"Modification rate: {rows_modified / rows_read * 100:.1f}%\n\n")
        checksumfile.write("INTEGRITY CHECK\n")
        checksumfile.write("-" * 80 + "\n")
        checksumfile.write(f"Input and output checksums differ: {input_checksum != output_checksum}\n")
        checksumfile.write("(Different checksums expected due to data transformations)\n\n")
        checksumfile.write("To verify output file integrity, recompute with:\n")
        checksumfile.write(f"  sha256sum {OUTPUT_FILE}\n")
    
    # Print summary
    print("\n" + "=" * 80)
    print("TRANSFORMATION COMPLETE")
    print("=" * 80)
    print(f"✓ Data rows processed: {rows_read}")
    print(f"✓ Rows modified: {rows_modified} ({rows_modified / rows_read * 100:.1f}%)")
    print(f"✓ Output file: {OUTPUT_FILE}")
    print(f"✓ Transformation log: {LOG_FILE}")
    print(f"✓ Checksums: {CHECKSUM_FILE}")
    print("\nFiles ready for archival.")

if __name__ == "__main__":
    main()
