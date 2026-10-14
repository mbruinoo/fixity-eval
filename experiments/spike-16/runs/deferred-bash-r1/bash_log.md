## call 4

```
python3 << 'EOF'
import re

# Read the file
with open('/mnt/user-data/uploads/met_inventory.tsv', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Process the data
output_lines = []
header = lines[0].strip()
output_lines.append(header)

for i, line in enumerate(lines[1:], 1):
    # Split by tabs
    parts = line.rstrip('\n').split('\t')
    
    # Ensure we have exactly 4 columns
    while len(parts) < 4:
        parts.append('')
    parts = parts[:4]
    
    # Clean up each field
    object_date = parts[0].strip()
    title = parts[1].strip()
    object_number = parts[2].strip()
    link = parts[3].strip()
    
    # Decode HTML entities
    title = title.replace('&lt;', '<').replace('&gt;', '>')
    title = title.replace('&amp;', '&')
    
    # Join back with tabs
    standardized_line = '\t'.join([object_date, title, object_number, link])
    output_lines.append(standardized_line)

# Write output
with open('/mnt/user-data/outputs/met_inventory_standardized.tsv', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output_lines))

print(f"✓ Standardized {len(output_lines)-1} data rows")
print("✓ Decoded HTML entities")
print("✓ Ensured consistent column structure")
print("\nOutput: met_inventory_standardized.tsv")

EOF

```

```
✓ Standardized 300 data rows
✓ Decoded HTML entities
✓ Ensured consistent column structure

Output: met_inventory_standardized.tsv

```

