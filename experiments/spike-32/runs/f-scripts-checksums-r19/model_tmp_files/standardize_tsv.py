#!/usr/bin/env python3
"""
Standardize TSV file with checksums
"""
import csv
import hashlib
import json
from pathlib import Path
from datetime import datetime

def compute_checksum(filepath):
    """Compute SHA256 checksum of a file"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def standardize_tsv(input_file, output_file, metadata_file):
    """
    Standardize the TSV file:
    - Ensure consistent tab delimiters
    - Normalize whitespace
    - Validate column headers
    - Write with UTF-8 encoding
    """
    
    # Compute source checksum
    source_checksum = compute_checksum(input_file)
    print(f"Source file checksum (SHA256): {source_checksum}")
    
    # Read the file
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse with csv module to handle tabs and quotes properly
    rows = []
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            rows.append(row)
    
    # Validate and standardize
    if not rows:
        print("Error: Empty file")
        return
    
    # Extract header
    headers = rows[0]
    print(f"\nHeaders found: {headers}")
    print(f"Column count: {len(headers)}")
    
    # Standardize all rows
    standardized_rows = [headers]
    row_count = 0
    
    for i, row in enumerate(rows[1:], start=2):
        # Pad rows to match header count
        while len(row) < len(headers):
            row.append('')
        # Trim to header count
        row = row[:len(headers)]
        
        # Strip leading/trailing whitespace from each field
        row = [field.strip() for field in row]
        
        standardized_rows.append(row)
        row_count += 1
    
    # Write standardized file
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t', lineterminator='\n', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(standardized_rows)
    
    # Compute output checksum
    output_checksum = compute_checksum(output_file)
    print(f"\nOutput file checksum (SHA256): {output_checksum}")
    
    # Create metadata file
    metadata = {
        "standardization_date": datetime.now().isoformat(),
        "source_file": Path(input_file).name,
        "output_file": Path(output_file).name,
        "source_checksum": source_checksum,
        "output_checksum": output_checksum,
        "rows_processed": row_count,
        "columns": len(headers),
        "column_headers": headers,
        "changes_made": [
            "Normalized tab delimiters",
            "Stripped leading/trailing whitespace from fields",
            "Ensured consistent row length (padded/trimmed to header count)",
            "UTF-8 encoding enforced",
            "Unix line endings (LF) enforced"
        ]
    }
    
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"\nFile standardization complete!")
    print(f"Data rows processed: {row_count}")
    print(f"Total columns: {len(headers)}")
    print(f"Metadata saved to: {Path(metadata_file).name}")
    
    return metadata

if __name__ == "__main__":
    input_file = "/mnt/user-data/uploads/met_inventory.tsv"
    output_file = "/mnt/user-data/outputs/met_inventory_standardized.tsv"
    metadata_file = "/mnt/user-data/outputs/standardization_metadata.json"
    
    standardize_tsv(input_file, output_file, metadata_file)
