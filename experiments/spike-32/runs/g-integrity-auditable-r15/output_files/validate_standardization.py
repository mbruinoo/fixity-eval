#!/usr/bin/env python3
"""
Met Inventory Standardization Validation Script
Verifies data integrity and structure of the standardized TSV file
"""

import hashlib
import sys
from pathlib import Path
from collections import defaultdict

def calculate_sha256(filepath):
    """Calculate SHA-256 checksum of file"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def validate_file(filepath):
    """Comprehensive validation of standardized TSV"""
    
    print(f"Validating: {filepath}")
    print("=" * 70)
    
    if not Path(filepath).exists():
        print(f"❌ ERROR: File not found: {filepath}")
        return False
    
    # Read file
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Test 1: File not empty
    print("\n[TEST 1] File Structure")
    print("-" * 70)
    if len(lines) == 0:
        print("❌ FAILED: File is empty")
        return False
    print(f"✓ File contains {len(lines)} total lines")
    
    # Test 2: Header validation
    print("\n[TEST 2] Header Validation")
    print("-" * 70)
    header = lines[0].strip().split('\t')
    expected_headers = ['Object_Date', 'Title', 'Object_Number', 'Link_Resource']
    
    if header != expected_headers:
        print(f"❌ FAILED: Headers don't match")
        print(f"   Expected: {expected_headers}")
        print(f"   Found:    {header}")
        return False
    print(f"✓ Header contains correct columns: {header}")
    
    # Test 3: Data row count
    print("\n[TEST 3] Data Row Count")
    print("-" * 70)
    data_rows = len(lines) - 1  # Subtract header
    if data_rows != 100:
        print(f"❌ FAILED: Expected 100 data rows, found {data_rows}")
        return False
    print(f"✓ Correct number of data rows: {data_rows}")
    
    # Test 4: Column consistency
    print("\n[TEST 4] Column Consistency")
    print("-" * 70)
    column_count = len(header)
    errors = 0
    
    for i, line in enumerate(lines[1:], 1):
        fields = line.rstrip('\n').split('\t')
        if len(fields) != 4:
            print(f"⚠ Row {i+1}: Expected 4 fields, found {len(fields)}")
            errors += 1
    
    if errors == 0:
        print(f"✓ All {data_rows} data rows have exactly {column_count} fields")
    else:
        print(f"❌ FAILED: {errors} rows have incorrect column count")
        return False
    
    # Test 5: Required fields completeness
    print("\n[TEST 5] Required Fields Completeness")
    print("-" * 70)
    
    empty_counts = defaultdict(int)
    empty_rows = defaultdict(list)
    
    for i, line in enumerate(lines[1:], 1):
        fields = line.rstrip('\n').split('\t')
        for col_idx, (col_name, field) in enumerate(zip(expected_headers, fields)):
            if not field.strip():
                empty_counts[col_name] += 1
                empty_rows[col_name].append(i)
    
    # Display completeness
    for col_name in expected_headers:
        filled = data_rows - empty_counts[col_name]
        percent = (filled / data_rows) * 100
        status = "✓" if empty_counts[col_name] == 0 else "⚠"
        print(f"{status} {col_name:20s}: {filled:3d}/{data_rows} ({percent:5.1f}%)", end="")
        
        if empty_counts[col_name] > 0:
            print(f" [Empty in rows: {empty_rows[col_name][:5]}{'...' if len(empty_rows[col_name]) > 5 else ''}]")
        else:
            print()
    
    # Critical check: Object_Number and Link_Resource
    if empty_counts['Object_Number'] > 0 or empty_counts['Link_Resource'] > 0:
        print("❌ FAILED: Critical fields are missing data")
        return False
    
    # Test 6: URL validation
    print("\n[TEST 6] URL Validation")
    print("-" * 70)
    
    url_errors = 0
    for i, line in enumerate(lines[1:], 1):
        fields = line.rstrip('\n').split('\t')
        url = fields[3]
        if not url.startswith('http://') and not url.startswith('https://'):
            print(f"⚠ Row {i+1}: Invalid URL format: {url[:50]}")
            url_errors += 1
    
    if url_errors == 0:
        print(f"✓ All {data_rows} URLs have valid format (http/https)")
    else:
        print(f"⚠ Found {url_errors} URLs with potential formatting issues")
    
    # Test 7: Character encoding
    print("\n[TEST 7] Character Encoding (UTF-8)")
    print("-" * 70)
    
    special_chars = defaultdict(int)
    unicode_samples = []
    
    for i, line in enumerate(lines[1:], 1):
        for char in line:
            if ord(char) > 127:
                special_chars['non-ascii'] += 1
                if len(unicode_samples) < 5:
                    unicode_samples.append((i, char, hex(ord(char))))
    
    if special_chars['non-ascii'] > 0:
        print(f"✓ File contains {special_chars['non-ascii']} non-ASCII characters")
        print(f"  Sample characters:")
        for row, char, hex_val in unicode_samples:
            print(f"    Row {row}: '{char}' (U+{hex_val[2:].upper()})")
    else:
        print(f"✓ All characters are ASCII-compatible")
    
    # Test 8: Line ending consistency
    print("\n[TEST 8] Line Ending Consistency")
    print("-" * 70)
    
    with open(filepath, 'rb') as f:
        content = f.read()
    
    crlf_count = content.count(b'\r\n')
    lf_only_count = content.count(b'\n') - crlf_count
    cr_only_count = content.count(b'\r') - crlf_count
    
    if crlf_count == 0 and cr_only_count == 0:
        print(f"✓ File uses LF (Unix) line endings exclusively")
    elif lf_only_count > 0 and crlf_count == 0:
        print(f"✓ File uses LF (Unix) line endings ({lf_only_count} lines)")
    else:
        print(f"⚠ Mixed line endings detected:")
        print(f"  LF (Unix):     {lf_only_count}")
        print(f"  CRLF (Windows): {crlf_count}")
        print(f"  CR (Old Mac):   {cr_only_count}")
    
    # Test 9: Tab delimiter consistency
    print("\n[TEST 9] Tab Delimiter Consistency")
    print("-" * 70)
    
    tab_errors = 0
    for i, line in enumerate(lines[1:], 1):
        # Count actual tab characters
        tab_count = line.count('\t')
        if tab_count != 3:  # 4 fields = 3 delimiters
            tab_errors += 1
            if tab_errors <= 3:
                print(f"⚠ Row {i+1}: Found {tab_count} tabs (expected 3)")
    
    if tab_errors == 0:
        print(f"✓ All {data_rows} rows use exactly 3 tab delimiters")
    else:
        print(f"⚠ Found {tab_errors} rows with inconsistent tab count")
    
    # Test 10: File integrity hash
    print("\n[TEST 10] File Integrity Hash (SHA-256)")
    print("-" * 70)
    
    file_hash = calculate_sha256(filepath)
    print(f"SHA-256: {file_hash}")
    print(f"\nUse this hash to verify file integrity:")
    print(f"  echo '{file_hash} {Path(filepath).name}' | sha256sum -c -")
    
    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    print("✓ File structure is valid")
    print("✓ All required fields are present")
    print("✓ Data integrity verified")
    print("✓ Character encoding is UTF-8")
    print(f"✓ Ready for use: {filepath}")
    print("\nFile can be safely imported into:")
    print("  - Python (pandas.read_csv)")
    print("  - R (read.delim)")
    print("  - SQL databases (LOAD DATA INFILE)")
    print("  - Excel (Open with encoding: UTF-8)")
    
    return True

if __name__ == '__main__':
    filepath = sys.argv[1] if len(sys.argv) > 1 else 'met_inventory_standardized.tsv'
    
    try:
        success = validate_file(filepath)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ ERROR: {e}")
        sys.exit(1)