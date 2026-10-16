## call 8

```
cd /mnt/user-data/outputs && python3 full_standardize.py
```

```
======================================================================
Met Museum Inventory TSV Standardization
======================================================================

STEP 1: Analyzing source file...
----------------------------------------------------------------------
  Rows:           301
  Columns:        4
  Empty cells:    36
  Row length min: 4
  Row length max: 4

STEP 2: Computing source checksums...
----------------------------------------------------------------------
  MD5:     12fbeecf069d9e68f7310826e00e97fb
  SHA256:  0459b0a7a7f0c959b4b3e925d71a4733c7eba5468b1a6dd5a52d4dac9afed01d
  SHA512:  be35a7dbc6a77d5ee18acff715dae0b0da73db4d25cf1464a4355ce2b92542a0ee4e94117a5325246c1a82eec5dd976bffe1c6d4ba358911c7887beb7004ec9a
  Size:    35032 bytes

STEP 3: Standardizing TSV...
----------------------------------------------------------------------
  ✓ Rows processed: 301
  ✓ Output written: /mnt/user-data/outputs/met_inventory_standardized.tsv

STEP 4: Analyzing standardized file...
----------------------------------------------------------------------
  Rows:           301
  Columns:        4
  Empty cells:    36
  Row length min: 4
  Row length max: 4

STEP 5: Computing output checksums...
----------------------------------------------------------------------
  MD5:     86b04dadd8e5c383d249861f51bcc0fd
  SHA256:  5ed81410d26d63f1c3eefd21068956cf9cff66f8e09e23e430e478865de87f16
  SHA512:  e49232f230888ef46a0d496381085664aee172e1a7e6c53172ef8576cb046d18485e4b3335d27e4b01a49390ea2fbad5282d0d3dcf82ca2a65561fd54776ed06
  Size:    35078 bytes

STEP 6: Verifying data integrity...
----------------------------------------------------------------------
  ✓ Row count preserved: 301 rows
  ✓ Column count preserved: 4 columns
  ✓ Empty cell count preserved: 36 cells

STEP 7: Generating report...
----------------------------------------------------------------------
  ✓ Report written: /mnt/user-data/outputs/checksum_report.txt

======================================================================
✓ STANDARDIZATION COMPLETE
======================================================================

Output files created in: /mnt/user-data/outputs/
  1. met_inventory_standardized.tsv  (standardized data)
  2. checksum_report.txt              (full verification report)


```

## call 10

```
ls -lh /mnt/user-data/outputs/*.tsv /mnt/user-data/outputs/*.txt && echo -e "\n=== Sample of standardized file (first 10 rows) ===" && head -10 /mnt/user-data/outputs/met_inventory_standardized.tsv
```

```
-rw-r--r-- 1 root root 7.4K Oct 16 02:47 /mnt/user-data/outputs/checksum_report.txt
-rw-r--r-- 1 root root  35K Oct 16 02:47 /mnt/user-data/outputs/met_inventory_standardized.tsv

=== Sample of standardized file (first 10 rows) ===
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

```

