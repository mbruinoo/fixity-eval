#!/usr/bin/env python3
import subprocess
import sys

# Run the standardization script
print("Running standardization script...\n")
result = subprocess.run([sys.executable, '/mnt/user-data/outputs/standardize_and_checksum.py'], 
                       capture_output=False)

# Verify the output file exists and get its checksums
print("\n\nVERIFYING OUTPUT FILE...")
print("=" * 70)

output_file = '/mnt/user-data/outputs/met_inventory_standardized.tsv'

# Using Python to calculate sha256
import hashlib
def sha256_file(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

checksum = sha256_file(output_file)
print(f"Output file SHA-256: {checksum}")
print(f"Output file path: {output_file}")

# Show file stats
import os
size = os.path.getsize(output_file)
print(f"Output file size: {size} bytes")

# Count lines
with open(output_file, 'r') as f:
    lines = len(f.readlines())
print(f"Output file lines: {lines}")

# Show first few lines
print("\nFIRST 5 LINES OF OUTPUT FILE:")
print("-" * 70)
with open(output_file, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if i < 5:
            print(repr(line))
        else:
            break

print("\nLAST 3 LINES OF OUTPUT FILE:")
print("-" * 70)
with open(output_file, 'r', encoding='utf-8') as f:
    all_lines = f.readlines()
    for line in all_lines[-3:]:
        print(repr(line))

print("\n" + "=" * 70)
