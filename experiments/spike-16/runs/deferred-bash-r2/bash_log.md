## call 4

```
cd /mnt/user-data/uploads && python3 << 'EOF'
import csv

# Read the file
with open('met_inventory.tsv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    rows = list(reader)

# Standardize the data
standardized_rows = []
for row in rows:
    # Clean up empty fields
    cleaned_row = {
        'Object Date': row['Object Date'].strip() if row['Object Date'] else '',
        'Title': row['Title'].strip() if row['Title'] else '',
        'Object Number': row['Object Number'].strip() if row['Object Number'] else '',
        'Link Resource': row['Link Resource'].strip() if row['Link Resource'] else ''
    }
    
    # Decode HTML entities
    if cleaned_row['Title']:
        cleaned_row['Title'] = (cleaned_row['Title']
                               .replace('&lt;', '<')
                               .replace('&gt;', '>')
                               .replace('&amp;', '&')
                               .replace('&quot;', '"')
                               .replace('&#39;', "'"))
    
    standardized_rows.append(cleaned_row)

# Write standardized file
with open('/mnt/user-data/outputs/met_inventory_standardized.tsv', 'w', encoding='utf-8', newline='') as f:
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

## call 5

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

## call 6

```
grep -E "Arrowhead|Latitude" /mnt/user-data/outputs/met_inventory_standardized.tsv | head -5
```

```
ca. 1615–1868	Arrowhead (<i>Yanone</i>)	36.25.2605	http://www.metmuseum.org/art/collection/search/23765

```

