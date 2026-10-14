## call 4

```
cd /mnt/user-data/outputs && md5sum /mnt/user-data/met_inventory.tsv
```

```

md5sum: /mnt/user-data/met_inventory.tsv: No such file or directory

```

## call 5

```
find /mnt -name "met_inventory*" -type f 2>/dev/null
```

```
/mnt/user-data/outputs/met_inventory_standardized.tsv
/mnt/user-data/uploads/met_inventory.tsv

```

## call 6

```
md5sum /mnt/user-data/uploads/met_inventory.tsv
```

```
098392f08012bb5d5d87731e80800f42  /mnt/user-data/uploads/met_inventory.tsv

```

## call 8

```
cd /mnt/user-data/outputs && python3 standardize_met_inventory.py /mnt/user-data/uploads/met_inventory.tsv met_inventory_standardized.tsv
```

```
Original file MD5: 098392f08012bb5d5d87731e80800f42
Output file MD5: 9b5fa1f67e092f5f54bcbba16f10f855

Standardization complete!
Input file:  /mnt/user-data/uploads/met_inventory.tsv
Output file: met_inventory_standardized.tsv
Rows processed: 100

Checksum verification:
  Original: 098392f08012bb5d5d87731e80800f42
  Output:   9b5fa1f67e092f5f54bcbba16f10f855

```

## call 10

```
head -20 /mnt/user-data/outputs/met_inventory_standardized.tsv
```

```
# Metropolitan Museum Inventory TSV - Standardized
# Generated: 2026-10-14T01:23:40.778911
# Original File MD5: 098392f08012bb5d5d87731e80800f42
# Input File: met_inventory.tsv
# Transformations Applied:
#   - Normalized column headers (spaces to underscores)
#   - Replaced empty titles with '[Untitled]'
#   - Replaced empty dates with '[Unknown date]'
#   - Simplified multilingual titles
#
Object_Date	Title	Object_Number	Link_Resource
7th–9th century	[Untitled]	2002.556.36	http://www.metmuseum.org/art/collection/search/65194
late 19th to early 20th century	[Untitled]	16.144.46	http://www.metmuseum.org/art/collection/search/42843
18th–19th century	[Untitled]	28.186.45	http://www.metmuseum.org/art/collection/search/60748
[Unknown date]	[Untitled]	1994.605.95	http://www.metmuseum.org/art/collection/search/44395
7th century	[Untitled]	1989.150	http://www.metmuseum.org/art/collection/search/38250
[Unknown date]	[Untitled]	CP157	http://www.metmuseum.org/art/collection/search/63485
second half of 19th century	[Untitled]	36.100.156a, b	http://www.metmuseum.org/art/collection/search/58338
[Unknown date]	[Untitled]	14.40.171	http://www.metmuseum.org/art/collection/search/46959
1793	[Untitled]	JIB182	http://www.metmuseum.org/art/collection/search/57912

```

## call 11

```
tail -10 /mnt/user-data/outputs/met_inventory_standardized.tsv
```

```
1855–65	Walking boots	2009.300.5484a, b	http://www.metmuseum.org/art/collection/search/169699
early 20th century	White Bearded Gnu, collector card from the Animals series (D9), issued by the Weber Baking Company to promote Onist Milk and Pullman Bread	63.350.307.9.29	http://www.metmuseum.org/art/collection/search/680219
5th century BCE	Arc-shaped pendant (Huang)	2009.92	http://www.metmuseum.org/art/collection/search/75285
1950s	Red and Blue, Two Attendants	2018.853.35	http://www.metmuseum.org/art/collection/search/816263
1840	Five Beauties	2015.500.9.12	http://www.metmuseum.org/art/collection/search/667347
#
# Output File MD5: 9b5fa1f67e092f5f54bcbba16f10f855
# Total rows processed: 100
# Verification: md5sum -c <output_file> or
#   echo 'expected_md5  output_file' | md5sum -c

```

