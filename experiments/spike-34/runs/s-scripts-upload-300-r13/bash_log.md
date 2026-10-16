## call 2

```
head -20 /mnt/user-data/uploads/met_inventory.tsv
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

```

## call 3

```
wc -l /mnt/user-data/uploads/met_inventory.tsv && tail -20 /mnt/user-data/uploads/met_inventory.tsv
```

```
301 /mnt/user-data/uploads/met_inventory.tsv
1644	Venus, from 'Game of Mythology' (Jeu de la Mythologie)	2012.136.811.12	http://www.metmuseum.org/art/collection/search/412356
1802	View of the Gate of St. Denis, taken from the Suburbs	24.46.10	http://www.metmuseum.org/art/collection/search/821817
ca. 1641	Virgin and Christ Child	17.50.17-297	http://www.metmuseum.org/art/collection/search/373773
1933	Volume 3: progressive proofs for plates 17-24 for Charlot's 'Picture Book'	34.80(3)	http://www.metmuseum.org/art/collection/search/713159
1760–70	Waistcoat	2009.300.2855	http://www.metmuseum.org/art/collection/search/157726
1855–65	Walking boots	2009.300.5484a, b	http://www.metmuseum.org/art/collection/search/169699
17th–18th century	Watch cock	13.173.123	http://www.metmuseum.org/art/collection/search/192463
third quarter 17th century	Wedding knife, fork and sheath	64.101.1595–.1597	http://www.metmuseum.org/art/collection/search/210073
early 20th century	White Bearded Gnu, collector card from the Animals series (D9), issued by the Weber Baking Company to promote Onist Milk and Pullman Bread	63.350.307.9.29	http://www.metmuseum.org/art/collection/search/680219
17th century	Window	93.26.14	http://www.metmuseum.org/art/collection/search/453572
ca. 1929	Yakima Canutt in Arrow Pictures from Western Stars or Scenes Exhibit Cards series (W412)	63.350.613.412.149	http://www.metmuseum.org/art/collection/search/773052
5th century BCE	东周 玉璜|Arc-shaped pendant (Huang)	2009.92	http://www.metmuseum.org/art/collection/search/75285
20th century	擦條|Sand-file for carving jade	1981.296.18	http://www.metmuseum.org/art/collection/search/62070
datable to 1506–10	明　文徵明　致丈人吳愈書　冊頁|Letter to the artist’s father-in-law, Wu Yu	1989.363.59	http://www.metmuseum.org/art/collection/search/45775
1950s	棟方志功筆　蒼赫二童子図|Red and Blue, Two Attendants	2018.853.35	http://www.metmuseum.org/art/collection/search/816263
19th century	清 緙絲乾隆南巡宮苑圖|Scenic Sites in the Qianlong Emperor’s Southern Inspection Tour	13.220.134	http://www.metmuseum.org/art/collection/search/68288
1838	蝉小川|The Cicada Stream (Semi no Ogawa)  蝉小川	2013.787a–c	http://www.metmuseum.org/art/collection/search/78689
1840	蹄斎北馬筆　五美人図|Five Beauties	2015.500.9.12	http://www.metmuseum.org/art/collection/search/667347
dated 1978	近代  應野平  破墨山水  扇面|Broken-ink Landscape	1986.267.410	http://www.metmuseum.org/art/collection/search/36399
dated 1978	近代  程十髮  雜畫  冊頁十四開|Various Subjects	1986.267.435a–p	http://www.metmuseum.org/art/collection/search/36421

```

## call 4

```
python3 << 'EOF'
import csv
import re

# Read the TSV file
input_file = '/mnt/user-data/uploads/met_inventory.tsv'
output_file = '/mnt/user-data/outputs/met_inventory_standardized.tsv'

# Read data
rows = []
with open(input_file, 'r', encoding='utf-8') as f:
    reader = csv.reader(f, delimiter='\t')
    for row in reader:
        rows.append(row)

print(f"Total rows read: {len(rows)}")
print(f"Sample row: {rows[0]}")
print(f"Column count in header: {len(rows[0])}")

# Check for inconsistent column counts
column_counts = [len(row) for row in rows]
print(f"\nColumn count distribution:")
print(f"Min: {min(column_counts)}, Max: {max(column_counts)}")
print(f"Unique counts: {set(column_counts)}")

# Show rows with different column counts
for i, count in enumerate(column_counts):
    if count != 4:
        print(f"Row {i}: {count} columns - {rows[i][:50] if len(rows[i]) > 0 else 'EMPTY'}")

EOF

```

```
Total rows read: 301
Sample row: ['Object Date', 'Title', 'Object Number', 'Link Resource']
Column count in header: 4

Column count distribution:
Min: 4, Max: 4
Unique counts: {4}

```

## call 5

