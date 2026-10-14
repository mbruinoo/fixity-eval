## call 4

```
cd /mnt/user-data/outputs && md5sum /mnt/user-data/met_inventory.tsv
```

```

md5sum: /mnt/user-data/met_inventory.tsv: No such file or directory

```

## call 5

```
find /mnt -name "met_inventory*" -type f 2>/dev/null
```

```
/mnt/user-data/outputs/met_inventory_standardized.tsv
/mnt/user-data/uploads/met_inventory.tsv

```

## call 6

```
md5sum /mnt/user-data/uploads/met_inventory.tsv
```

```
098392f08012bb5d5d87731e80800f42  /mnt/user-data/uploads/met_inventory.tsv

```

## call 8

```
cd /mnt/user-data/outputs && python3 standardize_met_inventory.py /mnt/user-data/uploads/met_inventory.tsv met_inventory_standardized.tsv
```

```
Original file MD5: 098392f08012bb5d5d87731e80800f42
Output file MD5: 9b5fa1f67e092f5f54bcbba16f10f855

Standardization complete!
Input file:  /mnt/user-data/uploads/met_inventory.tsv
Output file: met_inventory_standardized.tsv
Rows processed: 100

Checksum verification:
  Original: 098392f08012bb5d5d87731e80800f42
  Output:   9b5fa1f67e092f5f54bcbba16f10f855

```

