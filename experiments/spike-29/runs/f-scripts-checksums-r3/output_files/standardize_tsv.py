#!/usr/bin/env python3
"""
Standardize TSV file with checksum verification for data fixity.

This script:
1. Reads a TSV file
2. Normalizes header names (snake_case)
3. Standardizes data (empty cells marked as "N/A")
4. Computes SHA256 checksums of source and result
5. Generates a report
"""

import csv
import hashlib
import json
from pathlib import Path
from datetime import datetime


def compute_checksum(file_path):
    """Compute SHA256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def normalize_header(header):
    """Convert header to snake_case."""
    # Replace spaces with underscores and convert to lowercase
    normalized = header.strip().lower().replace(" ", "_")
    return normalized


def standardize_row(row):
    """Standardize a data row by replacing empty cells with N/A."""
    return [cell.strip() if cell.strip() else "N/A" for cell in row]


def standardize_tsv(input_path, output_path):
    """
    Standardize a TSV file.
    
    Returns a dict with checksums and processing stats.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    
    # Compute source checksum
    source_checksum = compute_checksum(input_path)
    
    # Read and standardize the TSV
    rows = []
    headers = None
    
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for i, row in enumerate(reader):
            if i == 0:
                # Normalize headers
                headers = [normalize_header(h) for h in row]
            else:
                # Standardize data rows
                standardized_row = standardize_row(row)
                rows.append(standardized_row)
    
    # Write standardized TSV
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(headers)
        writer.writerows(rows)
    
    # Compute result checksum
    result_checksum = compute_checksum(output_path)
    
    # Generate report
    report = {
        "timestamp": datetime.now().isoformat(),
        "source_file": str(input_path),
        "output_file": str(output_path),
        "source_checksum_sha256": source_checksum,
        "result_checksum_sha256": result_checksum,
        "total_rows": len(rows),
        "columns": headers,
        "column_count": len(headers),
        "changes": {
            "headers_normalized": True,
            "empty_cells_standardized": True,
            "delimiter": "tab"
        }
    }
    
    return report


def main():
    """Main execution function."""
    input_file = Path("/mnt/user-data/uploads/met_inventory.tsv")
    output_file = Path("/mnt/user-data/outputs/met_inventory_standardized.tsv")
    report_file = Path("/mnt/user-data/outputs/standardization_report.json")
    
    if not input_file.exists():
        print(f"Error: Input file not found at {input_file}")
        return 1
    
    print(f"Processing: {input_file}")
    report = standardize_tsv(input_file, output_file)
    
    # Write report
    report_file.parent.mkdir(parents=True, exist_ok=True)
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print("STANDARDIZATION COMPLETE")
    print("="*60)
    print(f"\nSource File: {report['source_file']}")
    print(f"  Checksum (SHA256): {report['source_checksum_sha256']}")
    print(f"\nOutput File: {report['output_file']}")
    print(f"  Checksum (SHA256): {report['result_checksum_sha256']}")
    print(f"\nData Summary:")
    print(f"  Total rows: {report['total_rows']}")
    print(f"  Columns: {report['column_count']}")
    print(f"  Column names: {', '.join(report['columns'])}")
    print(f"\nChanges Applied:")
    for change, value in report['changes'].items():
        print(f"  • {change}: {value}")
    print(f"\nReport saved to: {report_file}")
    print("="*60)
    
    return 0


if __name__ == "__main__":
    exit(main())
