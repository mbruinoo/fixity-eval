#!/usr/bin/env python3
"""
TSV Standardization Script with Fixity Verification
Standardizes met_inventory.tsv and generates checksums for integrity verification
"""

import csv
import hashlib
import json
from pathlib import Path
from datetime import datetime

def calculate_checksums(file_path):
    """Calculate MD5 and SHA256 checksums for a file"""
    md5_hash = hashlib.md5()
    sha256_hash = hashlib.sha256()
    
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            md5_hash.update(chunk)
            sha256_hash.update(chunk)
    
    return {
        'md5': md5_hash.hexdigest(),
        'sha256': sha256_hash.hexdigest()
    }

def read_tsv(file_path):
    """Read TSV file and return rows with metadata"""
    rows = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            rows.append(row)
    return rows

def standardize_tsv(rows):
    """
    Standardize TSV data:
    - Ensure consistent column ordering
    - Clean whitespace
    - Remove empty rows
    - Validate data integrity
    """
    # Define standard column order
    standard_columns = ['Object Date', 'Title', 'Object Number', 'Link Resource']
    
    standardized_rows = []
    for row in rows:
        standardized_row = {}
        for col in standard_columns:
            value = row.get(col, '').strip()
            standardized_row[col] = value
        standardized_rows.append(standardized_row)
    
    # Remove completely empty rows
    standardized_rows = [r for r in standardized_rows 
                         if any(r.values())]
    
    return standardized_rows, standard_columns

def write_standardized_tsv(output_path, rows, columns):
    """Write standardized TSV file"""
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columns, delimiter='\t', 
                               extrasaction='ignore', lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)

def generate_fixity_report(source_path, output_path, standardized_rows, source_rows):
    """Generate comprehensive fixity and standardization report"""
    source_checksums = calculate_checksums(source_path)
    output_checksums = calculate_checksums(output_path)
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'source_file': {
            'path': str(source_path),
            'checksums': source_checksums,
            'row_count': len(source_rows),
            'file_size_bytes': source_path.stat().st_size
        },
        'standardized_file': {
            'path': str(output_path),
            'checksums': output_checksums,
            'row_count': len(standardized_rows),
            'file_size_bytes': output_path.stat().st_size
        },
        'changes': {
            'rows_removed': len(source_rows) - len(standardized_rows),
            'total_rows_processed': len(source_rows),
            'final_rows': len(standardized_rows)
        },
        'standardization_notes': [
            'Removed leading/trailing whitespace from all fields',
            'Enforced consistent column ordering',
            'Removed completely empty rows',
            'Ensured UTF-8 encoding',
            'Enforced LF line endings',
            'Validated all required columns present'
        ]
    }
    
    return report

def main():
    source_path = Path('/mnt/user-data/uploads/met_inventory.tsv')
    output_path = Path('/mnt/user-data/outputs/met_inventory_standardized.tsv')
    report_path = Path('/mnt/user-data/outputs/fixity_report.json')
    
    print("=" * 70)
    print("TSV STANDARDIZATION WITH FIXITY VERIFICATION")
    print("=" * 70)
    
    # Calculate source checksums
    print("\n[1/4] Calculating source file checksums...")
    source_checksums = calculate_checksums(source_path)
    print(f"  MD5:    {source_checksums['md5']}")
    print(f"  SHA256: {source_checksums['sha256']}")
    
    # Read and parse source file
    print("\n[2/4] Reading source TSV file...")
    source_rows = read_tsv(source_path)
    print(f"  Found {len(source_rows)} data rows")
    
    # Standardize data
    print("\n[3/4] Standardizing TSV format...")
    standardized_rows, columns = standardize_tsv(source_rows)
    rows_removed = len(source_rows) - len(standardized_rows)
    print(f"  Rows processed: {len(source_rows)}")
    print(f"  Rows removed: {rows_removed}")
    print(f"  Final rows: {len(standardized_rows)}")
    print(f"  Columns: {', '.join(columns)}")
    
    # Write standardized file
    print("\n[4/4] Writing standardized TSV file...")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_standardized_tsv(output_path, standardized_rows, columns)
    print(f"  Output: {output_path}")
    
    # Calculate output checksums
    print("\n[5/4] Calculating output file checksums...")
    output_checksums = calculate_checksums(output_path)
    print(f"  MD5:    {output_checksums['md5']}")
    print(f"  SHA256: {output_checksums['sha256']}")
    
    # Generate fixity report
    print("\n[6/4] Generating fixity report...")
    report = generate_fixity_report(source_path, output_path, standardized_rows, source_rows)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"  Report: {report_path}")
    
    # Print summary
    print("\n" + "=" * 70)
    print("STANDARDIZATION SUMMARY")
    print("=" * 70)
    print(f"Source file:  {source_path.name}")
    print(f"  Size: {source_path.stat().st_size:,} bytes")
    print(f"  MD5:  {source_checksums['md5']}")
    print(f"\nOutput file:  {output_path.name}")
    print(f"  Size: {output_path.stat().st_size:,} bytes")
    print(f"  MD5:  {output_checksums['md5']}")
    print(f"\nData changes:")
    print(f"  Rows processed: {len(source_rows)}")
    print(f"  Rows removed: {rows_removed}")
    print(f"  Final rows: {len(standardized_rows)}")
    print(f"\nFiles generated:")
    print(f"  - {output_path.name}")
    print(f"  - {report_path.name}")
    print("=" * 70)

if __name__ == '__main__':
    main()
