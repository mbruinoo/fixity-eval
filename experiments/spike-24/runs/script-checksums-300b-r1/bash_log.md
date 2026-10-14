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
drwxr-xr-x 2 root root  4096 Oct 14 02:59 .
drwx------ 5 root root  4096 Oct 14 02:56 ..
-rw-r--r-- 1 root root 34514 Oct 14 02:59 met_inventory_standardized.tsv

```

## call 6

```
find /tmp -name "*met*" -o -name "*.tsv" 2>/dev/null | head -20
```

```
(no output, exit code 0)
```

