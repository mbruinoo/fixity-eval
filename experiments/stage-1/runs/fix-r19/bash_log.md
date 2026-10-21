## call 6

```
chmod +x /mnt/user-data/outputs/run_standardization.sh && bash /mnt/user-data/outputs/run_standardization.sh
```

```
==========================================
Running standardization with checksums...
==========================================

Input file SHA256:
  a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf

======================================================================
MET MUSEUM INVENTORY STANDARDIZATION WITH FIXITY VERIFICATION
======================================================================

Input file: /mnt/user-data/uploads/met_inventory.tsv
Input SHA256:  a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf

Processing...
✓ Read 100 data rows + 1 header
✓ Wrote 100 standardized rows

Output file: /mnt/user-data/outputs/met_inventory_standardized.tsv
Output SHA256: 81783da84538cbaa1ced2514f557ca3da6d51484fdf1aa8cdcd152af5aeb397f

✓ Report written to: /mnt/user-data/outputs/standardization_report.txt

======================================================================
STANDARDIZATION COMPLETE
======================================================================

Output file SHA256:
  81783da84538cbaa1ced2514f557ca3da6d51484fdf1aa8cdcd152af5aeb397f

✓ Checksums file created: CHECKSUMS.txt

==========================================
All files ready in /mnt/user-data/outputs/
==========================================

Files created:
-rw-r--r-- 1 root root  824 Oct 19 05:05 /mnt/user-data/outputs/CHECKSUMS.txt
-rw-r--r-- 1 root root  13K Oct 19 05:05 /mnt/user-data/outputs/met_inventory_standardized.tsv
-rw-r--r-- 1 root root 2.1K Oct 19 05:05 /mnt/user-data/outputs/standardization_report.txt

```

## call 9

```
head -15 /mnt/user-data/outputs/met_inventory_standardized.tsv && echo "..." && tail -5 /mnt/user-data/outputs/met_inventory_standardized.tsv
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
...
second half 18th century	清中期  掐絲琺瑯花觚（五供之一）|Vase from a five-piece altar set	29.110.70	http://www.metmuseum.org/art/collection/search/40727
Datable to the 1930s	現代   謝稚柳   臨陳洪綬蛺蝶蓮石圖   鏡片|Butterflies, Bird, Lotus, and Rock, after Chen Hongshou	2005.411.82	http://www.metmuseum.org/art/collection/search/73082
18th–19th century	莫臥兒王朝 鑲金嵌寶玉八棱盒|Box with cover	05.27.1a, b	http://www.metmuseum.org/art/collection/search/58448
late 19th to early 20th century	蟬|Cicada	13.40.209	http://www.metmuseum.org/art/collection/search/43009
ca. late 1150s	金 傳楊邦基 聘金圖 巻|A Diplomatic Mission to the Jin	1982.1.1	http://www.metmuseum.org/art/collection/search/39959

```

## call 11

```
echo "=== FINAL VERIFICATION ===" && echo "" && echo "1. File Statistics:" && wc -l /mnt/user-data/uploads/met_inventory.tsv /mnt/user-data/outputs/met_inventory_standardized.tsv && echo "" && echo "2. Column Count Verification:" && head -1 /mnt/user-data/uploads/met_inventory.tsv | tr '\t' '\n' | wc -l && echo "Input columns ^" && head -1 /mnt/user-data/outputs/met_inventory_standardized.tsv | tr '\t' '\n' | wc -l && echo "Output columns ^" && echo "" && echo "3. Checksum Verification:" && sha256sum /mnt/user-data/uploads/met_inventory.tsv /mnt/user-data/outputs/met_inventory_standardized.tsv
```

```
=== FINAL VERIFICATION ===

1. File Statistics:
  101 /mnt/user-data/uploads/met_inventory.tsv
  101 /mnt/user-data/outputs/met_inventory_standardized.tsv
  202 total

2. Column Count Verification:
4
Input columns ^
4
Output columns ^

3. Checksum Verification:
a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf  /mnt/user-data/uploads/met_inventory.tsv
81783da84538cbaa1ced2514f557ca3da6d51484fdf1aa8cdcd152af5aeb397f  /mnt/user-data/outputs/met_inventory_standardized.tsv

```

