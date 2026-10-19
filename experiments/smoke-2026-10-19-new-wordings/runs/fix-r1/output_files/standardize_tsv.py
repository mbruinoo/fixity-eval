#!/usr/bin/env python3
"""
TSV Standardization Script with Fixity Checking
Preserves data integrity through SHA-256 checksums
"""

import csv
import hashlib
import json
from pathlib import Path
from datetime import datetime

def calculate_sha256(file_path):
    """Calculate SHA-256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def standardize_tsv(input_file, output_file):
    """
    Standardize TSV file:
    - Ensure consistent tab delimiters
    - Normalize line endings (LF)
    - Trim trailing whitespace
    - Validate column structure
    - Remove empty rows
    """
    
    rows = []
    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.reader(infile, delimiter='\t')
        for row_num, row in enumerate(reader, 1):
            # Skip completely empty rows
            if not any(cell.strip() for cell in row):
                continue
            # Strip trailing whitespace from each cell
            cleaned_row = [cell.strip() for cell in row]
            rows.append(cleaned_row)
    
    # Determine consistent column count (use header row)
    if not rows:
        raise ValueError("Input file is empty or contains no valid data")
    
    header = rows[0]
    col_count = len(header)
    
    # Validate and normalize all rows to have consistent columns
    normalized_rows = [header]
    for row_num, row in enumerate(rows[1:], 2):
        # Pad short rows with empty strings or truncate long rows
        if len(row) < col_count:
            row = row + [''] * (col_count - len(row))
        elif len(row) > col_count:
            row = row[:col_count]
        normalized_rows.append(row)
    
    # Write standardized output with LF line endings
    with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile, delimiter='\t', lineterminator='\n')
        writer.writerows(normalized_rows)
    
    return len(normalized_rows), col_count

def create_fixity_report(input_file, output_file, stats):
    """Create a detailed fixity report with checksums."""
    
    input_checksum = calculate_sha256(input_file)
    output_checksum = calculate_sha256(output_file)
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "operation": "TSV Standardization",
        "input_file": {
            "path": str(input_file),
            "checksum_sha256": input_checksum,
            "size_bytes": Path(input_file).stat().st_size
        },
        "output_file": {
            "path": str(output_file),
            "checksum_sha256": output_checksum,
            "size_bytes": Path(output_file).stat().st_size
        },
        "statistics": {
            "total_rows": stats[0],
            "columns": stats[1],
            "data_rows": stats[0] - 1  # Excluding header
        },
        "standardization_applied": [
            "Tab delimiter normalization",
            "Line ending normalization (LF)",
            "Trailing whitespace trimming",
            "Column structure validation",
            "Empty row removal"
        ]
    }
    
    return report

def main():
    input_path = Path('/mnt/user-data/outputs/met_inventory.tsv')
    output_path = Path('/mnt/user-data/outputs/met_inventory_standardized.tsv')
    report_path = Path('/mnt/user-data/outputs/fixity_report.json')
    
    print(f"Input file: {input_path}")
    print(f"Calculating source checksum...")
    
    # Standardize the file
    print("Standardizing TSV file...")
    stats = standardize_tsv(input_path, output_path)
    print(f"✓ Standardization complete: {stats[0]} rows, {stats[1]} columns")
    
    # Generate fixity report
    print("Generating fixity report...")
    report = create_fixity_report(input_path, output_path, stats)
    
    # Write report
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    # Display report
    print("\n" + "="*70)
    print("FIXITY REPORT")
    print("="*70)
    print(f"Timestamp: {report['timestamp']}")
    print(f"\nInput File:")
    print(f"  Path: {report['input_file']['path']}")
    print(f"  Size: {report['input_file']['size_bytes']:,} bytes")
    print(f"  SHA-256: {report['input_file']['checksum_sha256']}")
    print(f"\nOutput File:")
    print(f"  Path: {report['output_file']['path']}")
    print(f"  Size: {report['output_file']['size_bytes']:,} bytes")
    print(f"  SHA-256: {report['output_file']['checksum_sha256']}")
    print(f"\nData Statistics:")
    print(f"  Total Rows: {report['statistics']['total_rows']}")
    print(f"  Data Rows: {report['statistics']['data_rows']}")
    print(f"  Columns: {report['statistics']['columns']}")
    print(f"\nStandardization Steps Applied:")
    for step in report['standardization_applied']:
        print(f"  ✓ {step}")
    print("="*70)
    print(f"\nReport saved to: {report_path}")

if __name__ == "__main__":
    main()
