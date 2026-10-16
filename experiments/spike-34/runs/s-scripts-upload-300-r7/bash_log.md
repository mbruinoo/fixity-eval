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
wc -l /mnt/user-data/uploads/met_inventory.tsv && echo "---" && tail -20 /mnt/user-data/uploads/met_inventory.tsv
```

```
301 /mnt/user-data/uploads/met_inventory.tsv
---
1644	Venus, from 'Game of Mythology' (Jeu de la Mythologie)	2012.136.811.12	http://www.metmuseum.org/art/collection/search/412356
1802	View of the Gate of St. Denis, taken from the Suburbs	24.46.10	http://www.metmuseum.org/art/collection/search/821817
ca. 1641	Virgin and Christ Child	17.50.17-297	http://www.metmuseum.org/art/collection/search/373773
1933	Volume 3: progressive proofs for plates 17-24 for Charlot's 'Picture Book'	34.80(3)	http://www.metmuseum.org/art/collection/search/713159
1760–70	Waistcoat	2009.300.2855	http://www.metmuseum.org/art/collection/search/157726
1855–65	Walking boots	2009.300.5484a, b	http://www.metmuseum.org/art/collection/search/169699
17th–18th century	Watch cock	13.173.123	http://www.metmuseum.org/art/collection/search/192463
third quarter 17th century	Wedding knife, fork and sheath	64.101.1595–.1597	http://www.metmuseum.org/art/collection/search/210073
early 20th century	White Bearded Gnu, collector card from the Animals series (D9), issued by the Weber Baking Company to promote Onist Milk and Pullman Bread	63.350.307.9.29	http://www.metmuseum.org/art/collection/search/680219
17th century	Window	93.26.14	http://www.metmuseum.org/art/collection/search/453572
ca. 1929	Yakima Canutt in Arrow Pictures from Western Stars or Scenes Exhibit Cards series (W412)	63.350.613.412.149	http://www.metmuseum.org/art/collection/search/773052
5th century BCE	东周 玉璜|Arc-shaped pendant (Huang)	2009.92	http://www.metmuseum.org/art/collection/search/75285
20th century	擦條|Sand-file for carving jade	1981.296.18	http://www.metmuseum.org/art/collection/search/62070
datable to 1506–10	明　文徵明　致丈人吳愈書　冊頁|Letter to the artist’s father-in-law, Wu Yu	1989.363.59	http://www.metmuseum.org/art/collection/search/45775
1950s	棟方志功筆　蒼赫二童子図|Red and Blue, Two Attendants	2018.853.35	http://www.metmuseum.org/art/collection/search/816263
19th century	清 緙絲乾隆南巡宮苑圖|Scenic Sites in the Qianlong Emperor’s Southern Inspection Tour	13.220.134	http://www.metmuseum.org/art/collection/search/68288
1838	蝉小川|The Cicada Stream (Semi no Ogawa)  蝉小川	2013.787a–c	http://www.metmuseum.org/art/collection/search/78689
1840	蹄斎北馬筆　五美人図|Five Beauties	2015.500.9.12	http://www.metmuseum.org/art/collection/search/667347
dated 1978	近代  應野平  破墨山水  扇面|Broken-ink Landscape	1986.267.410	http://www.metmuseum.org/art/collection/search/36399
dated 1978	近代  程十髮  雜畫  冊頁十四開|Various Subjects	1986.267.435a–p	http://www.metmuseum.org/art/collection/search/36421

```

## call 4

```
cat > /tmp/standardize_tsv.py << 'EOF'
import pandas as pd
import re

# Read the TSV file
df = pd.read_csv('/mnt/user-data/uploads/met_inventory.tsv', sep='\t', dtype=str)

