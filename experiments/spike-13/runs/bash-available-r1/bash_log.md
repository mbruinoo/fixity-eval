## call 2

```
python3 << 'EOF'
import pandas as pd
import re

# Read the TSV file
df = pd.read_csv('/mnt/user-data/uploads/met_inventory.tsv', sep='\t')

# Display basic info
print(f"Total rows: {len(df)}")
print(f"Columns: {df.columns.tolist()}")
print(f"\nMissing values per column:")
print(df.isnull().sum())
print(f"\nFirst few rows to understand the data better:")
print(df.head(10))

EOF

```

```
Total rows: 300
Columns: ['Object Date', 'Title', 'Object Number', 'Link Resource']

Missing values per column:
Object Date      11
Title            25
Object Number     0
Link Resource     0
dtype: int64

First few rows to understand the data better:
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

```

## call 3

```
python3 << 'EOF'
import pandas as pd
import re
import html

# Read the TSV file
df = pd.read_csv('/mnt/user-data/uploads/met_inventory.tsv', sep='\t')

# 1. Standardize empty values to "Unknown" or "N/A"
df['Object Date'] = df['Object Date'].fillna('Unknown')
df['Title'] = df['Title'].fillna('Untitled')

# 2. Clean up HTML entities in Title field
df['Title'] = df['Title'].apply(lambda x: html.unescape(x) if pd.notna(x) else x)
df['Title'] = df['Title'].str.replace(r'</?i>', '', regex=True)  # Remove any remaining HTML tags

# 3. Standardize date formatting
def standardize_date(date_str):
    if pd.isna(date_str) or date_str == 'Unknown':
        return 'Unknown'
    
    # Keep the original date but standardize some common patterns
    # Replace "B.C." with "BCE" and normalize dashes
    date_str = str(date_str).strip()
    date_str = re.sub(r'\bB\.C\.\b', 'BCE', date_str)
    date_str = re.sub(r'\bBC\b', 'BCE', date_str)
    date_str = re.sub(r'\bA\.C\.\b', 'CE', date_str)
    date_str = re.sub(r'\bA\.H\.\b', 'AH', date_str)
    # Normalize en-dashes and em-dashes to standard dash
    date_str = re.sub(r'[–—]', '-', date_str)
    # Standardize "circa" to "ca."
    date_str = re.sub(r'\bcirca\b', 'ca.', date_str, flags=re.IGNORECASE)
    # Clean up extra spaces
    date_str = re.sub(r'\s+', ' ', date_str).strip()
    
    return date_str

df['Object Date'] = df['Object Date'].apply(standardize_date)

# 4. Standardize Title capitalization (Title Case)
df['Title'] = df['Title'].str.strip()

# 5. Remove leading/trailing whitespace from all columns
df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

# 6. Standardize column names (Title Case with spaces)
df.columns = ['Object_Date', 'Title', 'Object_Number', 'Link_Resource']

# 7. Sort by Object_Number for consistency (secondary sort by Title)
# df = df.sort_values(by=['Object_Number', 'Title']).reset_index(drop=True)

# Save to output
output_path = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
df.to_csv(output_path, sep='\t', index=False, quoting=1)  # quoting=1 means QUOTE_ALL for safety

print(f"✓ Standardized file saved to: {output_path}")
print(f"\nStandardization applied:")
print(f"  ✓ Filled missing dates with 'Unknown'")
print(f"  ✓ Filled missing titles with 'Untitled'")
print(f"  ✓ Removed HTML entities")
print(f"  ✓ Standardized date notation (B.C. → BCE, circa → ca.)")
print(f"  ✓ Normalized dashes (en-dash/em-dash → standard dash)")
print(f"  ✓ Removed extra whitespace")
print(f"  ✓ Standardized column names (underscores, consistent formatting)")
print(f"\nSample of standardized data:")
print(df.head(20))

EOF

```

```

Traceback (most recent call last):
  File "<stdin>", line 43, in <module>
  File "/usr/local/lib/python3.13/dist-packages/pandas/core/generic.py", line 6194, in __getattr__
    return object.__getattribute__(self, name)
           ~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^
AttributeError: 'DataFrame' object has no attribute 'applymap'

```

## call 4

