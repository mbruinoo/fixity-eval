## call 2

```
python3 << 'EOF'
import csv
import re

# Read the TSV file
input_file = '/mnt/user-data/uploads/met_inventory.tsv'
output_file = '/mnt/user-data/outputs/met_inventory_standardized.tsv'

rows = []
with open(input_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        rows.append(row)

# Standardize the data
standardized_rows = []
for row in rows:
    # Clean up Object Date
    obj_date = row.get('Object Date', '').strip()
    
    # Clean up Title - remove extra quotes if present, keep brackets
    title = row.get('Title', '').strip()
    if title.startswith('"') and title.endswith('"'):
        title = title[1:-1]
    # Decode HTML entities
    title = title.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
    
    # Clean up Object Number
    obj_number = row.get('Object Number', '').strip()
    
    # Clean up Link Resource
    link = row.get('Link Resource', '').strip()
    
    standardized_rows.append({
        'Object Date': obj_date,
        'Title': title,
        'Object Number': obj_number,
        'Link Resource': link
    })

# Write standardized TSV
with open(output_file, 'w', encoding='utf-8', newline='') as f:
    fieldnames = ['Object Date', 'Title', 'Object Number', 'Link Resource']
    writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
    writer.writeheader()
    writer.writerows(standardized_rows)

print(f"Standardized file created with {len(standardized_rows)} records")

EOF

```

```
Standardized file created with 300 records

```

## call 3

```
head -20 /mnt/user-data/outputs/met_inventory_standardized.tsv
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

