## call 5

```
cd /mnt/user-data/outputs && python3 standardize_tsv.py
```

```
Calculating source file checksums...
Source file: /mnt/user-data/uploads/met_inventory.tsv
  SHA256: e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf
  SHA512: e3c240d7bf8042bd0e61894d34747a071e4dda58eec1406424a2ef81f9c61c0e2821d15b710e436313000cd223613e1222f91323476aedca41a0aab5233a63e4
  MD5:    023b98478ba290420a5194cca87b8a8a

Standardizing TSV file...
Output file: /mnt/user-data/outputs/met_inventory_standardized.tsv

Calculating output file checksums...
Output file: /mnt/user-data/outputs/met_inventory_standardized.tsv
  SHA256: e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf
  SHA512: e3c240d7bf8042bd0e61894d34747a071e4dda58eec1406424a2ef81f9c61c0e2821d15b710e436313000cd223613e1222f91323476aedca41a0aab5233a63e4
  MD5:    023b98478ba290420a5194cca87b8a8a

Checksum file written to: /mnt/user-data/outputs/checksums.txt

## INTEGRITY VERIFICATION
Source rows:  101
Output rows:  101
Rows match:   ✓ YES

```

## call 8

```
ls -lh /mnt/user-data/outputs/ && echo -e "\n--- Output File Sample ---" && head -5 /mnt/user-data/outputs/met_inventory_standardized.tsv
```

```
total 36K
-rw-r--r-- 1 root root 5.5K Oct 15 14:16 STANDARDIZATION_REPORT.md
-rw-r--r-- 1 root root  952 Oct 15 14:15 checksums.txt
-rw-r--r-- 1 root root  15K Oct 15 14:15 met_inventory_standardized.tsv
-rw-r--r-- 1 root root 4.3K Oct 15 14:15 standardize_tsv.py

--- Output File Sample ---
Object Date	Title	Object Number	Link Resource
late 19th century		C.I.46.9.189	http://www.metmuseum.org/art/collection/search/88288
19th century		81.1.379	http://www.metmuseum.org/art/collection/search/59814
19th century		38.25.136	http://www.metmuseum.org/art/collection/search/58999
4th century BCE		2002.201.82a–p	http://www.metmuseum.org/art/collection/search/59504

```

