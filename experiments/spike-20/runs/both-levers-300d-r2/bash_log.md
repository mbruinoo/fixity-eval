## call 3

```
cd /mnt/user-data/outputs && md5sum /mnt/user-data/met_inventory.tsv
```

```

md5sum: /mnt/user-data/met_inventory.tsv: No such file or directory

```

## call 4

```
find /mnt -name "met_inventory.tsv" 2>/dev/null
```

```
/mnt/user-data/uploads/met_inventory.tsv

```

## call 5

```
md5sum /mnt/user-data/uploads/met_inventory.tsv && sha256sum /mnt/user-data/uploads/met_inventory.tsv
```

```
098392f08012bb5d5d87731e80800f42  /mnt/user-data/uploads/met_inventory.tsv
5eb3a8afc4d1e5f20382fef7a6bd3d4bc38d58080b3f621d847087ac1451566e  /mnt/user-data/uploads/met_inventory.tsv

```

