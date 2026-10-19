## call 7

```
cd /mnt/user-data/outputs && python3 standardize_met_inventory.py
```

```
Starting Metropolitan Museum Inventory Standardization...
Input: /mnt/user-data/uploads/met_inventory.tsv
Output: /mnt/user-data/outputs/met_inventory_standardized.tsv
Checksums: /mnt/user-data/outputs/met_inventory_checksums.json


Traceback (most recent call last):
  File "/mnt/user-data/outputs/standardize_met_inventory.py", line 168, in <module>
    main()
    ~~~~^^
  File "/mnt/user-data/outputs/standardize_met_inventory.py", line 149, in main
    checksums, row_count = standardize_tsv(input_file, output_file, checksums_file)
                           ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/user-data/outputs/standardize_met_inventory.py", line 40, in standardize_tsv
    source_checksums['original_file_sha256'] = compute_hash(original_content)
                                               ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^
  File "/mnt/user-data/outputs/standardize_met_inventory.py", line 15, in compute_hash
    return hashlib.new(algorithm)(text.encode('utf-8')).hexdigest()
           ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^
TypeError: '_hashlib.HASH' object is not callable

```

## call 9

```
cd /mnt/user-data/outputs && python3 standardize_met_inventory.py
```

```
Starting Metropolitan Museum Inventory Standardization...
Input: /mnt/user-data/uploads/met_inventory.tsv
Output: /mnt/user-data/outputs/met_inventory_standardized.tsv
Checksums: /mnt/user-data/outputs/met_inventory_checksums.json

✓ Standardization completed successfully!

Processed 100 data rows

Source File Hash (SHA256):
  a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf

Standardized File Hash (SHA256):
  a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf

Sample Row Checksums (first 5 rows):
  Row 2 (91.1.396): dab578e49323f1c8...
  Row 3 (1972.45.1): 12a5270773362206...
  Row 4 (44.17.1): 17f35a7fa1e82ae1...
  Row 5 (2002.201.164): 9e481dff7eedd4aa...
  Row 6 (1992.72.44): 89f1afd2ee487ee3...

All checksums saved to met_inventory_checksums.json

```

## call 11

```
cd /mnt/user-data/outputs && python3 verify_met_inventory.py
```

```
============================================================
Metropolitan Museum Inventory Verification
============================================================

Verifying file integrity...
  ✓ File integrity verified (SHA256 and SHA512 match)

Verifying row integrity...
  ✓ All 100 data rows verified successfully

============================================================
✓ VERIFICATION PASSED - All files and rows are valid
============================================================

Detailed report saved to: /mnt/user-data/outputs/met_inventory_verification_report.json

```

## call 12

```
head -20 /mnt/user-data/outputs/met_inventory_standardized.tsv
```

```
Object Date	Title	Object Number	Link Resource
19th century		91.1.396	http://www.metmuseum.org/art/collection/search/51219
		1972.45.1	http://www.metmuseum.org/art/collection/search/65665
		44.17.1	http://www.metmuseum.org/art/collection/search/40399
4th–3rd century BCE		2002.201.164	http://www.metmuseum.org/art/collection/search/59554
15th–16th century		1992.72.44	http://www.metmuseum.org/art/collection/search/37593
19th century		79.2.447	http://www.metmuseum.org/art/collection/search/47205
19th century		30.75.967	http://www.metmuseum.org/art/collection/search/68930
		21.175.224a, b	http://www.metmuseum.org/art/collection/search/41434
19th century		10.211.836	http://www.metmuseum.org/art/collection/search/60168
		20.148.828	http://www.metmuseum.org/art/collection/search/71818
ca. 1650		36.120.598a, b	http://www.metmuseum.org/art/collection/search/63282
18th–19th century		62.32a, b	http://www.metmuseum.org/art/collection/search/60684
1949, printed ca. 1976	"""Lella,"" Brittany"	1976.609.1	http://www.metmuseum.org/art/collection/search/261910
ca. 1927	"""Plucky"" Lindbergh Ready to ""Hop Off"" from Lindbergh Exhibit Cards series (W451)"	63.350.619.451.6	http://www.metmuseum.org/art/collection/search/765705
1965	11 Pop Artists Portfolio Vol. I	2007.49.427a–k	http://www.metmuseum.org/art/collection/search/375953
probably 17th–18th century	Ancus	36.25.1870	http://www.metmuseum.org/art/collection/search/30846
ca. 1918 (?)	Blouse	C.I.64.69.2	http://www.metmuseum.org/art/collection/search/97854
probably late 17th–early 18th century	Bottle with figure of St. Nicholas (?)	83.1.45	http://www.metmuseum.org/art/collection/search/186259
ca. 4500–4000 B.C. (?)	Bracelet	07.228.65a	http://www.metmuseum.org/art/collection/search/570998

```

## call 13

```
wc -l /mnt/user-data/outputs/met_inventory_standardized.tsv && echo "---" && wc -l /mnt/user-data/uploads/met_inventory.tsv
```

```
101 /mnt/user-data/outputs/met_inventory_standardized.tsv
---
101 /mnt/user-data/uploads/met_inventory.tsv

```

