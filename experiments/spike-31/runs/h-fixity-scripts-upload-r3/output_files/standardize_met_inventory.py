#!/usr/bin/env python3
"""
Standardize Metropolitan Museum TSV inventory file while preserving fixity.
Creates checksums for source and standardized output.
"""

import hashlib
import csv
import sys
from pathlib import Path

def calculate_checksum(file_path, algorithm='sha256'):
    """Calculate file checksum."""
    hasher = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()

def standardize_tsv(input_file, output_file):
    """
    Standardize TSV file:
    - Normalize tab delimiters
    - Ensure consistent line endings (LF)
    - Remove trailing whitespace from cells
    - Sort by Object Date (with proper date parsing) then by Object Number
    - Validate structure (4 columns expected)
    """
    
    rows = []
    
    # Read and parse
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        header = next(reader)
        
        # Validate header
        if len(header) != 4:
            print(f"Warning: Expected 4 columns, found {len(header)}", file=sys.stderr)
        
        for i, row in enumerate(reader, start=2):
            # Ensure 4 columns
            while len(row) < 4:
                row.append('')
            if len(row) > 4:
                row = row[:4]
            
            # Strip whitespace
            row = [cell.strip() for cell in row]
            rows.append(row)
    
    # Sort rows
    def parse_date_key(date_str):
        """Create sortable key from date strings."""
        date_str = date_str.strip()
        
        # Handle BCE dates (extract numeric value)
        if 'BCE' in date_str or 'B.C.' in date_str:
            # Extract number and negate for reverse chronological order
            parts = date_str.split()
            try:
                year = int(parts[0])
                return (0, -year, date_str)  # BCE sorts before CE
            except:
                return (0, 0, date_str)
        
        # Handle date ranges and single years
        # Extract first number for sorting
        import re
        match = re.search(r'\d+', date_str)
        if match:
            year = int(match.group())
            return (1, year, date_str)  # CE dates
        
        # Undated items
        return (2, 0, date_str)
    
    rows.sort(key=lambda r: (parse_date_key(r[0]), r[2]))
    
    # Write standardized output
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t', lineterminator='\n')
        writer.writerow(header)
        writer.writerows(rows)
    
    return len(rows)

def main():
    input_file = 'met_inventory.tsv'
    output_file = 'met_inventory_standardized.tsv'
    checksum_file = 'met_inventory_checksums.txt'
    
    print(f"Processing: {input_file}")
    print(f"Output: {output_file}\n")
    
    # Calculate source checksum
    source_checksum = calculate_checksum(input_file)
    print(f"Source file SHA-256:")
    print(f"  {source_checksum}\n")
    
    # Standardize
    row_count = standardize_tsv(input_file, output_file)
    print(f"Standardization complete: {row_count} data rows processed\n")
    
    # Calculate output checksum
    output_checksum = calculate_checksum(output_file)
    print(f"Output file SHA-256:")
    print(f"  {output_checksum}\n")
    
    # Write checksums to file
    with open(checksum_file, 'w', encoding='utf-8') as f:
        f.write("Metropolitan Museum Inventory TSV Standardization\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Source file: {input_file}\n")
        f.write(f"Output file: {output_file}\n\n")
        f.write(f"Source SHA-256:  {source_checksum}\n")
        f.write(f"Output SHA-256:  {output_checksum}\n\n")
        f.write("Standardization applied:\n")
        f.write("  - Normalized tab delimiters\n")
        f.write("  - Consistent line endings (LF)\n")
        f.write("  - Stripped trailing whitespace from all cells\n")
        f.write("  - Sorted by Object Date (chronological), then Object Number\n")
        f.write(f"  - Total rows: {row_count}\n")
    
    print(f"Checksums saved to: {checksum_file}")
    
    return source_checksum, output_checksum

if __name__ == '__main__':
    main()
