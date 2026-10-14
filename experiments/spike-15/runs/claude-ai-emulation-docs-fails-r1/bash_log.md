## call 2

```
wc -l /mnt/user-data/uploads/met_inventory.tsv
```

```
301 /mnt/user-data/uploads/met_inventory.tsv

```

## call 3

```
python3 << 'EOF'
import pandas as pd

# Read the TSV file
df = pd.read_csv('/mnt/user-data/uploads/met_inventory.tsv', sep='\t')

# Standardize the dataframe
# 1. Remove extra whitespace from all cells
df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

# 2. Replace empty/NaN values with empty strings for consistency
df = df.fillna('')

# 3. Rename columns to be consistent (remove extra spaces)
df.columns = [col.strip() for col in df.columns]

# 4. Sort by Object Date (keeping entries with missing dates at the end)
# Create a sortable date column for sorting
def extract_sort_key(date_str):
    if not date_str:
        return (9999, '')
    # Simple sort: extract first year if possible
    import re
    numbers = re.findall(r'\d+', date_str)
    if numbers:
        first_year = int(numbers[0])
        return (first_year, date_str)
    return (9999, date_str)

df['sort_key'] = df['Object Date'].apply(extract_sort_key)
df = df.sort_values('sort_key').drop('sort_key', axis=1)
df = df.reset_index(drop=True)

# 5. Ensure consistent URL format
df['Link Resource'] = df['Link Resource'].apply(lambda x: x.strip() if isinstance(x, str) else x)

# Save standardized file
df.to_csv('/mnt/user-data/outputs/met_inventory_standardized.tsv', sep='\t', index=False, quoting=1)

print("Standardization complete!")
print(f"Total records: {len(df)}")
print(f"\nColumns: {list(df.columns)}")
print(f"\nMissing Title entries: {(df['Title'] == '').sum()}")
print(f"Missing Object Date entries: {(df['Object Date'] == '').sum()}")
print("\nFirst few rows:")
print(df.head(10))
print("\nLast few rows:")
print(df.tail(10))

EOF

```

```

Traceback (most recent call last):
  File "<stdin>", line 8, in <module>
  File "/usr/local/lib/python3.13/dist-packages/pandas/core/generic.py", line 6194, in __getattr__
    return object.__getattribute__(self, name)
           ~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^
AttributeError: 'DataFrame' object has no attribute 'applymap'

```

## call 4

```
python3 << 'EOF'
import pandas as pd

# Read the TSV file
df = pd.read_csv('/mnt/user-data/uploads/met_inventory.tsv', sep='\t')

# Standardize the dataframe
# 1. Remove extra whitespace from all cells
df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

# 2. Replace empty/NaN values with empty strings for consistency
df = df.fillna('')

# 3. Rename columns to be consistent (remove extra spaces)
df.columns = [col.strip() for col in df.columns]

# 4. Sort by Object Date (keeping entries with missing dates at the end)
# Create a sortable date column for sorting
def extract_sort_key(date_str):
    if not date_str:
        return (9999, '')
    # Simple sort: extract first year if possible
    import re
    numbers = re.findall(r'\d+', date_str)
    if numbers:
        first_year = int(numbers[0])
        return (first_year, date_str)
    return (9999, date_str)

df['sort_key'] = df['Object Date'].apply(extract_sort_key)
df = df.sort_values('sort_key').drop('sort_key', axis=1)
df = df.reset_index(drop=True)

# 5. Ensure consistent URL format
df['Link Resource'] = df['Link Resource'].apply(lambda x: x.strip() if isinstance(x, str) else x)

# Save standardized file
df.to_csv('/mnt/user-data/outputs/met_inventory_standardized.tsv', sep='\t', index=False, quoting=1)

print("Standardization complete!")
print(f"Total records: {len(df)}")
print(f"\nColumns: {list(df.columns)}")
print(f"\nMissing Title entries: {(df['Title'] == '').sum()}")
print(f"Missing Object Date entries: {(df['Object Date'] == '').sum()}")
print("\nFirst few rows:")
print(df.head(10))
print("\nLast few rows:")
print(df.tail(10))

EOF

```

