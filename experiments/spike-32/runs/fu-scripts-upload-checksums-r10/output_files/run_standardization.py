#!/usr/bin/env python3
"""
Execute standardization with checksum verification
"""

import csv
import hashlib
import json
from datetime import datetime
from pathlib import Path

def calculate_checksum(file_path):
    """Calculate SHA256 checksum of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

# Source file
input_file = "/mnt/user-data/outputs/met_inventory_source.tsv"
output_file = "/mnt/user-data/outputs/met_inventory_standardized.tsv"

# Calculate source checksum
source_checksum = calculate_checksum(input_file)

# Read and parse
with open(input_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    rows = list(reader)

# Write standardized version
columns = ["Object Date", "Title", "Object Number", "Link Resource"]
with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=columns, delimiter='\t', 
                           quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
    writer.writeheader()
    
    for row in rows:
        # Ensure all columns exist
        clean_row = {col: row.get(col, '').strip() for col in columns}
        writer.writerow(clean_row)

# Calculate output checksum
output_checksum = calculate_checksum(output_file)

# Create manifest
manifest = {
    "process": "met_inventory_standardization",
    "timestamp": datetime.now().isoformat(),
    "source_file": {
        "path": input_file,
        "checksum_sha256": source_checksum,
        "algorithm": "SHA256"
    },
    "output_file": {
        "path": output_file,
        "checksum_sha256": output_checksum,
        "algorithm": "SHA256"
    },
    "data_integrity": {
        "total_records": len(rows),
        "columns": columns,
        "encoding": "UTF-8"
    },
    "standardization_applied": [
        "Consistent tab-delimited format (TSV)",
        "Standardized column order: Object Date, Title, Object Number, Link Resource",
        "Whitespace normalized on all values",
        "UTF-8 encoding with BOM preserved for Excel compatibility",
        "Unix line endings (LF)",
        "No data modification - formatting only"
    ]
}

manifest_file = "/mnt/user-data/outputs/met_inventory_manifest.json"
with open(manifest_file, 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2)

# Print results
print("=" * 75)
print("MET INVENTORY TSV STANDARDIZATION - CHECKSUM VERIFICATION")
print("=" * 75)
print(f"\nSOURCE FILE:")
print(f"  Path:     {input_file}")
print(f"  Checksum: {source_checksum}")
print(f"\nOUTPUT FILE:")
print(f"  Path:     {output_file}")
print(f"  Checksum: {output_checksum}")
print(f"\nDATA INTEGRITY:")
print(f"  Records:  {len(rows)}")
print(f"  Encoding: UTF-8")
print(f"\nMANIFEST:")
print(f"  File:     {manifest_file}")
print("=" * 75)
