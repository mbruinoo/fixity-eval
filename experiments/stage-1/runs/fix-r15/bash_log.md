## call 3

```
cd /mnt/user-data/uploads && ls -la *.tsv
```

```
-rw-r--r-- 1 root root 12599 Oct 19 04:30 met_inventory.tsv

```

## call 4

```
python3 << 'EOF'
import csv
import hashlib
import sys

# Calculate SHA256 checksum of source file
def calculate_checksum(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

# Read and standardize the TSV
source_file = "/mnt/user-data/uploads/met_inventory.tsv"
output_file = "/mnt/user-data/outputs/met_inventory_standardized.tsv"

# Get source checksum
source_checksum = calculate_checksum(source_file)
print(f"SOURCE CHECKSUM (SHA256): {source_checksum}")
print(f"SOURCE FILE: {source_file}\n")

# Read the original file
with open(source_file, 'r', encoding='utf-8') as infile:
    # Read all lines
    lines = infile.readlines()
    
# Parse using tab delimiter
reader = csv.reader(lines, delimiter='\t')
rows = list(reader)

# Standardize: ensure 4 columns for all rows
standardized_rows = []

# Add header
header = ["Object Date", "Title", "Object Number", "Link Resource"]
standardized_rows.append(header)

# Process data rows
for i, row in enumerate(rows[1:], start=2):  # Skip original header
    # Pad row to 4 columns with empty strings if needed
    while len(row) < 4:
        row.append("")
    # Take only first 4 columns
    row = row[:4]
    standardized_rows.append(row)

# Write standardized output
with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
    writer = csv.writer(outfile, delimiter='\t', lineterminator='\n')
    writer.writerows(standardized_rows)

# Get output checksum
output_checksum = calculate_checksum(output_file)
print(f"OUTPUT CHECKSUM (SHA256): {output_checksum}")
print(f"OUTPUT FILE: {output_file}\n")

# Print statistics
print(f"STANDARDIZATION REPORT:")
print(f"Total rows processed: {len(standardized_rows) - 1} (excluding header)")
print(f"Columns: {len(header)}")
print(f"Format: Tab-separated values (TSV)")
print(f"Encoding: UTF-8")
print(f"Line terminator: LF (Unix)")
EOF

```

```
SOURCE CHECKSUM (SHA256): a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf
SOURCE FILE: /mnt/user-data/uploads/met_inventory.tsv

OUTPUT CHECKSUM (SHA256): a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf
OUTPUT FILE: /mnt/user-data/outputs/met_inventory_standardized.tsv

STANDARDIZATION REPORT:
Total rows processed: 100 (excluding header)
Columns: 4
Format: Tab-separated values (TSV)
Encoding: UTF-8
Line terminator: LF (Unix)

```

## call 5

```
python3 << 'EOF'
import csv
import hashlib

# Verify the file structure
source_file = "/mnt/user-data/uploads/met_inventory.tsv"
output_file = "/mnt/user-data/outputs/met_inventory_standardized.tsv"

# Check both files
for filepath in [source_file, output_file]:
    print(f"\n{'='*70}")
    print(f"VERIFICATION: {filepath}")
    print(f"{'='*70}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        rows = list(reader)
    
    print(f"Total rows: {len(rows)}")
    print(f"Header: {rows[0]}")
    print(f"Columns per row:")
    
    col_counts = {}
    for i, row in enumerate(rows):
        count = len(row)
        col_counts[count] = col_counts.get(count, 0) + 1
    
    for count, freq in sorted(col_counts.items()):
        print(f"  - {count} columns: {freq} rows")
    
    print(f"\nFirst 3 data rows:")
    for row in rows[1:4]:
        print(f"  {row}")
    
    print(f"\nLast 3 data rows:")
    for row in rows[-3:]:
        print(f"  {row}")

EOF

```

```

======================================================================
VERIFICATION: /mnt/user-data/uploads/met_inventory.tsv
======================================================================
Total rows: 101
Header: ['Object Date', 'Title', 'Object Number', 'Link Resource']
Columns per row:
  - 4 columns: 101 rows

First 3 data rows:
  ['19th century', '', '91.1.396', 'http://www.metmuseum.org/art/collection/search/51219']
  ['', '', '1972.45.1', 'http://www.metmuseum.org/art/collection/search/65665']
  ['', '', '44.17.1', 'http://www.metmuseum.org/art/collection/search/40399']

Last 3 data rows:
  ['18th–19th century', '莫臥兒王朝 鑲金嵌寶玉八棱盒|Box with cover', '05.27.1a, b', 'http://www.metmuseum.org/art/collection/search/58448']
  ['late 19th to early 20th century', '蟬|Cicada', '13.40.209', 'http://www.metmuseum.org/art/collection/search/43009']
  ['ca. late 1150s', '金 傳楊邦基 聘金圖 巻|A Diplomatic Mission to the Jin', '1982.1.1', 'http://www.metmuseum.org/art/collection/search/39959']

======================================================================
VERIFICATION: /mnt/user-data/outputs/met_inventory_standardized.tsv
======================================================================
Total rows: 101
Header: ['Object Date', 'Title', 'Object Number', 'Link Resource']
Columns per row:
  - 4 columns: 101 rows

First 3 data rows:
  ['19th century', '', '91.1.396', 'http://www.metmuseum.org/art/collection/search/51219']
  ['', '', '1972.45.1', 'http://www.metmuseum.org/art/collection/search/65665']
  ['', '', '44.17.1', 'http://www.metmuseum.org/art/collection/search/40399']

Last 3 data rows:
  ['18th–19th century', '莫臥兒王朝 鑲金嵌寶玉八棱盒|Box with cover', '05.27.1a, b', 'http://www.metmuseum.org/art/collection/search/58448']
  ['late 19th to early 20th century', '蟬|Cicada', '13.40.209', 'http://www.metmuseum.org/art/collection/search/43009']
  ['ca. late 1150s', '金 傳楊邦基 聘金圖 巻|A Diplomatic Mission to the Jin', '1982.1.1', 'http://www.metmuseum.org/art/collection/search/39959']

```

