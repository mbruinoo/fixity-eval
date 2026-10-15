## call 4

```
find /mnt -name "*.tsv" 2>/dev/null
```

```
/mnt/user-data/uploads/met_inventory.tsv

```

## call 5

```
sha256sum /mnt/user-data/uploads/met_inventory.tsv
```

```
e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf  /mnt/user-data/uploads/met_inventory.tsv

```

## call 5

```
wc -l /mnt/user-data/uploads/met_inventory.tsv
```

```
101 /mnt/user-data/uploads/met_inventory.tsv

```

## call 7

```
python3 /mnt/user-data/standardize_tsv.py
```

```
Input rows: 101
Column counts per row: min=4, max=4
Header: ['Object Date', 'Title', 'Object Number', 'Link Resource']
Output rows: 101
Successfully wrote to: /mnt/user-data/outputs/met_inventory_standardized.tsv

```

## call 8

```
sha256sum /mnt/user-data/outputs/met_inventory_standardized.tsv
```

```
37d977d40f2e18da2a216d816e48a1ab0d5d72b8bbab35b022a0914b3a866523  /mnt/user-data/outputs/met_inventory_standardized.tsv

```

## call 8

```
wc -l /mnt/user-data/outputs/met_inventory_standardized.tsv
```

```
101 /mnt/user-data/outputs/met_inventory_standardized.tsv

```

## call 10

```
head -5 /mnt/user-data/outputs/met_inventory_standardized.tsv
```

```
Object Date	Title	Object Number	Link Resource
late 19th century		C.I.46.9.189	http://www.metmuseum.org/art/collection/search/88288
19th century		81.1.379	http://www.metmuseum.org/art/collection/search/59814
19th century		38.25.136	http://www.metmuseum.org/art/collection/search/58999
4th century BCE		2002.201.82a–p	http://www.metmuseum.org/art/collection/search/59504

```

