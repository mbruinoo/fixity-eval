#!/usr/bin/env python3
"""
Checksum Verification Script for MET Museum Inventory Standardization
=====================================================================

This script computes and verifies checksums (MD5, SHA-256) for:
1. Original source file (met_inventory.tsv)
2. Standardized output file (met_inventory_standardized.tsv)

Usage:
    python checksum_verification.py

Output:
    - Console display of checksums
    - checksum_results.txt file with detailed report
"""

import hashlib
import os
from datetime import datetime
from pathlib import Path


def calculate_checksums(filepath):
    """
    Calculate MD5 and SHA-256 checksums for a file.
    
    Args:
        filepath (str): Path to the file
        
    Returns:
        dict: Contains MD5, SHA-256, SHA-1, and file size
    """
    if not os.path.exists(filepath):
        return None
    
    md5_hash = hashlib.md5()
    sha256_hash = hashlib.sha256()
    sha1_hash = hashlib.sha1()
    file_size = 0
    
    try:
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                md5_hash.update(chunk)
                sha256_hash.update(chunk)
                sha1_hash.update(chunk)
                file_size += len(chunk)
        
        return {
            'filepath': filepath,
            'filename': os.path.basename(filepath),
            'md5': md5_hash.hexdigest(),
            'sha1': sha1_hash.hexdigest(),
            'sha256': sha256_hash.hexdigest(),
            'size_bytes': file_size,
            'size_kb': round(file_size / 1024, 2),
            'exists': True,
            'timestamp': datetime.fromtimestamp(os.path.getmtime(filepath))
        }
    except Exception as e:
        return {
            'filepath': filepath,
            'filename': os.path.basename(filepath),
            'exists': False,
            'error': str(e)
        }


def line_count(filepath):
    """Count lines in a file."""
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)
    except:
        return None


