#!/usr/bin/env python3
"""
Met Inventory TSV Checksum Verification Script

This script validates the integrity of the standardized met_inventory.tsv file
by computing SHA256 checksums for each row and comparing them against stored values.

Usage:
    python3 verify_checksums.py met_inventory_standardized.tsv
"""

import sys
import hashlib
import os
from pathlib import Path


def compute_row_checksum(row_data):
    """
    Compute SHA256 checksum for a row (first 4 tab-separated fields).
    
    Args:
        row_data: List of field values [date, title, object_number, url]
    
    Returns:
        Hexadecimal SHA256 hash string
    """
    # Join the first 4 fields with tabs and encode
    row_string = '\t'.join(str(field) for field in row_data[:4])
    row_bytes = row_string.encode('utf-8')
    
    # Compute SHA256
    hash_obj = hashlib.sha256(row_bytes)
    return hash_obj.hexdigest()


def verify_file(filepath):
    """
    Verify all checksums in the TSV file.
    
    Args:
        filepath: Path to the standardized TSV file
    
    Returns:
        Dictionary with verification results
    """
    results = {
        'total_rows': 0,
        'valid_rows': 0,
        'invalid_rows': 0,
        'errors': []
    }
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        results['errors'].append(f"File not found: {filepath}")
        return results
    except Exception as e:
        results['errors'].append(f"Error reading file: {str(e)}")
        return results
    
    # Skip header row
    for line_num, line in enumerate(lines[1:], start=2):
        line = line.rstrip('\n\r')
        if not line.strip():  # Skip empty lines
            continue
        
        fields = line.split('\t')
        
        # Should have exactly 5 fields
        if len(fields) != 5:
            results['errors'].append(
                f"Line {line_num}: Expected 5 fields, got {len(fields)}"
            )
            results['total_rows'] += 1
            results['invalid_rows'] += 1
            continue
        
        date_field, title_field, object_num, url, stored_checksum = fields
        
        # Compute expected checksum
        computed_checksum = compute_row_checksum(
            [date_field, title_field, object_num, url]
        )
        
        results['total_rows'] += 1
        
        # Verify
        if computed_checksum == stored_checksum:
            results['valid_rows'] += 1
        else:
            results['invalid_rows'] += 1
            results['errors'].append(
                f"Line {line_num}: Checksum mismatch\n"
                f"  Object: {object_num}\n"
                f"  Expected: {computed_checksum}\n"
                f"  Stored:   {stored_checksum}"
            )
    
    return results


def print_report(results):
    """Print verification report to console."""
    print("\n" + "="*70)
    print("MET INVENTORY TSV CHECKSUM VERIFICATION REPORT")
    print("="*70 + "\n")
    
    print(f"Total Rows Checked:  {results['total_rows']}")
    print(f"Valid Rows:          {results['valid_rows']}")
    print(f"Invalid Rows:        {results['invalid_rows']}")
    
    if results['invalid_rows'] > 0:
        print("\n⚠️  INTEGRITY ISSUES DETECTED:\n")
        for error in results['errors'][:10]:  # Show first 10 errors
            print(f"  {error}\n")
        if len(results['errors']) > 10:
            print(f"  ... and {len(results['errors']) - 10} more errors")
    else:
        print("\n✓ All rows verified successfully!")
    
    print("\n" + "="*70 + "\n")


def create_test_row(date, title, obj_num, url):
    """
    Utility function to compute checksum for a new row (for creating new records).
    """
    checksum = compute_row_checksum([date, title, obj_num, url])
    return f"{date}\t{title}\t{obj_num}\t{url}\t{checksum}"


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 verify_checksums.py <path_to_tsv_file>")
        print("\nExample:")
        print("  python3 verify_checksums.py met_inventory_standardized.tsv")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    # Verify file exists
    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    
    # Run verification
    results = verify_file(filepath)
    print_report(results)
    
    # Exit with appropriate code
    sys.exit(0 if results['invalid_rows'] == 0 else 1)
