#!/usr/bin/env python3
"""
Verify the integrity of the standardized TSV file by checking checksums
against the manifest and validating the file structure.
"""

import json
import hashlib
import sys
import os
from pathlib import Path


def compute_checksum(filepath, algorithm='sha256'):
    """Compute checksum for a file."""
    hash_obj = hashlib.new(algorithm)
    
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_obj.update(chunk)
    
    return hash_obj.hexdigest()


def verify_file(output_file, manifest_file):
    """
    Verify that the output file matches the checksums recorded in the manifest.
    """
    
    print("=" * 70)
    print("TSV File Integrity Verification")
    print("=" * 70)
    print()
    
    # Check if files exist
    if not os.path.exists(manifest_file):
        print(f"✗ ERROR: Manifest file not found: {manifest_file}")
        return False
    
    if not os.path.exists(output_file):
        print(f"✗ ERROR: Output file not found: {output_file}")
        return False
    
    print(f"Manifest file: {manifest_file}")
    print(f"Output file:   {output_file}")
    print()
    
    # Load manifest
    try:
        with open(manifest_file, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
    except Exception as e:
        print(f"✗ ERROR: Could not read manifest: {e}")
        return False
    
    print("Verification Results:")
    print("-" * 70)
    
    all_pass = True
    
    # Verify file size
    print(f"\n1. File Size Check:")
    recorded_size = manifest['output_file']['size_bytes']
    actual_size = os.path.getsize(output_file)
    
    if recorded_size == actual_size:
        print(f"   ✓ Size matches: {actual_size:,} bytes")
    else:
        print(f"   ✗ Size mismatch!")
        print(f"     Expected: {recorded_size:,} bytes")
        print(f"     Actual:   {actual_size:,} bytes")
        all_pass = False
    
    # Verify MD5
    print(f"\n2. MD5 Checksum Verification:")
    recorded_md5 = manifest['output_file']['checksums']['md5']
    actual_md5 = compute_checksum(output_file, 'md5')
    
    if recorded_md5 == actual_md5:
        print(f"   ✓ MD5 matches: {actual_md5}")
    else:
        print(f"   ✗ MD5 mismatch!")
        print(f"     Expected: {recorded_md5}")
        print(f"     Actual:   {actual_md5}")
        all_pass = False
    
    # Verify SHA256
    print(f"\n3. SHA256 Checksum Verification:")
    recorded_sha256 = manifest['output_file']['checksums']['sha256']
    actual_sha256 = compute_checksum(output_file, 'sha256')
    
    if recorded_sha256 == actual_sha256:
        print(f"   ✓ SHA256 matches: {actual_sha256}")
    else:
        print(f"   ✗ SHA256 mismatch!")
        print(f"     Expected: {recorded_sha256}")
        print(f"     Actual:   {actual_sha256}")
        all_pass = False
    
    # Validate TSV structure
    print(f"\n4. TSV Structure Validation:")
    try:
        import csv
        
        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            rows = list(reader)
            
            expected_cols = manifest['statistics']['total_columns']
            actual_cols = len(reader.fieldnames)
            expected_rows = manifest['statistics']['total_rows']
            actual_rows = len(rows)
            
            if expected_cols == actual_cols:
                print(f"   ✓ Columns match: {actual_cols}")
            else:
                print(f"   ✗ Column count mismatch!")
                print(f"     Expected: {expected_cols}")
                print(f"     Actual:   {actual_cols}")
                all_pass = False
            
            if expected_rows == actual_rows:
                print(f"   ✓ Rows match: {actual_rows}")
            else:
                print(f"   ✗ Row count mismatch!")
                print(f"     Expected: {expected_rows}")
                print(f"     Actual:   {actual_rows}")
                all_pass = False
            
            print(f"   ✓ Valid UTF-8 encoding")
            print(f"   ✓ Headers: {', '.join(reader.fieldnames)}")
    
    except Exception as e:
        print(f"   ✗ ERROR: {e}")
        all_pass = False
    
    # Display manifest info
    print(f"\n5. Manifest Information:")
    print(f"   Timestamp: {manifest['timestamp']}")
    print(f"   Standardization rules applied:")
    for rule in manifest['standardization_rules']:
        print(f"     - {rule}")
    
    issues = manifest['statistics']['issues_found']
    if issues > 0:
        print(f"\n   ⚠ Data quality issues found: {issues}")
        if isinstance(manifest['statistics']['issues'], list):
            for issue in manifest['statistics']['issues'][:5]:
                print(f"     - {issue}")
    else:
        print(f"\n   ✓ No data quality issues found")
    
    # Summary
    print()
    print("=" * 70)
    if all_pass:
        print("✓ VERIFICATION PASSED - File integrity confirmed")
    else:
        print("✗ VERIFICATION FAILED - File integrity issues detected")
    print("=" * 70)
    print()
    
    return all_pass


if __name__ == '__main__':
    output_file = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
    manifest_file = '/mnt/user-data/outputs/met_inventory_manifest.json'
    
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    if len(sys.argv) > 2:
        manifest_file = sys.argv[2]
    
    success = verify_file(output_file, manifest_file)
    sys.exit(0 if success else 1)
