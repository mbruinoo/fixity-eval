#!/usr/bin/env python3
"""
Generate checksums for source TSV file to verify fixity.
This script must be run BEFORE standardization.
"""

import hashlib
import json
from pathlib import Path
from datetime import datetime

def calculate_checksums(file_path):
    """Calculate MD5, SHA256, and file statistics for integrity verification."""
    
    if not Path(file_path).exists():
        print(f"ERROR: File not found: {file_path}")
        return None
    
    checksums = {}
    
    try:
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        # Calculate hashes
        checksums['md5'] = hashlib.md5(file_content).hexdigest()
        checksums['sha256'] = hashlib.sha256(file_content).hexdigest()
        checksums['sha512'] = hashlib.sha512(file_content).hexdigest()
        
        # File statistics
        checksums['file_size_bytes'] = len(file_content)
        checksums['timestamp'] = datetime.now().isoformat()
        
        # Count lines for reference
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            checksums['line_count'] = len(lines)
            checksums['empty_lines'] = sum(1 for line in lines if line.strip() == '')
        
        return checksums
        
    except Exception as e:
        print(f"ERROR calculating checksums: {e}")
        return None


def main():
    source_file = "met_inventory.tsv"
    
    print("=" * 70)
    print("SOURCE FILE INTEGRITY VERIFICATION")
    print("=" * 70)
    print(f"\nFile: {source_file}")
    
    checksums = calculate_checksums(source_file)
    
    if checksums:
        print("\n--- FILE STATISTICS ---")
        print(f"File size: {checksums['file_size_bytes']:,} bytes")
        print(f"Line count: {checksums['line_count']}")
        print(f"Empty lines: {checksums['empty_lines']}")
        print(f"Timestamp: {checksums['timestamp']}")
        
        print("\n--- CHECKSUMS (for fixity verification) ---")
        print(f"MD5:    {checksums['md5']}")
        print(f"SHA256: {checksums['sha256']}")
        print(f"SHA512: {checksums['sha512']}")
        
        # Save to JSON for comparison
        with open('source_checksums.json', 'w') as f:
            json.dump(checksums, f, indent=2)
        print(f"\n✓ Checksums saved to: source_checksums.json")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
