#!/usr/bin/env python3
"""
Verification script for standardized Metropolitan Museum Inventory TSV
Validates checksums and file integrity against the checksums document.
"""

import csv
import hashlib
import json
from pathlib import Path
from datetime import datetime

def compute_hash(text, algorithm='sha256'):
    """Compute hash of text content."""
    h = hashlib.new(algorithm)
    h.update(text.encode('utf-8'))
    return h.hexdigest()

def compute_row_hash(row_dict, algorithm='sha256'):
    """Compute hash of a normalized row."""
    normalized = json.dumps(row_dict, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
    h = hashlib.new(algorithm)
    h.update(normalized.encode('utf-8'))
    return h.hexdigest()

def verify_standardized_file(tsv_file, checksums_file):
    """
    Verify the standardized TSV file against stored checksums.
    Returns a detailed verification report.
    """
    
    report = {
        'verification_date': datetime.now().isoformat(),
        'file_checks': {},
        'row_checks': {},
        'all_valid': True
    }
    
    # Load checksums
    with open(checksums_file, 'r', encoding='utf-8') as f:
        checksums = json.load(f)
    
    # Check file integrity
    print("Verifying file integrity...")
    
    with open(tsv_file, 'r', encoding='utf-8') as f:
        current_content = f.read()
    
    current_sha256 = compute_hash(current_content)
    current_sha512 = compute_hash(current_content, 'sha512')
    
    expected_sha256 = checksums['standardized_file']['standardized_file_sha256']
    expected_sha512 = checksums['standardized_file']['standardized_file_sha512']
    
    sha256_match = current_sha256 == expected_sha256
    sha512_match = current_sha512 == expected_sha512
    
    report['file_checks']['sha256_valid'] = sha256_match
    report['file_checks']['sha512_valid'] = sha512_match
    report['file_checks']['current_sha256'] = current_sha256
    report['file_checks']['expected_sha256'] = expected_sha256
    report['file_checks']['current_line_count'] = len(current_content.splitlines())
    report['file_checks']['expected_line_count'] = checksums['standardized_file']['standardized_line_count']
    
    if not sha256_match or not sha512_match:
        report['all_valid'] = False
        print("  ✗ File integrity check FAILED")
        print(f"    Expected SHA256: {expected_sha256}")
        print(f"    Current SHA256:  {current_sha256}")
    else:
        print("  ✓ File integrity verified (SHA256 and SHA512 match)")
    
    # Check row integrity
    print("\nVerifying row integrity...")
    
    row_mismatches = []
    verified_rows = 0
    
    with open(tsv_file, 'r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f, delimiter='\t')
        headers = reader.fieldnames
        
        for row_num, row in enumerate(reader, start=2):
            standardized_row = {h: (row.get(h, '') or '').strip() for h in headers}
            current_row_hash = compute_row_hash(standardized_row)
            
            # Find matching row in checksums
            stored_row_info = None
            for row_info in checksums['row_integrity']:
                if row_info['row_number'] == row_num:
                    stored_row_info = row_info
                    break
            
            if stored_row_info:
                if current_row_hash == stored_row_info['sha256']:
                    verified_rows += 1
                else:
                    row_mismatches.append({
                        'row_number': row_num,
                        'object_number': standardized_row.get('Object Number', 'UNKNOWN'),
                        'expected_hash': stored_row_info['sha256'],
                        'current_hash': current_row_hash
                    })
                    report['all_valid'] = False
    
    report['row_checks']['total_rows'] = verified_rows
    report['row_checks']['verified_rows'] = verified_rows
    report['row_checks']['mismatched_rows'] = row_mismatches
    
    if row_mismatches:
        print(f"  ✗ Row integrity check FAILED for {len(row_mismatches)} rows")
        for mismatch in row_mismatches[:5]:
            print(f"    Row {mismatch['row_number']} ({mismatch['object_number']})")
    else:
        print(f"  ✓ All {verified_rows} data rows verified successfully")
    
    return report

def main():
    tsv_file = Path('/mnt/user-data/outputs/met_inventory_standardized.tsv')
    checksums_file = Path('/mnt/user-data/outputs/met_inventory_checksums.json')
    report_file = Path('/mnt/user-data/outputs/met_inventory_verification_report.json')
    
    if not tsv_file.exists():
        print(f"Error: TSV file {tsv_file} not found")
        print("Please run standardize_met_inventory.py first")
        return
    
    if not checksums_file.exists():
        print(f"Error: Checksums file {checksums_file} not found")
        return
    
    print("=" * 60)
    print("Metropolitan Museum Inventory Verification")
    print("=" * 60)
    print()
    
    report = verify_standardized_file(tsv_file, checksums_file)
    
    print()
    print("=" * 60)
    if report['all_valid']:
        print("✓ VERIFICATION PASSED - All files and rows are valid")
    else:
        print("✗ VERIFICATION FAILED - Some checks did not pass")
    print("=" * 60)
    
    # Save verification report
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nDetailed report saved to: {report_file}")

if __name__ == '__main__':
    main()
