## call 2

```
cd /mnt/user-data/uploads && ls -la
```

```
total 24
drwxr-xr-x 2 root root  4096 Oct 15 14:15 .
drwx------ 5 root root  4096 Oct 15 14:16 ..
-rw-r--r-- 1 root root 15295 Oct 15 14:15 met_inventory.tsv

```

## call 2

```
md5sum /mnt/user-data/uploads/met_inventory.tsv
```

```
023b98478ba290420a5194cca87b8a8a  /mnt/user-data/uploads/met_inventory.tsv

```

## call 2

```
sha256sum /mnt/user-data/uploads/met_inventory.tsv
```

```
e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf  /mnt/user-data/uploads/met_inventory.tsv

```

## call 4

```
python3 /mnt/user-data/standardize_tsv.py
```

```
======================================================================
TSV STANDARDIZATION REPORT
======================================================================
Input file:  /mnt/user-data/uploads/met_inventory.tsv
Output file: /mnt/user-data/outputs/met_inventory_standardized.tsv

Rows read:    101
Rows written: 101

No issues found!

======================================================================

```

## call 5

```
md5sum /mnt/user-data/outputs/met_inventory_standardized.tsv
```

```
023b98478ba290420a5194cca87b8a8a  /mnt/user-data/outputs/met_inventory_standardized.tsv

```

## call 5

```
sha256sum /mnt/user-data/outputs/met_inventory_standardized.tsv
```

```
e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf  /mnt/user-data/outputs/met_inventory_standardized.tsv

```

## call 5

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
ls -lh /mnt/user-data/outputs/
```

```
total 28K
-rw-r--r-- 1 root root 2.5K Oct 15 14:16 CHECKSUMS.txt
-rw-r--r-- 1 root root 4.2K Oct 15 14:16 STANDARDIZATION_REPORT.md
-rw-r--r-- 1 root root  15K Oct 15 14:16 met_inventory_standardized.tsv

```

## call 8

```
head -3 /mnt/user-data/outputs/met_inventory_standardized.tsv
```

```
Object Date	Title	Object Number	Link Resource
late 19th century		C.I.46.9.189	http://www.metmuseum.org/art/collection/search/88288
19th century		81.1.379	http://www.metmuseum.org/art/collection/search/59814

```

