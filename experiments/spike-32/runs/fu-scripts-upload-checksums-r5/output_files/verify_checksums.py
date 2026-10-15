#!/usr/bin/env python3
"""
Checksum Verification Script
Verifies the integrity of the standardized TSV file using SHA256 checksums.
"""

import hashlib
import sys
from pathlib import Path


KNOWN_CHECKSUMS = {
    "/mnt/user-data/outputs/met_inventory_standardized.tsv": 
        "e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf",
}


def calculate_sha256(file_path):
    """Calculate SHA256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def verify_file_integrity(file_path, expected_checksum):
    """Verify that a file matches its expected checksum."""
    if not Path(file_path).exists():
        return False, f"File not found: {file_path}"
    
    actual_checksum = calculate_sha256(file_path)
    
    if actual_checksum == expected_checksum:
        return True, f"✓ VERIFIED: File integrity confirmed"
    else:
        return False, f"✗ MISMATCH: File has been modified or corrupted"


def main():
    print("=" * 80)
    print("TSV CHECKSUM VERIFICATION")
    print("=" * 80)
    print()
    
    all_verified = True
    
    for file_path, expected_checksum in KNOWN_CHECKSUMS.items():
        print(f"File: {file_path}")
        print(f"Expected: {expected_checksum}")
        
        verified, message = verify_file_integrity(file_path, expected_checksum)
        
        if verified:
            actual_checksum = calculate_sha256(file_path)
            print(f"Actual:   {actual_checksum}")
            print(f"Status:   {message}")
            print("Result:   PASS")
        else:
            print(f"Status:   {message}")
            print("Result:   FAIL")
            all_verified = False
        
        print()
    
    print("=" * 80)
    if all_verified:
        print("OVERALL RESULT: ALL FILES VERIFIED ✓")
        print("All files have maintained their integrity.")
        sys.exit(0)
    else:
        print("OVERALL RESULT: VERIFICATION FAILED ✗")
        print("One or more files have been modified or corrupted.")
        sys.exit(1)


if __name__ == "__main__":
    main()