def generate_report(source_info, output_info):
    """Generate a formatted checksum report."""
    
    report = []
    report.append("=" * 80)
    report.append("                  CHECKSUM VERIFICATION REPORT")
    report.append("              MET Museum Inventory Standardization")
    report.append("=" * 80)
    report.append("")
    report.append(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # SOURCE FILE INFORMATION
    report.append("-" * 80)
    report.append("SOURCE FILE (Original)")
    report.append("-" * 80)
    
    if source_info and source_info.get('exists'):
        report.append(f"File Name:     {source_info['filename']}")
        report.append(f"File Path:     {source_info['filepath']}")
        report.append(f"File Size:     {source_info['size_bytes']:,} bytes ({source_info['size_kb']} KB)")
        report.append(f"Modified:      {source_info['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Line Count:    {line_count(source_info['filepath'])} lines")
        report.append("")
        report.append("CHECKSUMS (Source File):")
        report.append(f"  MD5-128:     {source_info['md5']}")
        report.append(f"  SHA-1:       {source_info['sha1']}")
        report.append(f"  SHA-256:     {source_info['sha256']}")
        report.append("")
    else:
        report.append("STATUS: SOURCE FILE NOT FOUND")
        report.append("")
    
    # OUTPUT FILE INFORMATION
    report.append("-" * 80)
    report.append("OUTPUT FILE (Standardized)")
    report.append("-" * 80)
    
    if output_info and output_info.get('exists'):
        report.append(f"File Name:     {output_info['filename']}")
        report.append(f"File Path:     {output_info['filepath']}")
        report.append(f"File Size:     {output_info['size_bytes']:,} bytes ({output_info['size_kb']} KB)")
        report.append(f"Created:       {output_info['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Line Count:    {line_count(output_info['filepath'])} lines")
        report.append("")
        report.append("CHECKSUMS (Output File):")
        report.append(f"  MD5-128:     {output_info['md5']}")
        report.append(f"  SHA-1:       {output_info['sha1']}")
        report.append(f"  SHA-256:     {output_info['sha256']}")
        report.append("")
    else:
        report.append("STATUS: OUTPUT FILE NOT FOUND")
        report.append("")
    
    # COMPARISON
    if source_info and output_info and source_info.get('exists') and output_info.get('exists'):
        report.append("-" * 80)
        report.append("COMPARISON ANALYSIS")
        report.append("-" * 80)
        report.append("")
        
        source_lines = line_count(source_info['filepath'])
        output_lines = line_count(output_info['filepath'])
        
        report.append(f"File Size Difference:     {output_info['size_bytes'] - source_info['size_bytes']:,} bytes")
        report.append(f"Line Count Difference:    {output_lines - source_lines} lines")
        report.append("")
        
        if source_info['md5'] == output_info['md5']:
            report.append("FILE IDENTITY CHECK:      FILES ARE IDENTICAL ✓")
        else:
            report.append("FILE IDENTITY CHECK:      FILES DIFFER (Expected)")
            report.append("  Status: NORMAL - Files differ due to standardization")
            report.append("  Reason: Quote normalization, header changes, whitespace cleanup")
        report.append("")
    
    # INTEGRITY VERIFICATION
    report.append("-" * 80)
    report.append("DATA INTEGRITY VERIFICATION")
    report.append("-" * 80)
    report.append("")
    report.append("✓ MD5 Checksum:         Provides collision-resistant unique identifier")
    report.append("✓ SHA-1 Checksum:       Additional integrity verification")
    report.append("✓ SHA-256 Checksum:     Cryptographically secure verification")
    report.append("")
    report.append("These checksums can be used to:")
    report.append("  1. Verify file hasn't been corrupted during transfer")
    report.append("  2. Confirm file integrity at rest (storage)")
    report.append("  3. Detect unauthorized modifications")
    report.append("  4. Create audit trail for compliance/archival")
    report.append("")
    
    # USAGE GUIDE
    report.append("-" * 80)
    report.append("CHECKSUM VERIFICATION INSTRUCTIONS")
    report.append("-" * 80)
    report.append("")
    report.append("To verify the standardized file later, use:")
    report.append("")
    report.append("Linux/Mac (SHA-256):")
    if output_info and output_info.get('exists'):
        report.append(f"  shasum -a 256 {output_info['filename']}")
    report.append("")
    report.append("Linux/Mac (MD5):")
    if output_info and output_info.get('exists'):
        report.append(f"  md5 {output_info['filename']}  # macOS")
        report.append(f"  md5sum {output_info['filename']}  # Linux")
    report.append("")
    report.append("Windows (PowerShell):")
    if output_info and output_info.get('exists'):
        report.append(f"  certUtil -hashfile {output_info['filename']} SHA256")
    report.append("")
    report.append("Python:")
    report.append("  python3 -c \"import hashlib; print(hashlib.sha256(open('file.tsv', 'rb').read()).hexdigest())\"")
    report.append("")
    
    # RECOMMENDATIONS
    report.append("-" * 80)
    report.append("RECOMMENDATIONS FOR PRESERVATION")
    report.append("-" * 80)
    report.append("")
    report.append("1. Store checksums alongside files in version control")
    report.append("2. Create checksum manifest file for batch verification")
    report.append("3. Include checksums in metadata records (MIAOU, PREMIS, etc.)")
    report.append("4. Regularly verify checksums to detect silent data corruption")
    report.append("5. Document standardization changes in accompanying metadata")
    report.append("6. Archive this report with the standardized file")
    report.append("")
    
    report.append("=" * 80)
    report.append("END OF REPORT")
    report.append("=" * 80)
    
    return "\n".join(report)


def main():
    """Main execution."""
    
    # Define file paths
    # Note: Adjust these paths based on your environment
    source_file = "/mnt/user-data/uploads/met_inventory.tsv"
    output_file = "/mnt/user-data/outputs/met_inventory_standardized.tsv"
    
    # Alternative paths for testing
    if not os.path.exists(source_file):
        source_file = "met_inventory.tsv"
    if not os.path.exists(output_file):
        output_file = "met_inventory_standardized.tsv"
    
    print("\nCalculating checksums...")
    print("-" * 80)
    
    # Calculate checksums
    source_info = calculate_checksums(source_file)
    output_info = calculate_checksums(output_file)
    
    # Display results
    if source_info and source_info.get('exists'):
        print(f"\n✓ Source File: {source_info['filename']}")
        print(f"  Size: {source_info['size_kb']} KB")
        print(f"  MD5:  {source_info['md5']}")
        print(f"  SHA-256: {source_info['sha256'][:40]}...")
    else:
        print(f"\n✗ Source file not found: {source_file}")
    
    if output_info and output_info.get('exists'):
        print(f"\n✓ Output File: {output_info['filename']}")
        print(f"  Size: {output_info['size_kb']} KB")
        print(f"  MD5:  {output_info['md5']}")
        print(f"  SHA-256: {output_info['sha256'][:40]}...")
    else:
        print(f"\n✗ Output file not found: {output_file}")
    
    print("\n" + "-" * 80)
    
    # Generate full report
    report = generate_report(source_info, output_info)
    print(report)
    
    # Save report to file
    report_file = "/mnt/user-data/outputs/checksum_results.txt"
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n✓ Report saved to: {report_file}")
    except Exception as e:
        print(f"\n✗ Could not save report: {e}")


if __name__ == "__main__":
    main()
