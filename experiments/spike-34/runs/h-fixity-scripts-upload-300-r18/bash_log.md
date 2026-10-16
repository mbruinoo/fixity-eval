## call 5

```
cd /mnt/user-data/outputs && python3 standardize_met_inventory.py
```

```
Standardization complete!

Source file checksums:
  SHA-256: 1f487d12804e5cbd285ff6cf9f1d560595731455546be9230f887b7611e7860e
  MD5:     1c2323177f9fb869f2df32f5cb85e7a6

Output file checksums:
  SHA-256: d29688f6cfe8b8821f88dc78fff57bd32bf3555fb3a43cf7a4315f4143ea4853
  MD5:     40a44e788343362f9b0ba4a619480414

Total rows processed: 300

Files created:
  - met_inventory_standardized.tsv
  - fixity_report.json
  - README.md

```

## call 6

```
cd /mnt/user-data/outputs && head -20 met_inventory_standardized.tsv && echo "..." && wc -l met_inventory_standardized.tsv
```

```
Object Date	Title	Object Number	Link Resource
7th–9th century		2002.556.36	http://www.metmuseum.org/art/collection/search/65194
		02.18.509	http://www.metmuseum.org/art/collection/search/43906
19th century		93.1.168	http://www.metmuseum.org/art/collection/search/47519
late 19th to early 20th century		16.144.46	http://www.metmuseum.org/art/collection/search/42843
		CP148	http://www.metmuseum.org/art/collection/search/63476
19th century		2007.49.286	http://www.metmuseum.org/art/collection/search/73641
18th–19th century		28.186.45	http://www.metmuseum.org/art/collection/search/60748
1782, 2nd edition		CP311	http://www.metmuseum.org/art/collection/search/63677
18th–19th century		96.14.594	http://www.metmuseum.org/art/collection/search/66318
		1994.605.95	http://www.metmuseum.org/art/collection/search/44395
		20.148.231	http://www.metmuseum.org/art/collection/search/71220
		46.63.6	http://www.metmuseum.org/art/collection/search/53578
7th century		1989.150	http://www.metmuseum.org/art/collection/search/38250
19th century		42.91.22	http://www.metmuseum.org/art/collection/search/69230
3rd–2nd century BCE		2002.201.111, .112	http://www.metmuseum.org/art/collection/search/59523
		CP157	http://www.metmuseum.org/art/collection/search/63485
18th century		14.40.872a–c	http://www.metmuseum.org/art/collection/search/57947
19th century		09.50.3409	http://www.metmuseum.org/art/collection/search/68043
second half of 19th century		36.100.156a, b	http://www.metmuseum.org/art/collection/search/58338
...
301 met_inventory_standardized.tsv

```

## call 9

```
cd /mnt/user-data/outputs && sha256sum met_inventory_standardized.tsv && md5sum met_inventory_standardized.tsv && echo && echo "Tail of file (last 10 rows):" && tail -10 met_inventory_standardized.tsv
```

```
d29688f6cfe8b8821f88dc78fff57bd32bf3555fb3a43cf7a4315f4143ea4853  met_inventory_standardized.tsv
40a44e788343362f9b0ba4a619480414  met_inventory_standardized.tsv

Tail of file (last 10 rows):
ca. 1929	Yakima Canutt in Arrow Pictures from Western Stars or Scenes Exhibit Cards series (W412)	63.350.613.412.149	http://www.metmuseum.org/art/collection/search/773052
5th century BCE	东周 玉璜|Arc-shaped pendant (Huang)	2009.92	http://www.metmuseum.org/art/collection/search/75285
20th century	擦條|Sand-file for carving jade	1981.296.18	http://www.metmuseum.org/art/collection/search/62070
datable to 1506–10	明　文徵明　致丈人吳愈書　冊頁|Letter to the artist's father-in-law, Wu Yu	1989.363.59	http://www.metmuseum.org/art/collection/search/45775
1950s	棟方志功筆　蒼赫二童子図|Red and Blue, Two Attendants	2018.853.35	http://www.metmuseum.org/art/collection/search/816263
19th century	清 緙絲乾隆南巡宮苑圖|Scenic Sites in the Qianlong Emperor's Southern Inspection Tour	13.220.134	http://www.metmuseum.org/art/collection/search/68288
1838	蝉小川|The Cicada Stream (Semi no Ogawa)  蝉小川	2013.787a–c	http://www.metmuseum.org/art/collection/search/78689
1840	蹄斎北馬筆　五美人図|Five Beauties	2015.500.9.12	http://www.metmuseum.org/art/collection/search/667347
dated 1978	近代  應野平  破墨山水  扇面|Broken-ink Landscape	1986.267.410	http://www.metmuseum.org/art/collection/search/36399
dated 1978	近代  程十髮  雜畫  冊頁十四開|Various Subjects	1986.267.435a–p	http://www.metmuseum.org/art/collection/search/36421

```

## call 10

```
cd /mnt/user-data/outputs && ls -lh met_inventory* fixity* README* && echo && echo "=== FIXITY PRESERVATION SUMMARY ===" && echo && cat fixity_report.json | python3 -m json.tool
```

```
-rw-r--r-- 1 root root 1.4K Oct 16 02:37 README.md
-rw-r--r-- 1 root root  798 Oct 16 02:37 fixity_report.json
-rw-r--r-- 1 root root  35K Oct 16 02:37 met_inventory_source.txt
-rw-r--r-- 1 root root  35K Oct 16 02:37 met_inventory_standardized.tsv

=== FIXITY PRESERVATION SUMMARY ===

{
    "timestamp": "2026-10-16T02:37:59.425630",
    "source": {
        "filename": "met_inventory_source.txt",
        "sha256": "1f487d12804e5cbd285ff6cf9f1d560595731455546be9230f887b7611e7860e",
        "md5": "1c2323177f9fb869f2df32f5cb85e7a6"
    },
    "output": {
        "filename": "met_inventory_standardized.tsv",
        "sha256": "d29688f6cfe8b8821f88dc78fff57bd32bf3555fb3a43cf7a4315f4143ea4853",
        "md5": "40a44e788343362f9b0ba4a619480414",
        "rows": 300,
        "columns": 4
    },
    "standardization_actions": [
        "Removed duplicate/empty header rows",
        "Ensured 4 columns (Object Date, Title, Object Number, Link Resource)",
        "Normalized line endings to LF",
        "Stripped trailing whitespace from fields",
        "Used UTF-8 encoding throughout",
        "Applied minimal CSV quoting (QUOTE_MINIMAL)"
    ]
}

```

