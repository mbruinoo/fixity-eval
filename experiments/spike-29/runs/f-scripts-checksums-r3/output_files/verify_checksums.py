#!/usr/bin/env python3
"""
Verify checksums of the standardized TSV file.
This ensures data fixity and integrity.
"""

import hashlib
import json
from pathlib import Path


def verify_checksums():
    """Verify that files match their recorded checksums."""
    report_file = Path("/mnt/user-data/outputs/standardization_report.json")
    source_file = Path("/mnt/user-data/uploads/met_inventory.tsv")
    output_file = Path("/mnt/user-data/outputs/met_inventory_standardized.tsv")
    
    # Load the report
    with open(report_file, 'r') as f:
        report = json.load(f)
    
    # Compute current checksums
    def compute_checksum(file_path):
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    source_current = compute_checksum(source_file)
    output_current = compute_checksum(output_file)
    
    # Verify
    source_match = source_current == report['source_checksum_sha256']
    output_match = output_current == report['result_checksum_sha256']
    
    print("\n" + "="*60)
    print("CHECKSUM VERIFICATION REPORT")
    print("="*60)
    
    print(f"\nSource File: {source_file}")
    print(f"  Recorded: {report['source_checksum_sha256']}")
    print(f"  Current:  {source_current}")
    print(f"  Status:   {'✓ VALID' if source_match else '✗ MISMATCH'}")
    
    print(f"\nOutput File: {output_file}")
    print(f"  Recorded: {report['result_checksum_sha256']}")
    print(f"  Current:  {output_current}")
    print(f"  Status:   {'✓ VALID' if output_match else '✗ MISMATCH'}")
    
    print("\n" + "="*60)
    if source_match and output_match:
        print("✓ All checksums verified successfully!")
        print("  Data integrity confirmed.")
    else:
        print("✗ Checksum verification FAILED!")
        print("  Data may have been modified.")
    print("="*60 + "\n")
    
    return 0 if (source_match and output_match) else 1


if __name__ == "__main__":
    exit(verify_checksums())