```
python3 << 'EOF'
import csv
import re
from pathlib import Path

input_file = '/mnt/user-data/uploads/met_inventory.tsv'
output_file = '/mnt/user-data/outputs/met_inventory_standardized.tsv'

# Read the TSV file
rows = []
with open(input_file, 'r', encoding='utf-8') as f:
    reader = csv.reader(f, delimiter='\t')
    for row in reader:
        rows.append(row)

print("=== STANDARDIZATION REPORT ===\n")

# Process data
header = rows[0]
data_rows = rows[1:]

standardized_rows = [header]
issues_found = []

for row_idx, row in enumerate(data_rows, start=2):
    if len(row) != 4:
        issues_found.append(f"Row {row_idx}: Unexpected column count ({len(row)})")
        continue
    
    object_date, title, object_number, link_resource = row
    
    # 1. Trim whitespace
    object_date = object_date.strip()
    title = title.strip()
    object_number = object_number.strip()
    link_resource = link_resource.strip()
    
    # 2. Standardize empty fields to NULL or consistent marker
    if not object_date:
        object_date = ""
    if not title:
        title = ""
    if not object_number:
        object_number = ""
        issues_found.append(f"Row {row_idx}: Missing Object Number")
    if not link_resource:
        link_resource = ""
        issues_found.append(f"Row {row_idx}: Missing Link Resource")
    
    # 3. Clean up special characters (normalize dashes and spaces)
    object_date = re.sub(r'\s+', ' ', object_date)  # Normalize whitespace
    title = re.sub(r'\s+', ' ', title)
    
    # 4. Ensure Object Number consistency (no extra spaces)
    object_number = re.sub(r'\s+', ' ', object_number)
    
    # 5. Validate URL format
    if link_resource and not link_resource.startswith('http'):
        issues_found.append(f"Row {row_idx}: Invalid URL format - {link_resource[:50]}")
    
    standardized_rows.append([object_date, title, object_number, link_resource])

# Write standardized TSV
with open(output_file, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f, delimiter='\t')
    writer.writerows(standardized_rows)

print(f"✓ Standardized file created: {output_file}")
print(f"✓ Total rows processed: {len(data_rows)}")
print(f"✓ Output rows: {len(standardized_rows)}")

print(f"\n=== DATA QUALITY CHECKS ===")
print(f"Rows with missing Object Number: {sum(1 for row in standardized_rows[1:] if not row[2])}")
print(f"Rows with missing Link Resource: {sum(1 for row in standardized_rows[1:] if not row[3])}")
print(f"Rows with missing Title: {sum(1 for row in standardized_rows[1:] if not row[1])}")
print(f"Rows with missing Object Date: {sum(1 for row in standardized_rows[1:] if not row[0])}")

if issues_found:
    print(f"\n=== ISSUES FOUND ({len(issues_found)}) ===")
    for issue in issues_found[:20]:  # Show first 20
        print(f"  • {issue}")
    if len(issues_found) > 20:
        print(f"  ... and {len(issues_found) - 20} more issues")
else:
    print("\n✓ No issues found!")

EOF

```

```
=== STANDARDIZATION REPORT ===

✓ Standardized file created: /mnt/user-data/outputs/met_inventory_standardized.tsv
✓ Total rows processed: 300
✓ Output rows: 301

=== DATA QUALITY CHECKS ===
Rows with missing Object Number: 0
Rows with missing Link Resource: 0
Rows with missing Title: 25
Rows with missing Object Date: 11

✓ No issues found!

```

## call 6

```
head -20 /mnt/user-data/outputs/met_inventory_standardized.tsv && echo -e "\n---\n" && tail -10 /mnt/user-data/outputs/met_inventory_standardized.tsv
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

---

ca. 1929	Yakima Canutt in Arrow Pictures from Western Stars or Scenes Exhibit Cards series (W412)	63.350.613.412.149	http://www.metmuseum.org/art/collection/search/773052
5th century BCE	东周 玉璜|Arc-shaped pendant (Huang)	2009.92	http://www.metmuseum.org/art/collection/search/75285
20th century	擦條|Sand-file for carving jade	1981.296.18	http://www.metmuseum.org/art/collection/search/62070
datable to 1506–10	明 文徵明 致丈人吳愈書 冊頁|Letter to the artist’s father-in-law, Wu Yu	1989.363.59	http://www.metmuseum.org/art/collection/search/45775
1950s	棟方志功筆 蒼赫二童子図|Red and Blue, Two Attendants	2018.853.35	http://www.metmuseum.org/art/collection/search/816263
19th century	清 緙絲乾隆南巡宮苑圖|Scenic Sites in the Qianlong Emperor’s Southern Inspection Tour	13.220.134	http://www.metmuseum.org/art/collection/search/68288
1838	蝉小川|The Cicada Stream (Semi no Ogawa) 蝉小川	2013.787a–c	http://www.metmuseum.org/art/collection/search/78689
1840	蹄斎北馬筆 五美人図|Five Beauties	2015.500.9.12	http://www.metmuseum.org/art/collection/search/667347
dated 1978	近代 應野平 破墨山水 扇面|Broken-ink Landscape	1986.267.410	http://www.metmuseum.org/art/collection/search/36399
dated 1978	近代 程十髮 雜畫 冊頁十四開|Various Subjects	1986.267.435a–p	http://www.metmuseum.org/art/collection/search/36421

```

