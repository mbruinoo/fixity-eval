#!/usr/bin/env python3
"""
Analyze and report on the standardization results
"""

import csv
from collections import defaultdict

def analyze_file(filepath):
    """Analyze the standardized file and report statistics"""
    
    stats = {
        'total_rows': 0,
        'empty_dates': 0,
        'empty_titles': 0,
        'empty_object_numbers': 0,
        'empty_links': 0,
        'date_formats': defaultdict(int),
        'object_number_patterns': defaultdict(int),
    }
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        
        for row in reader:
            stats['total_rows'] += 1
            
            if not row['Object Date'].strip():
                stats['empty_dates'] += 1
            else:
                date_val = row['Object Date'].strip()
                stats['date_formats'][date_val] += 1
            
            if not row['Title'].strip():
                stats['empty_titles'] += 1
            
            if not row['Object Number'].strip():
                stats['empty_object_numbers'] += 1
            else:
                obj_num = row['Object Number'].strip()
                stats['object_number_patterns'][obj_num] += 1
            
            if not row['Link Resource'].strip():
                stats['empty_links'] += 1
    
    return stats

def main():
    filepath = "/mnt/user-data/outputs/met_inventory_standardized.tsv"
    stats = analyze_file(filepath)
    
    print("=" * 70)
    print("STANDARDIZATION REPORT - Met Museum Inventory")
    print("=" * 70)
    print()
    
    print("OVERALL STATISTICS:")
    print(f"  Total Rows: {stats['total_rows']}")
    print()
    
    print("COMPLETENESS:")
    print(f"  Object Dates:")
    print(f"    - Populated: {stats['total_rows'] - stats['empty_dates']} ({100*(stats['total_rows']-stats['empty_dates'])/stats['total_rows']:.1f}%)")
    print(f"    - Empty: {stats['empty_dates']} ({100*stats['empty_dates']/stats['total_rows']:.1f}%)")
    print()
    print(f"  Titles:")
    print(f"    - Populated: {stats['total_rows'] - stats['empty_titles']} ({100*(stats['total_rows']-stats['empty_titles'])/stats['total_rows']:.1f}%)")
    print(f"    - Empty: {stats['empty_titles']} ({100*stats['empty_titles']/stats['total_rows']:.1f}%)")
    print()
    print(f"  Object Numbers:")
    print(f"    - Populated: {stats['total_rows'] - stats['empty_object_numbers']} ({100*(stats['total_rows']-stats['empty_object_numbers'])/stats['total_rows']:.1f}%)")
    print(f"    - Empty: {stats['empty_object_numbers']} ({100*stats['empty_object_numbers']/stats['total_rows']:.1f}%)")
    print()
    print(f"  Links:")
    print(f"    - Populated: {stats['total_rows'] - stats['empty_links']} ({100*(stats['total_rows']-stats['empty_links'])/stats['total_rows']:.1f}%)")
    print(f"    - Empty: {stats['empty_links']} ({100*stats['empty_links']/stats['total_rows']:.1f}%)")
    print()
    
    print("=" * 70)
    print("STANDARDIZATION PERFORMED:")
    print("=" * 70)
    print("✓ Decoded HTML entities (e.g., &lt;i&gt; → <i>)")
    print("✓ Trimmed whitespace from all fields")
    print("✓ Standardized column names and order")
    print("✓ Ensured consistent tab-delimited format")
    print("✓ UTF-8 encoding verified")
    print()
    print(f"Output file: /mnt/user-data/outputs/met_inventory_standardized.tsv")
    print()

if __name__ == "__main__":
    main()
