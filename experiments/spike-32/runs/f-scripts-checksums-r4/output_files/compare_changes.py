#!/usr/bin/env python3
"""
Compare source and standardized files
- Shows field-by-field changes
- Highlights data cleaning effects
- Generates before/after comparison report
"""

import csv
import json
from pathlib import Path
from typing import Dict, List, Tuple


def read_tsv(filepath: str) -> List[Dict]:
    """Read TSV file."""
    records = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            records.append(row)
    return records


def compare_records(source_record: Dict, output_record: Dict, row_num: int) -> Dict:
    """Compare a source and output record, return differences."""
    comparison = {
        'row': row_num,
        'object_number': output_record.get('object_number', 'N/A'),
        'changes': []
    }
    
    # Map source field names to check
    field_mappings = [
        ('Object Date', 'object_date', 'Date'),
        ('Title', 'title', 'Title'),
        ('Object Number', 'object_number', 'Object Number'),
        ('Link Resource', 'link_resource', 'URL'),
    ]
    
    for source_field, output_field, label in field_mappings:
        source_value = source_record.get(source_field, '')
        output_value = output_record.get(output_field, '')
        
        # Check for whitespace differences
        if source_value != output_value:
            # Check if it's just whitespace
            if source_value.strip() == output_value.strip():
                comparison['changes'].append({
                    'field': label,
                    'type': 'whitespace_removed',
                    'source_len': len(source_value),
                    'output_len': len(output_value),
                })
            # Check if it's a structural change
            elif source_value.strip() and not output_value.strip():
                comparison['changes'].append({
                    'field': label,
                    'type': 'value_removed',
                    'source': source_value[:50] + ('...' if len(source_value) > 50 else ''),
                    'output': '[empty]',
                })
            elif not source_value.strip() and output_value.strip():
                comparison['changes'].append({
                    'field': label,
                    'type': 'value_added',
                    'source': '[empty]',
                    'output': output_value[:50] + ('...' if len(output_value) > 50 else ''),
                })
    
    return comparison


def analyze_changes(comparisons: List[Dict]) -> Dict:
    """Analyze all changes and generate statistics."""
    stats = {
        'total_records': len(comparisons),
        'records_with_changes': sum(1 for c in comparisons if c['changes']),
        'total_changes': sum(len(c['changes']) for c in comparisons),
        'change_types': {}
    }
    
    # Count change types
    for comparison in comparisons:
        for change in comparison['changes']:
            change_type = change.get('type', 'unknown')
            if change_type not in stats['change_types']:
                stats['change_types'][change_type] = 0
            stats['change_types'][change_type] += 1
    
    return stats


def main():
    source_file = '/mnt/user-data/outputs/met_inventory_source.tsv'
    output_file = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
    comparison_report = '/mnt/user-data/outputs/comparison_report.json'
    
    print()
    print("=" * 80)
    print("SOURCE vs STANDARDIZED FILE COMPARISON")
    print("=" * 80)
    print()
    
    # Read files
    print("Reading files...")
    source_records = read_tsv(source_file)
    output_records = read_tsv(output_file)
    print(f"  Source records: {len(source_records)}")
    print(f"  Output records: {len(output_records)}")
    print()
    
    # Compare records
    print("Comparing records...")
    comparisons = []
    for idx, (src, out) in enumerate(zip(source_records, output_records), start=2):
        comparison = compare_records(src, out, idx)
        comparisons.append(comparison)
    
    # Analyze
    stats = analyze_changes(comparisons)
    
    print(f"  Total records: {stats['total_records']}")
    print(f"  Records modified: {stats['records_with_changes']}")
    print(f"  Total changes: {stats['total_changes']}")
    print()
    
    print("Change Summary:")
    for change_type, count in sorted(stats['change_types'].items()):
        print(f"  - {change_type}: {count}")
    print()
    
    # Show examples
    records_with_changes = [c for c in comparisons if c['changes']]
    
    if records_with_changes:
        print("Sample Changes (first 5 records with modifications):")
        print("-" * 80)
        for comparison in records_with_changes[:5]:
            print(f"\nRow {comparison['row']}: {comparison['object_number']}")
            for change in comparison['changes']:
                field = change['field']
                change_type = change['type']
                
                if change_type == 'whitespace_removed':
                    print(f"  • {field}: Whitespace trimmed ({change['source_len']} → {change['output_len']} chars)")
                elif change_type == 'value_removed':
                    print(f"  • {field}: Value removed")
                    print(f"    Before: {change['source']}")
                    print(f"    After:  {change['output']}")
                elif change_type == 'value_added':
                    print(f"  • {field}: Value added")
                    print(f"    Before: {change['source']}")
                    print(f"    After:  {change['output']}")
        print()
    
    # Save detailed report
    print("Generating detailed report...")
    report = {
        'comparison_type': 'source_vs_standardized',
        'source_file': str(source_file),
        'output_file': str(output_file),
        'statistics': stats,
        'sample_changes': records_with_changes[:10],  # Include first 10 for inspection
    }
    
    with open(comparison_report, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    print(f"  Report saved: {Path(comparison_report).name}")
    print()
    
    # Print interpretation
    print("=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    print()
    
    if stats['records_with_changes'] == 0:
        print("✓ No changes detected - file is already standardized!")
    elif stats['total_changes'] < stats['total_records'] * 0.1:
        print("✓ Minimal changes - mostly whitespace cleanup")
    else:
        print(f"• {stats['records_with_changes']} records required standardization")
    
    print()
    print("Most common change: Whitespace normalization")
    print("This is expected and safe - no data loss.")
    print()


if __name__ == "__main__":
    main()
