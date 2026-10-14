#!/usr/bin/env python3
"""
Met Museum Inventory TSV Standardization Script

This script performs data standardization on the Met Museum inventory TSV file.
All transformations are logged and verified with checksums (MD5 and SHA256).

Transformations performed:
1. Fill missing titles with [Untitled]
2. Fill missing dates with [Unknown]
3. Extract English titles from multi-lingual entries (pipe-separated)
4. Verify all rows have exactly 4 columns
5. Remove leading/trailing whitespace
6. Verify data integrity with checksums
"""

import sys
import csv
import hashlib
import json
from pathlib import Path
from datetime import datetime


def calculate_checksums(file_path):
    """Calculate MD5 and SHA256 checksums for a file."""
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


def get_file_stats(file_path):
    """Get file statistics."""
    path = Path(file_path)
    return {
        'size_bytes': path.stat().st_size,
        'last_modified': datetime.fromtimestamp(path.stat().st_mtime).isoformat()
    }


def standardize_title(title):
    """
    Standardize title field.
    - Replace empty strings with [Untitled]
    - For multi-lingual entries (pipe-separated), extract English part
    """
    title = title.strip()
    
    if not title:
        return '[Untitled]'
    
    # Handle pipe-separated multi-lingual entries (e.g., "Chinese text|English text")
    if '|' in title:
        parts = title.split('|')
        # Return the last non-empty part (usually English translation)
        for part in reversed(parts):
            part = part.strip()
            if part:
                return part
        return '[Untitled]'
    
    return title


def standardize_date(date):
    """
    Standardize date field.
    - Replace empty strings with [Unknown]
    - Keep 'n.d.' as is (means "no date")
    """
    date = date.strip()
    return date if date else '[Unknown]'


def transform_row(row):
    """Transform a single row, applying all standardization rules."""
    if len(row) != 4:
        raise ValueError(f"Row has {len(row)} columns, expected 4. Row: {row}")
    
    date, title, object_num, link = row
    
    # Apply standardizations
    date = standardize_date(date)
    title = standardize_title(title)
    object_num = object_num.strip()
    link = link.strip()
    
    return [date, title, object_num, link]


def standardize_tsv(input_path, output_path, log_path):
    """
    Main transformation function.
    
    Args:
        input_path: Path to input TSV file
        output_path: Path to output TSV file
        log_path: Path to transformation log file
    """
    
    log_entries = {
        'timestamp': datetime.now().isoformat(),
        'script_version': '1.0',
        'input_file': str(input_path),
        'output_file': str(output_path),
        'transformations': [],
        'statistics': {
            'total_rows': 0,
            'rows_with_missing_title': 0,
            'rows_with_missing_date': 0,
            'rows_with_multilingual_title': 0,
            'transformations_applied': 0
        },
        'checksums': {}
    }
    
    # Calculate input checksums
    print("Calculating input file checksums...")
    log_entries['checksums']['input_file'] = calculate_checksums(input_path)
    log_entries['checksums']['input_file'].update(get_file_stats(input_path))
    print(f"  MD5: {log_entries['checksums']['input_file']['md5']}")
    print(f"  SHA256: {log_entries['checksums']['input_file']['sha256']}")
    
    # Read and transform data
    print("\nReading input file...")
    rows_data = []
    
    with open(input_path, 'r', encoding='utf-8') as infile:
        reader = csv.reader(infile, delimiter='\t')
        
        # Read header
        header = next(reader)
        print(f"Header: {header}")
        log_entries['header'] = header
        
        # Process data rows
        for row_num, row in enumerate(reader, start=2):  # Start at 2 (row 1 is header)
            if len(row) != 4:
                raise ValueError(f"Row {row_num} has {len(row)} columns, expected 4")
            
            original_row = row.copy()
            log_entries['statistics']['total_rows'] += 1
            
            # Track what needs transformation
            date_val, title_val, object_num, link_val = row
            
            if not date_val.strip():
                log_entries['statistics']['rows_with_missing_date'] += 1
            
            if not title_val.strip():
                log_entries['statistics']['rows_with_missing_title'] += 1
            elif '|' in title_val:
                log_entries['statistics']['rows_with_multilingual_title'] += 1
            
            # Transform row
            transformed_row = transform_row(row)
            
            # Log if row was changed
            if original_row != transformed_row:
                log_entries['statistics']['transformations_applied'] += 1
                log_entries['transformations'].append({
                    'row_number': row_num,
                    'original': original_row,
                    'transformed': transformed_row
                })
            
            rows_data.append(transformed_row)
    
    # Write output file
    print(f"\nWriting output file ({len(rows_data)} data rows)...")
    with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile, delimiter='\t')
        writer.writerow(header)
        writer.writerows(rows_data)
    
    # Calculate output checksums
    print("\nCalculating output file checksums...")
    log_entries['checksums']['output_file'] = calculate_checksums(output_path)
    log_entries['checksums']['output_file'].update(get_file_stats(output_path))
    print(f"  MD5: {log_entries['checksums']['output_file']['md5']}")
    print(f"  SHA256: {log_entries['checksums']['output_file']['sha256']}")
    
    # Verify transformation
    print("\nVerifying transformation...")
    with open(output_path, 'r', encoding='utf-8') as f:
        output_rows = list(csv.reader(f, delimiter='\t'))
    
    if len(output_rows) != len(rows_data) + 1:  # +1 for header
        raise ValueError("Output row count mismatch!")
    
    # Check that no empty cells remain
    empty_cells = 0
    for row_num, row in enumerate(output_rows[1:], start=2):
        for col_num, cell in enumerate(row):
            if not cell.strip() and col_num < 4:  # Check first 4 columns
                empty_cells += 1
                print(f"  WARNING: Empty cell at row {row_num}, column {col_num}")
    
    log_entries['statistics']['empty_cells_remaining'] = empty_cells
    
    if empty_cells == 0:
        print("  ✓ No empty cells found - verification PASSED")
    else:
        print(f"  ✗ Found {empty_cells} empty cells - verification FAILED")
    
    # Write log file
    print(f"\nWriting log file...")
    with open(log_path, 'w', encoding='utf-8') as logfile:
        json.dump(log_entries, logfile, indent=2)
    
    print(f"✓ Log written to {log_path}")
    
    # Print summary
    print("\n" + "="*60)
    print("TRANSFORMATION SUMMARY")
    print("="*60)
    print(f"Total rows processed: {log_entries['statistics']['total_rows']}")
    print(f"Rows with missing dates: {log_entries['statistics']['rows_with_missing_date']}")
    print(f"Rows with missing titles: {log_entries['statistics']['rows_with_missing_title']}")
    print(f"Rows with multilingual titles: {log_entries['statistics']['rows_with_multilingual_title']}")
    print(f"Total transformations applied: {log_entries['statistics']['transformations_applied']}")
    print(f"Empty cells remaining: {log_entries['statistics']['empty_cells_remaining']}")
    print("="*60)
    
    return log_entries


if __name__ == '__main__':
    # File paths
    input_file = Path(__file__).parent / 'met_inventory_original.tsv'
    output_file = Path(__file__).parent / 'met_inventory_standardized.tsv'
    log_file = Path(__file__).parent / 'standardization.log.json'
    
    if not input_file.exists():
        print(f"ERROR: Input file not found: {input_file}")
        sys.exit(1)
    
    try:
        print("Met Museum Inventory Standardization")
        print("=====================================\n")
        standardize_tsv(input_file, output_file, log_file)
        print("\n✓ Standardization completed successfully!")
    except Exception as e:
        print(f"\n✗ ERROR: {e}", file=sys.stderr)
        sys.exit(1)
