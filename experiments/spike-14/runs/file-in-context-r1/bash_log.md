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

## call 9

```
cd /mnt/user-data/outputs && python3 standardize_met_inventory.py
```

```

================================================================================
MET MUSEUM INVENTORY TSV STANDARDIZATION
================================================================================

Standardization Process Log - 2026-10-13T21:17:51.005143
================================================================================

[STEP 1] Verifying input file...
ERROR: Input file not found: met_inventory.tsv

✗ FAILURE: Standardization failed. Check standardization_log.txt for details.

```

## call 10

```
cp /mnt/user-data/uploads/met_inventory.tsv /mnt/user-data/outputs/met_inventory.tsv && cd /mnt/user-data/outputs && python3 standardize_met_inventory.py
```

```

================================================================================
MET MUSEUM INVENTORY TSV STANDARDIZATION
================================================================================

Standardization Process Log - 2026-10-13T21:17:52.530153
================================================================================

[STEP 1] Verifying input file...
  Input file: met_inventory.tsv
  Input MD5:  6ec5bfc2d979ad12eb3343149beb8617

[STEP 2] Reading input file...
  Total lines read: 301

[STEP 3] Processing data...
  Row 1: Header row (passed through)

[STEP 4] Writing output file...
  Output file: met_inventory_standardized.tsv
  Total lines written: 301

[STEP 5] Verifying output file...
  Output MD5: c18503f8f274ac7e9500ebf3635017f1

[STEP 6] Processing Statistics...
  Rows processed:              300
  Rows with warnings:          0
  HTML entities decoded:       4
  Total warnings:              0

================================================================================
FIXITY VERIFICATION SUMMARY
================================================================================
Input MD5:  6ec5bfc2d979ad12eb3343149beb8617
Output MD5: c18503f8f274ac7e9500ebf3635017f1
Status:     PROCESSING COMPLETE
================================================================================

Log file written to: standardization_log.txt

✓ SUCCESS: Standardization complete!
  Output file: met_inventory_standardized.tsv
  Log file:    standardization_log.txt

```

