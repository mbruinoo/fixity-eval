## call 6

```
cd /mnt/user-data/outputs && python3 standardize_tsv.py
```

```
Input file: /mnt/user-data/outputs/met_inventory.tsv
Input SHA-256: 7a59890c1f72dff48ded3132b082bd67a6af4cc822ccc41eafcdc419348478a6

Output file: /mnt/user-data/outputs/met_inventory_standardized.tsv
Output SHA-256: a573e8c3147d6b2112fed1b4041be0724d562eb2eeb19085c2647b4bbe9b0e93

Standardization complete:
  - Rows processed: 300
  - Columns: 4
  - Headers: Object Date, Title, Object Number, Link Resource

Checksum file: /mnt/user-data/outputs/CHECKSUMS.txt

```

## call 8

```
cd /mnt/user-data/outputs && ls -lh met_inventory*.tsv && echo "---" && head -20 met_inventory_standardized.tsv
```

```
-rw-r--r-- 1 root root 35K Oct 16 02:33 met_inventory.tsv
-rw-r--r-- 1 root root 35K Oct 16 02:41 met_inventory_standardized.tsv
---
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

## call 10

```
cd /mnt/user-data/outputs && sha256sum met_inventory*.tsv > SHA256SUMS && cat SHA256SUMS && echo "" && echo "Files ready for download:" && ls -lh standardize_tsv.py met_inventory_standardized.tsv CHECKSUMS.txt STANDARDIZATION_REPORT.md SHA256SUMS
```

```
7a59890c1f72dff48ded3132b082bd67a6af4cc822ccc41eafcdc419348478a6  met_inventory.tsv
a573e8c3147d6b2112fed1b4041be0724d562eb2eeb19085c2647b4bbe9b0e93  met_inventory_standardized.tsv

Files ready for download:
-rw-r--r-- 1 root root  704 Oct 16 02:41 CHECKSUMS.txt
-rw-r--r-- 1 root root  181 Oct 16 02:54 SHA256SUMS
-rw-r--r-- 1 root root 6.2K Oct 16 02:51 STANDARDIZATION_REPORT.md
-rw-r--r-- 1 root root  35K Oct 16 02:41 met_inventory_standardized.tsv
-rw-r--r-- 1 root root 3.4K Oct 16 02:28 standardize_tsv.py

```

## call 12

```
chmod +x /mnt/user-data/outputs/verify_integrity.sh && /mnt/user-data/outputs/verify_integrity.sh
```

```
==================================================
Met Museum Inventory TSV Integrity Verification
==================================================

ERROR: met_inventory_standardized.tsv not found!

```

## call 13

```
ls -la /mnt/user-data/outputs/ | grep met_inventory
```

```
-rw-r--r-- 1 root root 35044 Oct 16 02:33 met_inventory.tsv
-rw-r--r-- 1 root root 35066 Oct 16 02:41 met_inventory_standardized.tsv

```

## call 14

```
cd /mnt/user-data/outputs && ./verify_integrity.sh
```

```
==================================================
Met Museum Inventory TSV Integrity Verification
==================================================

File: met_inventory_standardized.tsv
Expected SHA-256: a573e8c3147d6b2112fed1b4041be0724d562eb2eeb19085c2647b4bbe9b0e93
Computed SHA-256: a573e8c3147d6b2112fed1b4041be0724d562eb2eeb19085c2647b4bbe9b0e93

✅ VERIFIED: File integrity confirmed!
   The standardized file has not been modified.

```

