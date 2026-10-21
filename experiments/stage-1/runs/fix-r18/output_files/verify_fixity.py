#!/usr/bin/env python3
"""
Verify the fixity of standardized files using checksums from the manifest.
Run this script to verify that files haven't been corrupted or modified.
"""

import json
import hashlib
import sys
from pathlib import Path

def calculate_checksum(filepath, algorithm='sha256'):
    """Calculate cryptographic checksum of a file."""
    if not Path(filepath).exists():
        print(f"Error: File not found: {filepath}")
        return None
    
    hash_obj = hashlib.new(algorithm)
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()

def verify_fixity(manifest_path='/mnt/user-data/outputs/fixity_manifest.json'):
    """Verify files against the fixity manifest."""
    
    print("=" * 70)
    print("FIXITY VERIFICATION REPORT")
    print("=" * 70)
    print()
    
    # Load manifest
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
    except FileNotFoundError:
        print(f"Error: Manifest not found at {manifest_path}")
        return False
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in manifest at {manifest_path}")
        return False
    
    print(f"Manifest file: {manifest_path}")
    print(f"Manifest timestamp: {manifest['timestamp']}")
    print()
    
    all_valid = True
    
    # Verify source file
    print("-" * 70)
    print("SOURCE FILE VERIFICATION")
    print("-" * 70)
    
    source_info = manifest['source_file']
    source_path = source_info['path']
    source_expected_hash = source_info['sha256']
    source_expected_size = source_info['size_bytes']
    
    print(f"File: {source_path}")
    print(f"Expected size: {source_expected_size} bytes")
    print(f"Expected SHA-256: {source_expected_hash}")
    print()
    
    if Path(source_path).exists():
        source_actual_hash = calculate_checksum(source_path, 'sha256')
        source_actual_size = Path(source_path).stat().st_size
        
        print(f"Actual size: {source_actual_size} bytes")
        print(f"Actual SHA-256: {source_actual_hash}")
        
        if source_actual_hash == source_expected_hash:
            print("✓ PASS - Source file integrity verified")
        else:
            print("✗ FAIL - Source file has been modified or corrupted")
            all_valid = False
        
        if source_actual_size != source_expected_size:
            print(f"⚠ WARNING - File size mismatch ({source_actual_size} vs {source_expected_size})")
            all_valid = False
    else:
        print("✗ FAIL - Source file not found")
        all_valid = False
    
    print()
    
    # Verify output file
    print("-" * 70)
    print("OUTPUT FILE VERIFICATION")
    print("-" * 70)
    
    output_info = manifest['output_file']
    output_path = output_info['path']
    output_expected_hash = output_info['sha256']
    output_expected_size = output_info['size_bytes']
    
    print(f"File: {output_path}")
    print(f"Expected size: {output_expected_size} bytes")
    print(f"Expected SHA-256: {output_expected_hash}")
    print()
    
    if Path(output_path).exists():
        output_actual_hash = calculate_checksum(output_path, 'sha256')
        output_actual_size = Path(output_path).stat().st_size
        
        print(f"Actual size: {output_actual_size} bytes")
        print(f"Actual SHA-256: {output_actual_hash}")
        
        if output_actual_hash == output_expected_hash:
            print("✓ PASS - Output file integrity verified")
        else:
            print("✗ FAIL - Output file has been modified or corrupted")
            all_valid = False
        
        if output_actual_size != output_expected_size:
            print(f"⚠ WARNING - File size mismatch ({output_actual_size} vs {output_expected_size})")
            all_valid = False
    else:
        print("✗ FAIL - Output file not found")
        all_valid = False
    
    print()
    print("-" * 70)
    print("STANDARDIZATION TRANSFORMATIONS APPLIED")
    print("-" * 70)
    print()
    
    for i, transformation in enumerate(manifest['standardization_applied'], 1):
        print(f"{i}. {transformation}")
    
    print()
    print("=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    
    if all_valid:
        print("✓ All integrity checks passed - Files are valid and unmodified")
        return True
    else:
        print("✗ Some checks failed - Please investigate the issues above")
        return False

if __name__ == '__main__':
    success = verify_fixity()
    sys.exit(0 if success else 1)