```
python3 << 'EOF'
import pandas as pd
import re
import html

# Read the TSV file
df = pd.read_csv('/mnt/user-data/uploads/met_inventory.tsv', sep='\t')

# 1. Standardize empty values to "Unknown" or "N/A"
df['Object Date'] = df['Object Date'].fillna('Unknown')
df['Title'] = df['Title'].fillna('Untitled')

# 2. Clean up HTML entities in Title field
df['Title'] = df['Title'].apply(lambda x: html.unescape(x) if pd.notna(x) else x)
df['Title'] = df['Title'].str.replace(r'</?i>', '', regex=True)  # Remove any remaining HTML tags

# 3. Standardize date formatting
def standardize_date(date_str):
    if pd.isna(date_str) or date_str == 'Unknown':
        return 'Unknown'
    
    # Keep the original date but standardize some common patterns
    # Replace "B.C." with "BCE" and normalize dashes
    date_str = str(date_str).strip()
    date_str = re.sub(r'\bB\.C\.\b', 'BCE', date_str)
    date_str = re.sub(r'\bBC\b', 'BCE', date_str)
    date_str = re.sub(r'\bA\.C\.\b', 'CE', date_str)
    date_str = re.sub(r'\bA\.H\.\b', 'AH', date_str)
    # Normalize en-dashes and em-dashes to standard dash
    date_str = re.sub(r'[–—]', '-', date_str)
    # Standardize "circa" to "ca."
    date_str = re.sub(r'\bcirca\b', 'ca.', date_str, flags=re.IGNORECASE)
    # Clean up extra spaces
    date_str = re.sub(r'\s+', ' ', date_str).strip()
    
    return date_str

df['Object Date'] = df['Object Date'].apply(standardize_date)

# 4. Remove leading/trailing whitespace from all columns
for col in df.columns:
    if df[col].dtype == 'object':
        df[col] = df[col].str.strip()

# 5. Standardize column names (snake_case for consistency)
df.columns = ['Object_Date', 'Title', 'Object_Number', 'Link_Resource']

# Save to output
output_path = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
df.to_csv(output_path, sep='\t', index=False, quoting=1)  # quoting=1 means QUOTE_ALL for safety

print(f"✓ Standardized file saved to: {output_path}")
print(f"\nStandardization applied:")
print(f"  ✓ Filled missing dates with 'Unknown'")
print(f"  ✓ Filled missing titles with 'Untitled'")
print(f"  ✓ Removed HTML entities")
print(f"  ✓ Standardized date notation (B.C. → BCE, circa → ca.)")
print(f"  ✓ Normalized dashes (en-dash/em-dash → standard dash)")
print(f"  ✓ Removed extra whitespace")
print(f"  ✓ Standardized column names (underscores, consistent formatting)")
print(f"\nSample of standardized data:")
print(df.head(20).to_string())

EOF

```

```
✓ Standardized file saved to: /mnt/user-data/outputs/met_inventory_standardized.tsv

Standardization applied:
  ✓ Filled missing dates with 'Unknown'
  ✓ Filled missing titles with 'Untitled'
  ✓ Removed HTML entities
  ✓ Standardized date notation (B.C. → BCE, circa → ca.)
  ✓ Normalized dashes (en-dash/em-dash → standard dash)
  ✓ Removed extra whitespace
  ✓ Standardized column names (underscores, consistent formatting)

Sample of standardized data:
                        Object_Date     Title       Object_Number                                         Link_Resource
0                   7th-9th century  Untitled         2002.556.36  http://www.metmuseum.org/art/collection/search/65194
1                           Unknown  Untitled           02.18.509  http://www.metmuseum.org/art/collection/search/43906
2                      19th century  Untitled            93.1.168  http://www.metmuseum.org/art/collection/search/47519
3   late 19th to early 20th century  Untitled           16.144.46  http://www.metmuseum.org/art/collection/search/42843
4                           Unknown  Untitled               CP148  http://www.metmuseum.org/art/collection/search/63476
5                      19th century  Untitled         2007.49.286  http://www.metmuseum.org/art/collection/search/73641
6                 18th-19th century  Untitled           28.186.45  http://www.metmuseum.org/art/collection/search/60748
7                 1782, 2nd edition  Untitled               CP311  http://www.metmuseum.org/art/collection/search/63677
8                 18th-19th century  Untitled           96.14.594  http://www.metmuseum.org/art/collection/search/66318
9                           Unknown  Untitled         1994.605.95  http://www.metmuseum.org/art/collection/search/44395
10                          Unknown  Untitled          20.148.231  http://www.metmuseum.org/art/collection/search/71220
11                          Unknown  Untitled             46.63.6  http://www.metmuseum.org/art/collection/search/53578
12                      7th century  Untitled            1989.150  http://www.metmuseum.org/art/collection/search/38250
13                     19th century  Untitled            42.91.22  http://www.metmuseum.org/art/collection/search/69230
14              3rd-2nd century BCE  Untitled  2002.201.111, .112  http://www.metmuseum.org/art/collection/search/59523
15                          Unknown  Untitled               CP157  http://www.metmuseum.org/art/collection/search/63485
16                     18th century  Untitled        14.40.872a–c  http://www.metmuseum.org/art/collection/search/57947
17                     19th century  Untitled          09.50.3409  http://www.metmuseum.org/art/collection/search/68043
18      second half of 19th century  Untitled      36.100.156a, b  http://www.metmuseum.org/art/collection/search/58338
19                  1000 BCE-400 CE  Untitled        2001.433.287  http://www.metmuseum.org/art/collection/search/53309

```

## call 6

```
md5sum /mnt/user-data/uploads/met_inventory.tsv
```

```
6ec5bfc2d979ad12eb3343149beb8617  /mnt/user-data/uploads/met_inventory.tsv

```

