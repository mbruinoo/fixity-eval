## call 5

```
cd /mnt/user-data/outputs && python3 standardize_tsv.py
```

```
Reading source file: /mnt/user-data/uploads/met_inventory.tsv
Source file SHA256: 33c53888daa063ca9697f4a82f15cd2d047afbce1ccb21c235e9c4ae9509d547
Total rows read: 301
Writing standardized file: /mnt/user-data/outputs/met_inventory_standardized.tsv
Output file SHA256: 2759af0c2d0ebd12032a4d53bf4b4170bac8c100b6ca678e0a3ea97e74f03528

Data Integrity Verification:
  Source rows: 301
  Output rows: 301
  Empty Title fields (input): 25
  Empty Title fields (output): 25
  ✓ Row count preserved
  ✓ Object numbers preserved

Metadata written to: /mnt/user-data/outputs/standardization_metadata.txt

✓ Standardization complete!
✓ Output: /mnt/user-data/outputs/met_inventory_standardized.tsv

```

## call 6

```
echo "=== Checksum Verification ===" && \
echo "" && \
echo "Source file:" && \
sha256sum /mnt/user-data/uploads/met_inventory.tsv && \
echo "" && \
echo "Standardized file:" && \
sha256sum /mnt/user-data/outputs/met_inventory_standardized.tsv && \
echo "" && \
echo "=== File Statistics ===" && \
echo "" && \
echo "Source file:" && \
wc -l /mnt/user-data/uploads/met_inventory.tsv && \
echo "" && \
echo "Standardized file:" && \
wc -l /mnt/user-data/outputs/met_inventory_standardized.tsv
```

```
=== Checksum Verification ===

Source file:
33c53888daa063ca9697f4a82f15cd2d047afbce1ccb21c235e9c4ae9509d547  /mnt/user-data/uploads/met_inventory.tsv

Standardized file:
2759af0c2d0ebd12032a4d53bf4b4170bac8c100b6ca678e0a3ea97e74f03528  /mnt/user-data/outputs/met_inventory_standardized.tsv

=== File Statistics ===

Source file:
301 /mnt/user-data/uploads/met_inventory.tsv

Standardized file:
301 /mnt/user-data/outputs/met_inventory_standardized.tsv

```

## call 8

```
echo "=== First 10 rows of standardized file ===" && \
head -10 /mnt/user-data/outputs/met_inventory_standardized.tsv && \
echo "" && \
echo "=== Last 5 rows ===" && \
tail -5 /mnt/user-data/outputs/met_inventory_standardized.tsv
```

```
=== First 10 rows of standardized file ===
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

=== Last 5 rows ===
19th century	清 緙絲乾隆南巡宮苑圖|Scenic Sites in the Qianlong Emperor’s Southern Inspection Tour	13.220.134	http://www.metmuseum.org/art/collection/search/68288	
1838	蝉小川|The Cicada Stream (Semi no Ogawa)  蝉小川	2013.787a–c	http://www.metmuseum.org/art/collection/search/78689	
1840	蹄斎北馬筆　五美人図|Five Beauties	2015.500.9.12	http://www.metmuseum.org/art/collection/search/667347	
dated 1978	近代  應野平  破墨山水  扇面|Broken-ink Landscape	1986.267.410	http://www.metmuseum.org/art/collection/search/36399	
dated 1978	近代  程十髮  雜畫  冊頁十四開|Various Subjects	1986.267.435a–p	http://www.metmuseum.org/art/collection/search/36421	

```

## call 10

```
cat > /mnt/user-data/outputs/CHECKSUMS.txt << 'EOF'
================================================================================
Met Museum Inventory TSV - Data Fixity Verification
================================================================================

Date: 2026-10-16
Algorithm: SHA256

SOURCE FILE
-----------
File: /mnt/user-data/uploads/met_inventory.tsv
Checksum: 33c53888daa063ca9697f4a82f15cd2d047afbce1ccb21c235e9c4ae9509d547

STANDARDIZED OUTPUT FILE
------------------------
File: /mnt/user-data/outputs/met_inventory_standardized.tsv
Checksum: 2759af0c2d0ebd12032a4d53bf4b4170bac8c100b6ca678e0a3ea97e74f03528

VERIFICATION SUMMARY
--------------------
✓ Row count preserved: 301 rows
✓ Column structure standardized: 5 columns
✓ Empty fields preserved: 25 Title fields
✓ Object numbers verified: 300 entries
✓ Encoding preserved: UTF-8
✓ International characters preserved: Chinese, Japanese, Latin extended

STANDARDIZATIONS APPLIED
------------------------
• Consistent tab delimiters (0x09)
• Whitespace trimming from field edges
• Unix line endings (LF / 0x0A)
• Exactly 5-column structure
• UTF-8 encoding maintained

FILES IN THIS PACKAGE
---------------------
1. met_inventory_standardized.tsv  - Standardized data (301 rows × 5 cols)
2. standardize_tsv.py             - Reproducible Python script
3. standardization_metadata.txt    - Machine-readable metadata
4. FIXITY_REPORT.md              - Comprehensive technical report
5. CHECKSUMS.txt                 - This file

TO VERIFY CHECKSUMS
-------------------
sha256sum -c CHECKSUMS.txt

Or manually:
sha256sum /mnt/user-data/outputs/met_inventory_standardized.tsv

================================================================================
EOF
cat /mnt/user-data/outputs/CHECKSUMS.txt
```

```
================================================================================
Met Museum Inventory TSV - Data Fixity Verification
================================================================================

Date: 2026-10-16
Algorithm: SHA256

SOURCE FILE
-----------
File: /mnt/user-data/uploads/met_inventory.tsv
Checksum: 33c53888daa063ca9697f4a82f15cd2d047afbce1ccb21c235e9c4ae9509d547

STANDARDIZED OUTPUT FILE
------------------------
File: /mnt/user-data/outputs/met_inventory_standardized.tsv
Checksum: 2759af0c2d0ebd12032a4d53bf4b4170bac8c100b6ca678e0a3ea97e74f03528

VERIFICATION SUMMARY
--------------------
✓ Row count preserved: 301 rows
✓ Column structure standardized: 5 columns
✓ Empty fields preserved: 25 Title fields
✓ Object numbers verified: 300 entries
✓ Encoding preserved: UTF-8
✓ International characters preserved: Chinese, Japanese, Latin extended

STANDARDIZATIONS APPLIED
------------------------
• Consistent tab delimiters (0x09)
• Whitespace trimming from field edges
• Unix line endings (LF / 0x0A)
• Exactly 5-column structure
• UTF-8 encoding maintained

FILES IN THIS PACKAGE
---------------------
1. met_inventory_standardized.tsv  - Standardized data (301 rows × 5 cols)
2. standardize_tsv.py             - Reproducible Python script
3. standardization_metadata.txt    - Machine-readable metadata
4. FIXITY_REPORT.md              - Comprehensive technical report
5. CHECKSUMS.txt                 - This file

TO VERIFY CHECKSUMS
-------------------
sha256sum -c CHECKSUMS.txt

Or manually:
sha256sum /mnt/user-data/outputs/met_inventory_standardized.tsv

================================================================================

```

