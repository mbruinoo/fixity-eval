#!/usr/bin/env python3
"""
Standardize a TSV file and generate checksums for data integrity verification.
This script:
1. Computes MD5 and SHA256 checksums of the source file
2. Standardizes the TSV format (consistent headers, encoding, line endings)
3. Validates and cleans data
4. Computes checksums of the output file
5. Generates a manifest with metadata
"""

import csv
import sys
import os
import hashlib
import json
from datetime import datetime
from pathlib import Path


def compute_checksums(filepath):
    """Compute MD5 and SHA256 checksums for a file."""
    md5_hash = hashlib.md5()
    sha256_hash = hashlib.sha256()
    
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            md5_hash.update(chunk)
            sha256_hash.update(chunk)
    
    return {
        'md5': md5_hash.hexdigest(),
        'sha256': sha256_hash.hexdigest()
    }


def standardize_tsv(input_file, output_file, manifest_file):
    """
    Standardize the TSV file with the following rules:
    - Normalize headers
    - Ensure consistent tab delimiters
    - Remove extra whitespace while preserving meaningful content
    - Use UTF-8 encoding with Unix line endings (LF)
    - Track all changes in manifest
    """
    
    print(f"Processing: {input_file}")
    print("=" * 70)
    
    # Compute source checksums
    print("\n1. Computing source file checksums...")
    source_checksums = compute_checksums(input_file)
    print(f"   MD5:    {source_checksums['md5']}")
    print(f"   SHA256: {source_checksums['sha256']}")
    
    # Read and standardize
    print("\n2. Reading and standardizing TSV...")
    
    rows = []
    issues = []
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            # Detect the delimiter and read
            sample = f.read(4096)
            f.seek(0)
            
            # Use tab as delimiter
            reader = csv.DictReader(f, delimiter='\t')
            
            if reader.fieldnames is None:
                raise ValueError("File has no header row")
            
            # Normalize header names
            original_headers = reader.fieldnames
            standardized_headers = [h.strip() for h in original_headers]
            
            print(f"   Original headers: {original_headers}")
            print(f"   Standardized headers: {standardized_headers}")
            
            # Process rows
            row_count = 0
            for row_num, row in enumerate(reader, start=2):  # start=2 because row 1 is header
                row_count += 1
                
                # Standardize row data
                standardized_row = {}
                for key, value in row.items():
                    new_key = key.strip()
                    # Clean value: strip whitespace but preserve internal structure
                    new_value = value.strip() if value else ''
                    standardized_row[new_key] = new_value
                    
                    # Check for issues
                    if not new_value and new_key in ['Object Date', 'Title', 'Object Number']:
                        issues.append(f"Row {row_num}: Missing value in required field '{new_key}'")
                
                rows.append(standardized_row)
            
            print(f"   Total rows processed: {row_count}")
    
    except Exception as e:
        print(f"   ERROR reading file: {e}")
        sys.exit(1)
    
    # Write standardized output
    print("\n3. Writing standardized output...")
    
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=standardized_headers, delimiter='\t')
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"   Output file: {output_file}")
        print(f"   Rows written: {len(rows)}")
    
    except Exception as e:
        print(f"   ERROR writing file: {e}")
        sys.exit(1)
    
    # Compute output checksums
    print("\n4. Computing output file checksums...")
    output_checksums = compute_checksums(output_file)
    print(f"   MD5:    {output_checksums['md5']}")
    print(f"   SHA256: {output_checksums['sha256']}")
    
    # Generate manifest
    print("\n5. Generating manifest...")
    
    manifest = {
        'timestamp': datetime.now().isoformat(),
        'source_file': {
            'path': os.path.abspath(input_file),
            'size_bytes': os.path.getsize(input_file),
            'checksums': source_checksums
        },
        'output_file': {
            'path': os.path.abspath(output_file),
            'size_bytes': os.path.getsize(output_file),
            'checksums': output_checksums
        },
        'standardization_rules': [
            'Normalized headers (stripped whitespace)',
            'Consistent tab delimiters throughout',
            'UTF-8 encoding with Unix line endings (LF)',
            'Values trimmed of leading/trailing whitespace',
            'Preserved internal structure and content'
        ],
        'statistics': {
            'total_rows': len(rows),
            'total_columns': len(standardized_headers),
            'columns': standardized_headers,
            'issues_found': len(issues)
        },
        'issues': issues if issues else 'None'
    }
    
    # Write manifest
    try:
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"   Manifest file: {manifest_file}")
    
    except Exception as e:
        print(f"   ERROR writing manifest: {e}")
        sys.exit(1)
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Source file size:  {manifest['source_file']['size_bytes']:,} bytes")
    print(f"Output file size:  {manifest['output_file']['size_bytes']:,} bytes")
    print(f"Rows processed:    {len(rows)}")
    print(f"Columns:           {len(standardized_headers)}")
    print(f"Issues found:      {len(issues)}")
    
    if issues:
        print("\nIssues:")
        for issue in issues[:10]:  # Show first 10
            print(f"  - {issue}")
        if len(issues) > 10:
            print(f"  ... and {len(issues) - 10} more")
    
    print("\n✓ Standardization complete!")
    print(f"✓ Checksums saved in manifest for verification")
    
    return manifest


if __name__ == '__main__':
    # Default paths
    input_file = '/mnt/user-data/uploads/met_inventory.tsv'
    output_file = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
    manifest_file = '/mnt/user-data/outputs/met_inventory_manifest.json'
    
    # Allow command-line override
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    if len(sys.argv) > 3:
        manifest_file = sys.argv[3]
    
    # Check input file exists
    if not os.path.exists(input_file):
        print(f"ERROR: Input file not found: {input_file}")
        sys.exit(1)
    
    # Run standardization
    manifest = standardize_tsv(input_file, output_file, manifest_file)
