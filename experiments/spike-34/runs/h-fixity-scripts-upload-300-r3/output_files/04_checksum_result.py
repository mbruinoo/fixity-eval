#!/usr/bin/env python3
"""
Verify the standardized TSV file checksums and compare with source.
This script must be run AFTER standardization.
"""

import hashlib
import json
from pathlib import Path
from datetime import datetime
from difflib import unified_diff


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


def compare_checksums(source_checksums, result_checksums):
    """Compare source and result checksums."""
    
    print("\n--- FIXITY VERIFICATION ---\n")
    
    print("Source File:")
    print(f"  Size: {source_checksums['file_size_bytes']:,} bytes")
    print(f"  Lines: {source_checksums['line_count']}")
    print(f"  MD5: {source_checksums['md5']}")
    
    print("\nResult File:")
    print(f"  Size: {result_checksums['file_size_bytes']:,} bytes")
    print(f"  Lines: {result_checksums['line_count']}")
    print(f"  MD5: {result_checksums['md5']}")
    
    print("\n--- COMPARISON ---\n")
    
    # File will be different due to standardization
    if source_checksums['md5'] == result_checksums['md5']:
        print("⚠ WARNING: Source and result are identical!")
        print("  (This may indicate standardization didn't occur)")
    else:
        print("✓ Files differ (expected due to standardization)")
    
    # But line count should be similar (header + data rows)
    source_data_rows = source_checksums['line_count'] - source_checksums['empty_lines']
    result_data_rows = result_checksums['line_count'] - 1  # subtract header
    
    print(f"\n  Source data rows (approx): {source_data_rows}")
    print(f"  Result data rows: {result_data_rows}")
    
    if source_data_rows == result_data_rows:
        print(f"  ✓ Row count preserved")
    else:
        print(f"  ⚠ Row count difference: {result_data_rows - source_data_rows}")
    
    return result_checksums


def main():
    source_file = "met_inventory.tsv"
    result_file = "met_inventory_STANDARDIZED.tsv"
    source_checksums_file = "source_checksums.json"
    
    print("=" * 70)
    print("RESULT FILE INTEGRITY VERIFICATION")
    print("=" * 70)
    
    # Load source checksums
    print(f"\nLoading source checksums from: {source_checksums_file}")
    try:
        with open(source_checksums_file, 'r') as f:
            source_checksums = json.load(f)
        print("✓ Source checksums loaded")
    except FileNotFoundError:
        print(f"✗ Source checksums file not found!")
        print(f"  Run 02_checksum_source.py first")
        return
    
    # Calculate result checksums
    print(f"\nCalculating result file checksums...")
    result_checksums = calculate_checksums(result_file)
    
    if not result_checksums:
        print(f"✗ Failed to calculate result checksums!")
        return
    
    # Compare
    compare_checksums(source_checksums, result_checksums)
    
    # Save result checksums
    result_checksums_file = "result_checksums.json"
    with open(result_checksums_file, 'w') as f:
        json.dump(result_checksums, f, indent=2)
    print(f"\n✓ Result checksums saved to: {result_checksums_file}")
    
    # Create fixity report
    fixity_report = {
        'source': source_checksums,
        'result': result_checksums,
        'transformation': 'TSV standardization',
        'standardization_date': datetime.now().isoformat(),
        'note': 'Files should differ; row count should be preserved'
    }
    
    with open('fixity_verification_report.json', 'w') as f:
        json.dump(fixity_report, f, indent=2)
    print(f"✓ Full fixity report saved to: fixity_verification_report.json")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
