## call 2

```
mkdir -p /mnt/user-data/outputs
```

```
(no output, exit code 0)
```

## call 5

```
cd /mnt/user-data/outputs && md5sum met_inventory.tsv > checksums.txt && cat checksums.txt
```

```

md5sum: met_inventory.tsv: No such file or directory

```

## call 6

```
find /mnt -name "met_inventory.tsv" -type f 2>/dev/null | head -5
```

```
(no output, exit code 0)
```

## call 7

```
ls -la /mnt/user-data/ 2>/dev/null || ls -la /root/ 2>/dev/null | head -20
```

```
total 16
drwx------  4 root root 4096 Oct 14 01:12 .
drwxrwxrwt 14 root root 4096 Oct 14 01:12 ..
drwxr-xr-x  2 root root 4096 Oct 14 01:14 outputs
drwxr-xr-x  2 root root 4096 Oct 14 01:12 uploads

```

## call 8

```
ls -la /mnt/user-data/uploads/
```

```
total 44
drwxr-xr-x 2 root root  4096 Oct 14 01:12 .
drwx------ 4 root root  4096 Oct 14 01:12 ..
-rw-r--r-- 1 root root 35052 Oct 14 01:12 met_inventory.tsv

```

## call 10

```
cd /mnt/user-data/outputs && python3 standardize_met_inventory.py
```

```
======================================================================
Met Inventory TSV Standardization Script
======================================================================

Step 1: Calculating input file checksum...

Traceback (most recent call last):
  File "/mnt/user-data/outputs/standardize_met_inventory.py", line 236, in <module>
    main()
    ~~~~^^
  File "/mnt/user-data/outputs/standardize_met_inventory.py", line 187, in main
    input_checksum = calculate_md5(INPUT_FILE)
  File "/mnt/user-data/outputs/standardize_met_inventory.py", line 32, in calculate_md5
    with open(file_path, 'rb') as f:
         ~~~~^^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: '/mnt/user-data/uploads/met_inventory.tsv'

```

## call 11

```
cp /mnt/user-data/uploads/met_inventory.tsv /mnt/user-data/outputs/met_inventory_input.tsv && ls -lh /mnt/user-data/outputs/
```

```
total 80K
-rw-r--r-- 1 root root    0 Oct 14 01:14 checksums.txt
-rw-r--r-- 1 root root  35K Oct 14 01:15 met_inventory_input.tsv
-rw-r--r-- 1 root root  35K Oct 14 01:14 met_inventory_standardized.tsv
-rw-r--r-- 1 root root 7.2K Oct 14 01:15 standardize_met_inventory.py

```

