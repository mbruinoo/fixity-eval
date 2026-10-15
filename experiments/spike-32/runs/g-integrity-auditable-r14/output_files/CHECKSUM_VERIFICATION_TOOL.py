#!/usr/bin/env python3
"""
MET Museum Inventory - Checksum Verification Tool
=================================================

This tool verifies the integrity of the standardized TSV file by:
1. Reading each row of the standardized file
2. Recalculating the CRC32 checksum from the original data fields
3. Comparing calculated vs. stored checksums
4. Reporting any mismatches or corruptions

Usage:
    python3 checksum_verification_tool.py met_inventory_standardized.tsv

Author: Data Integrity Service
Date: January 15, 2025
"""

import csv
import binascii
import sys
from pathlib import Path
from typing import List, Tuple, Dict


class ChecksumVerifier:
    """Verifies TSV file data integrity using CRC32 checksums"""
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.results = {
            'total_records': 0,
            'valid_records': 0,
            'invalid_records': 0,
            'mismatches': [],
            'errors': []
        }
    
    def calculate_checksum(self, data_string: str) -> str:
        """
        Calculate CRC32 checksum for a data string
        
        Args:
            data_string: Tab-separated data (date, title, object_num, url)
        
        Returns:
            8-character lowercase hex checksum
        """
        checksum = binascii.crc32(data_string.encode('utf-8')) & 0xffffffff
        return format(checksum, '08x')
    
    def verify_file(self) -> bool:
        """
        Verify all records in the TSV file
        
        Returns:
            True if all checksums match, False otherwise
        """
        if not self.file_path.exists():
            print(f"❌ ERROR: File not found: {self.file_path}")
            return False
        
        print(f"📋 Verifying: {self.file_path.name}")
        print(f"{'='*70}")
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                # Verify header
                expected_headers = {'Object_Date', 'Title', 'Object_Number', 
                                  'Link_Resource', 'Row_Checksum'}
                if set(reader.fieldnames) != expected_headers:
                    print(f"❌ Header mismatch!")
                    print(f"   Expected: {expected_headers}")
                    print(f"   Found: {set(reader.fieldnames)}")
                    return False
                
                print(f"✓ Header valid")
                print()
                
                # Verify each record
                for row_num, row in enumerate(reader, 1):
                    self.results['total_records'] += 1
                    
                    try:
                        # Extract fields
                        date_val = row.get('Object_Date', '')
                        title = row.get('Title', '')
                        obj_num = row.get('Object_Number', '')
                        url = row.get('Link_Resource', '')
                        stored_checksum = row.get('Row_Checksum', '').lower()
                        
                        # Reconstruct original data string
                        data_string = f"{date_val}\t{title}\t{obj_num}\t{url}"
                        
                        # Calculate checksum
                        calculated_checksum = self.calculate_checksum(data_string)
                        
                        # Compare
                        if calculated_checksum == stored_checksum:
                            self.results['valid_records'] += 1
                            print(f"✓ Row {row_num:3d}: {obj_num:<20s} OK", end="")
                            if row_num % 1 == 0:  # Show every row
                                print()
                        else:
                            self.results['invalid_records'] += 1
                            mismatch = {
                                'row': row_num,
                                'object_number': obj_num,
                                'calculated': calculated_checksum,
                                'stored': stored_checksum,
                                'object_date': date_val
                            }
                            self.results['mismatches'].append(mismatch)
                            print(f"❌ Row {row_num:3d}: {obj_num:<20s} MISMATCH!")
                            
                    except Exception as e:
                        self.results['errors'].append({
                            'row': row_num,
                            'error': str(e)
                        })
                        print(f"⚠️  Row {row_num}: Error processing record: {e}")
                
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return False
        
        return self.results['invalid_records'] == 0
    
    def print_summary(self):
        """Print verification summary"""
        print()
        print(f"{'='*70}")
        print("📊 VERIFICATION SUMMARY")
        print(f"{'='*70}")
        
        total = self.results['total_records']
        valid = self.results['valid_records']
        invalid = self.results['invalid_records']
        errors = len(self.results['errors'])
        
        print(f"Total records:      {total}")
        print(f"Valid checksums:    {valid} ({100*valid//total if total else 0}%)")
        print(f"Invalid checksums:  {invalid}")
        print(f"Processing errors:  {errors}")
        print()
        
        if invalid == 0 and errors == 0:
            print("✅ FILE INTEGRITY: VALID")
            print("   All records passed checksum verification.")
        else:
            print("⚠️  FILE INTEGRITY: ISSUES DETECTED")
            
            if self.results['mismatches']:
                print("\n❌ CHECKSUM MISMATCHES:")
                print("-" * 70)
                for mismatch in self.results['mismatches']:
                    print(f"  Row {mismatch['row']}: {mismatch['object_number']}")
                    print(f"    Date: {mismatch['object_date']}")
                    print(f"    Calculated: {mismatch['calculated']}")
                    print(f"    Stored:     {mismatch['stored']}")
                    print()
            
            if self.results['errors']:
                print("\n⚠️  PROCESSING ERRORS:")
                print("-" * 70)
                for error in self.results['errors']:
                    print(f"  Row {error['row']}: {error['error']}")
                print()
        
        print(f"{'='*70}")
    
    def generate_report(self, output_file: str = None):
        """
        Generate a detailed verification report
        
        Args:
            output_file: Optional path to save report
        """
        report = []
        report.append("=" * 80)
        report.append("MET MUSEUM INVENTORY - CHECKSUM VERIFICATION REPORT")
        report.append("=" * 80)
        report.append("")
        report.append(f"File: {self.file_path}")
        report.append(f"Total Records: {self.results['total_records']}")
        report.append(f"Valid Records: {self.results['valid_records']}")
        report.append(f"Invalid Records: {self.results['invalid_records']}")
        report.append("")
        
        if self.results['mismatches']:
            report.append("CHECKSUM MISMATCHES:")
            report.append("-" * 80)
            for mismatch in self.results['mismatches']:
                report.append(f"Row {mismatch['row']}: {mismatch['object_number']}")
                report.append(f"  Object Date:    {mismatch['object_date']}")
                report.append(f"  Calculated:     {mismatch['calculated']}")
                report.append(f"  Stored:         {mismatch['stored']}")
                report.append("")
        
        report_text = "\n".join(report)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            print(f"✓ Report saved to: {output_file}")
        
        return report_text


def main():
    """Main entry point"""
    
    # Check arguments
    if len(sys.argv) < 2:
        print("Usage: python3 checksum_verification_tool.py <tsv_file>")
        print()
        print("Example:")
        print("  python3 checksum_verification_tool.py met_inventory_standardized.tsv")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    # Create verifier
    verifier = ChecksumVerifier(file_path)
    
    # Run verification
    success = verifier.verify_file()
    
    # Print summary
    verifier.print_summary()
    
    # Generate optional report
    report_file = sys.argv[2] if len(sys.argv) > 2 else None
    if report_file:
        verifier.generate_report(report_file)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
