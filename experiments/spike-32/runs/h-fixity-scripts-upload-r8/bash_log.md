## call 5

```
cd /mnt/user-data && python3 standardize_tsv.py
```

```
======================================================================
TSV STANDARDIZATION WITH FIXITY VERIFICATION
======================================================================

Source file: /mnt/user-data/uploads/met_inventory.tsv
  File size: 15,295 bytes
  SHA256:    e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf

Standardization operations:
  ✓ Stripped leading/trailing whitespace from cells
  ✓ Normalized line endings to LF (Unix)
  ✓ Ensured consistent tab-delimited format
  ✓ Preserved all data integrity

Processed: 101 rows

Output file: /mnt/user-data/outputs/met_inventory_standardized.tsv
  File size: 15,295 bytes
  SHA256:    e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf

======================================================================
FIXITY RECORD
======================================================================
Input:  e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf (15,295 bytes)
Output: e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf (15,295 bytes)

Checksum manifest saved to: /mnt/user-data/outputs/CHECKSUMS.txt


```

## call 6

```
ls -lah /mnt/user-data/outputs/ && echo -e "\n---\n" && head -20 /mnt/user-data/outputs/met_inventory_standardized.tsv && echo -e "\n...\n"
```

```
total 28K
drwxr-xr-x 2 root root 4.0K Oct 15 13:14 .
drwx------ 5 root root 4.0K Oct 15 13:14 ..
-rw-r--r-- 1 root root  562 Oct 15 13:14 CHECKSUMS.txt
-rw-r--r-- 1 root root  15K Oct 15 13:14 met_inventory_standardized.tsv

---

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

...


```

