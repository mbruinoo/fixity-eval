## call 3

```
head -20 /mnt/user-data/uploads/met_inventory.tsv
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

## call 4

```
python3 << 'EOF'
import csv
import re
from pathlib import Path

# Read the TSV file
input_file = Path('/mnt/user-data/uploads/met_inventory.tsv')
output_file = Path('/mnt/user-data/outputs/met_inventory_standardized.tsv')

# Read the data
rows = []
with open(input_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        rows.append(row)

# Standardize the data
standardized_rows = []
for row in rows:
    standardized_row = {}
    
    # Standardize Object Date
    date = row.get('Object Date', '').strip()
    if not date:
        date = 'Unknown'
    standardized_row['Object Date'] = date
    
    # Standardize Title
    title = row.get('Title', '').strip()
    if not title:
        title = '[No title]'
    standardized_row['Title'] = title
    
    # Standardize Object Number
    obj_num = row.get('Object Number', '').strip()
    if not obj_num:
        obj_num = '[No number]'
    standardized_row['Object Number'] = obj_num
    
    # Standardize Link Resource
    link = row.get('Link Resource', '').strip()
    if not link:
        link = '[No link]'
    standardized_row['Link Resource'] = link
    
    standardized_rows.append(standardized_row)

# Write standardized data
with open(output_file, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['Object Date', 'Title', 'Object Number', 'Link Resource'], delimiter='\t')
    writer.writeheader()
    writer.writerows(standardized_rows)

print(f"✓ Standardized TSV file created: {output_file}")
print(f"✓ Total records: {len(standardized_rows)}")
print(f"\nSample of standardized data (first 3 rows):")
print("---")
for i, row in enumerate(standardized_rows[:3]):
    print(f"Row {i+1}:")
    for key, value in row.items():
        print(f"  {key}: {value}")
    print()

EOF

```

```
✓ Standardized TSV file created: /mnt/user-data/outputs/met_inventory_standardized.tsv
✓ Total records: 100

Sample of standardized data (first 3 rows):
---
Row 1:
  Object Date: late 19th century
  Title: [No title]
  Object Number: C.I.46.9.189
  Link Resource: http://www.metmuseum.org/art/collection/search/88288

Row 2:
  Object Date: 19th century
  Title: [No title]
  Object Number: 81.1.379
  Link Resource: http://www.metmuseum.org/art/collection/search/59814

Row 3:
  Object Date: 19th century
  Title: [No title]
  Object Number: 38.25.136
  Link Resource: http://www.metmuseum.org/art/collection/search/58999


```