```
Standardization complete!
Total records: 300

Columns: ['Object Date', 'Title', 'Object Number', 'Link Resource']

Missing Title entries: 25
Missing Object Date entries: 11

First few rows:
             Object Date  ...                                      Link Resource
0         August 1, 1870  ...  http://www.metmuseum.org/art/collection/search...
1      January 1st, 1874  ...  http://www.metmuseum.org/art/collection/search...
2    ca. 1st–2nd century  ...  http://www.metmuseum.org/art/collection/search...
3     2nd–3rd century CE  ...  http://www.metmuseum.org/art/collection/search...
4    3rd century BCE (?)  ...  http://www.metmuseum.org/art/collection/search...
5    3rd–2nd century BCE  ...  http://www.metmuseum.org/art/collection/search...
6        3rd–4th century  ...  http://www.metmuseum.org/art/collection/search...
7        4th century BCE  ...  http://www.metmuseum.org/art/collection/search...
8        4th–7th century  ...  http://www.metmuseum.org/art/collection/search...
9  4th–early 5th century  ...  http://www.metmuseum.org/art/collection/search...

[10 rows x 4 columns]

Last few rows:
    Object Date  ...                                      Link Resource
290              ...  http://www.metmuseum.org/art/collection/search...
291              ...  http://www.metmuseum.org/art/collection/search...
292              ...  http://www.metmuseum.org/art/collection/search...
293              ...  http://www.metmuseum.org/art/collection/search...
294              ...  http://www.metmuseum.org/art/collection/search...
295              ...  http://www.metmuseum.org/art/collection/search...
296              ...  http://www.metmuseum.org/art/collection/search...
297              ...  http://www.metmuseum.org/art/collection/search...
298              ...  http://www.metmuseum.org/art/collection/search...
299        n.d.  ...  http://www.metmuseum.org/art/collection/search...

[10 rows x 4 columns]

```

## call 6

```
cd /mnt/user-data/outputs && python3 << 'EOF'
import hashlib
import json
from datetime import datetime

# Calculate MD5 checksum of input file
def calculate_md5(filepath):
    md5_hash = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()

# Calculate SHA256 checksum of input file
def calculate_sha256(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

input_file = '/mnt/user-data/uploads/met_inventory.tsv'
input_md5 = calculate_md5(input_file)
input_sha256 = calculate_sha256(input_file)

print(f"Input file checksums:")
print(f"  MD5:    {input_md5}")
print(f"  SHA256: {input_sha256}")

EOF

```

```
Input file checksums:
  MD5:    6ec5bfc2d979ad12eb3343149beb8617
  SHA256: 33c53888daa063ca9697f4a82f15cd2d047afbce1ccb21c235e9c4ae9509d547

```

## call 8

```
cd /mnt/user-data/outputs && python3 standardize_met_inventory.py /mnt/user-data/uploads/met_inventory.tsv /mnt/user-data/outputs/met_inventory_standardized.tsv
```

```
======================================================================
METROPOLITAN MUSEUM OF ART INVENTORY STANDARDIZATION
======================================================================

Reading input file: /mnt/user-data/uploads/met_inventory.tsv
  MD5:    6ec5bfc2d979ad12eb3343149beb8617
  SHA256: 33c53888daa063ca9697f4a82f15cd2d047afbce1ccb21c235e9c4ae9509d547

Loading TSV file...
  Loaded 300 records with 4 columns

Step 1: Removing whitespace from all cells...
  ✓ Complete

Step 2: Standardizing missing values...
  ✓ Replaced 36 NaN values with empty strings

Step 3: Normalizing column names...
  Columns: ['Object Date', 'Title', 'Object Number', 'Link Resource']
  ✓ Complete

Step 4: Sorting records chronologically...
  ✓ Records sorted by Object Date (earliest to latest)

Step 5: Normalizing URL format...
  ✓ Complete

Data Quality Statistics:
  Total records: 300
  Records with missing titles: 25
  Records with missing dates: 11

Writing output file: /mnt/user-data/outputs/met_inventory_standardized.tsv
  ✓ File written

Calculating output file checksums...
  MD5:    32db7388e7cea3bf8a54edd68f65fb28
  SHA256: c7a32d6f208cc76dc8c87afd3fa09a827441ccb180dee6c1799e913e95d42670

======================================================================
STANDARDIZATION COMPLETE
======================================================================

FIXITY CHECK SUMMARY:
  Input file (met_inventory.tsv):
    MD5:    6ec5bfc2d979ad12eb3343149beb8617
    SHA256: 33c53888daa063ca9697f4a82f15cd2d047afbce1ccb21c235e9c4ae9509d547

  Output file (/mnt/user-data/outputs/met_inventory_standardized.tsv):
    MD5:    32db7388e7cea3bf8a54edd68f65fb28
    SHA256: c7a32d6f208cc76dc8c87afd3fa09a827441ccb180dee6c1799e913e95d42670

Timestamp: 2026-10-14T00:07:13.087317
======================================================================

```

## call 9

```
cp /mnt/user-data/uploads/met_inventory.tsv /mnt/user-data/outputs/met_inventory.tsv
```

```
(no output, exit code 0)
```

