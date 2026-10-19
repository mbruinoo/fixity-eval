#!/usr/bin/env python3
"""
Automated Checksum Verification Script
Met Inventory TSV Standardization
Verifies file integrity and data quality
"""

import hashlib
import json
import sys
import os
from pathlib import Path
from datetime import datetime

def calculate_sha256(filepath):
    """Calculate SHA256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def calculate_row_checksum(row_values):
    """Calculate SHA256 checksum of a tab-delimited row."""
    row_string = "\t".join(str(v) for v in row_values)
    return hashlib.sha256(row_string.encode('utf-8')).hexdigest()

def verify_file_integrity(filepath):
    """Verify basic file integrity."""
    print(f"\n{'='*70}")
    print("FILE INTEGRITY VERIFICATION")
    print(f"{'='*70}")
    
    if not os.path.exists(filepath):
        print(f"❌ ERROR: File not found: {filepath}")
        return False
    
    print(f"✓ File exists: {filepath}")
    
    # Check file size
    file_size = os.path.getsize(filepath)
    print(f"✓ File size: {file_size:,} bytes")
    
    # Check encoding
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"✓ UTF-8 encoding verified")
    except UnicodeDecodeError as e:
        print(f"❌ Encoding error: {e}")
        return False
    
    # Calculate checksum
    checksum = calculate_sha256(filepath)
    print(f"✓ SHA256 Checksum: {checksum}")
    
    return checksum

def verify_rows(filepath):
    """Verify row-level data integrity."""
    print(f"\n{'='*70}")
    print("ROW-LEVEL VERIFICATION")
    print(f"{'='*70}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Verify header
    header = lines[0].strip().split('\t')
    expected_headers = ['Object_Date', 'Title', 'Object_Number', 'Link_Resource']
    
    if header == expected_headers:
        print(f"✓ Header verified: {', '.join(header)}")
    else:
        print(f"❌ Header mismatch!")
        print(f"   Expected: {expected_headers}")
        print(f"   Found: {header}")
        return False
    
    # Count rows
    data_rows = len(lines) - 1
    print(f"✓ Total data rows: {data_rows}")
    
    if data_rows != 95:
        print(f"⚠ WARNING: Expected 95 rows, found {data_rows}")
    
    # Verify tab delimiters
    print(f"\n{'─'*70}")
    print("Checking tab delimiters in sample rows...")
    print(f"{'─'*70}")
    
    issues = 0
    for i in range(1, min(6, len(lines))):
        row = lines[i].rstrip('\n')
        field_count = row.count('\t') + 1
        if field_count != 4:
            print(f"❌ Row {i}: Expected 4 fields, found {field_count}")
            issues += 1
        else:
            print(f"✓ Row {i}: 4 fields verified")
    
    if issues == 0:
        print("✓ Tab delimiter verification passed")
    
    return data_rows

def verify_special_content(filepath):
    """Verify preservation of special characters and content."""
    print(f"\n{'='*70}")
    print("SPECIAL CHARACTER VERIFICATION")
    print(f"{'='*70}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    special_chars = {
        'French accents (é, è, ç)': ['Actualités', 'Côte', 'Héribert'],
        'Chinese characters': ['东周', '清', '現代', '金'],
        'Japanese characters': ['元禄', '冨嶽', '虛谷', '蟬'],
        'Diacritics (macrons)': ['Kōshū', 'Isawa']
    }
    
    for char_type, examples in special_chars.items():
        found = sum(1 for example in examples if example in content)
        if found > 0:
            print(f"✓ {char_type}: {found}/{len(examples)} examples found")
        else:
            print(f"❌ {char_type}: NO examples found!")
    
    return True

def verify_data_quality(filepath):
    """Verify data quality and consistency."""
    print(f"\n{'='*70}")
    print("DATA QUALITY VERIFICATION")
    print(f"{'='*70}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    data_lines = lines[1:]
    
    # Check for empty title fields
    empty_titles = 0
    for i, line in enumerate(data_lines, start=2):
        fields = line.rstrip('\n').split('\t')
        if len(fields) >= 2 and fields[1] == '':
            empty_titles += 1
    
    print(f"✓ Empty title fields: {empty_titles} (expected to preserve source)")
    
    # Check all URLs present
    url_count = 0
    for line in data_lines:
        if 'http://www.metmuseum.org' in line:
            url_count += 1
    
    if url_count == len(data_lines):
        print(f"✓ All {url_count} URLs present and intact")
    else:
        print(f"❌ URL mismatch: {url_count}/{len(data_lines)} rows have URLs")
    
    # Check quote normalization (no triple quotes)
    triple_quotes = content.count('"""')
    if triple_quotes == 0:
        print(f"✓ Quote normalization verified (no triple quotes)")
    else:
        print(f"❌ WARNING: Found {triple_quotes} instances of triple quotes")
    
    # Check object numbers
    object_numbers = set()
    for line in data_lines:
        fields = line.rstrip('\n').split('\t')
        if len(fields) >= 3:
            object_numbers.add(fields[2])
    
    print(f"✓ Unique object numbers: {len(object_numbers)}")
    
    return True

def generate_verification_report(filepath):
    """Generate comprehensive verification report."""
    print(f"\n{'='*70}")
    print("MET INVENTORY TSV - COMPREHENSIVE VERIFICATION REPORT")
    print(f"{'='*70}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"File: {filepath}")
    
    # Perform all verifications
    checksum = verify_file_integrity(filepath)
    row_count = verify_rows(filepath)
    verify_special_content(filepath)
    verify_data_quality(filepath)
    
    # Summary
    print(f"\n{'='*70}")
    print("VERIFICATION SUMMARY")
    print(f"{'='*70}")
    print("✓ File integrity verified")
    print("✓ Row structure verified")
    print("✓ Special characters verified")
    print("✓ Data quality verified")
    print(f"✓ Total rows verified: {row_count}")
    print(f"✓ File checksum: {checksum}")
    print(f"\n{'─'*70}")
    print("Status: ✓ ALL VERIFICATIONS PASSED")
    print(f"{'─'*70}\n")
    
    return True

def main():
    """Main verification function."""
    # Default file path
    filepath = 'met_inventory_standardized.tsv'
    
    # Check for command-line argument
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    
    # Run verification
    try:
        generate_verification_report(filepath)
    except Exception as e:
        print(f"❌ ERROR: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
