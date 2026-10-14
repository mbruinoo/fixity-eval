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

