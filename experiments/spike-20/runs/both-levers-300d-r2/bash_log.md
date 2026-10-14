## call 3

```
cd /mnt/user-data/outputs && md5sum /mnt/user-data/met_inventory.tsv
```

```

md5sum: /mnt/user-data/met_inventory.tsv: No such file or directory

```

## call 4

```
find /mnt -name "met_inventory.tsv" 2>/dev/null
```

```
/mnt/user-data/uploads/met_inventory.tsv

```

## call 5

```
md5sum /mnt/user-data/uploads/met_inventory.tsv && sha256sum /mnt/user-data/uploads/met_inventory.tsv
```

```
098392f08012bb5d5d87731e80800f42  /mnt/user-data/uploads/met_inventory.tsv
5eb3a8afc4d1e5f20382fef7a6bd3d4bc38d58080b3f621d847087ac1451566e  /mnt/user-data/uploads/met_inventory.tsv

```

## call 7

```
cd /mnt/user-data/outputs && python3 standardize_met_inventory.py
```

```
Input file: /mnt/user-data/uploads/met_inventory.tsv
  MD5:    098392f08012bb5d5d87731e80800f42
  SHA256: 5eb3a8afc4d1e5f20382fef7a6bd3d4bc38d58080b3f621d847087ac1451566e

Header: ['Object Date', 'Title', 'Object Number', 'Link Resource']
Total rows to process: 100

Output file: /mnt/user-data/outputs/met_inventory_standardized.tsv
  MD5:    49d6bed252721359d090007b3c4b9ecd
  SHA256: 2d8f1b775f9812671f4032e15eaf9f8bf47fee34bd6a4f53adf8d2c0fb323f25

Manifest file: /mnt/user-data/outputs/MANIFEST.txt

Standardization complete!

```

## call 8

```
cp /mnt/user-data/uploads/met_inventory.tsv /mnt/user-data/outputs/met_inventory_original.tsv && ls -lh /mnt/user-data/outputs/
```

```
total 36K
-rw-r--r-- 1 root root 1.8K Oct 14 01:25 MANIFEST.txt
-rw-r--r-- 1 root root  11K Oct 14 01:25 met_inventory_original.tsv
-rw-r--r-- 1 root root  12K Oct 14 01:25 met_inventory_standardized.tsv
-rw-r--r-- 1 root root 5.9K Oct 14 01:25 standardize_met_inventory.py

```

## call 10

```
cd /mnt/user-data/outputs && echo "=== VERIFICATION ===" && md5sum met_inventory_original.tsv && md5sum met_inventory_standardized.tsv && echo && sha256sum met_inventory_original.tsv && sha256sum met_inventory_standardized.tsv
```

```
=== VERIFICATION ===
098392f08012bb5d5d87731e80800f42  met_inventory_original.tsv
49d6bed252721359d090007b3c4b9ecd  met_inventory_standardized.tsv

5eb3a8afc4d1e5f20382fef7a6bd3d4bc38d58080b3f621d847087ac1451566e  met_inventory_original.tsv
2d8f1b775f9812671f4032e15eaf9f8bf47fee34bd6a4f53adf8d2c0fb323f25  met_inventory_standardized.tsv

```

## call 11

```
cd /mnt/user-data/outputs && echo "=== FIRST 5 ROWS OF STANDARDIZED OUTPUT ===" && head -6 met_inventory_standardized.tsv && echo && echo "=== LAST 3 ROWS (showing bilingual removal) ===" && tail -3 met_inventory_standardized.tsv
```

```
=== FIRST 5 ROWS OF STANDARDIZED OUTPUT ===
Object Date	Title	Object Number	Link Resource
7th–9th century	[Unknown]	2002.556.36	http://www.metmuseum.org/art/collection/search/65194
late 19th to early 20th century	[Unknown]	16.144.46	http://www.metmuseum.org/art/collection/search/42843
18th–19th century	[Unknown]	28.186.45	http://www.metmuseum.org/art/collection/search/60748
[Unknown]	[Unknown]	1994.605.95	http://www.metmuseum.org/art/collection/search/44395
7th century	[Unknown]	1989.150	http://www.metmuseum.org/art/collection/search/38250

=== LAST 3 ROWS (showing bilingual removal) ===
5th century BCE	Arc-shaped pendant (Huang)	2009.92	http://www.metmuseum.org/art/collection/search/75285
1950s	Red and Blue, Two Attendants	2018.853.35	http://www.metmuseum.org/art/collection/search/816263
1840	Five Beauties	2015.500.9.12	http://www.metmuseum.org/art/collection/search/667347

```

