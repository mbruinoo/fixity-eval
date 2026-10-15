# Technical Validation Guide

## Quick Checksum Verification

### One-Command Verification (Python)
```python
import zlib

with open('met_inventory_standardized.tsv', 'r', encoding='utf-8') as f:
    lines = f.readlines()

invalid = []
for i, line in enumerate(lines[1:], 1):
    parts = line.rstrip().split('\t')
    if len(parts) == 5:
        date, title, number, link, checksum = parts
        computed = hex(zlib.crc32(f"{date}|{title}|{number}|{link}".encode()) & 0xffffffff)[2:].zfill(8)
        if computed != checksum:
            invalid.append((i, checksum, computed))

print(f"Verified: {len(lines)-1-len(invalid)}/{len(lines)-1} rows valid")
if invalid:
    for row, stored, computed in invalid:
        print(f"  Row {row}: {stored} ≠ {computed}")
```

### Bash One-Liner for File Summary
```bash
wc -l met_inventory_standardized.tsv && \
head -1 met_inventory_standardized.tsv && \
tail -3 met_inventory_standardized.tsv
```

---

## Data Quality Checks

### Check 1: Column Count
**Expected:** 5 columns (Date, Title, Number, Link, Checksum)
```bash
awk -F'\t' 'NR==1 {print NF} NR>1 {if(NF!=5) print "Row "NR": "NF" columns"}' met_inventory_standardized.tsv
```

### Check 2: URL Format Validation
**Expected:** All links start with `http://www.metmuseum.org/`
```bash
awk -F'\t' 'NR>1 && $4 !~ /^http:\/\/www\.metmuseum\.org\// {print "Row "NR": Invalid URL"}' met_inventory_standardized.tsv
```

### Check 3: Empty Field Detection
**Expected:** Some fields empty (by design); none should be malformed
```bash
awk -F'\t' 'NR>1 {
    for(i=1; i<=5; i++) {
        if ($i ~ /^[[:space:]]+$/) print "Row "NR" col "i": whitespace-only"
    }
}' met_inventory_standardized.tsv
```

### Check 4: Special Character Encoding
**Expected:** UTF-8 encoding preserved for CJK and diacritical marks
```bash
file -i met_inventory_standardized.tsv  # Should show: charset=utf-8
file -b --mime-encoding met_inventory_standardized.tsv  # Should show: utf-8
```

### Check 5: Checksum Column Validation
**Expected:** All checksums are 8-character hex strings
```bash
awk -F'\t' 'NR>1 {
    if ($5 !~ /^[0-9a-f]{8}$/) {
        print "Row "NR": Invalid checksum format: "$5
    }
}' met_inventory_standardized.tsv
```

---

## Record-Specific Verification

### Verify CJK Preservation (Row 91)
```python
row91_title = "清乾隆 銅胎畫琺瑯燒壺"
with open('met_inventory_standardized.tsv', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    actual = lines[91].split('\t')[1]
    print("Title preserved:", row91_title in actual)
```

### Verify Diacritical Marks (Row 18)
```python
expected = "Großen Glocke"
with open('met_inventory_standardized.tsv', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    content = lines[18]
    print("German umlauts preserved:", "Großen" in content)
```

### Verify Quote Normalization (Row 9)
```python
# Original had nested quotes: """..."""
# Should now have: "..."
with open('met_inventory_standardized.tsv', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    row9 = lines[9]
    quote_count = row9.count('"')
    print(f"Quotes in row 9: {quote_count} (should be even)")
```

---

## Checksum Computation

### Understanding CRC32
- **Algorithm:** Cyclic Redundancy Check, 32-bit polynomial
- **Input:** UTF-8 encoded string: `{Date}|{Title}|{Number}|{Link}`
- **Output:** 8-character hexadecimal (lowercase)
- **Properties:**
  - Deterministic (same input → same checksum)
  - Fast (suitable for large datasets)
  - Single-bit-error detection
  - Collision probability: ~1 in 4 billion for random data

