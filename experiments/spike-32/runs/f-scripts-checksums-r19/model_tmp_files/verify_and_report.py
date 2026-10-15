#!/usr/bin/env python3
"""
Verify standardization and create detailed report
"""
import csv
import json
from pathlib import Path

def verify_tsv_integrity(filepath):
    """Verify TSV file integrity"""
    issues = []
    stats = {
        "file_size": Path(filepath).stat().st_size,
        "encoding": "UTF-8",
        "line_ending": None,
        "rows": 0,
        "columns": 0,
        "empty_cells": 0,
        "max_row_length": 0,
        "min_row_length": float('inf')
    }
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        # Detect line ending
        if '\r\n' in content:
            stats["line_ending"] = "CRLF (Windows)"
        elif '\n' in content:
            stats["line_ending"] = "LF (Unix)"
        elif '\r' in content:
            stats["line_ending"] = "CR (Old Mac)"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        rows = list(reader)
        stats["rows"] = len(rows)
        
        if rows:
            stats["columns"] = len(rows[0])
            
            for i, row in enumerate(rows):
                if len(row) != stats["columns"]:
                    issues.append(f"Row {i+1}: Expected {stats['columns']} columns, got {len(row)}")
                
                stats["max_row_length"] = max(stats["max_row_length"], len(row))
                stats["min_row_length"] = min(stats["min_row_length"], len(row))
                
                for cell in row:
                    if cell.strip() == '':
                        stats["empty_cells"] += 1
    
    return stats, issues

# Run verification
input_file = "/mnt/user-data/uploads/met_inventory.tsv"
output_file = "/mnt/user-data/outputs/met_inventory_standardized.tsv"

print("=" * 70)
print("TSV STANDARDIZATION VERIFICATION REPORT")
print("=" * 70)

print("\n📋 SOURCE FILE ANALYSIS")
print("-" * 70)
source_stats, source_issues = verify_tsv_integrity(input_file)
for key, value in source_stats.items():
    print(f"  {key:.<30} {value}")
if source_issues:
    print(f"  ⚠️  Issues found: {len(source_issues)}")
    for issue in source_issues[:5]:
        print(f"     - {issue}")

print("\n📋 OUTPUT FILE ANALYSIS")
print("-" * 70)
output_stats, output_issues = verify_tsv_integrity(output_file)
for key, value in output_stats.items():
    print(f"  {key:.<30} {value}")
if output_issues:
    print(f"  ⚠️  Issues found: {len(output_issues)}")
else:
    print("  ✅ No structural issues detected!")

print("\n📊 DATA QUALITY METRICS")
print("-" * 70)
with open(output_file, 'r', encoding='utf-8') as f:
    reader = csv.reader(f, delimiter='\t')
    rows = list(reader)
    
    if len(rows) > 1:
        data_rows = rows[1:]
        headers = rows[0]
        
        print(f"  Headers: {', '.join(headers)}")
        print(f"  Data rows: {len(data_rows)}")
        print(f"  Empty cells total: {output_stats['empty_cells']}")
        print(f"  Empty cells percentage: {(output_stats['empty_cells'] / (len(data_rows) * len(headers)) * 100):.2f}%")
        
        # Column-wise analysis
        print(f"\n  Column-wise statistics:")
        for col_idx, header in enumerate(headers):
            empty_count = sum(1 for row in data_rows if col_idx < len(row) and not row[col_idx].strip())
            filled_count = len(data_rows) - empty_count
            print(f"    {header:.<25} {filled_count:>3} filled, {empty_count:>3} empty")

print("\n✅ STANDARDIZATION COMPLETE")
print("=" * 70)
