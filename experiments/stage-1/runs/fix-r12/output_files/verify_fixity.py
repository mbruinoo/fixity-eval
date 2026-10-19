#!/usr/bin/env python3
"""
TSV Fixity Verification Script
Verifies the integrity of standardized files against documented checksums
"""

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

def verify_fixity(file_path, expected_checksums):
    """Verify a file matches expected checksums"""
    actual_checksums = calculate_checksums(file_path)
    
    md5_match = actual_checksums['md5'] == expected_checksums['md5']
    sha256_match = actual_checksums['sha256'] == expected_checksums['sha256']
    
    return {
        'file': str(file_path),
        'timestamp': datetime.now().isoformat(),
        'md5': {
            'expected': expected_checksums['md5'],
            'actual': actual_checksums['md5'],
            'match': md5_match
        },
        'sha256': {
            'expected': expected_checksums['sha256'],
            'actual': actual_checksums['sha256'],
            'match': sha256_match
        },
        'overall_match': md5_match and sha256_match
    }

def main():
    output_dir = Path('/mnt/user-data/outputs')
    standardized_file = output_dir / 'met_inventory_standardized.tsv'
    fixity_report_path = output_dir / 'fixity_report.json'
    verification_path = output_dir / 'verification_report.json'
    
    print("=" * 70)
    print("TSV FIXITY VERIFICATION")
    print("=" * 70)
    
    # Load expected checksums from fixity report
    print("\n[1/3] Loading expected checksums from fixity report...")
    with open(fixity_report_path, 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    expected = report['standardized_file']['checksums']
    print(f"  Expected MD5:    {expected['md5']}")
    print(f"  Expected SHA256: {expected['sha256']}")
    
    # Verify standardized file
    print("\n[2/3] Verifying standardized TSV file...")
    verification = verify_fixity(standardized_file, expected)
    
    print(f"  File: {standardized_file}")
    print(f"  MD5 Match:    {verification['md5']['match']}")
    print(f"    Expected: {verification['md5']['expected']}")
    print(f"    Actual:   {verification['md5']['actual']}")
    print(f"  SHA256 Match: {verification['sha256']['match']}")
    print(f"    Expected: {verification['sha256']['expected']}")
    print(f"    Actual:   {verification['sha256']['actual']}")
    
    # Save verification report
    print("\n[3/3] Saving verification report...")
    with open(verification_path, 'w', encoding='utf-8') as f:
        json.dump(verification, f, indent=2, ensure_ascii=False)
    print(f"  Saved to: {verification_path}")
    
    # Print result
    print("\n" + "=" * 70)
    if verification['overall_match']:
        print("✅ VERIFICATION SUCCESSFUL - FILE INTEGRITY CONFIRMED")
    else:
        print("❌ VERIFICATION FAILED - FILE MAY BE CORRUPTED")
    print("=" * 70)
    
    return 0 if verification['overall_match'] else 1

if __name__ == '__main__':
    exit(main())
