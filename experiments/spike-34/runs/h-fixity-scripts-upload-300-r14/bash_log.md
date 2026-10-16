## call 5

```
cd /mnt/user-data/outputs && python3 standardize_tsv.py
```

```
======================================================================
STANDARDIZING TSV FILE WITH FIXITY VERIFICATION
======================================================================

Input file: /mnt/user-data/uploads/met_inventory.tsv
  SHA256: 33c53888daa063ca9697f4a82f15cd2d047afbce1ccb21c235e9c4ae9509d547
  MD5:    6ec5bfc2d979ad12eb3343149beb8617

Processing file...
✓ File standardized successfully

Output file: /mnt/user-data/outputs/met_inventory_standardized.tsv
  SHA256: 4c8d7aae2855064971111cfa962994548817ae721c053ca002b2aaa9eb48203e
  MD5:    3b4b77a26e2316189c0200cff7cd4e51

======================================================================
STATISTICS
======================================================================
Input rows:   301
Output rows:  301
Input size:   35,052 bytes
Output size:  35,086 bytes

Manifest saved: /mnt/user-data/outputs/fixity_manifest.txt

✓ Standardization complete with fixity verification!

```

## call 7

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

## call 8

```
grep "Arrowhead" /mnt/user-data/outputs/met_inventory_standardized.tsv
```

```
ca. 1615–1868	Arrowhead (<i>Yanone</i>)	36.25.2605	http://www.metmuseum.org/art/collection/search/23765

```

## call 9

```
sha256sum /mnt/user-data/uploads/met_inventory.tsv /mnt/user-data/outputs/met_inventory_standardized.tsv
```

```
33c53888daa063ca9697f4a82f15cd2d047afbce1ccb21c235e9c4ae9509d547  /mnt/user-data/uploads/met_inventory.tsv
4c8d7aae2855064971111cfa962994548817ae721c053ca002b2aaa9eb48203e  /mnt/user-data/outputs/met_inventory_standardized.tsv

```

