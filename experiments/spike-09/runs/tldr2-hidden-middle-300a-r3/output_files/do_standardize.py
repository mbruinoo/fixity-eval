#!/usr/bin/env python3
import re

# Read original file
with open('/mnt/user-data/uploads/met_inventory.tsv', 'r', encoding='utf-8') as f:
    original_lines = f.readlines()

# Process lines
output_lines = []
changes = []

for line_num, line in enumerate(original_lines, 1):
    original_line = line.rstrip('\n')
    
    if line_num == 1:
        # Keep header as-is
        output_lines.append(original_line + '\n')
        continue
    
    # Split by tabs
    cells = original_line.split('\t')
    modified_cells = []
    
    for col_idx, cell in enumerate(cells, 1):
        original_cell = cell
        modified_cell = cell
        
        # Standardize spaces:
        # 1. Replace full-width spaces (U+3000) with regular spaces
        modified_cell = modified_cell.replace('\u3000', ' ')
        # 2. Collapse multiple consecutive spaces into single space
        modified_cell = re.sub(r' +', ' ', modified_cell)
        # 3. Strip leading/trailing spaces
        modified_cell = modified_cell.strip()
        
        # Track changes
        if modified_cell != original_cell:
            changes.append((line_num, col_idx, original_cell, modified_cell))
        
        modified_cells.append(modified_cell)
    
    # Rejoin cells with tabs
    output_line = '\t'.join(modified_cells)
    output_lines.append(output_line + '\n')

# Write output file
with open('/mnt/user-data/outputs/met_inventory.tsv', 'w', encoding='utf-8') as f:
    f.writelines(output_lines)

# Print report
print(f"Rows in: {len(original_lines)}")
print(f"Rows out: {len(output_lines)}")
print(f"\nTotal cells changed: {len(changes)}")
print("\nAll changes (row, column, before -> after):")
print("-" * 100)
for row, col, before, after in changes:
    col_names = ['Object Date', 'Title', 'Object Number', 'Link Resource']
    col_name = col_names[col-1] if col-1 < len(col_names) else f'Col{col}'
    print(f"Row {row}, Column {col} ({col_name}):")
    print(f"  Before: {repr(before)}")
    print(f"  After:  {repr(after)}")
    print()
