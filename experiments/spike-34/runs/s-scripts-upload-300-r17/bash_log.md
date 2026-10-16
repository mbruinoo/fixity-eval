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

## call 2

```
cd /mnt/user-data/uploads && wc -l met_inventory.tsv
```

```
301 met_inventory.tsv

```

## call 3

```
cat > /tmp/standardize_tsv.py << 'EOF'
import pandas as pd
import re

# Read the TSV file
input_file = '/mnt/user-data/uploads/met_inventory.tsv'
output_file = '/mnt/user-data/outputs/met_inventory_standardized.tsv'

# Read with tab delimiter
df = pd.read_csv(input_file, sep='\t', dtype=str)

print("Original shape:", df.shape)
print("\nColumn names:", df.columns.tolist())
print("\nFirst few rows:")
print(df.head(10))

# Standardization steps
print("\n--- Standardizing ---\n")

# 1. Fill NaN values with empty strings
df = df.fillna('')

# 2. Strip leading/trailing whitespace from all cells
df = df.apply(lambda x: x.str.strip() if x.dtype == 'object' else x)

# 3. Rename columns to standard format (remove trailing spaces, standardize naming)
df.columns = df.columns.str.strip()

# 4. Remove completely empty rows
df = df[(df != '').any(axis=1)]

# 5. Ensure no trailing/leading whitespace in the entire dataframe
df = df.apply(lambda x: x.str.strip() if x.dtype == 'object' else x)

print("Standardized shape:", df.shape)
print("\nStandardized columns:", df.columns.tolist())
print("\nFirst few rows after standardization:")
print(df.head(10))

# Write to output file
df.to_csv(output_file, sep='\t', index=False, quoting=False)
print(f"\n✓ Standardized file saved to: {output_file}")

# Print summary statistics
print("\n--- Summary Statistics ---")
print(f"Total rows: {len(df)}")
print(f"Total columns: {len(df.columns)}")
print(f"\nEmpty cells per column:")
for col in df.columns:
    empty_count = (df[col] == '').sum()
    print(f"  {col}: {empty_count}")

EOF
python /tmp/standardize_tsv.py

```

```
Original shape: (300, 4)

Column names: ['Object Date', 'Title', 'Object Number', 'Link Resource']

First few rows:
                       Object Date  ...                                      Link Resource
0                  7th–9th century  ...  http://www.metmuseum.org/art/collection/search...
1                              NaN  ...  http://www.metmuseum.org/art/collection/search...
2                     19th century  ...  http://www.metmuseum.org/art/collection/search...
3  late 19th to early 20th century  ...  http://www.metmuseum.org/art/collection/search...
4                              NaN  ...  http://www.metmuseum.org/art/collection/search...
5                     19th century  ...  http://www.metmuseum.org/art/collection/search...
6                18th–19th century  ...  http://www.metmuseum.org/art/collection/search...
7                1782, 2nd edition  ...  http://www.metmuseum.org/art/collection/search...
8                18th–19th century  ...  http://www.metmuseum.org/art/collection/search...
9                              NaN  ...  http://www.metmuseum.org/art/collection/search...

[10 rows x 4 columns]

--- Standardizing ---

Standardized shape: (300, 4)

Standardized columns: ['Object Date', 'Title', 'Object Number', 'Link Resource']

First few rows after standardization:
                       Object Date  ...                                      Link Resource
0                  7th–9th century  ...  http://www.metmuseum.org/art/collection/search...
1                                   ...  http://www.metmuseum.org/art/collection/search...
2                     19th century  ...  http://www.metmuseum.org/art/collection/search...
3  late 19th to early 20th century  ...  http://www.metmuseum.org/art/collection/search...
4                                   ...  http://www.metmuseum.org/art/collection/search...
5                     19th century  ...  http://www.metmuseum.org/art/collection/search...
6                18th–19th century  ...  http://www.metmuseum.org/art/collection/search...
7                1782, 2nd edition  ...  http://www.metmuseum.org/art/collection/search...
8                18th–19th century  ...  http://www.metmuseum.org/art/collection/search...
9                                   ...  http://www.metmuseum.org/art/collection/search...

[10 rows x 4 columns]

✓ Standardized file saved to: /mnt/user-data/outputs/met_inventory_standardized.tsv

--- Summary Statistics ---
Total rows: 300
Total columns: 4

Empty cells per column:
  Object Date: 11
  Title: 25
  Object Number: 0
  Link Resource: 0

```

## call 4

```
head -20 /mnt/user-data/outputs/met_inventory_standardized.tsv
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

