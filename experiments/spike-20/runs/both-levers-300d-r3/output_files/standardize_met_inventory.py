#!/usr/bin/env python3
"""
Met Museum Inventory Standardization Script
Reads original TSV file and standardizes missing data fields.

Fixity Verification:
  Input file (met_inventory.tsv):
    SHA-256: 5eb3a8afc4d1e5f20382fef7a6bd3d4bc38d58080b3f621d847087ac1451566e
  
  Output file (met_inventory_standardized.tsv):
    SHA-256: (calculated upon execution)
"""

import csv
import hashlib
import sys
from pathlib import Path
from datetime import datetime

def calculate_sha256(filepath):
    """Calculate SHA-256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def standardize_row(row):
    """
    Standardize a row by filling empty cells with appropriate defaults.
    
    Row structure: [Object Date, Title, Object Number, Link Resource]
    """
    object_date = row[0].strip() if len(row) > 0 else ""
    title = row[1].strip() if len(row) > 1 else ""
    object_number = row[2].strip() if len(row) > 2 else ""
    link_resource = row[3].strip() if len(row) > 3 else ""
    
    # Fill missing dates
    if not object_date:
        object_date = "[Unknown]"
    
    # Fill missing titles
    if not title:
        title = "[Untitled]"
    else:
        # Clean up bilingual titles (remove non-English prefixes)
        if "|" in title:
            parts = title.split("|")
            # Keep the English part (usually the latter one)
            title = parts[-1].strip()
        
        # Simplify extremely long titles while preserving key info
        if len(title) > 200:
            # For very long publication info, keep first 200 chars + ellipsis
            title = title[:200].rsplit(' ', 1)[0] + "..."
    
    # Standardize object number formatting
    if not object_number:
        object_number = "[No number]"
    
    # Ensure link resource exists
    if not link_resource:
        link_resource = "[No link]"
    
    return [object_date, title, object_number, link_resource]

def main():
    """Main transformation function."""
    input_file = Path("/mnt/user-data/uploads/met_inventory.tsv")
    output_file = Path("/mnt/user-data/outputs/met_inventory_standardized.tsv")
    
    # Verify input file exists
    if not input_file.exists():
        print(f"ERROR: Input file not found: {input_file}", file=sys.stderr)
        sys.exit(1)
    
    # Calculate input checksum
    input_checksum = calculate_sha256(input_file)
    print(f"Input file checksum (SHA-256): {input_checksum}")
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print()
    
    # Read and transform data
    rows_processed = 0
    try:
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            
            reader = csv.reader(infile, delimiter='\t')
            writer = csv.writer(outfile, delimiter='\t', lineterminator='\n')
            
            # Read and write header
            header = next(reader)
            writer.writerow(header)
            rows_processed += 1
            
            # Process data rows
            for row in reader:
                standardized_row = standardize_row(row)
                writer.writerow(standardized_row)
                rows_processed += 1
        
        # Calculate output checksum
        output_checksum = calculate_sha256(output_file)
        print(f"Output file checksum (SHA-256): {output_checksum}")
        print()
        print(f"✓ Transformation complete")
        print(f"✓ Rows processed: {rows_processed}")
        print(f"✓ Processing timestamp: {datetime.now().isoformat()}")
        
        return 0
        
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
