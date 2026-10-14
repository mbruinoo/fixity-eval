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

