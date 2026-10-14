## call 2

```
mkdir -p /mnt/user-data/outputs
```

```
(no output, exit code 0)
```

## call 5

```
cd /mnt/user-data && find . -name "*.tsv" -type f
```

```
./outputs/met_inventory_standardized.tsv
./uploads/met_inventory.tsv

```

## call 6

```
sha256sum /mnt/user-data/uploads/met_inventory.tsv
```

```
5eb3a8afc4d1e5f20382fef7a6bd3d4bc38d58080b3f621d847087ac1451566e  /mnt/user-data/uploads/met_inventory.tsv

```

## call 8

```
cd /mnt/user-data/outputs && python3 standardize_met_inventory.py
```

```
Input file checksum (SHA-256): 5eb3a8afc4d1e5f20382fef7a6bd3d4bc38d58080b3f621d847087ac1451566e
Input file: /mnt/user-data/uploads/met_inventory.tsv
Output file: /mnt/user-data/outputs/met_inventory_standardized.tsv

Output file checksum (SHA-256): 8846c08673b4b058fdf9a0add6f879d446c60bb772ddb327d7a3ac9e9e586c27

✓ Transformation complete
✓ Rows processed: 101
✓ Processing timestamp: 2026-10-14T01:26:47.799236

```

## call 9

```
cp /mnt/user-data/uploads/met_inventory.tsv /mnt/user-data/outputs/met_inventory_original.tsv
```

```
(no output, exit code 0)
```

## call 12

```
cd /mnt/user-data/outputs && ls -lh *.tsv *.py *.txt *.md 2>/dev/null && echo "" && echo "=== FILE CHECKSUMS ===" && sha256sum *.tsv *.py *.txt *.md
```

```
-rw-r--r-- 1 root root 5.2K Oct 14 01:27 FIXITY_VERIFICATION.txt
-rw-r--r-- 1 root root 4.2K Oct 14 01:27 README.md
-rw-r--r-- 1 root root  11K Oct 14 01:26 met_inventory_original.tsv
-rw-r--r-- 1 root root  11K Oct 14 01:26 met_inventory_standardized.tsv
-rw-r--r-- 1 root root 3.9K Oct 14 01:26 standardize_met_inventory.py

=== FILE CHECKSUMS ===
5eb3a8afc4d1e5f20382fef7a6bd3d4bc38d58080b3f621d847087ac1451566e  met_inventory_original.tsv
8846c08673b4b058fdf9a0add6f879d446c60bb772ddb327d7a3ac9e9e586c27  met_inventory_standardized.tsv
b0e352e9afe8cb049cbbae05f90ef9d883e4a785a7bd87850107f26110f6b287  standardize_met_inventory.py
0c25e0bbdf083da18d8d9a8fbae9aaaba167fcb347210ca7ac9da3d1e2e8cee6  FIXITY_VERIFICATION.txt
8883c60bc16671269d9d2b62b052f19c9161bafa16af105fa5e53dccbb5d4779  README.md

```

