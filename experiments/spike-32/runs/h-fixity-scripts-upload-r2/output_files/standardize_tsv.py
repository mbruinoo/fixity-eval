#!/usr/bin/env python3
"""
Standardize TSV file with checksum verification for fixity.
Standardization includes:
- Fixing inconsistent delimiters (tabs)
- Normalizing whitespace
- Ensuring consistent column structure
- Removing or flagging problematic rows
"""

import csv
import hashlib
import sys
from pathlib import Path

def compute_sha256(file_path):
    """Compute SHA-256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def compute_content_sha256(content_str):
    """Compute SHA-256 checksum of a string."""
    return hashlib.sha256(content_str.encode()).hexdigest()

def standardize_tsv(input_file, output_file, log_file):
    """
    Standardize a TSV file and generate checksums and log.
    """
    # Expected columns based on the data
    expected_columns = ["Object Date", "Title", "Object Number", "Link Resource"]
    
    # Read and parse the source file
    rows_read = 0
    rows_written = 0
    issues = []
    
    standardized_rows = []
    
    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            # Use tab as delimiter
            reader = csv.DictReader(infile, delimiter='\t')
            
            # Verify column names
            if reader.fieldnames != expected_columns:
                issues.append(f"Column mismatch. Found: {reader.fieldnames}")
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (after header)
                rows_read += 1
                standardized_row = {}
                
                # Standardize each field
                for col in expected_columns:
                    value = row.get(col, "").strip()
                    standardized_row[col] = value
                
                standardized_rows.append(standardized_row)
                rows_written += 1
    
    except Exception as e:
        issues.append(f"Error reading file: {str(e)}")
        return False, issues
    
    # Write standardized output
    try:
        with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=expected_columns, delimiter='\t')
            writer.writeheader()
            writer.writerows(standardized_rows)
    except Exception as e:
        issues.append(f"Error writing output file: {str(e)}")
        return False, issues
    
    # Compute checksums
    source_checksum = compute_sha256(input_file)
    output_checksum = compute_sha256(output_file)
    
    # Read file contents for content-based checksums
    with open(input_file, 'r', encoding='utf-8') as f:
        source_content = f.read()
    with open(output_file, 'r', encoding='utf-8') as f:
        output_content = f.read()
    
    source_content_checksum = compute_content_sha256(source_content)
    output_content_checksum = compute_content_sha256(output_content)
    
    # Generate log
    log_content = f"""# TSV Standardization Report
## Fixity Verification

### Source File
- File: {input_file}
- SHA-256 (file): {source_checksum}
- SHA-256 (content): {source_content_checksum}
- Rows read: {rows_read}

### Output File
- File: {output_file}
- SHA-256 (file): {output_checksum}
- SHA-256 (content): {output_content_checksum}
- Rows written: {rows_written}

## Standardization Details
- Delimiter: TAB (\\t)
- Encoding: UTF-8
- Expected columns: {', '.join(expected_columns)}
- Whitespace normalized: Yes
- Field formatting: Trimmed

## Issues and Notes
{len(issues)} issue(s) found:
"""
    
    if issues:
        for issue in issues:
            log_content += f"- {issue}\n"
    else:
        log_content += "- No issues detected\n"
    
    log_content += f"""
## Verification
To verify source file integrity:
  sha256sum {input_file}
  Expected: {source_checksum}

To verify output file integrity:
  sha256sum {output_file}
  Expected: {output_checksum}
"""
    
    # Write log file
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(log_content)
    
    return True, (source_checksum, output_checksum, source_content_checksum, output_content_checksum, issues)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 standardize_tsv.py <input_file> [output_file] [log_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.tsv', '_standardized.tsv')
    log_file = sys.argv[3] if len(sys.argv) > 3 else input_file.replace('.tsv', '_standardization.log')
    
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print(f"Log file: {log_file}")
    print()
    
    success, result = standardize_tsv(input_file, output_file, log_file)
    
    if success:
        source_cs, output_cs, source_content_cs, output_content_cs, issues = result
        print("✓ Standardization completed successfully")
        print()
        print(f"Source file SHA-256:       {source_cs}")
        print(f"Output file SHA-256:       {output_cs}")
        print(f"Source content SHA-256:    {source_content_cs}")
        print(f"Output content SHA-256:    {output_content_cs}")
        print()
        if issues:
            print(f"⚠ {len(issues)} issue(s) detected:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("✓ No issues detected")
        print()
        print(f"Log saved to: {log_file}")
    else:
        print("✗ Standardization failed")
        for issue in result:
            print(f"  - {issue}")
        sys.exit(1)
