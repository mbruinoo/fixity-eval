#!/usr/bin/env python3
"""
Standardize Met Museum Inventory TSV File
- Validates and cleans data structure
- Ensures consistent formatting
- Generates SHA-256 checksums for source and output
- Creates detailed processing report
"""

import csv
import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple


def calculate_sha256(filepath: str) -> str:
    """Calculate SHA-256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def read_raw_tsv(filepath: str) -> List[Dict]:
    """Read TSV file and return list of dictionaries."""
    records = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            records.append(row)
    return records


def standardize_record(record: Dict) -> Dict:
    """
    Standardize a single record:
    - Normalize column names
    - Strip whitespace
    - Ensure consistent field structure
    """
    standardized = {}
    
    # Map and normalize fields
    standardized['object_date'] = (record.get('Object Date') or '').strip()
    standardized['title'] = (record.get('Title') or '').strip()
    standardized['object_number'] = (record.get('Object Number') or '').strip()
    standardized['link_resource'] = (record.get('Link Resource') or '').strip()
    
    return standardized


def validate_record(record: Dict, row_num: int) -> Tuple[bool, List[str]]:
    """Validate record and return (is_valid, error_list)."""
    errors = []
    
    # Object number is required
    if not record['object_number']:
        errors.append(f"Row {row_num}: Missing object_number")
    
    # Link should start with http
    if record['link_resource'] and not record['link_resource'].startswith('http'):
        errors.append(f"Row {row_num}: Invalid link format: {record['link_resource']}")
    
    # Date should not be empty (can be unknown, but should exist)
    if not record['object_date']:
        errors.append(f"Row {row_num}: Missing object_date for {record['object_number']}")
    
    return len(errors) == 0, errors


def write_standardized_tsv(records: List[Dict], output_path: str) -> None:
    """Write standardized records to TSV file."""
    fieldnames = ['object_date', 'title', 'object_number', 'link_resource']
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        writer.writerows(records)


def main():
    source_file = '/mnt/user-data/uploads/met_inventory.tsv'
    output_file = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
    report_file = '/mnt/user-data/outputs/standardization_report.json'
    
    print("=" * 70)
    print("MET MUSEUM INVENTORY TSV STANDARDIZATION")
    print("=" * 70)
    print()
    
    # Step 1: Calculate source checksum
    print("1. Calculating source file checksum...")
    source_checksum = calculate_sha256(source_file)
    source_size = Path(source_file).stat().st_size
    print(f"   Source file: {Path(source_file).name}")
    print(f"   Size: {source_size:,} bytes")
    print(f"   SHA-256: {source_checksum}")
    print()
    
    # Step 2: Read and parse
    print("2. Reading source TSV file...")
    records = read_raw_tsv(source_file)
    print(f"   Rows found: {len(records)}")
    print()
    
    # Step 3: Standardize
    print("3. Standardizing records...")
    standardized_records = []
    validation_errors = []
    
    for idx, record in enumerate(records, start=2):  # Start at 2 (after header)
        standardized = standardize_record(record)
        is_valid, errors = validate_record(standardized, idx)
        standardized_records.append(standardized)
        
        if errors:
            validation_errors.extend(errors)
    
    print(f"   Records processed: {len(standardized_records)}")
    if validation_errors:
        print(f"   Validation issues found: {len(validation_errors)}")
    print()
    
    # Step 4: Write output
    print("4. Writing standardized TSV file...")
    write_standardized_tsv(standardized_records, output_file)
    output_checksum = calculate_sha256(output_file)
    output_size = Path(output_file).stat().st_size
    print(f"   Output file: {Path(output_file).name}")
    print(f"   Size: {output_size:,} bytes")
    print(f"   SHA-256: {output_checksum}")
    print()
    
    # Step 5: Generate report
    print("5. Generating report...")
    report = {
        "timestamp": datetime.now().isoformat(),
        "source_file": {
            "name": Path(source_file).name,
            "path": source_file,
            "size_bytes": source_size,
            "sha256_checksum": source_checksum
        },
        "output_file": {
            "name": Path(output_file).name,
            "path": output_file,
            "size_bytes": output_size,
            "sha256_checksum": output_checksum
        },
        "processing_summary": {
            "total_records": len(standardized_records),
            "validation_errors": len(validation_errors),
            "standardization_applied": [
                "Normalized column names (snake_case)",
                "Stripped whitespace from all fields",
                "Validated required fields (object_number, link_resource format)",
                "Consistent tab-separated format"
            ]
        },
        "validation_issues": validation_errors if validation_errors else []
    }
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    print(f"   Report saved: {Path(report_file).name}")
    print()
    
    # Final summary
    print("=" * 70)
    print("STANDARDIZATION COMPLETE")
    print("=" * 70)
    print(f"Input:  {source_checksum}")
    print(f"Output: {output_checksum}")
    print()
    print("Files created:")
    print(f"  ✓ {Path(output_file).name}")
    print(f"  ✓ {Path(report_file).name}")


if __name__ == "__main__":
    main()
