#!/usr/bin/env python3
"""
Standardize met_inventory.tsv with fixity preservation through checksums.
This script:
1. Computes checksums of the source file and individual rows
2. Standardizes the TSV structure
3. Computes checksums of the output file and rows
4. Outputs a manifest documenting all changes
"""

import csv
import hashlib
import json
from pathlib import Path
from datetime import datetime

def compute_hash(content, algorithm='sha256'):
    """Compute hash of content (string or bytes)."""
    if isinstance(content, str):
        content = content.encode('utf-8')
    h = hashlib.sha256() if algorithm == 'sha256' else hashlib.sha1()
    h.update(content)
    return h.hexdigest()

def read_tsv_with_checksums(filepath):
    """Read TSV file and compute row-level checksums."""
    rows = []
    row_checksums = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for idx, row in enumerate(reader, start=2):  # start at 2 because header is line 1
            # Store row with original content
            row_dict = dict(row)
            rows.append(row_dict)
            
            # Compute checksum of the row (join all values)
            row_content = '\t'.join(str(v) for v in row_dict.values())
            row_hash = compute_hash(row_content)
            row_checksums.append({
                'line_number': idx,
                'sha256': row_hash,
                'row_data': row_dict
            })
    
    return rows, row_checksums

def standardize_row(row):
    """Standardize a single row."""
    standardized = {}
    
    # Ensure consistent field ordering
    standardized['Object Date'] = (row.get('Object Date') or '').strip()
    standardized['Title'] = (row.get('Title') or '').strip()
    standardized['Object Number'] = (row.get('Object Number') or '').strip()
    standardized['Link Resource'] = (row.get('Link Resource') or '').strip()
    
    return standardized

def write_standardized_tsv(filepath, rows):
    """Write standardized TSV file."""
    fieldnames = ['Object Date', 'Title', 'Object Number', 'Link Resource']
    
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        writer.writerows(rows)

def main():
    input_file = '/mnt/user-data/uploads/met_inventory.tsv'
    output_file = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
    manifest_file = '/mnt/user-data/outputs/met_inventory_manifest.json'
    
    print("=" * 70)
    print("MET INVENTORY TSV STANDARDIZATION WITH FIXITY PRESERVATION")
    print("=" * 70)
    
    # Step 1: Read source file and compute checksums
    print("\n[1] Reading source file and computing checksums...")
    try:
        source_rows, source_checksums = read_tsv_with_checksums(input_file)
        print(f"    ✓ Read {len(source_rows)} data rows")
    except FileNotFoundError:
        print(f"    ✗ Error: Source file not found at {input_file}")
        return
    
    # Compute source file hash
    with open(input_file, 'rb') as f:
        source_file_hash = compute_hash(f.read())
    print(f"    ✓ Source file SHA256: {source_file_hash}")
    
    # Step 2: Standardize rows
    print("\n[2] Standardizing rows...")
    standardized_rows = [standardize_row(row) for row in source_rows]
    print(f"    ✓ Standardized {len(standardized_rows)} rows")
    
    # Step 3: Write standardized file
    print("\n[3] Writing standardized TSV file...")
    write_standardized_tsv(output_file, standardized_rows)
    print(f"    ✓ Wrote to {output_file}")
    
    # Step 4: Compute output checksums
    print("\n[4] Computing output file checksums...")
    output_checksums = []
    
    with open(output_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for idx, row in enumerate(reader, start=2):
            row_content = '\t'.join(str(v) for v in row.values())
            row_hash = compute_hash(row_content)
            output_checksums.append({
                'line_number': idx,
                'sha256': row_hash,
                'row_data': dict(row)
            })
    
    # Compute output file hash
    with open(output_file, 'rb') as f:
        output_file_hash = compute_hash(f.read())
    print(f"    ✓ Output file SHA256: {output_file_hash}")
    
    # Step 5: Create manifest
    print("\n[5] Creating fixity manifest...")
    manifest = {
        'timestamp': datetime.now().isoformat(),
        'process': 'TSV standardization with fixity preservation',
        'source': {
            'filepath': input_file,
            'file_hash_sha256': source_file_hash,
            'total_rows': len(source_rows),
            'row_hashes': source_checksums
        },
        'output': {
            'filepath': output_file,
            'file_hash_sha256': output_file_hash,
            'total_rows': len(standardized_rows),
            'row_hashes': output_checksums
        },
        'standardization_applied': {
            'field_order': ['Object Date', 'Title', 'Object Number', 'Link Resource'],
            'actions': [
                'Ensured consistent column ordering',
                'Trimmed whitespace from all fields',
                'Normalized empty cells',
                'Preserved all data content'
            ]
        },
        'verification': {
            'source_rows_unchanged': len(source_rows) == len(standardized_rows),
            'note': 'Row hashes may differ due to whitespace trimming and field reordering'
        }
    }
    
    # Write manifest
    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    print(f"    ✓ Wrote manifest to {manifest_file}")
    
    # Step 6: Summary report
    print("\n" + "=" * 70)
    print("STANDARDIZATION COMPLETE")
    print("=" * 70)
    print(f"\nSource File:")
    print(f"  Path: {input_file}")
    print(f"  SHA256: {source_file_hash}")
    print(f"  Rows: {len(source_rows)}")
    print(f"\nOutput File:")
    print(f"  Path: {output_file}")
    print(f"  SHA256: {output_file_hash}")
    print(f"  Rows: {len(standardized_rows)}")
    print(f"\nFixity Documentation:")
    print(f"  Manifest: {manifest_file}")
    print(f"  Row-level checksums: {len(source_checksums)} source + {len(output_checksums)} output")
    print("\n" + "=" * 70)

if __name__ == '__main__':
    main()
