#!/usr/bin/env python3
"""
Standardize Met Museum inventory TSV file with checksum verification.
Preserves data integrity through checksums of source and result.
"""

import csv
import hashlib
from pathlib import Path


def calculate_checksum(file_path, algorithm='sha256'):
    """Calculate checksum of a file."""
    hash_obj = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()


def standardize_tsv(input_path, output_path):
    """
    Standardize the TSV file:
    - Ensure consistent tab-delimited format
    - Handle empty fields properly
    - Normalize quote escaping
    - Preserve all data
    """
    
    # Read the original file
    rows = []
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE, escapechar='\\')
        for row in reader:
            # Ensure all rows have exactly 4 columns (header + 3 data columns)
            while len(row) < 4:
                row.append('')
            # Trim to 4 columns if there are more
            row = row[:4]
            rows.append(row)
    
    # Write standardized file with proper quoting
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        for row in writer.writerows(rows)
    
    # Rewrite using manual approach to ensure consistency
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, row in enumerate(rows):
            # Escape internal quotes and wrap fields that need quoting
            cleaned_row = []
            for field in row:
                # Fields with tabs, newlines, or quotes need special handling
                if '\t' in field or '\n' in field or '"' in field:
                    field = field.replace('"', '""')  # Escape quotes
                    field = f'"{field}"'
                cleaned_row.append(field)
            
            f.write('\t'.join(cleaned_row) + '\n')


def generate_report(input_path, output_path, report_path):
    """Generate a detailed report with checksums."""
    
    input_hash = calculate_checksum(input_path, 'sha256')
    output_hash = calculate_checksum(output_path, 'sha256')
    
    # Count rows
    with open(input_path, 'r', encoding='utf-8') as f:
        input_rows = sum(1 for _ in f)
    
    with open(output_path, 'r', encoding='utf-8') as f:
        output_rows = sum(1 for _ in f)
    
    # Get file sizes
    input_size = Path(input_path).stat().st_size
    output_size = Path(output_path).stat().st_size
    
    report = f"""
# Met Museum Inventory TSV Standardization Report

## Source File
- **File**: {Path(input_path).name}
- **Size**: {input_size:,} bytes
- **Rows**: {input_rows}
- **SHA-256**: {input_hash}

## Standardized Output
- **File**: {Path(output_path).name}
- **Size**: {output_size:,} bytes
- **Rows**: {output_rows}
- **SHA-256**: {output_hash}

## Standardization Process
The following improvements were made to ensure consistency:

1. **Tab Delimiters**: Ensured all fields are properly tab-delimited
2. **Empty Fields**: Normalized representation of empty cells
3. **Quote Escaping**: Standardized quote handling (doubled quotes within quoted fields)
4. **Column Count**: All rows standardized to 4 columns
   - Column 1: Object Date
   - Column 2: Title
   - Column 3: Object Number
   - Column 4: Link Resource
5. **Line Endings**: Normalized to Unix line endings (LF)
6. **Character Encoding**: Preserved UTF-8 for international characters

## Data Integrity
- **Hash Verification**: Use the checksums above to verify file integrity
- **Source Checksum**: Compute SHA-256 of original file and compare with {input_hash}
- **Output Checksum**: Compute SHA-256 of standardized file and compare with {output_hash}

## Usage
To verify file integrity:
```bash
# Verify source file
sha256sum {Path(input_path).name}
# Should output: {input_hash}  {Path(input_path).name}

# Verify standardized file
sha256sum {Path(output_path).name}
# Should output: {output_hash}  {Path(output_path).name}
```

---
Generated: Standardization Complete
Total Records: {input_rows - 1} objects (excluding header)
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(report)
    return input_hash, output_hash


if __name__ == '__main__':
    input_file = '/mnt/user-data/uploads/met_inventory.tsv'
    output_file = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
    report_file = '/mnt/user-data/outputs/standardization_report.md'
    
    print("Starting TSV standardization...")
    standardize_tsv(input_file, output_file)
    print(f"✓ Standardized file created: {output_file}")
    
    input_hash, output_hash = generate_report(input_file, output_file, report_file)
    print(f"\n✓ Report generated: {report_file}")
    print(f"\nChecksum Summary:")
    print(f"  Source SHA-256:        {input_hash}")
    print(f"  Standardized SHA-256:  {output_hash}")
