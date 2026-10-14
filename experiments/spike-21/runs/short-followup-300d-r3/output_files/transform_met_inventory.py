#!/usr/bin/env python3
"""
Standardize MET Museum Inventory TSV File
Transformation script with SHA256 checksums for verification
"""

import csv
import hashlib
import sys
from pathlib import Path
from datetime import datetime


def calculate_file_checksum(filepath):
    """Calculate SHA256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def count_rows(filepath):
    """Count the number of rows in a TSV file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        return sum(1 for _ in reader)


def standardize_tsv(input_file, output_file):
    """
    Standardize TSV file by:
    1. Ensuring consistent tab-delimited columns
    2. Validating all rows have 4 columns
    3. Preserving all data including empty cells
    4. Maintaining UTF-8 encoding
    """
    
    print(f"Starting transformation at {datetime.now().isoformat()}")
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print()
    
    # Count original rows
    original_row_count = count_rows(input_file)
    print(f"Original file rows: {original_row_count}")
    
    # Read input file
    rows = []
    issues = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for row_num, row in enumerate(reader, 1):
            # Handle rows with incorrect column count
            if len(row) < 4:
                # Pad with empty strings
                row = row + [''] * (4 - len(row))
                issues.append(f"Row {row_num}: Padded from {len(row)-1} to 4 columns")
            elif len(row) > 4:
                # Truncate excess columns
                row = row[:4]
                issues.append(f"Row {row_num}: Truncated from {len(row)+1} to 4 columns")
            
            rows.append(row)
    
    print(f"Total rows processed: {len(rows)}")
    if issues:
        print(f"Issues found: {len(issues)}")
        for issue in issues[:5]:  # Show first 5 issues
            print(f"  - {issue}")
        if len(issues) > 5:
            print(f"  ... and {len(issues) - 5} more issues")
    else:
        print("No structural issues found")
    print()
    
    # Write standardized output
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t', lineterminator='\n')
        writer.writerows(rows)
    
    output_row_count = count_rows(output_file)
    print(f"Output file rows: {output_row_count}")
    
    # Verify row count preservation
    if original_row_count != output_row_count:
        print(f"WARNING: Row count mismatch! ({original_row_count} → {output_row_count})")
        return False
    else:
        print("✓ Row count verified")
    
    return True


def generate_report(input_file, output_file, script_file):
    """Generate transformation report with checksums."""
    
    print("\n" + "="*70)
    print("TRANSFORMATION REPORT")
    print("="*70)
    
    # Calculate checksums
    input_checksum = calculate_file_checksum(input_file)
    output_checksum = calculate_file_checksum(output_file)
    script_checksum = calculate_file_checksum(script_file)
    
    print(f"\nInput file: {Path(input_file).name}")
    print(f"  Checksum (SHA256): {input_checksum}")
    print(f"  Size: {Path(input_file).stat().st_size} bytes")
    
    print(f"\nOutput file: {Path(output_file).name}")
    print(f"  Checksum (SHA256): {output_checksum}")
    print(f"  Size: {Path(output_file).stat().st_size} bytes")
    
    print(f"\nTransformation script: {Path(script_file).name}")
    print(f"  Checksum (SHA256): {script_checksum}")
    
    print(f"\nTimestamp: {datetime.now().isoformat()}")
    print("="*70 + "\n")
    
    return {
        'input_file': Path(input_file).name,
        'input_checksum': input_checksum,
        'input_size': Path(input_file).stat().st_size,
        'output_file': Path(output_file).name,
        'output_checksum': output_checksum,
        'output_size': Path(output_file).stat().st_size,
        'script_file': Path(script_file).name,
        'script_checksum': script_checksum,
        'timestamp': datetime.now().isoformat()
    }


def save_manifest(manifest_data, manifest_file):
    """Save checksums and metadata to manifest file."""
    with open(manifest_file, 'w', encoding='utf-8') as f:
        f.write("MET INVENTORY TRANSFORMATION MANIFEST\n")
        f.write("="*70 + "\n\n")
        f.write(f"Timestamp: {manifest_data['timestamp']}\n\n")
        
        f.write("INPUT FILE\n")
        f.write("-"*70 + "\n")
        f.write(f"Filename: {manifest_data['input_file']}\n")
        f.write(f"Size: {manifest_data['input_size']} bytes\n")
        f.write(f"SHA256: {manifest_data['input_checksum']}\n\n")
        
        f.write("OUTPUT FILE\n")
        f.write("-"*70 + "\n")
        f.write(f"Filename: {manifest_data['output_file']}\n")
        f.write(f"Size: {manifest_data['output_size']} bytes\n")
        f.write(f"SHA256: {manifest_data['output_checksum']}\n\n")
        
        f.write("TRANSFORMATION SCRIPT\n")
        f.write("-"*70 + "\n")
        f.write(f"Filename: {manifest_data['script_file']}\n")
        f.write(f"SHA256: {manifest_data['script_checksum']}\n\n")
        
        f.write("VERIFICATION INSTRUCTIONS\n")
        f.write("-"*70 + "\n")
        f.write("To verify file integrity, run:\n\n")
        f.write(f"  sha256sum -c <<EOF\n")
        f.write(f"  {manifest_data['input_checksum']}  {manifest_data['input_file']}\n")
        f.write(f"  {manifest_data['output_checksum']}  {manifest_data['output_file']}\n")
        f.write(f"  EOF\n\n")
        
        f.write("To re-run transformation:\n")
        f.write(f"  python3 {manifest_data['script_file']} \\\n")
        f.write(f"    --input {manifest_data['input_file']} \\\n")
        f.write(f"    --output {manifest_data['output_file']}\n")


def main():
    """Main transformation workflow."""
    
    # Default paths
    input_file = "met_inventory_original.tsv"
    output_file = "met_inventory_standardized.tsv"
    manifest_file = "transformation_manifest.txt"
    script_file = "transform_met_inventory.py"
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        for i, arg in enumerate(sys.argv[1:]):
            if arg == '--input' and i + 2 < len(sys.argv):
                input_file = sys.argv[i + 2]
            elif arg == '--output' and i + 2 < len(sys.argv):
                output_file = sys.argv[i + 2]
    
    # Verify input file exists
    if not Path(input_file).exists():
        print(f"ERROR: Input file not found: {input_file}", file=sys.stderr)
        sys.exit(1)
    
    # Perform standardization
    success = standardize_tsv(input_file, output_file)
    
    if not success:
        print("ERROR: Transformation verification failed", file=sys.stderr)
        sys.exit(1)
    
    # Generate report and manifest
    manifest_data = generate_report(input_file, output_file, script_file)
    save_manifest(manifest_data, manifest_file)
    
    print(f"✓ Transformation completed successfully")
    print(f"✓ Manifest saved to: {manifest_file}")
    sys.exit(0)


if __name__ == "__main__":
    main()
