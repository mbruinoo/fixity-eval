#!/usr/bin/env python3
"""
Verify fixity of the Met Inventory standardized TSV file.
This script validates the file and row-level checksums from the manifest.
"""

import csv
import hashlib
import json
import sys
from pathlib import Path

def compute_hash(content):
    """Compute SHA256 hash of content."""
    if isinstance(content, str):
        content = content.encode('utf-8')
    h = hashlib.sha256()
    h.update(content)
    return h.hexdigest()

def verify_file_integrity(filepath, expected_hash):
    """Verify the file's overall integrity."""
    print(f"\n📁 Verifying file: {filepath}")
    
    if not Path(filepath).exists():
        print(f"   ✗ File not found!")
        return False
    
    with open(filepath, 'rb') as f:
        actual_hash = compute_hash(f.read())
    
    if actual_hash == expected_hash:
        print(f"   ✓ File hash matches expected value")
        return True
    else:
        print(f"   ✗ File hash MISMATCH!")
        print(f"     Expected: {expected_hash}")
        print(f"     Actual:   {actual_hash}")
        return False

def verify_row_checksums(filepath, manifest_checksums):
    """Verify row-level checksums from the TSV file."""
    print(f"\n📋 Verifying row-level checksums...")
    
    mismatches = []
    matches = 0
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for idx, row in enumerate(reader, start=2):
            # Compute hash of current row
            row_content = '\t'.join(str(v) for v in row.values())
            actual_hash = compute_hash(row_content)
            
            # Find matching row in manifest
            manifest_row = next((r for r in manifest_checksums if r['line_number'] == idx), None)
            
            if manifest_row is None:
                mismatches.append(f"   ✗ Line {idx}: No manifest entry found")
            elif actual_hash == manifest_row['sha256']:
                matches += 1
            else:
                mismatches.append(f"   ✗ Line {idx}: Hash mismatch")
                mismatches.append(f"     Expected: {manifest_row['sha256']}")
                mismatches.append(f"     Actual:   {actual_hash}")
    
    print(f"   ✓ Rows verified: {matches}/{matches + len(mismatches)}")
    
    if mismatches:
        for msg in mismatches:
            print(msg)
        return False
    return True

def main():
    manifest_file = '/mnt/user-data/outputs/met_inventory_manifest.json'
    
    print("=" * 70)
    print("FIXITY VERIFICATION FOR MET INVENTORY STANDARDIZED TSV")
    print("=" * 70)
    
    # Load manifest
    print(f"\n📄 Loading manifest: {manifest_file}")
    try:
        with open(manifest_file, 'r') as f:
            manifest = json.load(f)
        print(f"   ✓ Manifest loaded")
        print(f"   ✓ Process: {manifest['process']}")
        print(f"   ✓ Timestamp: {manifest['timestamp']}")
    except FileNotFoundError:
        print(f"   ✗ Manifest file not found!")
        return False
    except json.JSONDecodeError:
        print(f"   ✗ Manifest is not valid JSON!")
        return False
    
    # Verify source file
    source_ok = verify_file_integrity(
        manifest['source']['filepath'],
        manifest['source']['file_hash_sha256']
    )
    
    # Verify output file
    output_ok = verify_file_integrity(
        manifest['output']['filepath'],
        manifest['output']['file_hash_sha256']
    )
    
    # Verify output row checksums
    rows_ok = verify_row_checksums(
        manifest['output']['filepath'],
        manifest['output']['row_hashes']
    )
    
    # Summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    
    results = [
        ("Source file integrity", source_ok),
        ("Output file integrity", output_ok),
        ("Row-level checksums", rows_ok),
    ]
    
    for check, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{check:.<50} {status}")
    
    all_ok = all(r for _, r in results)
    print("\n" + "=" * 70)
    if all_ok:
        print("✓ ALL FIXITY CHECKS PASSED - DATA INTEGRITY VERIFIED")
    else:
        print("✗ SOME FIXITY CHECKS FAILED - PLEASE INVESTIGATE")
    print("=" * 70 + "\n")
    
    return all_ok

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
