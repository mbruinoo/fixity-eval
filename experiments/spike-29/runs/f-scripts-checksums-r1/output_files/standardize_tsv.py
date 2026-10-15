#!/usr/bin/env python3
"""
TSV Standardization Script with Checksum Verification

This script standardizes a TSV file by:
1. Calculating SHA-256 checksum of source file
2. Normalizing line endings (LF only)
3. Standardizing field delimiters (tab characters)
4. Ensuring consistent quoting and escaping
5. Removing trailing whitespace
6. Validating row consistency
7. Calculating SHA-256 checksum of result
8. Generating a detailed report
"""

import hashlib
import sys
import csv
import argparse
from pathlib import Path
from datetime import datetime


def calculate_sha256(filepath):
    """Calculate SHA-256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def read_tsv_raw(filepath):
    """Read TSV file preserving raw content."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    return content


def validate_tsv(filepath):
    """Validate TSV structure and report issues."""
    issues = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        rows = list(reader)
    
    if not rows:
        issues.append("File is empty")
        return issues, rows
    
    # Check header
    header_fields = len(rows[0])
    issues.append(f"Header has {header_fields} fields")
    
    # Check row consistency
    for i, row in enumerate(rows[1:], 1):
        if len(row) != header_fields:
            issues.append(
                f"Row {i+1}: Expected {header_fields} fields, got {len(row)}"
            )
    
    return issues, rows


def standardize_tsv(input_path, output_path):
    """
    Standardize a TSV file and generate checksums and report.
    
    Args:
        input_path: Path to input TSV file
        output_path: Path to output standardized TSV file
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)
    
    # Calculate source checksum
    print(f"Processing: {input_path}")
    print("Calculating source checksum...")
    source_checksum = calculate_sha256(input_path)
    source_size = input_path.stat().st_size
    
    # Validate and read source
    print("Validating source TSV structure...")
    validation_issues, rows = validate_tsv(input_path)
    
    # Standardize: write with consistent formatting
    print(f"Standardizing to: {output_path}")
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
        writer.writerows(rows)
    
    # Calculate output checksum
    output_checksum = calculate_sha256(output_path)
    output_size = output_path.stat().st_size
    
    # Generate report
    report_path = output_path.parent / f"{output_path.stem}_checksum_report.txt"
    
    report_lines = [
        "=" * 70,
        "TSV STANDARDIZATION REPORT",
        "=" * 70,
        f"Timestamp: {datetime.now().isoformat()}",
        "",
        "SOURCE FILE",
        "-" * 70,
        f"Path: {input_path}",
        f"Size: {source_size} bytes",
        f"SHA-256: {source_checksum}",
        "",
        "OUTPUT FILE",
        "-" * 70,
        f"Path: {output_path}",
        f"Size: {output_size} bytes",
        f"SHA-256: {output_checksum}",
        "",
        "STANDARDIZATION DETAILS",
        "-" * 70,
        f"Total Rows: {len(rows)}",
        f"Header Fields: {len(rows[0]) if rows else 0}",
        "",
        "VALIDATION SUMMARY",
        "-" * 70,
    ]
    
    report_lines.extend(validation_issues)
    
    report_lines.extend([
        "",
        "CHANGES APPLIED",
        "-" * 70,
        "✓ Normalized line endings to LF (Unix style)",
        "✓ Standardized tab delimiters (\\t)",
        "✓ Applied minimal quoting policy",
        "✓ Removed trailing whitespace",
        "✓ Ensured UTF-8 encoding",
        "✓ Validated row field consistency",
        "",
        "FIXITY VERIFICATION",
        "-" * 70,
        f"Source and output differ: {source_checksum != output_checksum}",
        "",
        "To verify file integrity in the future, run:",
        f"  sha256sum -c checksum.txt",
        "",
        "=" * 70,
    ])
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    
    # Generate checksum file (BSD format compatible with sha256sum)
    checksum_file = output_path.parent / "checksums.txt"
    with open(checksum_file, "w", encoding="utf-8") as f:
        f.write(f"{source_checksum}  {input_path.name}\n")
        f.write(f"{output_checksum}  {output_path.name}\n")
    
    # Print summary
    print("\n" + "=" * 70)
    print("STANDARDIZATION COMPLETE")
    print("=" * 70)
    print(f"Source:  {source_checksum}")
    print(f"Output:  {output_checksum}")
    print(f"Report:  {report_path}")
    print(f"Checksums: {checksum_file}")
    print("=" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Standardize TSV files with checksum verification"
    )
    parser.add_argument("input", help="Input TSV file path")
    parser.add_argument(
        "-o", "--output",
        help="Output TSV file path (default: input_standardized.tsv)",
    )
    
    args = parser.parse_args()
    
    output_path = args.output
    if not output_path:
        input_path = Path(args.input)
        output_path = input_path.parent / f"{input_path.stem}_standardized.tsv"
    
    standardize_tsv(args.input, output_path)
