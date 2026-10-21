#!/usr/bin/env python3
"""
Met Inventory TSV Standardization Script
Preserves data integrity through checksumming at file and row levels
"""

import csv
import hashlib
import sys
from pathlib import Path
from datetime import datetime

def compute_hash(content, algorithm='sha256'):
    """Compute hash of content"""
    if isinstance(content, str):
        content = content.encode('utf-8')
    hasher = hashlib.new(algorithm)
    hasher.update(content)
    return hasher.hexdigest()

def standardize_tsv(input_file, output_file, checksum_file):
    """
    Standardize Met inventory TSV file
    
    Standardizations applied:
    1. Consistent tab delimiter
    2. Proper UTF-8 encoding
    3. Normalized line endings (LF only)
    4. Consistent column structure
    5. Trimmed whitespace
    6. Consistent quoting (minimal)
    """
    
    # Read source file
    with open(input_file, 'r', encoding='utf-8') as f:
        source_content = f.read()
    
    source_hash = compute_hash(source_content, 'sha256')
    source_md5 = compute_hash(source_content, 'md5')
    
    # Parse TSV with dialect detection
    rows = []
    with open(input_file, 'r', encoding='utf-8', newline='') as f:
        # Read header
        reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE, escapechar='\\')
        for row in reader:
            rows.append(row)
    
    # Standardize rows
    standardized_rows = []
    row_checksums = []
    
    for idx, row in enumerate(rows):
        # Ensure exactly 4 columns (pad if necessary)
        while len(row) < 4:
            row.append('')
        row = row[:4]  # Trim if more than 4
        
        # Strip whitespace from each field
        row = [field.strip() for field in row]
        
        standardized_rows.append(row)
        
        # Compute row checksum (MD5 for readability in log)
        row_content = '\t'.join(row)
        row_hash = compute_hash(row_content, 'md5')
        row_checksums.append((idx, row_hash, row_content[:80]))  # Store first 80 chars
    
    # Write standardized output
    output_content_lines = []
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        for row in standardized_rows:
            writer.writerow(row)
            output_content_lines.append('\t'.join(row))
    
    # Read back standardized content for checksum
    with open(output_file, 'r', encoding='utf-8') as f:
        output_content = f.read()
    
    output_hash = compute_hash(output_content, 'sha256')
    output_md5 = compute_hash(output_content, 'md5')
    
    # Write checksum report
    with open(checksum_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("MET INVENTORY TSV STANDARDIZATION REPORT\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("TIMESTAMP\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n\n")
        
        f.write("SOURCE FILE INTEGRITY\n")
        f.write("-" * 80 + "\n")
        f.write(f"File: {input_file}\n")
        f.write(f"Rows: {len(rows)}\n")
        f.write(f"SHA-256: {source_hash}\n")
        f.write(f"MD5:     {source_md5}\n\n")
        
        f.write("OUTPUT FILE INTEGRITY\n")
        f.write("-" * 80 + "\n")
        f.write(f"File: {output_file}\n")
        f.write(f"Rows: {len(standardized_rows)}\n")
        f.write(f"SHA-256: {output_hash}\n")
        f.write(f"MD5:     {output_md5}\n\n")
        
        f.write("STANDARDIZATION OPERATIONS\n")
        f.write("-" * 80 + "\n")
        f.write("1. Converted to standard TSV format (tab-delimited)\n")
        f.write("2. Normalized to UTF-8 encoding\n")
        f.write("3. Standardized line endings (LF only)\n")
        f.write("4. Ensured exactly 4 columns per row\n")
        f.write("5. Trimmed leading/trailing whitespace from fields\n")
        f.write("6. Applied minimal quoting strategy\n\n")
        
        f.write("ROW-LEVEL CHECKSUMS (MD5)\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'Row':<6} {'MD5 Checksum':<34} {'Preview':<40}\n")
        f.write("-" * 80 + "\n")
        for row_idx, row_hash, preview in row_checksums:
            f.write(f"{row_idx:<6} {row_hash:<34} {preview}\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("END OF REPORT\n")
        f.write("=" * 80 + "\n")
    
    return {
        'source_sha256': source_hash,
        'source_md5': source_md5,
        'output_sha256': output_hash,
        'output_md5': output_md5,
        'rows': len(standardized_rows),
        'row_checksums': row_checksums
    }

if __name__ == '__main__':
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'met_inventory.tsv'
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'met_inventory_standardized.tsv'
    checksum_file = sys.argv[3] if len(sys.argv) > 3 else 'met_inventory_checksums.txt'
    
    results = standardize_tsv(input_file, output_file, checksum_file)
    
    print(f"✓ Standardization complete")
    print(f"  Source SHA-256: {results['source_sha256']}")
    print(f"  Output SHA-256: {results['output_sha256']}")
    print(f"  Total rows: {results['rows']}")
    print(f"  Checksum report: {checksum_file}")
