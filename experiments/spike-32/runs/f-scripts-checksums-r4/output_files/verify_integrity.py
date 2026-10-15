#!/usr/bin/env python3
"""
Integrity Verification Script
- Validates checksums against report
- Compares source and standardized files
- Generates detailed comparison report
"""

import hashlib
import json
import csv
from pathlib import Path
from typing import Dict, List


def calculate_sha256(filepath: str) -> str:
    """Calculate SHA-256 checksum."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def read_tsv(filepath: str) -> List[Dict]:
    """Read TSV file."""
    records = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            records.append(row)
    return records


def verify_checksums():
    """Verify file checksums against report."""
    report_path = '/mnt/user-data/outputs/standardization_report.json'
    
    with open(report_path, 'r') as f:
        report = json.load(f)
    
    source_file = report['source_file']['path']
    output_file = report['output_file']['path']
    
    print("CHECKSUM VERIFICATION")
    print("=" * 70)
    print()
    
    # Verify source
    print("Source File Verification:")
    reported_source_sha = report['source_file']['sha256_checksum']
    actual_source_sha = calculate_sha256(source_file)
    match = "✓ MATCH" if reported_source_sha == actual_source_sha else "✗ MISMATCH"
    print(f"  Reported: {reported_source_sha}")
    print(f"  Actual:   {actual_source_sha}")
    print(f"  {match}")
    print()
    
    # Verify output
    print("Output File Verification:")
    reported_output_sha = report['output_file']['sha256_checksum']
    actual_output_sha = calculate_sha256(output_file)
    match = "✓ MATCH" if reported_output_sha == actual_output_sha else "✗ MISMATCH"
    print(f"  Reported: {reported_output_sha}")
    print(f"  Actual:   {actual_output_sha}")
    print(f"  {match}")
    print()


def compare_files():
    """Compare source and standardized files."""
    source_file = '/mnt/user-data/outputs/met_inventory_source.tsv'
    output_file = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
    
    source_records = read_tsv(source_file)
    output_records = read_tsv(output_file)
    
    print("RECORD COUNT COMPARISON")
    print("=" * 70)
    print(f"  Source records: {len(source_records)}")
    print(f"  Output records: {len(output_records)}")
    print(f"  Match: {'✓ YES' if len(source_records) == len(output_records) else '✗ NO'}")
    print()
    
    print("FIELD STRUCTURE COMPARISON")
    print("=" * 70)
    
    source_fields = set(source_records[0].keys()) if source_records else set()
    output_fields = set(output_records[0].keys()) if output_records else set()
    
    print(f"  Source fields: {sorted(source_fields)}")
    print(f"  Output fields: {sorted(output_fields)}")
    print()
    
    # Check for data preservation
    print("DATA PRESERVATION CHECK")
    print("=" * 70)
    
    object_numbers_source = {r.get('Object Number', '').strip() for r in source_records}
    object_numbers_output = {r.get('object_number', '').strip() for r in output_records}
    
    missing_in_output = object_numbers_source - object_numbers_output
    added_in_output = object_numbers_output - object_numbers_source
    
    if missing_in_output:
        print(f"  ✗ Missing in output: {len(missing_in_output)} objects")
        for obj_num in sorted(list(missing_in_output))[:5]:
            print(f"    - {obj_num}")
        if len(missing_in_output) > 5:
            print(f"    ... and {len(missing_in_output) - 5} more")
    else:
        print(f"  ✓ All source objects preserved in output")
    
    if added_in_output:
        print(f"  ✗ Added in output: {len(added_in_output)} objects")
    else:
        print(f"  ✓ No spurious objects added")
    
    print()


def main():
    print()
    print("▓" * 70)
    print("MET MUSEUM INVENTORY INTEGRITY VERIFICATION")
    print("▓" * 70)
    print()
    
    verify_checksums()
    compare_files()
    
    print("=" * 70)
    print("VERIFICATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