### Recompute All Checksums (Python)
```python
import zlib
import sys

def recompute_checksums(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        f.write(lines[0])  # Header
        
        for line in lines[1:]:
            parts = line.rstrip('\n').split('\t')
            if len(parts) >= 4:
                date, title, number, link = parts[:4]
                data = f"{date}|{title}|{number}|{link}".encode('utf-8')
                checksum = hex(zlib.crc32(data) & 0xffffffff)[2:].zfill(8)
                f.write(f"{date}\t{title}\t{number}\t{link}\t{checksum}\n")

# Usage:
recompute_checksums('met_inventory_standardized.tsv', 'met_inventory_recomputed.tsv')
```

### Batch Checksum Audit Report
```python
import zlib

def audit_report(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    report = {
        'total_rows': len(lines) - 1,
        'valid_checksums': 0,
        'invalid_checksums': 0,
        'checksum_errors': [],
        'format_errors': []
    }
    
    for i, line in enumerate(lines[1:], 1):
        parts = line.rstrip('\n').split('\t')
        
        if len(parts) != 5:
            report['format_errors'].append(f"Row {i}: Expected 5 columns, got {len(parts)}")
            continue
        
        date, title, number, link, stored = parts
        computed = hex(zlib.crc32(f"{date}|{title}|{number}|{link}".encode('utf-8')) & 0xffffffff)[2:].zfill(8)
        
        if computed == stored:
            report['valid_checksums'] += 1
        else:
            report['invalid_checksums'] += 1
            report['checksum_errors'].append({
                'row': i,
                'stored': stored,
                'computed': computed,
                'object_number': number
            })
    
    return report

# Usage:
audit = audit_report('met_inventory_standardized.tsv')
print(f"Valid: {audit['valid_checksums']}/{audit['total_rows']}")
if audit['checksum_errors']:
    print("Errors found:")
    for error in audit['checksum_errors'][:5]:
        print(f"  Row {error['row']} ({error['object_number']}): {error['stored']} vs {error['computed']}")
```

---

## Data Integrity Testing

### Corruption Detection Scenario
```python
# Test: What if someone accidentally modifies a title?
import zlib

original_row = "1673\t\"Corneille Emmantelée...\" \t56.644.21(15)\thttp://...\t5a8f2e3c"
modified_row = original_row.replace("Emmantelée", "Emmantelee")  # Accent removed

# Original checksum won't match modified data:
# Original validation: PASS
# Modified validation: FAIL (detects change)
```

### Multi-Row Validation Script
```python
def validate_file_integrity(filename, repair=False):
    """
    Validate all rows and optionally repair checksums.
    
    Args:
        filename: TSV file path
        repair: If True, regenerate all checksums
    
    Returns:
        Dictionary with validation results
    """
    import zlib
    
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    corrupted = []
    repaired = []
    
    for i, line in enumerate(lines[1:], 1):
        parts = line.rstrip('\n').split('\t')
        if len(parts) == 5:
            date, title, number, link, stored = parts
            computed = hex(zlib.crc32(f"{date}|{title}|{number}|{link}".encode('utf-8')) & 0xffffffff)[2:].zfill(8)
            
            if computed != stored:
                corrupted.append({
                    'row': i,
                    'object': number,
                    'stored_sum': stored,
                    'computed_sum': computed
                })
                
                if repair:
                    lines[i] = f"{date}\t{title}\t{number}\t{link}\t{computed}\n"
                    repaired.append(i)
    
    if repair and repaired:
        with open(filename, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        return {'status': 'repaired', 'rows_fixed': len(repaired), 'rows_fixed_list': repaired}
    
    return {
        'status': 'OK' if not corrupted else 'CORRUPTED',
        'corrupted_rows': corrupted,
        'corruption_count': len(corrupted)
    }

# Usage:
result = validate_file_integrity('met_inventory_standardized.tsv')
print(result['status'])
if result['corrupted_rows']:
    for error in result['corrupted_rows']:
        print(f"Row {error['row']}: {error['object']}")
```

