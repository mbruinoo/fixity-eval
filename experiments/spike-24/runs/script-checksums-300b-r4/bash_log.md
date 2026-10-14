## call 2

```
mkdir -p /mnt/user-data/outputs
```

```
(no output, exit code 0)
```

## call 5

```
cd /mnt/user-data/outputs && ls -la
```

```
total 44
drwxr-xr-x 2 root root  4096 Oct 14 11:35 .
drwx------ 5 root root  4096 Oct 14 11:32 ..
-rw-r--r-- 1 root root 34879 Oct 14 11:35 met_inventory_standardized.tsv

```

## call 6

```
find /mnt -name "met_inventory.tsv" -type f 2>/dev/null
```

```
/mnt/user-data/uploads/met_inventory.tsv

```

## call 7

```
cp /mnt/user-data/uploads/met_inventory.tsv /mnt/user-data/outputs/met_inventory_original.tsv
```

```
(no output, exit code 0)
```

