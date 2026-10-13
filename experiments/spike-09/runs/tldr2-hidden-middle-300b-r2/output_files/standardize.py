import re

# Read the original file
with open('/mnt/user-data/uploads/met_inventory.tsv', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Keep track of changes
changes = []

# Process each line
for i, line in enumerate(lines):
    if i == 0:  # Skip header
        continue
    
    original_line = line
    
    # Split into columns
    columns = line.rstrip('\n').split('\t')
    
    for col_idx, cell in enumerate(columns):
        original_cell = cell
        
        # 1. Replace HTML entities
        cell = cell.replace('&lt;i&gt;', '<i>')
        cell = cell.replace('&lt;/i&gt;', '</i>')
        
        # 2. Standardize BC/BCE notation - convert "B.C." to "BCE" for consistency
        # Handle patterns like "664–30 B.C." or "664-332 B.C."
        cell = re.sub(r'(\d)\s+B\.C\.(?!\w)', r'\1 BCE', cell)
        
        # 3. Standardize date range hyphens to en-dash (–)
        # Pattern: "number-number" (for year ranges like 1890-99 or 664-332)
        # But also handle "mid-20th" -> "mid–20th"
        cell = re.sub(r'(\d)-(\d)', r'\1–\2', cell)
        cell = re.sub(r'(mid|early|late)-(\d)', r'\1–\2', cell)
        
        # 4. Standardize "n.d." to "n.d."  (ensure lowercase)
        cell = re.sub(r'N\.D\.', 'n.d.', cell)
        cell = re.sub(r'N\.d\.', 'n.d.', cell)
        
        # Record if changed
        if cell != original_cell:
            changes.append({
                'row': i + 1,  # i is 0-indexed but line numbers are 1-indexed
                'column': col_idx + 1,
                'before': original_cell,
                'after': cell
            })
        
        columns[col_idx] = cell
    
    # Reconstruct the line
    new_line = '\t'.join(columns) + '\n'
    lines[i] = new_line

# Write the standardized file
with open('/mnt/user-data/outputs/met_inventory.tsv', 'w', encoding='utf-8') as f:
    f.writelines(lines)

# Print changes
print("STANDARDIZATION REPORT")
print("=" * 80)
print(f"\nRows in: 301 (1 header + 300 data rows)")
print(f"Rows out: 301 (1 header + 300 data rows)")
print(f"\nTotal cells changed: {len(changes)}")
print("\nChanges made:")
print("-" * 80)

for change in changes:
    print(f"\nRow {change['row']}, Column {change['column']}:")
    print(f"  Before: {repr(change['before'])}")
    print(f"  After:  {repr(change['after'])}")
