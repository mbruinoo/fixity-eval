## call 2

```
cd /mnt/user-data/uploads && head -20 met_inventory.tsv
```

```
Object Date	Title	Object Number	Link Resource
7th–9th century		2002.556.36	http://www.metmuseum.org/art/collection/search/65194
		02.18.509	http://www.metmuseum.org/art/collection/search/43906
19th century		93.1.168	http://www.metmuseum.org/art/collection/search/47519
late 19th to early 20th century		16.144.46	http://www.metmuseum.org/art/collection/search/42843
		CP148	http://www.metmuseum.org/art/collection/search/63476
19th century		2007.49.286	http://www.metmuseum.org/art/collection/search/73641
18th–19th century		28.186.45	http://www.metmuseum.org/art/collection/search/60748
1782, 2nd edition		CP311	http://www.metmuseum.org/art/collection/search/63677
18th–19th century		96.14.594	http://www.metmuseum.org/art/collection/search/66318
		1994.605.95	http://www.metmuseum.org/art/collection/search/44395
		20.148.231	http://www.metmuseum.org/art/collection/search/71220
		46.63.6	http://www.metmuseum.org/art/collection/search/53578
7th century		1989.150	http://www.metmuseum.org/art/collection/search/38250
19th century		42.91.22	http://www.metmuseum.org/art/collection/search/69230
3rd–2nd century BCE		2002.201.111, .112	http://www.metmuseum.org/art/collection/search/59523
		CP157	http://www.metmuseum.org/art/collection/search/63485
18th century		14.40.872a–c	http://www.metmuseum.org/art/collection/search/57947
19th century		09.50.3409	http://www.metmuseum.org/art/collection/search/68043
second half of 19th century		36.100.156a, b	http://www.metmuseum.org/art/collection/search/58338

```

## call 3

```
cat > /tmp/standardize_tsv.py << 'EOF'
import csv
import sys
from pathlib import Path

def standardize_tsv(input_file, output_file):
    """
    Standardize the TSV file by:
    1. Ensuring proper tab-separated format
    2. Removing empty rows
    3. Handling missing Title values (empty cells)
    4. Ensuring consistent column structure
    5. Properly quoting fields with special characters
    """
    
    rows = []
    
    # Read the file with tab delimiter
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            rows.append(row)
    
    # Process rows
    standardized_rows = []
    for i, row in enumerate(rows):
        # Keep header row
        if i == 0:
            standardized_rows.append(row)
            continue
        
        # Skip completely empty rows
        if not any(cell.strip() for cell in row):
            continue
        
        # Ensure we have exactly 4 columns
        while len(row) < 4:
            row.append('')
        row = row[:4]
        
        # Trim whitespace from each cell
        row = [cell.strip() for cell in row]
        
        standardized_rows.append(row)
    
    # Write standardized output
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(standardized_rows)
    
    return len(standardized_rows) - 1  # Excluding header

if __name__ == '__main__':
    input_file = '/mnt/user-data/uploads/met_inventory.tsv'
    output_file = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
    
    num_rows = standardize_tsv(input_file, output_file)
    print(f"✓ Standardization complete!")
    print(f"  Input file: {input_file}")
    print(f"  Output file: {output_file}")
    print(f"  Data rows processed: {num_rows}")
EOF
python /tmp/standardize_tsv.py

```

```
✓ Standardization complete!
  Input file: /mnt/user-data/uploads/met_inventory.tsv
  Output file: /mnt/user-data/outputs/met_inventory_standardized.tsv
  Data rows processed: 300

```

## call 4

```
echo "=== VERIFICATION ===" && \
echo "" && \
echo "Original file stats:" && \
wc -l /mnt/user-data/uploads/met_inventory.tsv && \
echo "" && \
echo "Standardized file stats:" && \
wc -l /mnt/user-data/outputs/met_inventory_standardized.tsv && \
echo "" && \
echo "First 10 rows of standardized file:" && \
head -10 /mnt/user-data/outputs/met_inventory_standardized.tsv
```

```
=== VERIFICATION ===

Original file stats:
301 /mnt/user-data/uploads/met_inventory.tsv

Standardized file stats:
301 /mnt/user-data/outputs/met_inventory_standardized.tsv

First 10 rows of standardized file:
Object Date	Title	Object Number	Link Resource
7th–9th century		2002.556.36	http://www.metmuseum.org/art/collection/search/65194
		02.18.509	http://www.metmuseum.org/art/collection/search/43906
19th century		93.1.168	http://www.metmuseum.org/art/collection/search/47519
late 19th to early 20th century		16.144.46	http://www.metmuseum.org/art/collection/search/42843
		CP148	http://www.metmuseum.org/art/collection/search/63476
19th century		2007.49.286	http://www.metmuseum.org/art/collection/search/73641
18th–19th century		28.186.45	http://www.metmuseum.org/art/collection/search/60748
1782, 2nd edition		CP311	http://www.metmuseum.org/art/collection/search/63677
18th–19th century		96.14.594	http://www.metmuseum.org/art/collection/search/66318

```

## call 5

```
cat > /tmp/analyze_tsv.py << 'EOF'
import csv

def analyze_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        rows = list(reader)
    
    print("📊 STANDARDIZATION REPORT")
    print("=" * 60)
    print(f"\nTotal rows: {len(rows)}")
    print(f"Header: {rows[0]}")
    print(f"Data rows: {len(rows) - 1}")
    
    # Analyze columns
    print("\n📋 COLUMN ANALYSIS:")
    print("-" * 60)
    
    headers = rows[0]
    for col_idx, header in enumerate(headers):
        non_empty = sum(1 for row in rows[1:] if len(row) > col_idx and row[col_idx].strip())
        print(f"  {col_idx + 1}. {header}")
        print(f"     Non-empty values: {non_empty}/{len(rows)-1}")
    
    # Check for consistency
    print("\n✓ QUALITY CHECKS:")
    print("-" * 60)
    
    all_consistent = True
    for i, row in enumerate(rows):
        if len(row) != 4:
            print(f"  ⚠ Row {i+1}: Expected 4 columns, got {len(row)}")
            all_consistent = False
    
    if all_consistent:
        print("  ✓ All rows have exactly 4 columns")
    
    # Check for empty rows
    empty_rows = [i+1 for i, row in enumerate(rows[1:]) if not any(cell.strip() for cell in row)]
    if empty_rows:
        print(f"  ⚠ Found {len(empty_rows)} empty rows")
    else:
        print("  ✓ No completely empty rows")
    
    print("\n✅ Standardization successful!")

analyze_file('/mnt/user-data/outputs/met_inventory_standardized.tsv')
EOF
python /tmp/analyze_tsv.py

```

```
📊 STANDARDIZATION REPORT
============================================================

Total rows: 301
Header: ['Object Date', 'Title', 'Object Number', 'Link Resource']
Data rows: 300

📋 COLUMN ANALYSIS:
------------------------------------------------------------
  1. Object Date
     Non-empty values: 289/300
  2. Title
     Non-empty values: 275/300
  3. Object Number
     Non-empty values: 300/300
  4. Link Resource
     Non-empty values: 300/300

✓ QUALITY CHECKS:
------------------------------------------------------------
  ✓ All rows have exactly 4 columns
  ✓ No completely empty rows

✅ Standardization successful!

```

