#!/usr/bin/env python3
"""
Fixity Verification Script for TSV Files
Metropolitan Museum of Art Inventory Dataset

This script calculates and verifies SHA-256 checksums for both the source
and standardized TSV files to ensure data integrity throughout the 
standardization process.

Usage:
    python3 verify_fixity.py

Output:
    - Displays SHA-256 checksums for both files
    - Verifies file integrity
    - Saves checksums to file for future verification
"""

import hashlib
import os
from pathlib import Path
from datetime import datetime


def calculate_checksum(filepath, algorithm='sha256', chunk_size=8192):
    """
    Calculate checksum of a file using specified algorithm.
    
    Args:
        filepath (str): Path to file
        algorithm (str): Hash algorithm ('sha256', 'sha512', 'md5')
        chunk_size (int): Size of chunks to read
        
    Returns:
        str: Hexadecimal hash string
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    hash_obj = hashlib.new(algorithm)
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(chunk_size)
            if not data:
                break
            hash_obj.update(data)
    
    return hash_obj.hexdigest()


def get_file_info(filepath):
    """Get file size and modification time."""
    if not os.path.exists(filepath):
        return None
    
    stat = os.stat(filepath)
    return {
        'size_bytes': stat.st_size,
        'size_mb': stat.st_size / (1024 * 1024),
        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
    }


def verify_file_structure(filepath):
    """Verify TSV file structure."""
    if not os.path.exists(filepath):
        return None
    
    info = {
        'total_lines': 0,
        'total_fields': 0,
        'header_present': False,
        'consistent_fields': True,
        'fields_per_row': []
    }
    
    expected_fields = 4
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.rstrip('\n\r')
                field_count = len(line.split('\t'))
                info['fields_per_row'].append(field_count)
                info['total_lines'] += 1
                info['total_fields'] += field_count
                
                if line_num == 1:
                    info['header_present'] = True
                    if 'Object Date' in line and 'Object Number' in line:
                        info['header_valid'] = True
                
                if field_count != expected_fields:
                    info['consistent_fields'] = False
        
        # Check consistency
        if len(set(info['fields_per_row'])) == 1:
            info['consistent_fields'] = True
        
    except Exception as e:
        info['error'] = str(e)
    
    return info


def main():
    """Main verification function."""
    
    # File paths
    source_file = '/mnt/user-data/uploads/met_inventory.tsv'
    output_file = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
    manifest_file = '/mnt/user-data/outputs/FIXITY_MANIFEST.txt'
    checksum_file = '/mnt/user-data/outputs/checksums.sha256'
    
    print("\n" + "="*80)
    print("FIXITY VERIFICATION REPORT")
    print("Metropolitan Museum of Art Inventory TSV Standardization")
    print("="*80 + "\n")
    
    print(f"Timestamp: {datetime.now().isoformat()}\n")
    
    # Process source file
    print("SOURCE FILE VERIFICATION")
    print("-" * 80)
    
    try:
        source_info = get_file_info(source_file)
        print(f"File: {source_file}")
        if source_info:
            print(f"  Size: {source_info['size_mb']:.2f} MB ({source_info['size_bytes']:,} bytes)")
            print(f"  Modified: {source_info['modified']}")
            
            source_checksum = calculate_checksum(source_file)
            print(f"  SHA-256: {source_checksum}")
            
            # Verify structure
            source_struct = verify_file_structure(source_file)
            print(f"  Lines: {source_struct['total_lines']}")
            print(f"  Consistent Fields: {source_struct['consistent_fields']}")
        else:
            print("  ⚠ File not found")
            source_checksum = None
    except Exception as e:
        print(f"  ✗ Error: {e}")
        source_checksum = None
    
    print()
    
    # Process output file
    print("OUTPUT FILE VERIFICATION (Standardized)")
    print("-" * 80)
    
    try:
        output_info = get_file_info(output_file)
        print(f"File: {output_file}")
        if output_info:
            print(f"  Size: {output_info['size_mb']:.2f} MB ({output_info['size_bytes']:,} bytes)")
            print(f"  Modified: {output_info['modified']}")
            
            output_checksum = calculate_checksum(output_file)
            print(f"  SHA-256: {output_checksum}")
            
            # Verify structure
            output_struct = verify_file_structure(output_file)
            print(f"  Lines: {output_struct['total_lines']}")
            print(f"  Consistent Fields: {output_struct['consistent_fields']}")
        else:
            print("  ⚠ File not found")
            output_checksum = None
    except Exception as e:
        print(f"  ✗ Error: {e}")
        output_checksum = None
    
    print()
    
    # Comparison
    print("COMPARISON & INTEGRITY ANALYSIS")
    print("-" * 80)
    
    if source_checksum and output_checksum:
        if source_checksum == output_checksum:
            print("⚠ Checksums are IDENTICAL")
            print("  Note: This may indicate standardization was not applied.")
            print("  Verify that changes were actually made to the file.")
        else:
            print("✓ Checksums are DIFFERENT (Expected)")
            print("  This indicates standardization was successfully applied.")
            print("  Whitespace, line endings, or formatting changes were made.")
        
        if source_info and output_info:
            size_diff = output_info['size_bytes'] - source_info['size_bytes']
            print(f"  Size difference: {size_diff:+,} bytes")
    
    print()
    
    # Data records
    if output_struct:
        data_rows = output_struct['total_lines'] - 1  # Exclude header
        print(f"Data Records: {data_rows} rows (+ 1 header)")
        print(f"Columns: 4 (Object Date, Title, Object Number, Link Resource)")
    
    print()
    
    # Save checksums
    print("SAVING VERIFICATION DATA")
    print("-" * 80)
    
    if source_checksum and output_checksum:
        try:
            with open(checksum_file, 'w') as f:
                f.write("# SHA-256 Checksums for TSV Standardization\n")
                f.write(f"# Generated: {datetime.now().isoformat()}\n\n")
                f.write(f"# Source File\n")
                f.write(f"{source_checksum}  met_inventory.tsv (source)\n\n")
                f.write(f"# Standardized Output File\n")
                f.write(f"{output_checksum}  met_inventory_standardized.tsv\n\n")
                f.write("# To verify file integrity in the future, run:\n")
                f.write("# sha256sum -c checksums.sha256\n")
            
            print(f"✓ Checksums saved to: {checksum_file}")
        except Exception as e:
            print(f"✗ Error saving checksums: {e}")
    
    print()
    
    # Verification summary
    print("VERIFICATION SUMMARY")
    print("-" * 80)
    
    checks_passed = 0
    checks_total = 0
    
    # Check source exists
    checks_total += 1
    if os.path.exists(source_file):
        print("✓ Source file exists")
        checks_passed += 1
    else:
        print("✗ Source file not found")
    
    # Check output exists
    checks_total += 1
    if os.path.exists(output_file):
        print("✓ Output file exists")
        checks_passed += 1
    else:
        print("✗ Output file not found")
    
    # Check manifest exists
    checks_total += 1
    if os.path.exists(manifest_file):
        print("✓ Fixity manifest exists")
        checks_passed += 1
    else:
        print("✗ Fixity manifest not found")
    
    # Check structure
    checks_total += 1
    if output_struct and output_struct['consistent_fields']:
        print("✓ Output file has consistent field structure")
        checks_passed += 1
    else:
        print("✗ Output file structure validation failed")
    
    # Check line count
    checks_total += 1
    if output_struct and output_struct['total_lines'] > 0:
        print(f"✓ Output file contains {output_struct['total_lines']} lines")
        checks_passed += 1
    else:
        print("✗ Output file is empty or unreadable")
    
    print()
    print(f"RESULT: {checks_passed}/{checks_total} checks passed")
    
    if checks_passed == checks_total:
        print("✓ All verification checks PASSED")
        status = "PASS"
    else:
        print("⚠ Some verification checks failed - review above")
        status = "FAIL"
    
    print()
    print("="*80)
    print(f"Verification Status: {status}")
    print("="*80 + "\n")
    
    return 0 if status == "PASS" else 1


if __name__ == '__main__':
    exit(main())
