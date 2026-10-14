## call 2

```
mkdir -p /mnt/user-data/outputs
```

```
(no output, exit code 0)
```

## call 5

```
cd /mnt/user-data/outputs && md5sum met_inventory.tsv > checksums.txt && cat checksums.txt
```

```

md5sum: met_inventory.tsv: No such file or directory

```

## call 6

```
find /mnt -name "met_inventory.tsv" -type f 2>/dev/null | head -5
```

```
(no output, exit code 0)
```

## call 7

```
ls -la /mnt/user-data/ 2>/dev/null || ls -la /root/ 2>/dev/null | head -20
```

```
total 16
drwx------  4 root root 4096 Oct 14 01:12 .
drwxrwxrwt 14 root root 4096 Oct 14 01:12 ..
drwxr-xr-x  2 root root 4096 Oct 14 01:14 outputs
drwxr-xr-x  2 root root 4096 Oct 14 01:12 uploads

```

## call 8

```
ls -la /mnt/user-data/uploads/
```

```
total 44
drwxr-xr-x 2 root root  4096 Oct 14 01:12 .
drwx------ 4 root root  4096 Oct 14 01:12 ..
-rw-r--r-- 1 root root 35052 Oct 14 01:12 met_inventory.tsv

```

