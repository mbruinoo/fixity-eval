## call 4

```
python3 << 'EOF'
import csv
import html

# Read the TSV file
input_file = '/mnt/user-data/uploads/met_inventory.tsv'
output_file = '/mnt/user-data/outputs/met_inventory_standardized.tsv'

# Read all rows
rows = []
with open(input_file, 'r', encoding='utf-8') as f:
    reader = csv.reader(f, delimiter='\t')
    for row in reader:
        rows.append(row)

# Process rows - standardize and clean
standardized_rows = [rows[0]]  # Keep header

for i, row in enumerate(rows[1:], 1):
    # Ensure we have 4 columns
    while len(row) < 4:
        row.append('')
    
    # Trim to 4 columns if more exist
    row = row[:4]
    
    # Clean up each field
    object_date = row[0].strip()
    title = row[1].strip()
    object_number = row[2].strip()
    link_resource = row[3].strip()
    
    # Decode HTML entities
    if title:
        title = html.unescape(title)
    
    # Standardize empty cells to truly empty (not whitespace)
    standardized_rows.append([
        object_date,
        title,
        object_number,
        link_resource
    ])

# Write standardized file
with open(output_file, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f, delimiter='\t', lineterminator='\n')
    writer.writerows(standardized_rows)

print(f"✓ Standardized TSV file created")
print(f"✓ Total rows: {len(standardized_rows)} (including header)")
print(f"✓ HTML entities decoded")
print(f"✓ Columns normalized to 4 fields")

EOF

```

```
✓ Standardized TSV file created
✓ Total rows: 301 (including header)
✓ HTML entities decoded
✓ Columns normalized to 4 fields

```