print("Original file info:")
print(f"Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
print(f"\nFirst few rows:")
print(df.head(10))
print(f"\nNull/Empty counts per column:")
print(df.isnull().sum())

# Standardization tasks:
# 1. Fill empty/null values with "N/A"
df = df.fillna('N/A')

# 2. Strip whitespace from all cells
for col in df.columns:
    if df[col].dtype == 'object':
        df[col] = df[col].str.strip()

# 3. Standardize column names to snake_case
df.columns = [col.lower().replace(' ', '_') for col in df.columns]

# 4. Remove duplicate rows
df = df.drop_duplicates()

# 5. Ensure proper URL format consistency
df['link_resource'] = df['link_resource'].apply(
    lambda x: x if x.startswith('http') else 'N/A'
)

# 6. Ensure Object Number is not empty (should have values)
# Rows without an object number might be malformed
df = df[df['object_number'] != 'N/A']

print("\n\nAfter standardization:")
print(f"Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
print(f"\nFirst few rows:")
print(df.head(10))
print(f"\nNull/Empty counts per column:")
print(df.isnull().sum())

# Write to output
output_path = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
df.to_csv(output_path, sep='\t', index=False, encoding='utf-8')
print(f"\n✓ Standardized file saved to: {output_path}")

# Also create a summary report
summary_path = '/mnt/user-data/outputs/standardization_report.txt'
with open(summary_path, 'w', encoding='utf-8') as f:
    f.write("STANDARDIZATION REPORT\n")
    f.write("=" * 60 + "\n\n")
    f.write(f"Original rows: 301 (including header)\n")
    f.write(f"Final rows: {len(df) + 1} (including header)\n")
    f.write(f"Rows removed: {301 - (len(df) + 1)}\n\n")
    f.write("CHANGES MADE:\n")
    f.write("1. Filled empty/null values with 'N/A'\n")
    f.write("2. Stripped leading/trailing whitespace from all cells\n")
    f.write("3. Standardized column names to snake_case\n")
    f.write("4. Removed duplicate rows\n")
    f.write("5. Validated URL format in 'link_resource' column\n")
    f.write("6. Removed rows with missing 'object_number' values\n\n")
    f.write("COLUMN INFORMATION:\n")
    for col in df.columns:
        non_na = (df[col] != 'N/A').sum()
        f.write(f"  - {col}: {non_na} filled values, {len(df) - non_na} N/A\n")

print(f"✓ Report saved to: {summary_path}")
EOF
python /tmp/standardize_tsv.py

```

```
Original file info:
Shape: (300, 4)
Columns: ['Object Date', 'Title', 'Object Number', 'Link Resource']

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

Null/Empty counts per column:
Object Date      11
Title            25
Object Number     0
Link Resource     0
dtype: int64


After standardization:
Shape: (300, 4)
Columns: ['object_date', 'title', 'object_number', 'link_resource']

First few rows:
                       object_date  ...                                      link_resource
0                  7th–9th century  ...  http://www.metmuseum.org/art/collection/search...
1                              N/A  ...  http://www.metmuseum.org/art/collection/search...
2                     19th century  ...  http://www.metmuseum.org/art/collection/search...
3  late 19th to early 20th century  ...  http://www.metmuseum.org/art/collection/search...
4                              N/A  ...  http://www.metmuseum.org/art/collection/search...
5                     19th century  ...  http://www.metmuseum.org/art/collection/search...
6                18th–19th century  ...  http://www.metmuseum.org/art/collection/search...
7                1782, 2nd edition  ...  http://www.metmuseum.org/art/collection/search...
8                18th–19th century  ...  http://www.metmuseum.org/art/collection/search...
9                              N/A  ...  http://www.metmuseum.org/art/collection/search...

[10 rows x 4 columns]

Null/Empty counts per column:
object_date      0
title            0
object_number    0
link_resource    0
dtype: int64

✓ Standardized file saved to: /mnt/user-data/outputs/met_inventory_standardized.tsv
✓ Report saved to: /mnt/user-data/outputs/standardization_report.txt

```

## call 5

```
echo "=== STANDARDIZED FILE SAMPLE ===" && head -15 /mnt/user-data/outputs/met_inventory_standardized.tsv && echo -e "\n=== STANDARDIZATION REPORT ===" && cat /mnt/user-data/outputs/standardization_report.txt
```

```
=== STANDARDIZED FILE SAMPLE ===
object_date	title	object_number	link_resource
7th–9th century	N/A	2002.556.36	http://www.metmuseum.org/art/collection/search/65194
N/A	N/A	02.18.509	http://www.metmuseum.org/art/collection/search/43906
19th century	N/A	93.1.168	http://www.metmuseum.org/art/collection/search/47519
late 19th to early 20th century	N/A	16.144.46	http://www.metmuseum.org/art/collection/search/42843
N/A	N/A	CP148	http://www.metmuseum.org/art/collection/search/63476
19th century	N/A	2007.49.286	http://www.metmuseum.org/art/collection/search/73641
18th–19th century	N/A	28.186.45	http://www.metmuseum.org/art/collection/search/60748
1782, 2nd edition	N/A	CP311	http://www.metmuseum.org/art/collection/search/63677
18th–19th century	N/A	96.14.594	http://www.metmuseum.org/art/collection/search/66318
N/A	N/A	1994.605.95	http://www.metmuseum.org/art/collection/search/44395
N/A	N/A	20.148.231	http://www.metmuseum.org/art/collection/search/71220
N/A	N/A	46.63.6	http://www.metmuseum.org/art/collection/search/53578
7th century	N/A	1989.150	http://www.metmuseum.org/art/collection/search/38250
19th century	N/A	42.91.22	http://www.metmuseum.org/art/collection/search/69230

=== STANDARDIZATION REPORT ===
STANDARDIZATION REPORT
============================================================

Original rows: 301 (including header)
Final rows: 301 (including header)
Rows removed: 0

CHANGES MADE:
1. Filled empty/null values with 'N/A'
2. Stripped leading/trailing whitespace from all cells
3. Standardized column names to snake_case
4. Removed duplicate rows
5. Validated URL format in 'link_resource' column
6. Removed rows with missing 'object_number' values

COLUMN INFORMATION:
  - object_date: 289 filled values, 11 N/A
  - title: 275 filled values, 25 N/A
  - object_number: 300 filled values, 0 N/A
  - link_resource: 300 filled values, 0 N/A

```

