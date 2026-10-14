## call 2

```
mkdir -p /mnt/user-data/outputs
```

```
(no output, exit code 0)
```

## call 5

```
cd /mnt/user-data && find . -name "met_inventory.tsv" -o -name "*.tsv" | head -20
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
33c53888daa063ca9697f4a82f15cd2d047afbce1ccb21c235e9c4ae9509d547  /mnt/user-data/uploads/met_inventory.tsv

```

## call 8

```
cd /mnt/user-data/outputs && python3 transform_met_inventory.py
```

```

ERROR: Input file not found: /mnt/user-data/uploads/met_inventory.tsv

```

## call 9

```
ls -la /mnt/user-data/uploads/ 2>&1 || ls -la /mnt/user-data/ 2>&1 || find /mnt -name "met_inventory.tsv" 2>/dev/null
```

```
total 44
drwxr-xr-x 2 root root  4096 Oct 14 01:09 .
drwx------ 4 root root  4096 Oct 14 01:09 ..
-rw-r--r-- 1 root root 35052 Oct 14 01:09 met_inventory.tsv

```

## call 10

```
ls -la /mnt/user-data/
```

```
total 16
drwx------  4 root root 4096 Oct 14 01:09 .
drwxrwxrwt 14 root root 4096 Oct 14 01:11 ..
drwxr-xr-x  2 root root 4096 Oct 14 01:11 outputs
drwxr-xr-x  2 root root 4096 Oct 14 01:09 uploads

```

## call 12

```
cd /mnt/user-data/outputs && python3 transform_met_inventory.py
```

```
Processing: /mnt/user-data/uploads/met_inventory.tsv
======================================================================

Input File Checksum (SHA256):
  33c53888daa063ca9697f4a82f15cd2d047afbce1ccb21c235e9c4ae9509d547

Output File Checksum (SHA256):
  4de9017ec71e69ea80912339e5fcd00aa1027901aa9bb379649bb4733e76b347

Processing Statistics:
  Total Rows Processed: 300
  Rows with Missing Titles: 25
  Rows with Missing Dates: 11

Output File: /mnt/user-data/outputs/met_inventory_standardized.tsv
======================================================================

✓ Standardization complete!
  Input:  /mnt/user-data/uploads/met_inventory.tsv
  Output: /mnt/user-data/outputs/met_inventory_standardized.tsv

```

