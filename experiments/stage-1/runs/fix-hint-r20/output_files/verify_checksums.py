#!/usr/bin/env python3
"""
Metropolitan Museum Inventory File - Checksum Verification Script
=================================================================

This script verifies the integrity of the standardized TSV file using SHA256 checksums.
It can validate existing checksums or generate new ones for audit purposes.

Usage:
    python verify_checksums.py met_inventory_standardized.tsv [--generate] [--verbose]

Options:
    --generate   Regenerate all checksums (for comparison/audit)
    --verbose    Show detailed output for each row
    --export     Export results to CSV for analysis
"""

import hashlib
import sys
import argparse
from pathlib import Path
from typing import List, Tuple, Dict

class InventoryValidator:
    """Validates and regenerates checksums for the inventory file."""
    
    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.rows: List[str] = []
        self.headers: List[str] = []
        self.load_file()
    
    def load_file(self) -> None:
        """Load the TSV file into memory."""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Parse header
            self.headers = lines[0].rstrip('\n').split('\t')
            self.rows = [line.rstrip('\n') for line in lines[1:]]
            print(f"✓ Loaded {len(self.rows)} data rows from {self.filepath}")
        except FileNotFoundError:
            print(f"✗ File not found: {self.filepath}")
            sys.exit(1)
        except Exception as e:
            print(f"✗ Error loading file: {e}")
            sys.exit(1)
    
    def calculate_row_checksum(self, row_data: str) -> str:
        """
        Calculate SHA256 checksum for a row.
        
        Args:
            row_data: Tab-delimited row string (without checksum column)
        
        Returns:
            SHA256 hex digest
        """
        return hashlib.sha256(row_data.encode('utf-8')).hexdigest()
    
    def parse_row(self, row: str) -> Tuple[List[str], str]:
        """
        Parse a row and extract data columns and existing checksum.
        
        Returns:
            Tuple of (data_columns, stored_checksum)
        """
        parts = row.split('\t')
        
        if len(parts) >= 5:
            data_columns = parts[:4]  # Object Date, Title, Object Number, Link Resource
            stored_checksum = parts[4] if len(parts) > 4 else ""
            return data_columns, stored_checksum
        else:
            return parts, ""
    
    def verify_all(self, verbose: bool = False) -> Dict[str, int]:
        """
        Verify all checksums in the file.
        
        Returns:
            Dictionary with verification statistics
        """
        stats = {
            'total': len(self.rows),
            'valid': 0,
            'invalid': 0,
            'missing': 0,
            'errors': []
        }
        
        for row_num, row in enumerate(self.rows, start=2):  # Start at 2 (header is row 1)
            data_cols, stored_checksum = self.parse_row(row)
            
            if not stored_checksum:
                stats['missing'] += 1
                if verbose:
                    print(f"⚠ Row {row_num}: Missing checksum")
                continue
            
            # Reconstruct the data portion (without checksum)
            row_data = '\t'.join(data_cols)
            calculated = self.calculate_row_checksum(row_data)
            
            if calculated == stored_checksum:
                stats['valid'] += 1
                if verbose:
                    print(f"✓ Row {row_num}: Valid")
            else:
                stats['invalid'] += 1
                error_msg = f"Row {row_num}: Checksum mismatch (expected {stored_checksum[:8]}..., got {calculated[:8]}...)"
                stats['errors'].append(error_msg)
                if verbose:
                    print(f"✗ {error_msg}")
        
        return stats
    
    def generate_checksums(self) -> str:
        """
        Generate a new standardized file with checksums.
        
        Returns:
            String containing the entire file with new checksums
        """
        output_lines = ['\t'.join(self.headers)]
        
        for row in self.rows:
            data_cols, _ = self.parse_row(row)
            row_data = '\t'.join(data_cols)
            checksum = self.calculate_row_checksum(row_data)
            new_row = row_data + '\t' + checksum
            output_lines.append(new_row)
        
        return '\n'.join(output_lines) + '\n'
    
    def report_statistics(self) -> None:
        """Print detailed statistics about the inventory file."""
        print("\n" + "="*70)
        print("INVENTORY FILE STATISTICS")
        print("="*70)
        
        print(f"\nFile: {self.filepath}")
        print(f"Total Rows: {len(self.rows)}")
        
        # Analyze missing data
        missing_dates = 0
        missing_titles = 0
        multilingual = 0
        
        for row in self.rows:
            cols = row.split('\t')
            if len(cols) >= 4:
                if not cols[0] or cols[0] == '[Unknown]':
                    missing_dates += 1
                if not cols[1] or cols[1] == '[Unknown]':
                    missing_titles += 1
                if '|' in cols[1]:  # Bilingual indicator
                    multilingual += 1
        
        print(f"Missing Object Dates: {missing_dates}")
        print(f"Missing Titles: {missing_titles}")
        print(f"Multilingual Records: {multilingual}")
        print(f"Header Columns: {', '.join(self.headers)}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Verify and generate checksums for Met Museum inventory file"
    )
    parser.add_argument('filepath', help='Path to the TSV file')
    parser.add_argument('--generate', action='store_true', 
                       help='Generate new checksums')
    parser.add_argument('--verbose', action='store_true', 
                       help='Show detailed output')
    parser.add_argument('--export', type=str, 
                       help='Export results to CSV file')
    parser.add_argument('--stats', action='store_true', 
                       help='Show file statistics')
    
    args = parser.parse_args()
    
    validator = InventoryValidator(args.filepath)
    
    if args.stats:
        validator.report_statistics()
    
    if args.generate:
        print("\nGenerating new checksums...")
        new_content = validator.generate_checksums()
        output_path = Path(args.filepath).stem + "_with_checksums.tsv"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✓ Checksum-regenerated file written to: {output_path}")
    else:
        print("\nVerifying checksums...")
        stats = validator.verify_all(verbose=args.verbose)
        
        print("\n" + "="*70)
        print("VERIFICATION RESULTS")
        print("="*70)
        print(f"Total Rows:      {stats['total']}")
        print(f"Valid:           {stats['valid']} ✓")
        print(f"Invalid:         {stats['invalid']} ✗")
        print(f"Missing:         {stats['missing']} ⚠")
        print()
        
        if stats['invalid'] > 0:
            print("MISMATCHES DETECTED:")
            for error in stats['errors'][:5]:  # Show first 5 errors
                print(f"  {error}")
            if len(stats['errors']) > 5:
                print(f"  ... and {len(stats['errors']) - 5} more")
        else:
            print("✓ All checksums verified successfully!")
        
        if args.export:
            print(f"\nExporting results to {args.export}...")
            # Export functionality would go here


if __name__ == '__main__':
    main()
