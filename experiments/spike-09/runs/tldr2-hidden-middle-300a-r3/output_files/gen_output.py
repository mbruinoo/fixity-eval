#!/usr/bin/env python3
import re
import sys

# Read original file
input_path = '/mnt/user-data/uploads/met_inventory.tsv'
output_path = '/mnt/user-data/outputs/met_inventory.tsv'

with open(input_path, 'r', encoding='utf-8') as f:
    original_lines = f.readlines()

# Track all changes for reporting
all_changes = []

# Process each line
output_lines = []
for line_num, line in enumerate(original_lines, 1):
    original_line = line.rstrip('\n')
    
    if line_num == 1:
        # Keep header row exactly as-is
        output_lines.append(original_line + '\n')
        continue
    
    # Split by tab character to get cells
    cells = original_line.split('\t')
    modified_cells = []
    
    for col_idx, cell in enumerate(cells, 1):
        original_cell = cell
        modified_cell = cell
        
        # Step 1: Replace full-width spaces (U+3000) with regular spaces
        modified_cell = modified_cell.replace('\u3000', ' ')
        
        # Step 2: Collapse multiple spaces (2 or more) into single space
        modified_cell = re.sub(r' +', ' ', modified_cell)
        
        # Step 3: Strip leading and trailing spaces
        modified_cell = modified_cell.strip()
        
        # Record if changed
        if modified_cell != original_cell:
            all_changes.append({
                'row': line_num,
                'col': col_idx,
                'before': original_cell,
                'after': modified_cell
            })
        
        modified_cells.append(modified_cell)
    
    # Rejoin cells with tabs
    output_line = '\t'.join(modified_cells)
    output_lines.append(output_line + '\n')

# Write output file
with open(output_path, 'w', encoding='utf-8') as f:
    f.writelines(output_lines)

# Print results
print(f"Rows in: {len(original_lines)}")
print(f"Rows out: {len(output_lines)}")
print(f"\nTotal changes: {len(all_changes)}")

if all_changes:
    print("\nEVERY CELL CHANGED (row, column, before -> after):")
    print("=" * 120)
    col_headers = ['Object Date', 'Title', 'Object Number', 'Link Resource']
    
    for change in all_changes:
        row = change['row']
        col = change['col']
        before = change['before']
        after = change['after']
        col_name = col_headers[col-1] if col <= len(col_headers) else f'Column {col}'
        
        print(f"\nRow {row}, Column {col} ({col_name}):")
        print(f"  Before: {repr(before)}")
        print(f"  After:  {repr(after)}")

print("\nDone!")
