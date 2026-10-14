## call 1

```
cd /mnt/user-data/outputs && head -50 <<'EOF'
Object Date	Title	Object Number	Link Resource
EOF

```

```
Object Date	Title	Object Number	Link Resource

```

## call 4

```
cd /mnt/user-data && find . -name "*.tsv" -o -name "*inventory*" | head -20
```

```
./outputs/met_inventory_standardized.tsv
./uploads/met_inventory.tsv

```

## call 5

```
cd /mnt/user-data && sha256sum uploads/met_inventory.tsv && md5sum uploads/met_inventory.tsv
```

```
33c53888daa063ca9697f4a82f15cd2d047afbce1ccb21c235e9c4ae9509d547  uploads/met_inventory.tsv
6ec5bfc2d979ad12eb3343149beb8617  uploads/met_inventory.tsv

```

## call 7

```
cd /mnt/user-data/outputs && python3 standardize_met_inventory.py
```

```
Starting Met Museum Inventory Standardization

Calculating checksums for input file: /mnt/user-data/uploads/met_inventory.tsv

Traceback (most recent call last):
  File "/mnt/user-data/outputs/standardize_met_inventory.py", line 271, in <module>
    input_checksums, output_checksums, rows_processed = process_inventory(input_file, output_file)
                                                        ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/user-data/outputs/standardize_met_inventory.py", line 144, in process_inventory
    input_checksums = calculate_checksums(input_file)
  File "/mnt/user-data/outputs/standardize_met_inventory.py", line 27, in calculate_checksums
    with open(filepath, 'rb') as f:
         ~~~~^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: '/mnt/user-data/uploads/met_inventory.tsv'

```

## call 8

```
find /mnt -name "met_inventory.tsv" -type f 2>/dev/null
```

```
(no output, exit code 0)
```

## call 9

```
ls -la /mnt/user-data/ && echo "---" && find /mnt -type d -name "uploads" 2>/dev/null
```

```
total 16
drwx------  4 root root 4096 Oct 14 01:15 .
drwxrwxrwt 14 root root 4096 Oct 14 01:18 ..
drwxr-xr-x  2 root root 4096 Oct 14 01:18 outputs
drwxr-xr-x  2 root root 4096 Oct 14 01:15 uploads
---
/mnt/user-data/uploads

```

## call 10

```
ls -la /mnt/user-data/uploads/
```

```
total 44
drwxr-xr-x 2 root root  4096 Oct 14 01:15 .
drwx------ 4 root root  4096 Oct 14 01:15 ..
-rw-r--r-- 1 root root 35052 Oct 14 01:15 met_inventory.tsv

```

## call 11

```
cd /mnt/user-data && python3 /mnt/user-data/outputs/standardize_met_inventory.py
```

```
Starting Met Museum Inventory Standardization

Calculating checksums for input file: /mnt/user-data/uploads/met_inventory.tsv

Traceback (most recent call last):
  File "/mnt/user-data/outputs/standardize_met_inventory.py", line 271, in <module>
    input_checksums, output_checksums, rows_processed = process_inventory(input_file, output_file)
                                                        ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/user-data/outputs/standardize_met_inventory.py", line 144, in process_inventory
    input_checksums = calculate_checksums(input_file)
  File "/mnt/user-data/outputs/standardize_met_inventory.py", line 27, in calculate_checksums
    with open(filepath, 'rb') as f:
         ~~~~^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: '/mnt/user-data/uploads/met_inventory.tsv'

```

