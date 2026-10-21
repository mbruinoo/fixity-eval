## call 5

```
cd /mnt/user-data/outputs && python3 standardize_met_inventory.py
```

```
Computing input file checksum...
Input SHA256:  a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf
Input file:    /mnt/user-data/uploads/met_inventory.tsv

Standardizing TSV file...
Output file:   /mnt/user-data/outputs/met_inventory_standardized.tsv

Computing output file checksum...
Output SHA256: a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf

Verifying output structure...
Total lines:   101
Header fields: 4
Header:        ['Object Date', 'Title', 'Object Number', 'Link Resource']

Sample rows:
  Line 2: 4 fields
  Line 3: 4 fields
  Line 11: 4 fields
  Line 51: 4 fields
  Line 0: 4 fields

Writing checksums to file...
Checksums written to: /mnt/user-data/outputs/met_inventory_checksums.txt

✓ Standardization complete!

```

## call 6

```
cd /mnt/user-data && sha256sum uploads/met_inventory.tsv outputs/met_inventory_standardized.tsv
```

```
a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf  uploads/met_inventory.tsv
a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf  outputs/met_inventory_standardized.tsv

```

## call 7

```
cd /mnt/user-data/outputs && echo "=== FILE INFO ===" && wc -l met_inventory_standardized.tsv && echo && echo "=== FIRST 5 LINES ===" && head -5 met_inventory_standardized.tsv && echo && echo "=== CHECKING TAB DELIMITERS ===" && head -5 met_inventory_standardized.tsv | cat -A
```

```
=== FILE INFO ===
101 met_inventory_standardized.tsv

=== FIRST 5 LINES ===
Object Date	Title	Object Number	Link Resource
19th century		91.1.396	http://www.metmuseum.org/art/collection/search/51219
		1972.45.1	http://www.metmuseum.org/art/collection/search/65665
		44.17.1	http://www.metmuseum.org/art/collection/search/40399
4th–3rd century BCE		2002.201.164	http://www.metmuseum.org/art/collection/search/59554

=== CHECKING TAB DELIMITERS ===
Object Date^ITitle^IObject Number^ILink Resource$
19th century^I^I91.1.396^Ihttp://www.metmuseum.org/art/collection/search/51219$
^I^I1972.45.1^Ihttp://www.metmuseum.org/art/collection/search/65665$
^I^I44.17.1^Ihttp://www.metmuseum.org/art/collection/search/40399$
4thM-bM-^@M-^S3rd century BCE^I^I2002.201.164^Ihttp://www.metmuseum.org/art/collection/search/59554$

```

