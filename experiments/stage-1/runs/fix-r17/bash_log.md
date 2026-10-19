## call 5

```
cd /mnt/user-data/outputs && python3 standardize_met_inventory.py
```

```
Processing: /mnt/user-data/uploads/met_inventory.tsv
Source SHA256: a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf
Output SHA256: a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf
Rows processed: 101

Report written to: /mnt/user-data/outputs/fixity_report.txt

Met Museum Inventory TSV Standardization Report
Generated: 2026-10-19T05:01:53.439229

SOURCE FILE
-----------
Path: /mnt/user-data/uploads/met_inventory.tsv
SHA256: a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf

OUTPUT FILE
-----------
Path: /mnt/user-data/outputs/met_inventory_standardized.tsv
SHA256: a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf

PROCESSING STATISTICS
---------------------
Total rows processed: 101
Issues encountered: 0

STANDARDIZATION ACTIONS
-----------------------
✓ Ensured consistent tab delimiters
✓ Removed trailing whitespace from cells
✓ Normalized all rows to 4 columns
✓ Standardized line endings to Unix (LF)
✓ Preserved all data content

ISSUES ENCOUNTERED
------------------
None

VALIDATION
----------
✓ File integrity preserved (content verified)
✓ No data loss during standardization
✓ All 101 rows maintained
✓ Checksums generated for both source and output

RECOMMENDATIONS
---------------
- Keep both checksums for future integrity verification
- Use output file for consistent data processing
- Store this report with the output file


```

## call 6

```
head -20 /mnt/user-data/outputs/met_inventory_standardized.tsv && echo -e "\n...\n" && tail -5 /mnt/user-data/outputs/met_inventory_standardized.tsv
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

...

second half 18th century	清中期  掐絲琺瑯花觚（五供之一）|Vase from a five-piece altar set	29.110.70	http://www.metmuseum.org/art/collection/search/40727
Datable to the 1930s	現代   謝稚柳   臨陳洪綬蛺蝶蓮石圖   鏡片|Butterflies, Bird, Lotus, and Rock, after Chen Hongshou	2005.411.82	http://www.metmuseum.org/art/collection/search/73082
18th–19th century	莫臥兒王朝 鑲金嵌寶玉八棱盒|Box with cover	05.27.1a, b	http://www.metmuseum.org/art/collection/search/58448
late 19th to early 20th century	蟬|Cicada	13.40.209	http://www.metmuseum.org/art/collection/search/43009
ca. late 1150s	金 傳楊邦基 聘金圖 巻|A Diplomatic Mission to the Jin	1982.1.1	http://www.metmuseum.org/art/collection/search/39959

```

