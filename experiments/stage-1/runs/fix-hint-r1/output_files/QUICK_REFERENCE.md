# Met Museum Inventory Standardization - Quick Reference

## File Overview

| File | Purpose | Format |
|------|---------|--------|
| `met_inventory_standardized.tsv` | Standardized inventory data | TSV, UTF-8 |
| `checksums.json` | Integrity checksums | JSON |
| `standardization_report.md` | Detailed transformation rules | Markdown |
| `INTEGRITY_VERIFICATION.txt` | Verification commands & results | Text |
| `FIXITY_DOCUMENTATION.md` | Complete technical documentation | Markdown |
| `standardize_met_inventory.py` | Standardization script | Python 3 |
| `run_standardization.sh` | Orchestration script | Bash |

## Data Changes

### Column Names
```
BEFORE                  AFTER
Object Date      →      object_date
Title            →      title  
Object Number    →      object_number
Link Resource    →      resource_link
```

### Transformations Applied
- ✓ Trimmed whitespace from all fields
- ✓ Empty titles → `[Untitled]`
- ✓ All Unicode preserved (CJK characters, accents, etc.)
- ✓ Complex object numbers preserved (e.g., "36.120.598a, b")
- ✓ URLs validated but not modified

### Record Count
- **Source records**: 100 data rows
- **Output records**: 100 data rows
- **Status**: ✓ All records standardized

## Quick Verification

### Verify Files Haven't Changed
```bash
# Check source file
sha256sum met_inventory.tsv
# Should match: [see checksums.json or INTEGRITY_VERIFICATION.txt]

# Check output file
sha256sum met_inventory_standardized.tsv
# Should match: [see checksums.json or INTEGRITY_VERIFICATION.txt]
```

### View Checksums
```bash
# Display all checksums
cat checksums.json

# Display file-level checksums only
cat checksums.json | jq '.["source_file", "output_file"]'

# Display first 10 row checksums
cat checksums.json | jq '.row_transformations | to_entries | .[0:10]'
```

### Inspect Transformed Data
```bash
# View first 5 rows (with header)
head -6 met_inventory_standardized.tsv

# Count total rows
wc -l met_inventory_standardized.tsv

# Display rows with empty titles
awk -F'\t' '$2 ~ /\[Untitled\]/ {print NR": " $0}' met_inventory_standardized.tsv

# Find specific object number
grep "91.1.396" met_inventory_standardized.tsv
```

## Common Tasks

### Re-run Standardization
```bash
# Requires Python 3
python3 standardize_met_inventory.py

# Or use the bash orchestration script
bash run_standardization.sh
```

### Compare Before/After
```bash
# Side-by-side comparison (first row)
paste <(head -2 met_inventory.tsv | tail -1) \
      <(head -2 met_inventory_standardized.tsv | tail -1)
```

### Export Specific Records
```bash
# Export records by date range
awk -F'\t' '$1 ~ /19th century/ {print}' met_inventory_standardized.tsv > 19th_century.tsv

# Export records with specific object number pattern
awk -F'\t' '$3 ~ /1976\./ {print}' met_inventory_standardized.tsv > 1976_objects.tsv
```

### Validate TSV Format
```bash
# Count columns (should be 4)
head -1 met_inventory_standardized.tsv | tr '\t' '\n' | wc -l

# Check for consistent column count
awk -F'\t' '{print NF}' met_inventory_standardized.tsv | sort | uniq -c
# Should show: 101 4 (100 rows + 1 header, all with 4 columns)
```

## Fixity Assurance Level

| Check | Status | Evidence |
|-------|--------|----------|
| Whole file integrity | ✓ Verified | SHA256 in checksums.json |
| Record integrity | ✓ Verified | 100 row-level checksums |
| Transformation completeness | ✓ Verified | All rows standardized |
| Unicode preservation | ✓ Verified | CJK characters present |
| Data completeness | ✓ Verified | 100 input = 100 output |

## If You Detect Corruption

1. **Check the checksums**
   ```bash
   sha256sum met_inventory_standardized.tsv
   ```

2. **Compare with known good checksums**
   ```bash
   grep "output_file" checksums.json
   ```

3. **If corrupted**:
   - Do not modify the file
   - Restore from backup
   - Re-run standardization script
   - Verify new checksums match originals

4. **Document the incident**:
   - Record discovery date/time
   - Note which files were affected
   - Keep corrupted copies for analysis
   - Update preservation log

## Standards and Best Practices

- **Checksum Algorithm**: SHA256 (NIST FIPS 180-4)
- **Encoding**: UTF-8
- **Format**: TSV (RFC 4180)
- **Serialization**: JSON (RFC 8259)
- **Preservation Standard**: Aligned with PREMIS

## Files for Different Audiences

- **Data Users**: Start with `met_inventory_standardized.tsv`
- **Administrators**: Read `INTEGRITY_VERIFICATION.txt` 
- **Preservationists**: Study `FIXITY_DOCUMENTATION.md`
- **Developers**: Review `standardize_met_inventory.py`
- **Auditors**: Check `checksums.json` and `standardization_report.md`

## Archive This Package Together

Recommended folder structure for long-term preservation:

```
met_museum_inventory_standardized/
├── data/
│   ├── met_inventory_standardized.tsv
│   └── met_inventory.tsv  [original, optional]
├── checksums/
│   └── checksums.json
├── documentation/
│   ├── FIXITY_DOCUMENTATION.md
│   ├── standardization_report.md
│   ├── INTEGRITY_VERIFICATION.txt
│   └── QUICK_REFERENCE.md
└── scripts/
    ├── standardize_met_inventory.py
    └── run_standardization.sh
```

**Keep all files together** for complete audit trail and reproducibility.
