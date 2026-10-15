#!/usr/bin/env python3
"""
TSV Validation and Analysis Tool
Analyzes and validates both source and standardized TSV files.
"""

import csv
import json
import sys
from pathlib import Path
from collections import defaultdict


class TSVValidator:
    """Validates and analyzes TSV files."""
    
    def __init__(self, filepath):
        self.filepath = filepath
        self.rows = []
        self.header = []
        self.stats = {
            'file_path': str(filepath),
            'file_size': Path(filepath).stat().st_size,
            'row_count': 0,
            'column_count': 0,
            'empty_fields': defaultdict(int),
            'column_consistency': True,
            'encoding': 'utf-8',
            'issues': []
        }
        
    def load(self):
        """Load and parse the TSV file."""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter='\t')
                for row_num, row in enumerate(reader):
                    if row_num == 0:
                        self.header = row
                        self.stats['column_count'] = len(row)
                    else:
                        self.rows.append(row)
            
            self.stats['row_count'] = len(self.rows)
            return True
        except Exception as e:
            self.stats['issues'].append(f"Load error: {str(e)}")
            return False
    
    def check_column_consistency(self):
        """Check if all rows have consistent column count."""
        if not self.rows:
            return True
        
        expected_cols = len(self.header)
        inconsistent_rows = []
        
        for row_num, row in enumerate(self.rows, 2):  # Start at 2 (after header)
            if len(row) != expected_cols:
                inconsistent_rows.append({
                    'row': row_num,
                    'expected': expected_cols,
                    'actual': len(row),
                    'data': row[:3]  # First 3 columns for reference
                })
        
        if inconsistent_rows:
            self.stats['column_consistency'] = False
            self.stats['issues'].append(
                f"Column inconsistency in {len(inconsistent_rows)} rows"
            )
            return False
        
        return True
    
    def check_empty_fields(self):
        """Count empty fields per column."""
        for col_idx in range(len(self.header)):
            empty_count = 0
            for row in self.rows:
                if col_idx >= len(row) or not row[col_idx].strip():
                    empty_count += 1
            
            self.stats['empty_fields'][self.header[col_idx]] = empty_count
    
    def check_special_characters(self):
        """Check for unusual characters."""
        special_chars_found = set()
        for row in self.rows:
            for field in row:
                for char in field:
                    if ord(char) > 127:  # Non-ASCII
                        special_chars_found.add(char)
        
        if special_chars_found:
            self.stats['has_unicode'] = True
            self.stats['unicode_sample'] = list(special_chars_found)[:5]
        
        return True
    
    def check_sorting(self):
        """Check if Object Number column (index 2) is sorted."""
        if len(self.rows) < 2:
            return True
        
        col_idx = 2  # Object Number column
        prev_value = ""
        
        for row_num, row in enumerate(self.rows, 2):
            if col_idx >= len(row):
                continue
            current_value = row[col_idx]
            if current_value < prev_value:
                self.stats['issues'].append(
                    f"Not sorted: row {row_num} value '{current_value}' < '{prev_value}'"
                )
                return False
            prev_value = current_value
        
        self.stats['is_sorted'] = True
        return True
    
    def analyze(self):
        """Run all validation checks."""
        if not self.load():
            return False
        
        self.check_column_consistency()
        self.check_empty_fields()
        self.check_special_characters()
        self.check_sorting()
        
        return True
    
    def get_report(self):
        """Generate a detailed report."""
        return self.stats


