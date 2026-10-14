## call 2

```
mkdir -p /mnt/user-data/outputs
```

```
(no output, exit code 0)
```

## call 5

```
find /mnt/user-data -name "*.tsv" -type f 2>/dev/null
```

```
/mnt/user-data/outputs/met_inventory_standardized.tsv
/mnt/user-data/uploads/met_inventory.tsv

```

## call 6

```
cp /mnt/user-data/uploads/met_inventory.tsv /mnt/user-data/outputs/met_inventory_original.tsv && md5sum /mnt/user-data/outputs/met_inventory_original.tsv
```

```
6ec5bfc2d979ad12eb3343149beb8617  /mnt/user-data/outputs/met_inventory_original.tsv

```

## call 8

```
cd /mnt/user-data/outputs && python3 standardize_met_inventory.py met_inventory_original.tsv met_inventory_standardized_new.tsv
```

```
======================================================================
Met Museum Inventory TSV Standardization
======================================================================

Input file: met_inventory_original.tsv
Input checksum (MD5): 6ec5bfc2d979ad12eb3343149beb8617

Original headers: ['Object Date', 'Title', 'Object Number', 'Link Resource']
Standardized headers: ['Object_Date', 'Title', 'Object_Number', 'Link_Resource']

Output file: met_inventory_standardized_new.tsv
Output checksum (MD5): c4ab743f4175c8362ad6da1fe9d8ff6d

======================================================================
Transformation Summary
======================================================================
Total rows read (including header): 301
Data rows transformed: 300
Input file size: 35052 bytes
Output file size: 35022 bytes
Files are different: True
======================================================================

```

