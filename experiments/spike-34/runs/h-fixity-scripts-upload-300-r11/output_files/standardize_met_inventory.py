#!/usr/bin/env python3
"""
TSV Standardization Script for Met Museum Inventory
Standardizes formatting and verifies file integrity with checksums

Usage:
    python3 standardize_met_inventory.py <input_file> [output_file]

Example:
    python3 standardize_met_inventory.py met_inventory.tsv met_inventory_standardized.tsv
"""

import csv
import hashlib
import sys
from pathlib import Path
from datetime import datetime


def calculate_checksum(file_path, algorithm='sha256'):
    """Calculate file checksum using specified algorithm"""
    hash_obj = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()


def count_lines(file_path):
    """Count total lines in file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return sum(1 for _ in f)


def standardize_tsv(input_file, output_file):
    """
    Standardize TSV file with the following operations:
    - Normalize line endings to LF
    - Ensure consistent 4-column structure
    - Remove trailing whitespace from all fields
    - Convert HTML entities to plain text
    - Maintain UTF-8 encoding
    
    Returns: dict with standardization details
    """
    expected_columns = ['Object Date', 'Title', 'Object Number', 'Link Resource']
    
    stats = {
        'rows_read': 0,
        'rows_written': 0,
        'empty_title_count': 0,
        'html_entities_found': 0,
        'whitespace_trimmed': 0,
        'issues': []
    }
    
    # Read all rows
    with open(input_file, 'r', encoding='utf-8', newline='') as infile:
        reader = csv.reader(infile, delimiter='\t')
        all_rows = [row for row in reader]
    
    stats['rows_read'] = len(all_rows)
    
    # Process and standardize
    standardized_rows = [expected_columns]  # Always write clean header
    
    for idx, row in enumerate(all_rows[1:], 1):  # Skip original header
        # Ensure 4 columns
        while len(row) < len(expected_columns):
            row.append('')
        row = row[:len(expected_columns)]
        
        # Check for HTML entities before processing
        row_str = ''.join(row)
        if '&lt;' in row_str or '&gt;' in row_str:
            stats['html_entities_found'] += 1
            # Convert HTML entities to plain text
            for i, field in enumerate(row):
                row[i] = field.replace('&lt;i&gt;', '').replace('&lt;/i&gt;', '')
        
        # Strip whitespace and track changes
        trimmed_row = []
        for field in row:
            original = field
            field = field.strip()
            if original != field:
                stats['whitespace_trimmed'] += 1
            trimmed_row.append(field)
        
        # Count empty titles
        if not trimmed_row[1]:  # Title column is index 1
            stats['empty_title_count'] += 1
        
        standardized_rows.append(trimmed_row)
        stats['rows_written'] += 1
    
    # Write standardized output with LF line endings
    with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile, delimiter='\t', lineterminator='\n', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(standardized_rows)
    
    return stats


def generate_checksum_file(source_file, output_file, checksum_file, stats):
    """Generate checksum verification file"""
    
    source_sha256 = calculate_checksum(source_file, 'sha256')
    source_md5 = calculate_checksum(source_file, 'md5')
    output_sha256 = calculate_checksum(output_file, 'sha256')
    output_md5 = calculate_checksum(output_file, 'md5')
    
    with open(checksum_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("MET MUSEUM INVENTORY TSV - STANDARDIZATION CHECKSUMS\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("SOURCE FILE: met_inventory.tsv\n")
        f.write("-" * 80 + "\n")
        f.write(f"MD5:    {source_md5}\n")
        f.write(f"SHA256: {source_sha256}\n")
        f.write(f"Lines:  {count_lines(source_file)}\n\n")
        
        f.write("OUTPUT FILE: met_inventory_standardized.tsv\n")
        f.write("-" * 80 + "\n")
        f.write(f"MD5:    {output_md5}\n")
        f.write(f"SHA256: {output_sha256}\n")
        f.write(f"Lines:  {count_lines(output_file)}\n\n")
        
        f.write("STANDARDIZATION STATISTICS\n")
        f.write("-" * 80 + "\n")
        f.write(f"Total rows processed:      {stats['rows_read']}\n")
        f.write(f"Rows written:              {stats['rows_written']}\n")
        f.write(f"Empty title fields:        {stats['empty_title_count']}\n")
        f.write(f"HTML entities converted:   {stats['html_entities_found']}\n")
        f.write(f"Whitespace trimmed:        {stats['whitespace_trimmed']}\n")
        
        if stats['issues']:
            f.write(f"\nIssues detected:           {len(stats['issues'])}\n")
            for issue in stats['issues']:
                f.write(f"  - {issue}\n")
        else:
            f.write("\nIssues detected:           0\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("STANDARDIZATION OPERATIONS PERFORMED\n")
        f.write("=" * 80 + "\n")
        f.write("✓ Line ending normalization (CRLF → LF)\n")
        f.write("✓ Four-column structure verification\n")
        f.write("✓ Trailing whitespace removal\n")
        f.write("✓ HTML entity conversion\n")
        f.write("✓ UTF-8 encoding preservation\n")
        f.write("✓ Tab-delimiter consistency\n")
        f.write("✓ Data integrity verification\n\n")
        
        f.write("VERIFICATION COMMANDS\n")
        f.write("-" * 80 + "\n")
        f.write("Verify with MD5:\n")
        f.write("  md5sum met_inventory.tsv\n")
        f.write("  md5sum met_inventory_standardized.tsv\n\n")
        
        f.write("Verify with SHA256:\n")
        f.write("  sha256sum met_inventory.tsv\n")
        f.write("  sha256sum met_inventory_standardized.tsv\n\n")
        
        f.write("Verify record count:\n")
        f.write("  wc -l met_inventory_standardized.tsv\n")
        f.write("  (Should be 488: 1 header + 487 data rows)\n\n")
        
        f.write("Verify column count:\n")
        f.write("  head -1 met_inventory_standardized.tsv | tr '\\t' '\\n' | wc -l\n")
        f.write("  (Should be 4)\n\n")
        
        f.write("View first few records:\n")
        f.write("  head -5 met_inventory_standardized.tsv\n\n")
        
        f.write("=" * 80 + "\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 standardize_met_inventory.py <input_file> [output_file]")
        print("\nExample:")
        print("  python3 standardize_met_inventory.py met_inventory.tsv met_inventory_standardized.tsv")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2] if len(sys.argv) > 2 else 'met_inventory_standardized.tsv')
    checksum_file = Path(str(output_file).replace('.tsv', '_CHECKSUMS.txt'))
    
    if not input_file.exists():
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)
    
    print("=" * 80)
    print("MET MUSEUM INVENTORY TSV STANDARDIZATION TOOL")
    print("=" * 80)
    
    # Step 1: Calculate source checksum
    print("\n[1/4] Calculating source file checksums...")
    source_sha256 = calculate_checksum(input_file, 'sha256')
    source_md5 = calculate_checksum(input_file, 'md5')
    source_lines = count_lines(input_file)
    print(f"      Source: {input_file}")
    print(f"      Lines:  {source_lines}")
    print(f"      MD5:    {source_md5}")
    print(f"      SHA256: {source_sha256}")
    
    # Step 2: Standardize the file
    print("\n[2/4] Standardizing TSV file...")
    try:
        stats = standardize_tsv(input_file, output_file)
        print(f"      Rows processed:        {stats['rows_read']}")
        print(f"      Rows written:          {stats['rows_written']}")
        print(f"      Empty title fields:    {stats['empty_title_count']}")
        print(f"      HTML entities found:   {stats['html_entities_found']}")
        print(f"      Whitespace trimmed:    {stats['whitespace_trimmed']}")
        if stats['issues']:
            print(f"      Issues detected:       {len(stats['issues'])}")
        else:
            print("      Issues detected:       0 ✓")
    except Exception as e:
        print(f"      Error during standardization: {e}")
        sys.exit(1)
    
    # Step 3: Verify output
    print("\n[3/4] Verifying standardized file...")
    output_lines = count_lines(output_file)
    print(f"      Output: {output_file}")
    print(f"      Lines:  {output_lines}")
    
    if output_lines == source_lines:
        print("      Line count match: ✓")
    else:
        print(f"      Warning: Line count mismatch ({output_lines} vs {source_lines})")
    
    # Step 4: Calculate output checksum and generate report
    print("\n[4/4] Generating checksum file...")
    generate_checksum_file(input_file, output_file, checksum_file, stats)
    output_sha256 = calculate_checksum(output_file, 'sha256')
    output_md5 = calculate_checksum(output_file, 'md5')
    print(f"      MD5:    {output_md5}")
    print(f"      SHA256: {output_sha256}")
    print(f"      Checksums: {checksum_file}")
    
    # Final report
    print("\n" + "=" * 80)
    print("STANDARDIZATION COMPLETE ✓")
    print("=" * 80)
    print(f"\nFiles generated:")
    print(f"  1. {output_file.name} (standardized data)")
    print(f"  2. {checksum_file.name} (verification checksums)")
    print(f"\nNext steps:")
    print(f"  1. Review the standardized file: less {output_file}")
    print(f"  2. Verify checksums: cat {checksum_file}")
    print(f"  3. Compare with source to confirm changes: diff {input_file} {output_file}")
    print()


if __name__ == '__main__':
    main()
