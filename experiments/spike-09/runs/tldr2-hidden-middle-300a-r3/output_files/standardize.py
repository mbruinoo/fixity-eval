#!/usr/bin/env python3

import re

# Read the original file
with open('/mnt/user-data/uploads/met_inventory.tsv', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Track changes
changes = []

# Process each line
output_lines = []
for line_num, line in enumerate(lines, 1):
    # Remove trailing newline to work with the content
    original_line = line.rstrip('\n')
    modified_line = original_line
    
    # Skip header row
    if line_num == 1:
        output_lines.append(modified_line + '\n')
        continue
    
    # Split by tabs to process each cell
    cells = original_line.split('\t')
    modified_cells = []
    
    for col_idx, cell in enumerate(cells, 1):
        original_cell = cell
        modified_cell = cell
        
        # Standardize spaces: collapse multiple spaces into single space
        # Handle both regular spaces and full-width spaces (U+3000)
        # First, replace multiple regular spaces with single space
        modified_cell = re.sub(r' {2,}', ' ', modified_cell)
        # Replace full-width spaces with regular spaces
        modified_cell = modified_cell.replace('\u3000', ' ')
        # Now collapse any resulting multiple spaces again
        modified_cell = re.sub(r' {2,}', ' ', modified_cell)
        # Strip leading/trailing spaces
        modified_cell = modified_cell.strip()
        
        # Only record if changed
        if modified_cell != original_cell:
            changes.append({
                'row': line_num,
                'col': col_idx,
                'before': original_cell,
                'after': modified_cell
            })
        
        modified_cells.append(modified_cell)
    
    # Rejoin with tabs
    modified_line = '\t'.join(modified_cells)
    output_lines.append(modified_line + '\n')

# Write the standardized file
with open('/mnt/user-data/outputs/met_inventory.tsv', 'w', encoding='utf-8') as f:
    f.writelines(output_lines)

# Print summary
print(f"Input rows: {len(lines)}")
print(f"Output rows: {len(output_lines)}")
print(f"Total changes made: {len(changes)}")
print("\nChanges (row, column, before, after):")
for change in changes:
    print(f"Row {change['row']}, Column {change['col']}:")
    print(f"  Before: {repr(change['before'])}")
    print(f"  After:  {repr(change['after'])}")
