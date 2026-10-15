#!/usr/bin/env python3
"""
Calculate SHA-256 checksum of the source TSV file.
"""
import hashlib

def calculate_checksum(filepath):
    """Calculate SHA-256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

if __name__ == "__main__":
    source_file = "/mnt/user-data/uploads/met_inventory.tsv"
    checksum = calculate_checksum(source_file)
    print(f"Source file: {source_file}")
    print(f"SHA-256 Checksum: {checksum}")
    
    # Save checksum to file for reference
    with open("/mnt/user-data/outputs/source_checksum.txt", "w") as f:
        f.write(f"File: met_inventory.tsv\n")
        f.write(f"SHA-256: {checksum}\n")
