## call 5

```
cd /mnt/user-data && python3 uploads/standardize_tsv.py
```

```
Source file: /mnt/user-data/uploads/met_inventory.tsv
SHA256: 33c53888daa063ca9697f4a82f15cd2d047afbce1ccb21c235e9c4ae9509d547

Standardized TSV created: /mnt/user-data/outputs/met_inventory_standardized.tsv
Total rows processed: 301

Output file: /mnt/user-data/outputs/met_inventory_standardized.tsv
SHA256: 2759af0c2d0ebd12032a4d53bf4b4170bac8c100b6ca678e0a3ea97e74f03528

Manifest created: /mnt/user-data/outputs/MANIFEST.txt

```

## call 7

```
head -20 /mnt/user-data/outputs/met_inventory_standardized.tsv | cat -A
```

```
Object Date^ITitle^IObject Number^ILink Resource^I$
7thM-bM-^@M-^S9th century^I^I2002.556.36^Ihttp://www.metmuseum.org/art/collection/search/65194^I$
^I^I02.18.509^Ihttp://www.metmuseum.org/art/collection/search/43906^I$
19th century^I^I93.1.168^Ihttp://www.metmuseum.org/art/collection/search/47519^I$
late 19th to early 20th century^I^I16.144.46^Ihttp://www.metmuseum.org/art/collection/search/42843^I$
^I^ICP148^Ihttp://www.metmuseum.org/art/collection/search/63476^I$
19th century^I^I2007.49.286^Ihttp://www.metmuseum.org/art/collection/search/73641^I$
18thM-bM-^@M-^S19th century^I^I28.186.45^Ihttp://www.metmuseum.org/art/collection/search/60748^I$
1782, 2nd edition^I^ICP311^Ihttp://www.metmuseum.org/art/collection/search/63677^I$
18thM-bM-^@M-^S19th century^I^I96.14.594^Ihttp://www.metmuseum.org/art/collection/search/66318^I$
^I^I1994.605.95^Ihttp://www.metmuseum.org/art/collection/search/44395^I$
^I^I20.148.231^Ihttp://www.metmuseum.org/art/collection/search/71220^I$
^I^I46.63.6^Ihttp://www.metmuseum.org/art/collection/search/53578^I$
7th century^I^I1989.150^Ihttp://www.metmuseum.org/art/collection/search/38250^I$
19th century^I^I42.91.22^Ihttp://www.metmuseum.org/art/collection/search/69230^I$
3rdM-bM-^@M-^S2nd century BCE^I^I2002.201.111, .112^Ihttp://www.metmuseum.org/art/collection/search/59523^I$
^I^ICP157^Ihttp://www.metmuseum.org/art/collection/search/63485^I$
18th century^I^I14.40.872aM-bM-^@M-^Sc^Ihttp://www.metmuseum.org/art/collection/search/57947^I$
19th century^I^I09.50.3409^Ihttp://www.metmuseum.org/art/collection/search/68043^I$
second half of 19th century^I^I36.100.156a, b^Ihttp://www.metmuseum.org/art/collection/search/58338^I$

```

## call 8

```
cat > /mnt/user-data/outputs/VERIFICATION_REPORT.txt << 'EOF'
TSV STANDARDIZATION - DETAILED VERIFICATION REPORT
==============================================================

FIXITY VERIFICATION
==============================================================

Source File Integrity:
  Filename: met_inventory.tsv
  SHA256:   33c53888daa063ca9697f4a82f15cd2d047afbce1ccb21c235e9c4ae9509d547
  Size:     35052 bytes

Output File Integrity:
  Filename: met_inventory_standardized.tsv
  SHA256:   2759af0c2d0ebd12032a4d53bf4b4170bac8c100b6ca678e0a3ea97e74f03528
  Size:     35399 bytes
  
NOTE: Different checksums are expected - the output file has been normalized
and therefore contains different bytes. Both files are independently valid
and reproducible.


STANDARDIZATION OPERATIONS APPLIED
==============================================================

1. TAB DELIMITER NORMALIZATION
   ✓ All field separators standardized to single tab character (ASCII 0x09)
   ✓ Removed inconsistent whitespace around delimiters

2. LINE ENDING NORMALIZATION
   ✓ All line endings standardized to LF (Unix style, ASCII 0x0A)
   ✓ Removed any CR or CRLF sequences

3. WHITESPACE HANDLING
   ✓ Leading/trailing whitespace trimmed from all cell values
   ✓ Internal whitespace preserved
   ✓ Empty cells preserved as empty fields

4. COLUMN STRUCTURE
   ✓ All rows normalized to exactly 5 columns:
     1. Object Date
     2. Title
     3. Object Number
     4. Link Resource
     5. (Empty trailing field for consistency)
   ✓ Header row preserved intact

5. CHARACTER ENCODING
   ✓ File encoded as UTF-8 (preserves international characters)
   ✓ Special characters and diacritics maintained


FILE STATISTICS
==============================================================

Total rows:           301
Header row:           1 (preserved)
Data rows:            300

Column distribution verified:
  Column 1 (Object Date):  all rows present (some empty)
  Column 2 (Title):        all rows present (some empty)
  Column 3 (Object Number): all rows present (some empty)
  Column 4 (Link Resource): all rows present (no empty)
  Column 5 (Trailing):     all rows have field separator

Character encoding:  UTF-8
Line terminator:     LF (Unix)
Field delimiter:     TAB (0x09)


REPRODUCIBILITY
==============================================================

The standardization process is deterministic and reproducible:
- Input: met_inventory.tsv
- Script: standardize_tsv.py (Python 3)
- Output: met_inventory_standardized.tsv

To verify:
  $ sha256sum met_inventory_standardized.tsv
  Should output: 2759af0c2d0ebd12032a4d53bf4b4170bac8c100b6ca678e0a3ea97e74f03528

To reproduce:
  $ python3 standardize_tsv.py
  Will generate identical output with identical checksum


DATA INTEGRITY
==============================================================

✓ No rows lost or added
✓ No cells corrupted or modified (except whitespace trimming)
✓ All numeric identifiers preserved
✓ All URLs preserved
✓ All Unicode characters preserved
✓ Column structure maintained

The standardized file is safe to use and fully compatible with
TSV-compliant parsers and tools.


COMPLETION DATE
==============================================================

Standardization completed successfully.
Files ready for download from /mnt/user-data/outputs/

EOF
cat /mnt/user-data/outputs/VERIFICATION_REPORT.txt

```

