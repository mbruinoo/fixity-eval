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

