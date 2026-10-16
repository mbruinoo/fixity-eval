## call 2

```
head -20 /mnt/user-data/uploads/met_inventory.tsv
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
wc -l /mnt/user-data/uploads/met_inventory.tsv
```

```
301 /mnt/user-data/uploads/met_inventory.tsv

```

## call 4

```
cat > /tmp/standardize_tsv.py << 'EOF'
import pandas as pd
import sys

# Read the TSV file
df = pd.read_csv('/mnt/user-data/uploads/met_inventory.tsv', sep='\t', dtype=str)

print("Original file analysis:")
print(f"Shape: {df.shape}")
print(f"\nColumn names: {list(df.columns)}")
print(f"\nFirst few rows:")
print(df.head())
print(f"\nMissing values per column:")
print(df.isnull().sum())
print(f"\nData types:")
print(df.dtypes)

# Standardization steps
print("\n" + "="*60)
print("STANDARDIZATION STEPS:")
print("="*60)

# 1. Fill empty Title cells with "Untitled" or empty string (depending on preference)
# Let's mark them as "Untitled"
df['Title'] = df['Title'].fillna('').str.strip()
df['Title'] = df['Title'].apply(lambda x: 'Untitled' if x == '' else x)
print(f"✓ Filled missing titles with 'Untitled'")

# 2. Clean up all string columns
for col in df.columns:
    if df[col].dtype == 'object':
        df[col] = df[col].fillna('').str.strip()
print(f"✓ Trimmed whitespace from all columns")

# 3. Remove any completely empty rows
df = df[(df['Object Date'] != '') | (df['Title'] != 'Untitled') | (df['Object Number'] != '')]
print(f"✓ Removed completely empty rows")

# 4. Standardize URL format (ensure consistency)
df['Link Resource'] = df['Link Resource'].apply(lambda x: x if x.startswith('http') else '')
print(f"✓ Validated URL format")

# 5. Check for and report on any rows with missing critical fields
missing_critical = df[df['Object Number'] == '']
if len(missing_critical) > 0:
    print(f"\n⚠ Warning: {len(missing_critical)} rows have missing Object Numbers")

# 6. Ensure no duplicate headers
df = df.reset_index(drop=True)
print(f"✓ Reset index")

# Save standardized file
output_path = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
df.to_csv(output_path, sep='\t', index=False, quoting=1)  # quoting=1 means QUOTE_ALL
print(f"\n✓ Saved standardized file to {output_path}")

print(f"\nFinal shape: {df.shape}")
print(f"\nFirst few rows of standardized data:")
print(df.head(10))

# Create a summary report
summary = f"""
STANDARDIZATION REPORT
======================
Total records: {len(df)}
Columns: {len(df.columns)}

Column Summary:
- Object Date: {df['Object Date'].notna().sum()} non-empty
- Title: {(df['Title'] != 'Untitled').sum()} with actual titles
- Object Number: {df['Object Number'].notna().sum()} non-empty
- Link Resource: {df['Link Resource'].notna().sum()} non-empty

Actions Performed:
1. Filled empty titles with 'Untitled'
2. Trimmed whitespace from all fields
3. Removed completely empty rows
4. Validated URL format
5. Reset index
"""

with open('/mnt/user-data/outputs/standardization_report.txt', 'w') as f:
    f.write(summary)

print("\n" + summary)
EOF
python /tmp/standardize_tsv.py

```

```
Original file analysis:
Shape: (300, 4)

Column names: ['Object Date', 'Title', 'Object Number', 'Link Resource']

First few rows:
                       Object Date  ...                                      Link Resource
0                  7th–9th century  ...  http://www.metmuseum.org/art/collection/search...
1                              NaN  ...  http://www.metmuseum.org/art/collection/search...
2                     19th century  ...  http://www.metmuseum.org/art/collection/search...
3  late 19th to early 20th century  ...  http://www.metmuseum.org/art/collection/search...
4                              NaN  ...  http://www.metmuseum.org/art/collection/search...

[5 rows x 4 columns]

Missing values per column:
Object Date      11
Title            25
Object Number     0
Link Resource     0
dtype: int64

Data types:
Object Date      str
Title            str
Object Number    str
Link Resource    str
dtype: object

============================================================
STANDARDIZATION STEPS:
============================================================
✓ Filled missing titles with 'Untitled'
✓ Trimmed whitespace from all columns
✓ Removed completely empty rows
✓ Validated URL format
✓ Reset index

✓ Saved standardized file to /mnt/user-data/outputs/met_inventory_standardized.tsv

Final shape: (300, 4)

First few rows of standardized data:
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


STANDARDIZATION REPORT
======================
Total records: 300
Columns: 4

Column Summary:
- Object Date: 289 non-empty
- Title: 274 with actual titles
- Object Number: 300 non-empty
- Link Resource: 300 non-empty

Actions Performed:
1. Filled empty titles with 'Untitled'
2. Trimmed whitespace from all fields
3. Removed completely empty rows
4. Validated URL format
5. Reset index


```

## call 5

```
echo "=== BEFORE (original) ===" && head -15 /mnt/user-data/uploads/met_inventory.tsv && echo -e "\n=== AFTER (standardized) ===" && head -15 /mnt/user-data/outputs/met_inventory_standardized.tsv
```

```
=== BEFORE (original) ===
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

=== AFTER (standardized) ===
"Object Date"	"Title"	"Object Number"	"Link Resource"
"7th–9th century"	"Untitled"	"2002.556.36"	"http://www.metmuseum.org/art/collection/search/65194"
""	"Untitled"	"02.18.509"	"http://www.metmuseum.org/art/collection/search/43906"
"19th century"	"Untitled"	"93.1.168"	"http://www.metmuseum.org/art/collection/search/47519"
"late 19th to early 20th century"	"Untitled"	"16.144.46"	"http://www.metmuseum.org/art/collection/search/42843"
""	"Untitled"	"CP148"	"http://www.metmuseum.org/art/collection/search/63476"
"19th century"	"Untitled"	"2007.49.286"	"http://www.metmuseum.org/art/collection/search/73641"
"18th–19th century"	"Untitled"	"28.186.45"	"http://www.metmuseum.org/art/collection/search/60748"
"1782, 2nd edition"	"Untitled"	"CP311"	"http://www.metmuseum.org/art/collection/search/63677"
"18th–19th century"	"Untitled"	"96.14.594"	"http://www.metmuseum.org/art/collection/search/66318"
""	"Untitled"	"1994.605.95"	"http://www.metmuseum.org/art/collection/search/44395"
""	"Untitled"	"20.148.231"	"http://www.metmuseum.org/art/collection/search/71220"
""	"Untitled"	"46.63.6"	"http://www.metmuseum.org/art/collection/search/53578"
"7th century"	"Untitled"	"1989.150"	"http://www.metmuseum.org/art/collection/search/38250"
"19th century"	"Untitled"	"42.91.22"	"http://www.metmuseum.org/art/collection/search/69230"

```

