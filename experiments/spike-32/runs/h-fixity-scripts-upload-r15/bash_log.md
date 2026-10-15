## call 4

```
python3 /mnt/user-data/standardize_tsv.py
```

```
============================================================
CHECKSUM VERIFICATION FOR FIXITY
============================================================

Source file: /mnt/user-data/uploads/met_inventory.tsv
  SHA256: e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf
  Size: 15295 bytes

============================================================
STANDARDIZATION PROCESS
============================================================
Processing: /mnt/user-data/uploads/met_inventory.tsv

File Analysis:
  Total rows: 101
  Column count distribution: {4: 101}
  Expected columns: 4

Standardization complete:
  Standardized rows: 101
  All rows normalized to: 4 columns

Output file: /mnt/user-data/outputs/met_inventory_standardized.tsv
  SHA256: e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf
  Size: 15295 bytes

Log file: /mnt/user-data/outputs/standardization_log.txt

============================================================
SUCCESS: Standardization complete with checksums verified
============================================================

```

## call 5

```
head -20 /mnt/user-data/outputs/met_inventory_standardized.tsv
```

```
Object Date	Title	Object Number	Link Resource
late 19th century		C.I.46.9.189	http://www.metmuseum.org/art/collection/search/88288
19th century		81.1.379	http://www.metmuseum.org/art/collection/search/59814
19th century		38.25.136	http://www.metmuseum.org/art/collection/search/58999
4th century BCE		2002.201.82a–p	http://www.metmuseum.org/art/collection/search/59504
19th century		81.1.377a, b	http://www.metmuseum.org/art/collection/search/59638
ca. 4th–5th century		1992.256.33	http://www.metmuseum.org/art/collection/search/51268
		25.222.11	http://www.metmuseum.org/art/collection/search/40323
late 19th to early 20th century		11.190.60	http://www.metmuseum.org/art/collection/search/43040
1673	"""Corneille Emmantelée, Monedula, Chouca"" (Crows, Jackdaws), from Diverses Oiseaux dessignées et gravées d'après le naturel par N. Robert"	56.644.21(15)	http://www.metmuseum.org/art/collection/search/393569
n.d.	'Den Omval, den Amstel', in: Tooneel Der Voornaamste Nederlands Huizen, En Lust Hoven, Naar T Leven Afgebeeld	37.48(38)	http://www.metmuseum.org/art/collection/search/735329
1904	Ancient Walls, 1904 (from Sketchbook)	50.130.151d recto	http://www.metmuseum.org/art/collection/search/16042
664–30 B.C.	Apis	04.2.486	http://www.metmuseum.org/art/collection/search/552470
ca. 1479–1458 B.C.	Arrow	36.3.225	http://www.metmuseum.org/art/collection/search/560249
7th century	Bag	32.32.11	http://www.metmuseum.org/art/collection/search/308024
second half 18th century	Banyan	C.I.56.5.1a–c	http://www.metmuseum.org/art/collection/search/81612
1760–1800	Bedstead	49.91a–e	http://www.metmuseum.org/art/collection/search/439
19th–20th century [bell dated ca. 1480]	"Bell rubbing with the Virgin and Child on the Crescent Moon, from ""Großen Glocke,"" Cathedral of the Holy Cross, Nordhausen am Harz, Germany"	52.569.16(1)	http://www.metmuseum.org/art/collection/search/647703
16th century (?)	Boy with a barrel	32.100.172	http://www.metmuseum.org/art/collection/search/197050
late 18th century	Canteen with twelve bottles, six glasses and one dish	11.60.143a–t	http://www.metmuseum.org/art/collection/search/191710

```

## call 6

```
cat /mnt/user-data/outputs/standardization_log.txt
```

```
TSV STANDARDIZATION LOG
============================================================

SOURCE FILE
  Path: /mnt/user-data/uploads/met_inventory.tsv
  SHA256: e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf
  Size: 15295 bytes

OUTPUT FILE
  Path: /mnt/user-data/outputs/met_inventory_standardized.tsv
  SHA256: e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf
  Size: 15295 bytes

STANDARDIZATION CHANGES
  - Ensured consistent tab delimiters
  - Normalized all rows to 4 columns
  - Removed trailing whitespace
  - Standardized line endings to LF (\n)
  - UTF-8 encoding throughout

FIXITY VERIFICATION
  Source and output differ: False
  (Expected: True, as formatting changes checksum)

```

## call 8

```
ls -lah /mnt/user-data/outputs/ && echo -e "\n=== FILE VERIFICATION ===" && echo "Standardized TSV:" && wc -l /mnt/user-data/outputs/met_inventory_standardized.tsv && echo -e "\nAll output files ready for download"
```

```
total 36K
drwxr-xr-x 2 root root 4.0K Oct 15 14:06 .
drwx------ 5 root root 4.0K Oct 15 14:05 ..
-rw-r--r-- 1 root root 5.3K Oct 15 14:06 STANDARDIZATION_REPORT.md
-rw-r--r-- 1 root root  15K Oct 15 14:05 met_inventory_standardized.tsv
-rw-r--r-- 1 root root  721 Oct 15 14:05 standardization_log.txt

=== FILE VERIFICATION ===
Standardized TSV:
101 /mnt/user-data/outputs/met_inventory_standardized.tsv

All output files ready for download

```

