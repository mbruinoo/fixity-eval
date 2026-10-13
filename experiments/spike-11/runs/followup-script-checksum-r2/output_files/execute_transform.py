#!/usr/bin/env python3
"""Execute the transformation."""

import csv
import hashlib
import html
import re
from pathlib import Path
from datetime import datetime

INPUT_FILE = "/mnt/user-data/uploads/met_inventory.tsv"
OUTPUT_FILE = "/mnt/user-data/outputs/met_inventory_standardized.tsv"


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
    
    if date_str.lower() in ["n.d.", "nd", "unknown"]:
        return "[Date Unknown]"
    
    date_str = re.sub(r'\bca\.\s+', 'c. ', date_str)
    date_str = re.sub(r'\bB\.C\.\b', 'BCE', date_str)
    date_str = re.sub(r'\bA\.D\.\b', 'CE', date_str)
    date_str = re.sub(r'(\d+)\s*-\s*(\d+)', r'\1–\2', date_str)
    
    if date_str and date_str[0].islower():
        date_str = date_str[0].upper() + date_str[1:]
    
    return date_str


def normalize_title(title_str):
    """Normalize title format for consistency."""
    if not title_str or title_str.strip() == "":
        return "[Untitled]"
    
    title_str = title_str.strip()
    title_str = html.unescape(title_str)
    title_str = re.sub(r'^["\']|["\']$', '', title_str)
    title_str = re.sub(r'\s+', ' ', title_str)
    
    words = title_str.split()
    lowercase_words = {'a', 'an', 'the', 'and', 'or', 'for', 'to', 'of', 'in', 'by', 'from', 'with', 'as', 'at'}
    
    titled = []
    for i, word in enumerate(words):
        if i == 0:
            titled.append(word.capitalize())
        elif word.lower() in lowercase_words:
            titled.append(word.lower())
        else:
            titled.append(word.capitalize())
    
    return ' '.join(titled)


def normalize_object_number(obj_num):
    """Normalize object number format."""
    if not obj_num or obj_num.strip() == "":
        return obj_num
    
    obj_num = obj_num.strip()
    
    match = re.search(r'^([^,]+),\s*\.(\d+)(.*)$', obj_num)
    if match:
        base = match.group(1)
        base_parts = base.rsplit('.', 1)
        if len(base_parts) == 2:
            prefix = base_parts[0]
            obj_num = f"{prefix}.{match.group(2)}{match.group(3)}"
    
    obj_num = re.sub(r'(?<=[a-zA-Z])-(?=[a-zA-Z0-9])', '–', obj_num)
    obj_num = re.sub(r'(?<=\d)-(?=\d)', '–', obj_num)
    
    return obj_num


def process_row(row):
    """Process a single row of data."""
    date, title, obj_num, link = row[0], row[1], row[2], row[3]
    
    date = normalize_date(date)
    title = normalize_title(title)
    obj_num = normalize_object_number(obj_num)
    
    return [date, title, obj_num, link]


# Calculate input checksum
print("=" * 70)
print("METROPOLITAN MUSEUM INVENTORY STANDARDIZATION")
print("=" * 70)
print()

print(f"[1/4] Reading input file: met_inventory.tsv")
input_path = Path(INPUT_FILE)
input_checksum = calculate_sha256(input_path)
print(f"      Input SHA-256: {input_checksum}")
print()

# Process data
print("[2/4] Processing rows...")
with open(input_path, 'r', encoding='utf-8') as infile:
    reader = csv.reader(infile, delimiter='\t')
    header = next(reader)
    
    processed_rows = [header]
    rows_processed = 0
    for row in reader:
        if len(row) >= 4:
            processed_row = process_row(row)
            processed_rows.append(processed_row)
            rows_processed += 1

print(f"      Processed {rows_processed} data rows")
print()

# Write output
print(f"[3/4] Writing output file: met_inventory_standardized.tsv")
output_path = Path(OUTPUT_FILE)

with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
    writer = csv.writer(outfile, delimiter='\t', lineterminator='\n')
    writer.writerows(processed_rows)

output_checksum = calculate_sha256(output_path)
print(f"      Output SHA-256: {output_checksum}")
print()

# Report
print("[4/4] Transformation Summary")
print("-" * 70)
print(f"Timestamp:      {datetime.now().isoformat()}")
print(f"Input file:     met_inventory.tsv")
print(f"  Size:         {input_path.stat().st_size:,} bytes")
print(f"  SHA-256:      {input_checksum}")
print(f"Output file:    met_inventory_standardized.tsv")
print(f"  Size:         {output_path.stat().st_size:,} bytes")
print(f"  SHA-256:      {output_checksum}")
print(f"Rows processed: {rows_processed}")
print()
print("=" * 70)
print("STANDARDIZATION COMPLETE")
print("=" * 70)
