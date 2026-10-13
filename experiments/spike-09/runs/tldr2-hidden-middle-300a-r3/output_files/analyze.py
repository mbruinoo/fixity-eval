#!/usr/bin/env python3
import re

# Read the file
with open('/mnt/user-data/uploads/met_inventory.tsv', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Look for lines with multiple spaces or full-width spaces
issues = []

for line_num, line in enumerate(lines, 1):
    if line_num == 1:
        continue
    
    cells = line.rstrip('\n').split('\t')
    
    for col_idx, cell in enumerate(cells, 1):
        # Check for multiple spaces
        if '  ' in cell:  # double space or more
            issues.append({
                'line': line_num,
                'col': col_idx,
                'type': 'multiple_spaces',
                'content': cell
            })
        
        # Check for full-width spaces
        if '\u3000' in cell:
            issues.append({
                'line': line_num,
                'col': col_idx,
                'type': 'fullwidth_space',
                'content': cell
            })

print(f"Found {len(issues)} cells with spacing issues:\n")
for issue in issues:
    print(f"Line {issue['line']}, Col {issue['col']} ({issue['type']}):")
    print(f"  {repr(issue['content'][:80])}")
    print()
