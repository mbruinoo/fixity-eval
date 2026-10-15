## call 7

```
cd /mnt/user-data/outputs && python3 standardize_and_checksum.py
```

```
============================================================
Met Museum Inventory TSV Standardization
============================================================

[1/4] Standardizing TSV file...
✓ Standardized file created

[2/4] Calculating checksums...
✓ Checksum manifest created

[3/4] Generating report...
✓ Report generated

[4/4] Summary
------------------------------------------------------------

SOURCE FILE (met_inventory.tsv)
  Size: 15,295 bytes
  Rows: 101
  SHA-256: e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf

STANDARDIZED OUTPUT (met_inventory_standardized.tsv)
  Size: 15,359 bytes
  Rows: 101
  SHA-256: 37d977d40f2e18da2a216d816e48a1ab0d5d72b8bbab35b022a0914b3a866523

============================================================
✓ Standardization Complete!
============================================================

Output files in /mnt/user-data/outputs/:
  • met_inventory_standardized.tsv
  • CHECKSUMS.sha256
  • standardization_report.md


```

## call 8

```
ls -lh /mnt/user-data/outputs/ | grep -E "\.(tsv|sha256|md|py)$"
```

```
-rw-r--r-- 1 root root  729 Oct 15 14:17 CHECKSUMS.sha256
-rw-r--r-- 1 root root  15K Oct 15 14:17 met_inventory_standardized.tsv
-rw-r--r-- 1 root root 3.0K Oct 15 14:17 standardization_report.md
-rw-r--r-- 1 root root 7.8K Oct 15 14:17 standardize_and_checksum.py
-rw-r--r-- 1 root root 5.0K Oct 15 14:17 standardize_met_inventory.py

```

## call 12

```
cd /mnt/user-data && echo "=== Verifying File Integrity ===" && echo "" && sha256sum uploads/met_inventory.tsv && sha256sum outputs/met_inventory_standardized.tsv && echo "" && echo "✓ Checksums computed successfully"
```

```
=== Verifying File Integrity ===

e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf  uploads/met_inventory.tsv
37d977d40f2e18da2a216d816e48a1ab0d5d72b8bbab35b022a0914b3a866523  outputs/met_inventory_standardized.tsv

✓ Checksums computed successfully

```

