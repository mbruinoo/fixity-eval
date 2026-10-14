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

