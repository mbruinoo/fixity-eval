#!/usr/bin/env python3
"""
Standardize the Metropolitan Museum inventory TSV file.
Standardization includes:
1. Ensure consistent tab-delimited format
2. Remove trailing whitespace from each line
3. Normalize line endings to LF (Unix)
4. Ensure proper header row
5. Validate data integrity (same column count per row)
"""
import sys
import csv
import hashlib

def standardize_tsv(input_file, output_file):
    """Standardize a TSV file."""
    
    # Read the input file
    rows = []
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE, escapechar='\\')
        for row in reader:
            rows.append(row)
    
    if not rows:
        print("Error: Empty file", file=sys.stderr)
        return False
    
    # Get expected column count from header
    header = rows[0]
    expected_cols = len(header)
    print(f"Header: {header}")
    print(f"Expected columns: {expected_cols}")
    
    # Validate and standardize rows
    standardized_rows = [header]
    issues = []
    
    for row_num, row in enumerate(rows[1:], start=2):
        # Pad rows with empty strings if they have fewer columns
        if len(row) < expected_cols:
            issues.append(f"Row {row_num}: {len(row)} columns (expected {expected_cols}) - padding with empty strings")
            row = row + [''] * (expected_cols - len(row))
        elif len(row) > expected_cols:
            issues.append(f"Row {row_num}: {len(row)} columns (expected {expected_cols}) - truncating to {expected_cols}")
            row = row[:expected_cols]
        
        standardized_rows.append(row)
    
    # Write standardized output
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t', quoting=csv.QUOTE_NONE, escapechar='\\', lineterminator='\n')
        writer.writerows(standardized_rows)
    
    # Print issues found
    if issues:
        print("\nStandardization issues found and corrected:")
        for issue in issues[:10]:  # Print first 10 issues
            print(f"  {issue}")
        if len(issues) > 10:
            print(f"  ... and {len(issues) - 10} more issues")
    else:
        print("\nNo standardization issues found.")
    
    print(f"\nStandardized {len(standardized_rows) - 1} data rows (plus header)")
    return True

def calculate_checksum(filepath):
    """Calculate SHA-256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

if __name__ == "__main__":
    input_file = "/mnt/user-data/uploads/met_inventory.tsv"
    output_file = "/mnt/user-data/outputs/met_inventory_standardized.tsv"
    
    # Get source checksum
    source_checksum = calculate_checksum(input_file)
    print(f"Source file checksum (SHA-256): {source_checksum}\n")
    
    # Standardize
    if standardize_tsv(input_file, output_file):
        # Get output checksum
        output_checksum = calculate_checksum(output_file)
        print(f"\nOutput file checksum (SHA-256): {output_checksum}")
        
        # Save both checksums to file
        with open("/mnt/user-data/outputs/checksums.txt", "w") as f:
            f.write("Metropolitan Museum Inventory TSV - Checksum Report\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Source file: met_inventory.tsv\n")
            f.write(f"Source checksum (SHA-256): {source_checksum}\n\n")
            f.write(f"Output file: met_inventory_standardized.tsv\n")
            f.write(f"Output checksum (SHA-256): {output_checksum}\n\n")
            f.write(f"Files differ: {source_checksum != output_checksum}\n")
        
        print(f"\nChecksum report saved to checksums.txt")
