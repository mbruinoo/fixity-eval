import re

# Read the original file
with open('/mnt/user-data/uploads/met_inventory.tsv', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Track changes
changes = []

# Process each line
standardized_lines = []
for row_num, line in enumerate(lines, 1):
    # Remove trailing newline
    line = line.rstrip('\n')
    
    # Split by tab to process each cell
    cells = line.split('\t')
    new_cells = []
    
    for col_num, cell in enumerate(cells, 1):
        original_cell = cell
        
        # Replace multiple spaces with single space
        # But preserve intentional spacing patterns
        cell = re.sub(r'  +', ' ', cell)
        
        # Track if this cell changed
        if cell != original_cell:
            changes.append({
                'row': row_num,
                'col': col_num,
                'before': original_cell,
                'after': cell
            })
        
        new_cells.append(cell)
    
    # Rejoin with tabs
    standardized_lines.append('\t'.join(new_cells))

# Write the standardized file
with open('/mnt/user-data/outputs/met_inventory.tsv', 'w', encoding='utf-8') as f:
    for line in standardized_lines:
        f.write(line + '\n')

# Print summary
print(f"Rows in: {len(lines)}")
print(f"Rows out: {len(standardized_lines)}")
print(f"\nChanges made: {len(changes)}")
print("\nDetailed changes:")
for change in changes:
    print(f"Row {change['row']}, Column {change['col']}")
    print(f"  Before: '{change['before']}'")
    print(f"  After:  '{change['after']}'")
    print()
