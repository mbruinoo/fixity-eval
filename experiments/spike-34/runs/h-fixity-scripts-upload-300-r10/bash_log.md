## call 4

```
cd /mnt/user-data && find . -name "*.tsv" -o -name "*inventory*" 2>/dev/null | head -20
```

```
./uploads/met_inventory.tsv

```

## call 5

```
md5sum /mnt/user-data/uploads/met_inventory.tsv && sha256sum /mnt/user-data/uploads/met_inventory.tsv
```

```
6ec5bfc2d979ad12eb3343149beb8617  /mnt/user-data/uploads/met_inventory.tsv
33c53888daa063ca9697f4a82f15cd2d047afbce1ccb21c235e9c4ae9509d547  /mnt/user-data/uploads/met_inventory.tsv

```

## call 6

```
head -5 /mnt/user-data/uploads/met_inventory.tsv | cat -A
```

```
Object Date^ITitle^IObject Number^ILink Resource$
7thM-bM-^@M-^S9th century^I^I2002.556.36^Ihttp://www.metmuseum.org/art/collection/search/65194$
^I^I02.18.509^Ihttp://www.metmuseum.org/art/collection/search/43906$
19th century^I^I93.1.168^Ihttp://www.metmuseum.org/art/collection/search/47519$
late 19th to early 20th century^I^I16.144.46^Ihttp://www.metmuseum.org/art/collection/search/42843$

```

## call 7

```
python3 << 'EOF'
import csv
import sys

# Read the original file
with open('/mnt/user-data/uploads/met_inventory.tsv', 'r', encoding='utf-8') as infile:
    reader = csv.DictReader(infile, delimiter='\t')
    rows = list(reader)

# Standardize the data
standardized_rows = []
for row in rows:
    standardized_row = {}
    # Normalize keys
    for key, value in row.items():
        # Clean up the key (remove extra whitespace)
        clean_key = key.strip() if key else ''
        # Clean up the value (remove extra whitespace but preserve content)
        clean_value = value.strip() if value else ''
        standardized_row[clean_key] = clean_value
    standardized_rows.append(standardized_row)

# Write the standardized file
with open('/mnt/user-data/outputs/met_inventory_standardized.tsv', 'w', encoding='utf-8', newline='') as outfile:
    fieldnames = ['Object Date', 'Title', 'Object Number', 'Link Resource']
    writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter='\t', extrasaction='ignore')
    writer.writeheader()
    writer.writerows(standardized_rows)

print(f"Standardized {len(standardized_rows)} rows")
print(f"Fieldnames: {fieldnames}")
EOF

```

```
Standardized 300 rows
Fieldnames: ['Object Date', 'Title', 'Object Number', 'Link Resource']

```

## call 8

```
md5sum /mnt/user-data/outputs/met_inventory_standardized.tsv && sha256sum /mnt/user-data/outputs/met_inventory_standardized.tsv
```

```
9c8318b6a37ebfd7867a7e65888fc327  /mnt/user-data/outputs/met_inventory_standardized.tsv
522c91490d71dfa0836ec34d70817df4d3449bd23ab4238442f645570febc133  /mnt/user-data/outputs/met_inventory_standardized.tsv

```

## call 9

```
echo "=== Original File ===" && wc -l /mnt/user-data/uploads/met_inventory.tsv && echo -e "\n=== Standardized File ===" && wc -l /mnt/user-data/outputs/met_inventory_standardized.tsv && echo -e "\n=== Sample of Standardized File ===" && head -6 /mnt/user-data/outputs/met_inventory_standardized.tsv
```

```
=== Original File ===
301 /mnt/user-data/uploads/met_inventory.tsv

=== Standardized File ===
301 /mnt/user-data/outputs/met_inventory_standardized.tsv

=== Sample of Standardized File ===
Object Date	Title	Object Number	Link Resource
7th–9th century		2002.556.36	http://www.metmuseum.org/art/collection/search/65194
		02.18.509	http://www.metmuseum.org/art/collection/search/43906
19th century		93.1.168	http://www.metmuseum.org/art/collection/search/47519
late 19th to early 20th century		16.144.46	http://www.metmuseum.org/art/collection/search/42843
		CP148	http://www.metmuseum.org/art/collection/search/63476

```

