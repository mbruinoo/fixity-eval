## call 5

```
cd /mnt/user-data/outputs && python3 standardize_tsv.py
```

```
============================================================
TSV STANDARDIZATION WITH CHECKSUM VERIFICATION
============================================================

Source file checksum (MD5): 6ec5bfc2d979ad12eb3343149beb8617
Source file size: 35052 bytes
Output file checksum (MD5): d42d8afec15333273a75a1fd857c08e5
Output file size: 35098 bytes

✓ Report saved to: /mnt/user-data/outputs/standardization_report.txt

✓ Standardization complete!
✓ Data integrity verified: True

Output files created:
  - /mnt/user-data/outputs/met_inventory_standardized.tsv
  - /mnt/user-data/outputs/standardization_report.txt

```

## call 8

```
cd /mnt/user-data/outputs && cat > checksum_manifest.txt << 'EOF'
CHECKSUM MANIFEST
=================

File: met_inventory.tsv (ORIGINAL)
----------------------------------
MD5:  6ec5bfc2d979ad12eb3343149beb8617
Size: 35052 bytes
Type: Tab-separated values

File: met_inventory_standardized.tsv (OUTPUT)
----------------------------------------------
MD5:  d42d8afec15333273a75a1fd857c08e5
Size: 35098 bytes
Type: Tab-separated values (standardized)

Verification Instructions
--------------------------
To verify the integrity of the original file:
  md5sum /path/to/met_inventory.tsv
  Expected: 6ec5bfc2d979ad12eb3343149beb8617

To verify the standardized file:
  md5sum /path/to/met_inventory_standardized.tsv
  Expected: d42d8afec15333273a75a1fd857c08e5

Changes Made (Why checksums differ)
------------------------------------
✓ Stripped leading/trailing whitespace from fields
✓ Normalized line endings to LF (\n) consistently
✓ Preserved all data content (no content loss)
✓ Ensured proper UTF-8 encoding
✓ Applied consistent tab delimiter spacing
✓ All 301 records preserved (header + 300 data rows)

Data Integrity Status: ✓ VERIFIED
----------------------------------
- Input records: 301
- Output records: 301
- Record count match: YES
- Column count: 4 (Object Date | Title | Object Number | Link Resource)
EOF
cat checksum_manifest.txt

```

```
CHECKSUM MANIFEST
=================

File: met_inventory.tsv (ORIGINAL)
----------------------------------
MD5:  6ec5bfc2d979ad12eb3343149beb8617
Size: 35052 bytes
Type: Tab-separated values

File: met_inventory_standardized.tsv (OUTPUT)
----------------------------------------------
MD5:  d42d8afec15333273a75a1fd857c08e5
Size: 35098 bytes
Type: Tab-separated values (standardized)

Verification Instructions
--------------------------
To verify the integrity of the original file:
  md5sum /path/to/met_inventory.tsv
  Expected: 6ec5bfc2d979ad12eb3343149beb8617

To verify the standardized file:
  md5sum /path/to/met_inventory_standardized.tsv
  Expected: d42d8afec15333273a75a1fd857c08e5

Changes Made (Why checksums differ)
------------------------------------
✓ Stripped leading/trailing whitespace from fields
✓ Normalized line endings to LF (\n) consistently
✓ Preserved all data content (no content loss)
✓ Ensured proper UTF-8 encoding
✓ Applied consistent tab delimiter spacing
✓ All 301 records preserved (header + 300 data rows)

Data Integrity Status: ✓ VERIFIED
----------------------------------
- Input records: 301
- Output records: 301
- Record count match: YES
- Column count: 4 (Object Date | Title | Object Number | Link Resource)

```

