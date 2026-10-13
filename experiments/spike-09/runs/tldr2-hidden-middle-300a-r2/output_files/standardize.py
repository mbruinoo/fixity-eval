import re

# Read the original file
with open('/mnt/user-data/uploads/met_inventory.tsv', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines in file: {len(lines)}")
print(f"Data rows (excluding header): {len(lines) - 1}")

# Process the file
output_lines = []
changes = []

for line_num, line in enumerate(lines, 1):
    if line_num == 1:  # Keep header as-is
        output_lines.append(line)
        continue
    
    # Split by tabs
    parts = line.rstrip('\n').split('\t')
    
    # Standardize the "Object Date" column (first column)
    if len(parts) > 0:
        original_date = parts[0]
        standardized_date = original_date
        
        # Fix double spaces in dates
        standardized_date = re.sub(r'\s{2,}', ' ', standardized_date)
        
        if original_date != standardized_date:
            changes.append((line_num, 1, original_date, standardized_date))
            parts[0] = standardized_date
    
    # Reconstruct the line
    output_line = '\t'.join(parts) + '\n'
    output_lines.append(output_line)

# Write the standardized file
with open('/mnt/user-data/outputs/met_inventory.tsv', 'w', encoding='utf-8') as f:
    f.writelines(output_lines)

print(f"\nChanges made: {len(changes)}")
for row, col, before, after in changes:
    print(f"Row {row}, Column {col}: '{before}' -> '{after}'")
