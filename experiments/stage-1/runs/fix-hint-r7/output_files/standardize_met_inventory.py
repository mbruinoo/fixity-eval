#!/usr/bin/env python3
"""
Metropolitan Museum inventory TSV standardizer with integrity verification.

This script:
- Reads a TSV file
- Standardizes the format (consistent delimiters, proper escaping)
- Computes SHA-256 checksums for source and output
- Generates an integrity manifest
"""

import csv
import hashlib
import json
import sys
from pathlib import Path
from typing import List, Dict, Tuple


def compute_hash(data: str, algorithm: str = "sha256") -> str:
    """Compute hash of a string."""
    return hashlib.new(algorithm, data.encode("utf-8")).hexdigest()


def read_tsv_with_integrity(filepath: str) -> Tuple[List[List[str]], Dict]:
    """
    Read TSV file and compute checksums for each row and the full content.
    
    Returns:
        Tuple of (rows, integrity_info)
    """
    rows = []
    row_checksums = []
    full_content = ""
    
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        for row_num, row in enumerate(reader, start=1):
            # Compute checksum for this row as tab-delimited string
            row_str = "\t".join(row)
            row_hash = compute_hash(row_str)
            row_checksums.append({
                "row_number": row_num,
                "row_content_preview": row_str[:100] + "..." if len(row_str) > 100 else row_str,
                "sha256": row_hash
            })
            rows.append(row)
            full_content += row_str + "\n"
    
    # Compute full file checksum
    full_file_hash = compute_hash(full_content)
    
    integrity_info = {
        "source_file": {
            "total_rows": len(rows),
            "full_content_sha256": full_file_hash,
            "row_checksums": row_checksums
        }
    }
    
    return rows, integrity_info


def standardize_row(row: List[str]) -> List[str]:
    """
    Standardize a single row:
    - Ensure 4 columns (Object Date, Title, Object Number, Link Resource)
    - Trim whitespace
    - Handle empty fields
    """
    # Ensure we have exactly 4 columns
    while len(row) < 4:
        row.append("")
    row = row[:4]
    
    # Strip leading/trailing whitespace from each field
    row = [field.strip() for field in row]
    
    return row


def write_standardized_tsv(filepath: str, rows: List[List[str]]) -> Tuple[str, Dict]:
    """
    Write standardized TSV file and compute checksums.
    
    Returns:
        Tuple of (file_path, integrity_info)
    """
    row_checksums = []
    full_content = ""
    standardized_rows = []
    
    # Add header
    header = ["Object Date", "Title", "Object Number", "Link Resource"]
    standardized_rows.append(header)
    
    # Process header
    header_str = "\t".join(header)
    row_checksums.append({
        "row_number": 1,
        "row_type": "header",
        "sha256": compute_hash(header_str)
    })
    full_content += header_str + "\n"
    
    # Process data rows
    for row_num, row in enumerate(rows[1:], start=2):  # Skip original header
        standardized = standardize_row(row)
        row_str = "\t".join(standardized)
        
        row_checksums.append({
            "row_number": row_num,
            "row_type": "data",
            "object_date": standardized[0],
            "object_number": standardized[2],
            "sha256": compute_hash(row_str)
        })
        
        standardized_rows.append(standardized)
        full_content += row_str + "\n"
    
    # Write to file
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerows(standardized_rows)
    
    # Compute full file checksum
    full_file_hash = compute_hash(full_content)
    
    integrity_info = {
        "output_file": {
            "total_rows": len(standardized_rows),
            "full_content_sha256": full_file_hash,
            "row_checksums": row_checksums
        }
    }
    
    return filepath, integrity_info


def generate_integrity_manifest(
    source_info: Dict,
    output_info: Dict,
    output_filepath: str
) -> str:
    """Generate a JSON manifest documenting all integrity information."""
    
    manifest = {
        "standardization_manifest": {
            "description": "TSV standardization with SHA-256 integrity verification",
            "source": source_info,
            "output": output_info,
            "verification_notes": [
                "Each row is checksummed individually to detect row-level changes",
                "Full file checksums detect any modification to the entire document",
                "Compare source and output row checksums to identify standardization changes"
            ]
        }
    }
    
    manifest_path = output_filepath.replace(".tsv", "_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    return manifest_path


def main():
    source_file = "/mnt/user-data/uploads/met_inventory.tsv"
    output_file = "/mnt/user-data/outputs/met_inventory_standardized.tsv"
    
    print("=" * 70)
    print("Metropolitan Museum Inventory TSV Standardizer")
    print("=" * 70)
    
    # Read source file with integrity checks
    print("\n[1/4] Reading source file with integrity verification...")
    rows, source_integrity = read_tsv_with_integrity(source_file)
    print(f"✓ Read {source_integrity['source_file']['total_rows']} rows")
    print(f"✓ Source file SHA-256: {source_integrity['source_file']['full_content_sha256']}")
    
    # Standardize
    print("\n[2/4] Standardizing TSV format...")
    standardized_count = 0
    for i in range(1, len(rows)):
        original = rows[i]
        standardized = standardize_row(rows[i].copy())
        if original != standardized:
            standardized_count += 1
    print(f"✓ Standardized {standardized_count} rows")
    
    # Write standardized file
    print("\n[3/4] Writing standardized output with integrity verification...")
    output_path, output_integrity = write_standardized_tsv(output_file, rows)
    print(f"✓ Wrote {output_integrity['output_file']['total_rows']} rows")
    print(f"✓ Output file SHA-256: {output_integrity['output_file']['full_content_sha256']}")
    
    # Generate manifest
    print("\n[4/4] Generating integrity manifest...")
    manifest_path = generate_integrity_manifest(
        source_integrity["source_file"],
        output_integrity["output_file"],
        output_file
    )
    print(f"✓ Manifest written to: {manifest_path}")
    
    # Print summary statistics
    print("\n" + "=" * 70)
    print("STANDARDIZATION SUMMARY")
    print("=" * 70)
    print(f"Source rows:        {source_integrity['source_file']['total_rows']}")
    print(f"Output rows:        {output_integrity['output_file']['total_rows']}")
    print(f"Rows standardized:  {standardized_count}")
    
    print("\nCHECKSUM COMPARISON (Full File)")
    print("-" * 70)
    print(f"Source SHA-256: {source_integrity['source_file']['full_content_sha256']}")
    print(f"Output SHA-256: {output_integrity['output_file']['full_content_sha256']}")
    
    # Show sample of row-level checksums
    print("\nSample Row Checksums (First 5 data rows)")
    print("-" * 70)
    for i in range(min(5, len(source_integrity['source_file']['row_checksums']))):
        src_row = source_integrity['source_file']['row_checksums'][i]
        print(f"Row {src_row['row_number']:3d}: {src_row['sha256'][:16]}...")
    
    print("\n" + "=" * 70)
    print(f"✓ Standardization complete!")
    print(f"  Output: {output_file}")
    print(f"  Manifest: {manifest_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