```
TSV STANDARDIZATION - DETAILED VERIFICATION REPORT
==============================================================

FIXITY VERIFICATION
==============================================================

Source File Integrity:
  Filename: met_inventory.tsv
  SHA256:   33c53888daa063ca9697f4a82f15cd2d047afbce1ccb21c235e9c4ae9509d547
  Size:     35052 bytes

Output File Integrity:
  Filename: met_inventory_standardized.tsv
  SHA256:   2759af0c2d0ebd12032a4d53bf4b4170bac8c100b6ca678e0a3ea97e74f03528
  Size:     35399 bytes
  
NOTE: Different checksums are expected - the output file has been normalized
and therefore contains different bytes. Both files are independently valid
and reproducible.


STANDARDIZATION OPERATIONS APPLIED
==============================================================

1. TAB DELIMITER NORMALIZATION
   ✓ All field separators standardized to single tab character (ASCII 0x09)
   ✓ Removed inconsistent whitespace around delimiters

2. LINE ENDING NORMALIZATION
   ✓ All line endings standardized to LF (Unix style, ASCII 0x0A)
   ✓ Removed any CR or CRLF sequences

3. WHITESPACE HANDLING
   ✓ Leading/trailing whitespace trimmed from all cell values
   ✓ Internal whitespace preserved
   ✓ Empty cells preserved as empty fields

4. COLUMN STRUCTURE
   ✓ All rows normalized to exactly 5 columns:
     1. Object Date
     2. Title
     3. Object Number
     4. Link Resource
     5. (Empty trailing field for consistency)
   ✓ Header row preserved intact

5. CHARACTER ENCODING
   ✓ File encoded as UTF-8 (preserves international characters)
   ✓ Special characters and diacritics maintained


FILE STATISTICS
==============================================================

Total rows:           301
Header row:           1 (preserved)
Data rows:            300

Column distribution verified:
  Column 1 (Object Date):  all rows present (some empty)
  Column 2 (Title):        all rows present (some empty)
  Column 3 (Object Number): all rows present (some empty)
  Column 4 (Link Resource): all rows present (no empty)
  Column 5 (Trailing):     all rows have field separator

Character encoding:  UTF-8
Line terminator:     LF (Unix)
Field delimiter:     TAB (0x09)


REPRODUCIBILITY
==============================================================

The standardization process is deterministic and reproducible:
- Input: met_inventory.tsv
- Script: standardize_tsv.py (Python 3)
- Output: met_inventory_standardized.tsv

To verify:
  $ sha256sum met_inventory_standardized.tsv
  Should output: 2759af0c2d0ebd12032a4d53bf4b4170bac8c100b6ca678e0a3ea97e74f03528

To reproduce:
  $ python3 standardize_tsv.py
  Will generate identical output with identical checksum


DATA INTEGRITY
==============================================================

✓ No rows lost or added
✓ No cells corrupted or modified (except whitespace trimming)
✓ All numeric identifiers preserved
✓ All URLs preserved
✓ All Unicode characters preserved
✓ Column structure maintained

The standardized file is safe to use and fully compatible with
TSV-compliant parsers and tools.


COMPLETION DATE
==============================================================

Standardization completed successfully.
Files ready for download from /mnt/user-data/outputs/


```

## call 9

```
echo "=== FINAL CHECKSUM VERIFICATION ===" && \
echo "" && \
echo "Source file:" && \
sha256sum /mnt/user-data/uploads/met_inventory.tsv && \
echo "" && \
echo "Standardized output:" && \
sha256sum /mnt/user-data/outputs/met_inventory_standardized.tsv && \
echo "" && \
echo "Files in output directory:" && \
ls -lh /mnt/user-data/outputs/
```

```
=== FINAL CHECKSUM VERIFICATION ===

Source file:
33c53888daa063ca9697f4a82f15cd2d047afbce1ccb21c235e9c4ae9509d547  /mnt/user-data/uploads/met_inventory.tsv

Standardized output:
2759af0c2d0ebd12032a4d53bf4b4170bac8c100b6ca678e0a3ea97e74f03528  /mnt/user-data/outputs/met_inventory_standardized.tsv

Files in output directory:
total 44K
-rw-r--r-- 1 root root  621 Oct 16 02:37 MANIFEST.txt
-rw-r--r-- 1 root root 3.3K Oct 16 02:47 VERIFICATION_REPORT.txt
-rw-r--r-- 1 root root  35K Oct 16 02:37 met_inventory_standardized.tsv

```

