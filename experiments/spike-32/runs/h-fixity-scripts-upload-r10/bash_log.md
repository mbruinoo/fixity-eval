## call 6

```
cd /mnt/user-data/outputs && python3 checksum_source.py
```

```
Source file: /mnt/user-data/uploads/met_inventory.tsv
SHA-256 Checksum: e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf

```

## call 6

```
cd /mnt/user-data/outputs && python3 standardize_tsv.py
```

```
Source file checksum (SHA-256): e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf

Header: ['Object Date', 'Title', 'Object Number', 'Link Resource']
Expected columns: 4

No standardization issues found.

Standardized 100 data rows (plus header)

Output file checksum (SHA-256): 6dacf89c79b4322e0a21c34c379671ec614bbd5501a20729ac72d8e806f629dd

Checksum report saved to checksums.txt

```

## call 7

```
cat /mnt/user-data/outputs/checksums.txt
```

```
Metropolitan Museum Inventory TSV - Checksum Report
============================================================

Source file: met_inventory.tsv
Source checksum (SHA-256): e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf

Output file: met_inventory_standardized.tsv
Output checksum (SHA-256): 6dacf89c79b4322e0a21c34c379671ec614bbd5501a20729ac72d8e806f629dd

Files differ: True

```

## call 8

```
head -20 /mnt/user-data/outputs/met_inventory_standardized.tsv | cat -A
```

```
Object Date^ITitle^IObject Number^ILink Resource$
late 19th century^I^IC.I.46.9.189^Ihttp://www.metmuseum.org/art/collection/search/88288$
19th century^I^I81.1.379^Ihttp://www.metmuseum.org/art/collection/search/59814$
19th century^I^I38.25.136^Ihttp://www.metmuseum.org/art/collection/search/58999$
4th century BCE^I^I2002.201.82aM-bM-^@M-^Sp^Ihttp://www.metmuseum.org/art/collection/search/59504$
19th century^I^I81.1.377a, b^Ihttp://www.metmuseum.org/art/collection/search/59638$
ca. 4thM-bM-^@M-^S5th century^I^I1992.256.33^Ihttp://www.metmuseum.org/art/collection/search/51268$
^I^I25.222.11^Ihttp://www.metmuseum.org/art/collection/search/40323$
late 19th to early 20th century^I^I11.190.60^Ihttp://www.metmuseum.org/art/collection/search/43040$
1673^I\"\"\"Corneille EmmantelM-CM-)e, Monedula, Chouca\"\" (Crows, Jackdaws), from Diverses Oiseaux dessignM-CM-)es et gravM-CM-)es d'aprM-CM-(s le naturel par N. Robert\"^I56.644.21(15)^Ihttp://www.metmuseum.org/art/collection/search/393569$
n.d.^I'Den Omval, den Amstel', in: Tooneel Der Voornaamste Nederlands Huizen, En Lust Hoven, Naar T Leven Afgebeeld^I37.48(38)^Ihttp://www.metmuseum.org/art/collection/search/735329$
1904^IAncient Walls, 1904 (from Sketchbook)^I50.130.151d recto^Ihttp://www.metmuseum.org/art/collection/search/16042$
664M-bM-^@M-^S30 B.C.^IApis^I04.2.486^Ihttp://www.metmuseum.org/art/collection/search/552470$
ca. 1479M-bM-^@M-^S1458 B.C.^IArrow^I36.3.225^Ihttp://www.metmuseum.org/art/collection/search/560249$
7th century^IBag^I32.32.11^Ihttp://www.metmuseum.org/art/collection/search/308024$
second half 18th century^IBanyan^IC.I.56.5.1aM-bM-^@M-^Sc^Ihttp://www.metmuseum.org/art/collection/search/81612$
1760M-bM-^@M-^S1800^IBedstead^I49.91aM-bM-^@M-^Se^Ihttp://www.metmuseum.org/art/collection/search/439$
19thM-bM-^@M-^S20th century [bell dated ca. 1480]^I\"Bell rubbing with the Virgin and Child on the Crescent Moon, from \"\"GroM-CM-^_en Glocke,\"\" Cathedral of the Holy Cross, Nordhausen am Harz, Germany\"^I52.569.16(1)^Ihttp://www.metmuseum.org/art/collection/search/647703$
16th century (?)^IBoy with a barrel^I32.100.172^Ihttp://www.metmuseum.org/art/collection/search/197050$
late 18th century^ICanteen with twelve bottles, six glasses and one dish^I11.60.143aM-bM-^@M-^St^Ihttp://www.metmuseum.org/art/collection/search/191710$

```

## call 10

```
wc -l /mnt/user-data/outputs/met_inventory_standardized.tsv && echo "---" && tail -5 /mnt/user-data/outputs/met_inventory_standardized.tsv
```

```
101 /mnt/user-data/outputs/met_inventory_standardized.tsv
---
second half of the 19th century	蝶秋草蒔絵短冊箱|Box for Paper (Ryōshibako) with Decoration of Butterflies and Autumn Grasses	14.40.883a–c	http://www.metmuseum.org/art/collection/search/57951
	装身具|Body ornament	1975.268.331	http://www.metmuseum.org/art/collection/search/62312
	装身具|Body ornament	1975.268.277	http://www.metmuseum.org/art/collection/search/62258
ca. 1832	諸國瀧廻リ　木曽路ノ奥 阿彌陀ヶ瀧|The Amida Falls in the Far Reaches of the Kisokaidō Road (Kisoji no oku Amida-ga-taki), from the series A Tour of Waterfalls in Various Provinces (Shokoku taki meguri)	JP2928	http://www.metmuseum.org/art/collection/search/56143
early 20th century	해강  김규진  묵란도|海岡   金圭鎭   墨蘭圖|Orchids in Hanging Basket	2015.300.300	http://www.metmuseum.org/art/collection/search/72471

```

## call 12

```
ls -lh /mnt/user-data/outputs/ | grep -v "^total"
```

```
-rw-r--r-- 1 root root 5.3K Oct 15 13:15 STANDARDIZATION_REPORT.md
-rw-r--r-- 1 root root 3.6K Oct 15 13:15 VERIFICATION_SUMMARY.txt
-rw-r--r-- 1 root root  814 Oct 15 13:14 checksum_source.py
-rw-r--r-- 1 root root  394 Oct 15 13:15 checksums.txt
-rw-r--r-- 1 root root  15K Oct 15 13:15 met_inventory_standardized.tsv
-rw-r--r-- 1 root root   98 Oct 15 13:15 source_checksum.txt
-rw-r--r-- 1 root root 3.8K Oct 15 13:14 standardize_tsv.py

```

## call 14

```
cat /mnt/user-data/outputs/checksums.txt && echo "" && echo "=== FINAL FILE MANIFEST ===" && ls -1 /mnt/user-data/outputs/ | sort
```

```
Metropolitan Museum Inventory TSV - Checksum Report
============================================================

Source file: met_inventory.tsv
Source checksum (SHA-256): e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf

Output file: met_inventory_standardized.tsv
Output checksum (SHA-256): 6dacf89c79b4322e0a21c34c379671ec614bbd5501a20729ac72d8e806f629dd

Files differ: True

=== FINAL FILE MANIFEST ===
README.md
STANDARDIZATION_REPORT.md
VERIFICATION_SUMMARY.txt
checksum_source.py
checksums.txt
met_inventory_standardized.tsv
source_checksum.txt
standardize_tsv.py

```

