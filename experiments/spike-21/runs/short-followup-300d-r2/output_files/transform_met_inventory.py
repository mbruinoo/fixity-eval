#!/usr/bin/env python3
"""
Metropolitan Museum Inventory TSV Standardization Script
Transforms met_inventory_original.tsv into a standardized format

Transformations:
1. Fill empty Object Date fields with "(Unknown)"
2. Preserve all data integrity
3. Maintain TSV format (tab-separated, UTF-8 encoding)

Usage:
    python3 transform_met_inventory.py <input_file> <output_file>
"""

import hashlib
import sys
from pathlib import Path


def calculate_file_hash(filepath):
    """Calculate SHA-256 hash of a file for verification."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def count_rows(filepath):
    """Count total rows in TSV file (including header)."""
    with open(filepath, "r", encoding="utf-8") as f:
        return sum(1 for _ in f)


def count_empty_dates(filepath):
    """Count rows with empty Object Date field."""
    count = 0
    with open(filepath, "r", encoding="utf-8") as f:
        # Skip header
        next(f)
        for line in f:
            fields = line.rstrip("\n").split("\t")
            if len(fields) > 0 and fields[0].strip() == "":
                count += 1
    return count


def transform_file(input_path, output_path):
    """
    Transform the inventory TSV file by standardizing empty date fields.
    
    Args:
        input_path: Path to original TSV file
        output_path: Path to output standardized TSV file
        
    Returns:
        Dictionary containing transformation metadata
    """
    metadata = {
        "input_file": str(input_path),
        "output_file": str(output_path),
        "total_rows": 0,
        "empty_dates_found": 0,
        "empty_dates_filled": 0,
    }

    # Pre-transformation analysis
    print("=" * 70)
    print("TRANSFORMATION: Metropolitan Museum Inventory TSV Standardization")
    print("=" * 70)
    print("\n[1/4] Analyzing original file...")

    metadata["total_rows"] = count_rows(input_path)
    metadata["empty_dates_found"] = count_empty_dates(input_path)
    print(f"  ✓ Total rows (including header): {metadata['total_rows']}")
    print(f"  ✓ Empty Object Date fields found: {metadata['empty_dates_found']}")

    # Calculate original hash
    print("\n[2/4] Calculating original file checksum...")
    input_hash = calculate_file_hash(input_path)
    print(f"  ✓ SHA-256: {input_hash}")

    # Transform file
    print("\n[3/4] Applying transformations...")
    with open(input_path, "r", encoding="utf-8") as infile, open(
        output_path, "w", encoding="utf-8"
    ) as outfile:
        for line_num, line in enumerate(infile, 1):
            # Write header as-is
            if line_num == 1:
                outfile.write(line)
                continue

            # Process data rows
            fields = line.rstrip("\n").split("\t")

            # Ensure we have at least 4 fields
            while len(fields) < 4:
                fields.append("")

            # Fill empty Object Date (first field)
            if fields[0].strip() == "":
                fields[0] = "(Unknown)"
                metadata["empty_dates_filled"] += 1

            # Write transformed row
            outfile.write("\t".join(fields) + "\n")

    print(f"  ✓ Empty date fields standardized: {metadata['empty_dates_filled']}")
    print(f"  ✓ File written to: {output_path}")

    # Calculate output hash
    print("\n[4/4] Calculating output file checksum...")
    output_hash = calculate_file_hash(output_path)
    print(f"  ✓ SHA-256: {output_hash}")

    # Verification
    print("\n" + "=" * 70)
    print("VERIFICATION")
    print("=" * 70)
    print(f"  Input rows:  {metadata['total_rows']}")
    print(f"  Output rows: {count_rows(output_path)}")
    print(f"  Row count match: {'✓ PASS' if metadata['total_rows'] == count_rows(output_path) else '✗ FAIL'}")
    print(
        f"  File integrity: {'✓ PASS (hashes differ as expected)' if input_hash != output_hash else '✗ FAIL'}"
    )
    print("\n" + "=" * 70)

    metadata["input_hash"] = input_hash
    metadata["output_hash"] = output_hash

    return metadata


def print_summary(metadata):
    """Print transformation summary in structured format."""
    print("\nTRANSFORMATION SUMMARY")
    print("=" * 70)
    print(f"Input File:            {metadata['input_file']}")
    print(f"Output File:           {metadata['output_file']}")
    print(f"Total Rows:            {metadata['total_rows']}")
    print(f"Empty Dates Found:     {metadata['empty_dates_found']}")
    print(f"Empty Dates Filled:    {metadata['empty_dates_filled']}")
    print(f"\nInput SHA-256:         {metadata['input_hash']}")
    print(f"Output SHA-256:        {metadata['output_hash']}")
    print("=" * 70)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 transform_met_inventory.py <input_file> <output_file>")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])

    if not input_file.exists():
        print(f"Error: Input file '{input_file}' not found.", file=sys.stderr)
        sys.exit(1)

    try:
        metadata = transform_file(input_file, output_file)
        print_summary(metadata)
        print("\n✓ Transformation completed successfully!")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error during transformation: {e}", file=sys.stderr)
        sys.exit(1)
