## call 3

```
cd /mnt/user-data/outputs && md5sum /mnt/user-data/met_inventory.tsv > met_inventory_original.md5
```

```

md5sum: /mnt/user-data/met_inventory.tsv: No such file or directory

```

## call 4

```
find /mnt -name "met_inventory*" -type f 2>/dev/null | head -20
```

```
/mnt/user-data/outputs/met_inventory_standardized.tsv
/mnt/user-data/outputs/met_inventory_original.md5
/mnt/user-data/uploads/met_inventory.tsv

```

## call 5

```
cd /mnt/user-data/outputs && md5sum /mnt/user-data/uploads/met_inventory.tsv > met_inventory_original.md5 && cat met_inventory_original.md5
```

```
6ec5bfc2d979ad12eb3343149beb8617  /mnt/user-data/uploads/met_inventory.tsv

```

