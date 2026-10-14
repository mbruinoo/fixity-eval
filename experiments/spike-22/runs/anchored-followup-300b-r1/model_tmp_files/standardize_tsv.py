import csv
import sys

# Read the TSV file
with open('/tmp/met_inventory.tsv', 'r', encoding='utf-8') as f:
    content = f.read()

# Parse as TSV
reader = csv.reader(content.strip().split('\n'), delimiter='\t')
rows = list(reader)

# Standardize: ensure consistent column count and clean data
if rows:
    headers = rows[0]
    num_cols = len(headers)
    
    # Write standardized TSV
    with open('/mnt/user-data/outputs/met_inventory_standardized.tsv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t', lineterminator='\n')
        
        # Write header
        writer.writerow(headers)
        
        # Write data rows, ensuring consistent columns
        for row in rows[1:]:
            # Pad or trim row to match header count
            while len(row) < num_cols:
                row.append('')
            row = row[:num_cols]
            writer.writerow(row)

print(f"Standardized TSV created with {len(rows)-1} data rows and {num_cols} columns")