def compare_files(source_path, output_path):
    """Compare source and standardized files."""
    source_validator = TSVValidator(source_path)
    output_validator = TSVValidator(output_path)
    
    print("=" * 70)
    print("TSV FILE VALIDATION AND COMPARISON")
    print("=" * 70)
    
    # Validate source
    print("\n[1] VALIDATING SOURCE FILE")
    print("-" * 70)
    print(f"File: {source_path}")
    
    if not source_validator.analyze():
        print("✗ Failed to load source file")
        return False
    
    source_stats = source_validator.get_report()
    print(f"✓ Successfully loaded")
    print(f"  Rows: {source_stats['row_count']}")
    print(f"  Columns: {source_stats['column_count']}")
    print(f"  Size: {source_stats['file_size']} bytes")
    print(f"  Column Consistency: {'✓' if source_stats['column_consistency'] else '✗'}")
    
    if source_stats.get('is_sorted'):
        print(f"  Sorted by Object Number: ✓")
    
    if source_stats['issues']:
        print(f"  Issues found ({len(source_stats['issues'])}):")
        for issue in source_stats['issues']:
            print(f"    - {issue}")
    
    # Validate output
    print("\n[2] VALIDATING OUTPUT FILE")
    print("-" * 70)
    print(f"File: {output_path}")
    
    if not output_validator.analyze():
        print("✗ Failed to load output file")
        return False
    
    output_stats = output_validator.get_report()
    print(f"✓ Successfully loaded")
    print(f"  Rows: {output_stats['row_count']}")
    print(f"  Columns: {output_stats['column_count']}")
    print(f"  Size: {output_stats['file_size']} bytes")
    print(f"  Column Consistency: {'✓' if output_stats['column_consistency'] else '✗'}")
    
    if output_stats.get('is_sorted'):
        print(f"  Sorted by Object Number: ✓")
    
    if output_stats['issues']:
        print(f"  Issues found ({len(output_stats['issues'])}):")
        for issue in output_stats['issues']:
            print(f"    - {issue}")
    else:
        print(f"  Issues: None ✓")
    
    # Comparison
    print("\n[3] COMPARISON")
    print("-" * 70)
    
    comparison = {
        'row_count_preserved': source_stats['row_count'] == output_stats['row_count'],
        'column_count_preserved': source_stats['column_count'] == output_stats['column_count'],
        'source_stats': source_stats,
        'output_stats': output_stats
    }
    
    if comparison['row_count_preserved']:
        print(f"✓ Row count preserved: {output_stats['row_count']}")
    else:
        print(f"✗ Row count changed: {source_stats['row_count']} → {output_stats['row_count']}")
    
    if comparison['column_count_preserved']:
        print(f"✓ Column count preserved: {output_stats['column_count']}")
    else:
        print(f"✗ Column count changed: {source_stats['column_count']} → {output_stats['column_count']}")
    
    if output_stats['column_consistency']:
        print(f"✓ All rows have consistent column count")
    
    # Empty fields analysis
    print("\n[4] EMPTY FIELDS ANALYSIS")
    print("-" * 70)
    print("Source file empty fields by column:")
    for col_name, count in source_stats['empty_fields'].items():
        pct = (count / source_stats['row_count'] * 100) if source_stats['row_count'] > 0 else 0
        print(f"  {col_name}: {count} ({pct:.1f}%)")
    
    print("\nOutput file empty fields by column:")
    for col_name, count in output_stats['empty_fields'].items():
        pct = (count / output_stats['row_count'] * 100) if output_stats['row_count'] > 0 else 0
        print(f"  {col_name}: {count} ({pct:.1f}%)")
    
    # Unicode content
    if source_stats.get('has_unicode'):
        print("\n[5] UNICODE CONTENT")
        print("-" * 70)
        print(f"✓ File contains Unicode characters (sample): {source_stats.get('unicode_sample', [])}")
    
    # Summary
    print("\n[6] SUMMARY")
    print("-" * 70)
    
    all_good = (
        comparison['row_count_preserved'] and
        comparison['column_count_preserved'] and
        output_stats['column_consistency'] and
        len(output_stats['issues']) == 0
    )
    
    if all_good:
        print("✓ STANDARDIZATION SUCCESSFUL")
        print("  - All data preserved")
        print("  - Column consistency verified")
        print("  - No outstanding issues")
        if output_stats.get('is_sorted'):
            print("  - Data properly sorted")
    else:
        print("✗ ISSUES DETECTED")
        print("  Please review the details above")
    
    print("\n" + "=" * 70)
    
    return comparison


def main():
    """Main function."""
    if len(sys.argv) < 3:
        print("Usage: python validate_tsv.py <source_file> <output_file>")
        print("\nExample:")
        print("  python validate_tsv.py met_inventory.tsv met_inventory_standardized.tsv")
        sys.exit(1)
    
    source_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # Verify files exist
    if not Path(source_file).exists():
        print(f"Error: Source file not found: {source_file}")
        sys.exit(1)
    
    if not Path(output_file).exists():
        print(f"Error: Output file not found: {output_file}")
        sys.exit(1)
    
    compare_files(source_file, output_file)


if __name__ == '__main__':
    main()
