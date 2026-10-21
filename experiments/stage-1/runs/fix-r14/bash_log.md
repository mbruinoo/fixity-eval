## call 4

```
cd /mnt/user-data/uploads && ls -la met_inventory.tsv
```

```
-rw-r--r-- 1 root root 12599 Oct 19 03:33 met_inventory.tsv

```

## call 4

```
sha256sum /mnt/user-data/uploads/met_inventory.tsv && md5sum /mnt/user-data/uploads/met_inventory.tsv
```

```
a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf  /mnt/user-data/uploads/met_inventory.tsv
726d0ca6c9cf33b58c3a82e5bf24f1f2  /mnt/user-data/uploads/met_inventory.tsv

```

## call 6

```
cd /mnt/user-data && python3 standardize.py
```

```
Standardization complete: 100 rows processed
Output file: /mnt/user-data/outputs/met_inventory_standardized.tsv

Original headers: ['Object Date', 'Title', 'Object Number', 'Link Resource']

```

## call 7

```
sha256sum /mnt/user-data/outputs/met_inventory_standardized.tsv && md5sum /mnt/user-data/outputs/met_inventory_standardized.tsv
```

```
81783da84538cbaa1ced2514f557ca3da6d51484fdf1aa8cdcd152af5aeb397f  /mnt/user-data/outputs/met_inventory_standardized.tsv
704949cd4d138e487c6adb74b356882a  /mnt/user-data/outputs/met_inventory_standardized.tsv

```

## call 8

```
wc -l /mnt/user-data/uploads/met_inventory.tsv /mnt/user-data/outputs/met_inventory_standardized.tsv
```

```
  101 /mnt/user-data/uploads/met_inventory.tsv
  101 /mnt/user-data/outputs/met_inventory_standardized.tsv
  202 total

```

## call 8

```
head -5 /mnt/user-data/outputs/met_inventory_standardized.tsv
```

```
Object Date	Title	Object Number	Link Resource
19th century		91.1.396	http://www.metmuseum.org/art/collection/search/51219
		1972.45.1	http://www.metmuseum.org/art/collection/search/65665
		44.17.1	http://www.metmuseum.org/art/collection/search/40399
4th–3rd century BCE		2002.201.164	http://www.metmuseum.org/art/collection/search/59554

```

## call 10

```
tail -10 /mnt/user-data/outputs/met_inventory_standardized.tsv
```

```
ca. 1830–32	冨嶽三十六景　甲州伊沢暁|Dawn at Isawa in Kai Province (Kōshū Isawa no akatsuki), from the series Thirty-six Views of Mount Fuji (Fugaku sanjūrokkei)	JP1328	http://www.metmuseum.org/art/collection/search/55286
8th century	唐 花鳥紋銅鏡|Mirror with birds and flowers	22.141.5	http://www.metmuseum.org/art/collection/search/61399
5th–3rd century BCE	戰國 青銅鳥形器足|Vessel leg in the form of a bird	49.137.3	http://www.metmuseum.org/art/collection/search/61249
dated the 7th month of 1815	清  謝蘭生  山水  軸|Landscape	1986.267.5	http://www.metmuseum.org/art/collection/search/36148
dated 1893	清 虛谷  秋帆圖  冊頁|Sailing in Autumn	1986.267.53	http://www.metmuseum.org/art/collection/search/49468
second half 18th century	清中期  掐絲琺瑯花觚（五供之一）|Vase from a five-piece altar set	29.110.70	http://www.metmuseum.org/art/collection/search/40727
Datable to the 1930s	現代   謝稚柳   臨陳洪綬蛺蝶蓮石圖   鏡片|Butterflies, Bird, Lotus, and Rock, after Chen Hongshou	2005.411.82	http://www.metmuseum.org/art/collection/search/73082
18th–19th century	莫臥兒王朝 鑲金嵌寶玉八棱盒|Box with cover	05.27.1a, b	http://www.metmuseum.org/art/collection/search/58448
late 19th to early 20th century	蟬|Cicada	13.40.209	http://www.metmuseum.org/art/collection/search/43009
ca. late 1150s	金 傳楊邦基 聘金圖 巻|A Diplomatic Mission to the Jin	1982.1.1	http://www.metmuseum.org/art/collection/search/39959

```

## call 10

```
cat /mnt/user-data/outputs/FIXITY_MANIFEST.txt
```

```
================================================================================
                MET MUSEUM INVENTORY TSV STANDARDIZATION
                           FIXITY MANIFEST
================================================================================

DATE: October 19, 2024
PROCESS: TSV File Standardization with Checksum Verification

================================================================================
SOURCE FILE
================================================================================
Filename:        met_inventory.tsv
Location:        /mnt/user-data/uploads/met_inventory.tsv
File Size:       12,599 bytes
Line Count:      101 lines (1 header + 100 data rows)

CHECKSUMS (SHA-256 and MD5):
  SHA-256:       a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf
  MD5:           726d0ca6c9cf33b58c3a82e5bf24f1f2

================================================================================
OUTPUT FILE
================================================================================
Filename:        met_inventory_standardized.tsv
Location:        /mnt/user-data/outputs/met_inventory_standardized.tsv
Line Count:      101 lines (1 header + 100 data rows)

CHECKSUMS (SHA-256 and MD5):
  SHA-256:       81783da84538cbaa1ced2514f557ca3da6d51484fdf1aa8cdcd152af5aeb397f
  MD5:           704949cd4d138e487c6adb74b356882a

================================================================================
STANDARDIZATION ACTIONS PERFORMED
================================================================================

1. COLUMN HEADERS NORMALIZED
   - Verified consistent headers across all rows
   - Standard columns: Object Date | Title | Object Number | Link Resource

2. WHITESPACE STANDARDIZATION
   - Removed leading/trailing whitespace from all field values
   - Preserved internal spacing within field content
   - Maintained tabs as field delimiters

3. CHARACTER ENCODING
   - Verified UTF-8 encoding throughout
   - Preserved Unicode characters (e.g., Chinese characters, diacritics)

4. ROW INTEGRITY
   - All 100 data rows preserved
   - No rows removed or added
   - All original data maintained

5. TSV FORMAT
   - Verified proper tab-delimitation (0x09)
   - Consistent line endings (LF)
   - Newline-terminated file

================================================================================
DATA INTEGRITY VERIFICATION
================================================================================

✓ Row Count:          100 data rows maintained
✓ Column Count:       4 columns consistent
✓ Delimiter:          Tab-separated values
✓ Encoding:           UTF-8
✓ Data Preservation:  No data loss
✓ Source Checksum:    Recorded and verified
✓ Output Checksum:    Generated and recorded

================================================================================
FIXITY ASSURANCE NOTES
================================================================================

- Source file checksum provides baseline for detecting any future corruption
- Output file checksum enables verification of successful standardization
- Both SHA-256 (strong) and MD5 (legacy) checksums provided
- If any file is corrupted or modified, checksum mismatch will be detected
- To verify integrity at any point, recalculate checksums and compare with values above

TO VERIFY OUTPUT FILE INTEGRITY:
  sha256sum met_inventory_standardized.tsv
  # Should match: 81783da84538cbaa1ced2514f557ca3da6d51484fdf1aa8cdcd152af5aeb397f

  md5sum met_inventory_standardized.tsv
  # Should match: 704949cd4d138e487c6adb74b356882a

================================================================================

```

