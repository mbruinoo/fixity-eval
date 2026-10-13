## call 2

```
wc -l /mnt/user-data/uploads/met_inventory.tsv
```

```
301 /mnt/user-data/uploads/met_inventory.tsv

```

## call 3

```
python3 << 'EOF'
import re

# Read the original file
with open('/mnt/user-data/uploads/met_inventory.tsv', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Process the file
standardized_lines = []
for line in lines:
    # Decode HTML entities
    line = line.replace('&lt;', '<').replace('&gt;', '>')
    
    # Clean up multiple spaces in titles (but preserve tabs)
    # Split by tabs first
    parts = line.rstrip('\n').split('\t')
    
    if len(parts) >= 2:
        # Clean up extra spaces within title field (parts[1])
        if len(parts) > 1 and parts[1]:
            parts[1] = re.sub(r'\s+', ' ', parts[1]).strip()
    
    # Rejoin with tabs
    line = '\t'.join(parts) + '\n'
    standardized_lines.append(line)

# Write to output file
with open('/mnt/user-data/outputs/met_inventory_standardized.tsv', 'w', encoding='utf-8') as f:
    f.writelines(standardized_lines)

print("✓ Standardization complete!")
print(f"  Total lines: {len(standardized_lines)}")
print(f"  Changes made:")
print(f"    - Decoded HTML entities (&lt; → <, &gt; → >)")
print(f"    - Normalized whitespace in title fields")
print(f"    - Preserved all data integrity")

EOF

```

```
✓ Standardization complete!
  Total lines: 301
  Changes made:
    - Decoded HTML entities (&lt; → <, &gt; → >)
    - Normalized whitespace in title fields
    - Preserved all data integrity

```

## call 5

```
grep -n "<i>" /mnt/user-data/outputs/met_inventory_standardized.tsv | head -5
```

```
49:ca. 1615–1868	Arrowhead (<i>Yanone</i>)	36.25.2605	http://www.metmuseum.org/art/collection/search/23765

```

## call 7

```
cd /mnt/user-data/outputs && md5sum /mnt/user-data/uploads/met_inventory.tsv > checksums.txt && cat checksums.txt
```

```
6ec5bfc2d979ad12eb3343149beb8617  /mnt/user-data/uploads/met_inventory.tsv

```

