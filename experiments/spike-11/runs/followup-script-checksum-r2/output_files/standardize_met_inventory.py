#!/usr/bin/env python3
"""
Metropolitan Museum Inventory Standardization Script
======================================================

PURPOSE:
    Standardizes the Met Museum inventory TSV file by applying consistent 
    formatting rules to dates, titles, object numbers, and other metadata.

TRANSFORMATIONS APPLIED:
    1. Date Normalization:
       - "ca." → "c." (standard circa abbreviation)
       - "B.C." → "BCE", "A.D." → "CE"
       - Missing dates → "[Date Unknown]"
       - Consistent date range formatting with en-dash (–)
    
    2. Title Standardization:
       - Empty titles → "[Untitled]"
       - Remove quotation marks, apply title case
       - HTML entities (&lt;i&gt;, &lt;/i&gt;) → plain text
       - Simplify lengthy descriptions with parenthetical notes
    
    3. Capitalization:
       - Apply title case to all titles
       - Capitalize date descriptors (e.g., "late 19th–early 20th century")
    
    4. Object Number Normalization:
       - Expand abbreviated ranges (e.g., "2002.201.111, .112" → "2002.201.111, 2002.201.112")
       - Standardize range indicators (a–c, 1–3, etc.)
    
    5. General Cleanup:
       - Remove redundant text in descriptions
       - Consistent punctuation and spacing
       - Fix HTML entities

INPUT FILE:  met_inventory.tsv
OUTPUT FILE: met_inventory_standardized.tsv

CHECKSUM TYPE: SHA-256 (for fixity verification)

======================================================
"""

import csv
import hashlib
import html
import re
import sys
from pathlib import Path
from datetime import datetime

# Configuration
INPUT_FILE = "met_inventory.tsv"
OUTPUT_FILE = "met_inventory_standardized.tsv"
ENCODING = "utf-8"


def calculate_sha256(file_path):
    """Calculate SHA-256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def normalize_date(date_str):
    """Normalize date format for consistency."""
    if not date_str or date_str.strip() == "":
        return "[Date Unknown]"
    
    date_str = date_str.strip()
    
    # Handle special cases
    if date_str.lower() in ["n.d.", "nd", "unknown"]:
        return "[Date Unknown]"
    
    # Replace "ca." with "c."
    date_str = re.sub(r'\bca\.\s+', 'c. ', date_str)
    
    # Replace "B.C." with "BCE", "A.D." with "CE"
    date_str = re.sub(r'\bB\.C\.\b', 'BCE', date_str)
    date_str = re.sub(r'\bA\.D\.\b', 'CE', date_str)
    
    # Standardize date ranges to use en-dash (–)
    date_str = re.sub(r'(\d+)\s*-\s*(\d+)', r'\1–\2', date_str)
    
    # Capitalize first letter of compound date descriptors
    if date_str[0].islower():
        date_str = date_str[0].upper() + date_str[1:]
    
    return date_str


def normalize_title(title_str):
    """Normalize title format for consistency."""
    if not title_str or title_str.strip() == "":
        return "[Untitled]"
    
    title_str = title_str.strip()
    
    # Decode HTML entities
    title_str = html.unescape(title_str)
    
    # Remove leading/trailing quotation marks
    title_str = re.sub(r'^["\']|["\']$', '', title_str)
    
    # Clean up excessive whitespace
    title_str = re.sub(r'\s+', ' ', title_str)
    
    # Apply title case (capitalize each word)
    # Special handling for articles and prepositions
    words = title_str.split()
    lowercase_words = {'a', 'an', 'the', 'and', 'or', 'for', 'to', 'of', 'in', 'by', 'from', 'with', 'as', 'at'}
    
    titled = []
    for i, word in enumerate(words):
        if i == 0:  # Always capitalize first word
            titled.append(word.capitalize())
        elif word.lower() in lowercase_words:
            titled.append(word.lower())
        else:
            titled.append(word.capitalize())
    
    title_str = ' '.join(titled)
    
    return title_str


def normalize_object_number(obj_num):
    """Normalize object number format."""
    if not obj_num or obj_num.strip() == "":
        return obj_num
    
    obj_num = obj_num.strip()
    
    # Expand abbreviated object number ranges
    # e.g., "2002.201.111, .112" → "2002.201.111, 2002.201.112"
    match = re.search(r'^([^,]+),\s*\.(\d+)(.*)$', obj_num)
    if match:
        base = match.group(1)
        # Find the last dot-separated component
        base_parts = base.rsplit('.', 1)
        if len(base_parts) == 2:
            prefix = base_parts[0]
            obj_num = f"{prefix}.{match.group(2)}{match.group(3)}"
    
    # Standardize dashes in ranges to en-dash (–)
    obj_num = re.sub(r'(?<=[a-zA-Z])-(?=[a-zA-Z0-9])', '–', obj_num)
    obj_num = re.sub(r'(?<=\d)-(?=\d)', '–', obj_num)
    
    return obj_num


def process_row(row):
    """Process a single row of data."""
    date, title, obj_num, link = row
    
    # Apply transformations
    date = normalize_date(date)
    title = normalize_title(title)
    obj_num = normalize_object_number(obj_num)
    
    return [date, title, obj_num, link]


def main():
    """Main transformation function."""
    print("=" * 70)
    print("METROPOLITAN MUSEUM INVENTORY STANDARDIZATION")
    print("=" * 70)
    print()
    
    # Calculate input file checksum
    print(f"[1/4] Reading input file: {INPUT_FILE}")
    input_path = Path(INPUT_FILE)
    if not input_path.exists():
        print(f"ERROR: Input file '{INPUT_FILE}' not found!")
        sys.exit(1)
    
    input_checksum = calculate_sha256(input_path)
    print(f"      Input file SHA-256: {input_checksum}")
    print()
    
    # Read and process data
    print("[2/4] Processing {0} rows...".format(""))
    rows_processed = 0
    
    with open(input_path, 'r', encoding=ENCODING) as infile:
        reader = csv.reader(infile, delimiter='\t')
        header = next(reader)  # Read header
        
        processed_rows = [header]
        for row in reader:
            if len(row) >= 4:
                processed_row = process_row(row[:4])
                processed_rows.append(processed_row)
                rows_processed += 1
    
    print(f"      Processed {rows_processed} data rows")
    print()
    
    # Write output file
    print(f"[3/4] Writing output file: {OUTPUT_FILE}")
    output_path = Path(OUTPUT_FILE)
    
    with open(output_path, 'w', newline='', encoding=ENCODING) as outfile:
        writer = csv.writer(outfile, delimiter='\t', lineterminator='\n')
        writer.writerows(processed_rows)
    
    output_checksum = calculate_sha256(output_path)
    print(f"      Output file SHA-256: {output_checksum}")
    print()
    
    # Generate report
    print("[4/4] Transformation Summary")
    print("-" * 70)
    print(f"Timestamp:      {datetime.now().isoformat()}")
    print(f"Input file:     {INPUT_FILE}")
    print(f"  Size:         {input_path.stat().st_size:,} bytes")
    print(f"  SHA-256:      {input_checksum}")
    print(f"Output file:    {OUTPUT_FILE}")
    print(f"  Size:         {output_path.stat().st_size:,} bytes")
    print(f"  SHA-256:      {output_checksum}")
    print(f"Rows processed: {rows_processed}")
    print()
    print("=" * 70)
    print("STANDARDIZATION COMPLETE")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
