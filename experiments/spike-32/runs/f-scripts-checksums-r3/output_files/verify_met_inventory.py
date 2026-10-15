#!/usr/bin/env python3
"""
Verify Met Museum inventory TSV files for integrity and standardization.
Checks checksums, file format, and data consistency.
"""

import csv
import hashlib
import sys
from pathlib import Path

def calculate_sha256(file_path):
    """Calculate SHA256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def verify_tsv_format(file_path):
    """Verify TSV file format and structure."""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            
            # Check headers
            expected_headers = {'Object Date', 'Title', 'Object Number', 'Link Resource'}
            if set(reader.fieldnames) != expected_headers:
                issues.append(f"Invalid headers. Expected: {expected_headers}, Got: {set(reader.fieldnames)}")
            
            # Check rows
            row_count = 0
            for row_num, row in enumerate(reader, start=2):
                row_count += 1
                
                # Verify all fields present
                if len(row) != 4:
                    issues.append(f"Row {row_num}: Expected 4 fields, got {len(row)}")
                
                # Check that Link Resource is a valid URL
                link = row.get('Link Resource', '').strip()
                if link and not link.startswith('http'):
                    issues.append(f"Row {row_num}: Invalid URL format in Link Resource: {link[:50]}")
        
        return row_count, issues
        
    except UnicodeDecodeError as e:
        return 0, [f"Encoding error: {e}"]
    except Exception as e:
        return 0, [f"Format error: {e}"]

def main():
    source_file = Path("met_inventory.tsv")
    standardized_file = Path("met_inventory_standardized.tsv")
    
    print("=" * 70)
    print("MET MUSEUM INVENTORY TSV VERIFICATION")
    print("=" * 70)
    print()
    
    # Check if files exist
    if not standardized_file.exists():
        print(f"ERROR: {standardized_file} not found")
        sys.exit(1)
    
    print("FILE INTEGRITY CHECKS")
    print("-" * 70)
    
    # Calculate checksums
    print(f"\nCalculating checksums...")
    standardized_checksum = calculate_sha256(standardized_file)
    print(f"Standardized file SHA256: {standardized_checksum}")
    
    if source_file.exists():
        source_checksum = calculate_sha256(source_file)
        print(f"Source file SHA256:      {source_checksum}")
    else:
        print(f"Source file not found (optional check)")
    
    # Check file sizes
    standardized_size = standardized_file.stat().st_size
    print(f"\nFile size: {standardized_size} bytes")
    
    print("\n" + "=" * 70)
    print("FORMAT VALIDATION")
    print("-" * 70)
    
    row_count, format_issues = verify_tsv_format(standardized_file)
    
    if format_issues:
        print(f"✗ Format validation FAILED")
        for issue in format_issues:
            print(f"  - {issue}")
    else:
        print(f"✓ Format validation PASSED")
        print(f"  - Rows: {row_count}")
        print(f"  - Columns: 4 (Object Date, Title, Object Number, Link Resource)")
        print(f"  - Encoding: UTF-8")
        print(f"  - Delimiter: Tab (\\t)")
        print(f"  - All URLs valid format")
    
    print("\n" + "=" * 70)
    print("STANDARDIZATION CHECKS")
    print("-" * 70)
    
    # Read and check standardization
    with open(standardized_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    checks = []
    
    # Check line endings
    all_lf = all('\r' not in line for line in lines)
    checks.append(("LF line endings (POSIX)", all_lf))
    
    # Check UTF-8 encoding
    try:
        with open(standardized_file, 'rb') as f:
            f.read().decode('utf-8')
        checks.append(("UTF-8 encoding", True))
    except:
        checks.append(("UTF-8 encoding", False))
    
    # Check delimiter consistency
    delimiter_ok = all(
        line.count('\t') == 3 or i == 0 for i, line in enumerate(lines) if line.strip()
    )
    checks.append(("Tab delimiter consistency", delimiter_ok))
    
    # Check for no trailing whitespace on header
    header_clean = not lines[0].rstrip('\n').endswith(' ')
    checks.append(("Header whitespace trimmed", header_clean))
    
    for check_name, result in checks:
        symbol = "✓" if result else "✗"
        print(f"{symbol} {check_name}")
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("-" * 70)
    
    all_passed = all(result for _, result in checks) and not format_issues
    
    if all_passed:
        print("✓ All checks PASSED - File is properly standardized")
        sys.exit(0)
    else:
        print("✗ Some checks FAILED - Please review above")
        sys.exit(1)

if __name__ == "__main__":
    main()