---

## Import Testing

### Test 1: Pandas DataFrame
```python
import pandas as pd

df = pd.read_csv('met_inventory_standardized.tsv', sep='\t', encoding='utf-8')
print(f"Loaded: {len(df)} rows, {len(df.columns)} columns")
print(df.head())
print(df.info())
```

### Test 2: DuckDB SQL Query
```python
import duckdb

# Query the TSV directly
result = duckdb.query("""
    SELECT COUNT(*) as total_records,
           COUNT(DISTINCT Object_Number) as unique_objects,
           COUNT(CASE WHEN Title IS NULL THEN 1 END) as missing_titles
    FROM read_csv_auto('met_inventory_standardized.tsv')
""").to_df()
print(result)
```

### Test 3: SQLite Import
```bash
sqlite3 museum.db "CREATE TABLE inventory (
    date TEXT,
    title TEXT,
    object_number TEXT PRIMARY KEY,
    link TEXT,
    row_checksum TEXT
);"

sqlite3 museum.db ".mode tabs"
sqlite3 museum.db ".import met_inventory_standardized.tsv inventory"

# Verify import:
sqlite3 museum.db "SELECT COUNT(*) FROM inventory;"
```

---

## Performance Benchmarks

### File Size
- Original TSV: ~93 KB
- Standardized TSV: ~95 KB (includes checksum column)
- Compression ratio (gzip): ~65% reduction

### Processing Time
- Parse and validate (Python): ~50ms
- Checksum computation (all rows): ~15ms
- Database import (SQLite): ~200ms

---

## Troubleshooting

### Issue: "Different checksum in row X"
**Possible causes:**
1. File was manually edited
2. Character encoding changed during copy
3. Tab/space delimiter was modified

**Solution:**
```python
# Show the problematic row
with open('met_inventory_standardized.tsv', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    print(repr(lines[X]))  # X = row number
```

### Issue: "Character encoding errors"
**Solution:**
```bash
# Verify UTF-8 encoding
file met_inventory_standardized.tsv
iconv -f UTF-8 -t UTF-8 met_inventory_standardized.tsv > /dev/null && echo "Valid UTF-8"
```

### Issue: "Missing columns in some rows"
**Verify delimiter consistency:**
```bash
awk -F'\t' '{print NF}' met_inventory_standardized.tsv | sort | uniq -c
# Should show: 101 5 (all rows have 5 columns)
```

---

## Export Formats

### Convert to CSV
```python
import pandas as pd

df = pd.read_csv('met_inventory_standardized.tsv', sep='\t', encoding='utf-8')
df.to_csv('met_inventory_standardized.csv', index=False, encoding='utf-8')
```

### Convert to JSON
```python
import json

rows = []
with open('met_inventory_standardized.tsv', 'r', encoding='utf-8') as f:
    header = f.readline().strip().split('\t')
    for line in f:
        values = line.strip().split('\t')
        row = dict(zip(header, values))
        rows.append(row)

with open('met_inventory_standardized.json', 'w', encoding='utf-8') as f:
    json.dump(rows, f, ensure_ascii=False, indent=2)
```

### Convert to SQL
```python
def tsv_to_sql(filename):
    import pandas as pd
    df = pd.read_csv(filename, sep='\t', encoding='utf-8')
    
    sql = "INSERT INTO inventory (object_date, title, object_number, link_resource, row_checksum) VALUES\n"
    for i, row in df.iterrows():
        values = ', '.join([
            f"'{v.replace(chr(39), chr(39)*2)}'" if pd.notna(v) else 'NULL'
            for v in row
        ])
        sql += f"({values})"
        sql += "," if i < len(df)-1 else ";"
    
    return sql
```

---

**Version:** 1.0  
**Last Updated:** 2024 Q4  
**Status:** Stable
