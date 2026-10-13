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

