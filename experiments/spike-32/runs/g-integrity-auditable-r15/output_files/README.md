# Met Museum Inventory Standardization

**Status:** ✓ Complete with full audit trail and data integrity verification

---

## Quick Start

### Files You've Received

| File | Purpose | Use Case |
|------|---------|----------|
| **met_inventory_standardized.tsv** | Standardized data file | Import into your analysis tools (Python, R, Excel, SQL) |
| **Standardization_Audit_Report.md** | Comprehensive audit trail | Understand what changed and why; verify data integrity |
| **validate_standardization.py** | Validation script | Run verification tests after download |
| **CHECKSUMS.txt** | File integrity manifest | Verify downloads haven't been corrupted |
| **README.md** | This file | Quick reference guide |

---

## What Was Standardized

### Headers (Machine-Readable Format)

```
BEFORE:  Object Date    Title    Object Number    Link Resource
AFTER:   Object_Date    Title    Object_Number    Link_Resource
```

**Change:** Spaces replaced with underscores for database/programming language compatibility

### File Format

- **Encoding:** UTF-8 (no BOM)
- **Line Endings:** LF (Unix standard)
- **Delimiter:** Tab (single 0x09 byte)
- **Format:** TSV (Tab-Separated Values)

### Data Preservation

✓ **100% data integrity maintained**
- All 100 records preserved
- All field values unchanged
- All special characters retained (accents, dashes, Unicode)
- Empty cells maintained as empty

---

## Key Statistics

| Metric | Value | Status |
|--------|-------|--------|
| Data rows | 100 | ✓ Complete |
| Columns | 4 | ✓ Complete |
| Object_Number filled | 100% (100/100) | ✓ Complete |
| Link_Resource filled | 100% (100/100) | ✓ Complete |
| Object_Date filled | 96% (96/100) | ⚠ 4 rows missing |
| Title filled | 98% (98/100) | ⚠ 2 rows missing |

---

## How to Import

### Python (Pandas)

```python
import pandas as pd

# Read the standardized file
df = pd.read_csv('met_inventory_standardized.tsv', sep='\t', encoding='utf-8')

# Verify shape
print(df.shape)  # Should print: (100, 4)

# View first few rows
print(df.head())

# Access specific columns
print(df['Object_Number'])
print(df['Link_Resource'])
```

### R

```r
# Read the standardized file
data <- read.delim('met_inventory_standardized.tsv', encoding='UTF-8')

# Verify dimensions
dim(data)  # Should print: [1] 100   4

# View first few rows
head(data)

# Access specific columns
data$Object_Number
data$Link_Resource
```

### Excel

1. Open Excel
2. File → Open
3. Select `met_inventory_standardized.tsv`
4. Import settings:
   - Delimiter: Tab
   - Text encoding: UTF-8
5. Click OK

### SQL (MySQL)

```sql
LOAD DATA INFILE '/path/to/met_inventory_standardized.tsv'
INTO TABLE inventory
FIELDS TERMINATED BY '\t'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(Object_Date, Title, Object_Number, Link_Resource);
```

### SQL (PostgreSQL)

```sql
COPY inventory(Object_Date, Title, Object_Number, Link_Resource)
FROM '/path/to/met_inventory_standardized.tsv'
WITH (FORMAT text, DELIMITER E'\t', ENCODING 'UTF-8', HEADER);
```

---

## Verifying File Integrity

### Check After Download

**Linux/macOS:**
```bash
sha256sum -c CHECKSUMS.txt
```

**Windows PowerShell:**
```powershell
$expected = "your-hash-here"
$actual = (Get-FileHash met_inventory_standardized.tsv -Algorithm SHA256).Hash
$actual -eq $expected  # Returns True if file is valid
```

**Python:**
```python
import hashlib

with open('met_inventory_standardized.tsv', 'rb') as f:
    computed = hashlib.sha256(f.read()).hexdigest()
    print(computed)
```

### Run Validation Script

```bash
python3 validate_standardization.py met_inventory_standardized.tsv
```

This runs 10 comprehensive tests:
1. ✓ File structure
2. ✓ Header validation
3. ✓ Data row count
4. ✓ Column consistency
5. ✓ Required fields completeness
6. ✓ URL validation
7. ✓ Character encoding (UTF-8)
8. ✓ Line ending consistency
9. ✓ Tab delimiter consistency
10. ✓ File integrity hash

---

## Data Quality Notes

### Complete Fields
- **Object_Number:** 100% complete (all 100 rows)
- **Link_Resource:** 100% complete (all 100 rows, valid URLs)

### Incomplete Fields
- **Object_Date:** 96% complete (4 missing)
  - Empty in rows: 1, 7, 84, 85
- **Title:** 98% complete (2 missing)
  - Empty in rows: 1, 7

**Note:** Missing values are preserved as empty fields (not converted to nulls or "N/A"). This maintains original data integrity.

---

## Understanding the Data

### Column Descriptions

| Column | Type | Example | Notes |
|--------|------|---------|-------|
| Object_Date | String | "1673", "19th century", "ca. 1742" | Various date formats; some missing |
| Title | String | "Apis", "Ancient Walls, 1904 (from Sketchbook)" | Some multilingual; some missing |
| Object_Number | String | "C.I.46.9.189", "81.1.377a, b" | Museum object identifier |
| Link_Resource | URL | "http://www.metmuseum.org/art/collection/search/88288" | Direct link to museum collection page |

### Accessing Object Information

Each `Link_Resource` URL is a direct link to that object's page on the Metropolitan Museum website. Simply open the URL in a browser to see:
- High-resolution images
- Full object description
- Provenance and exhibition history
- Acquisition information
- Related objects

### Special Characters in Data

The file contains several non-ASCII characters that are properly preserved:

- **French accents:** é, è, ô (in titles like "Coupé")
- **German umlauts:** ö, ü (in German artwork titles)
- **En-dash:** – (used for date ranges like "1760–1800")
- **CJK characters:** Chinese (中文), Japanese (日本語), and Korean (한글) text
  - 6 rows contain titles in Asian languages
  - All properly encoded as UTF-8

---

## Audit Trail

For complete transformation documentation, see **Standardization_Audit_Report.md**

The report includes:
- Section 1: Transformation summary (what changed/didn't change)
- Section 2: Data audit results (completeness, quality metrics)
- Section 3: Special cases handled
- Section 4: Checksum verification procedures
- Section 5: Transformation rules applied
- Section 7: Before/after comparison with examples
- Section 8: Verification checklist
- Section 9: Recommendations for use and maintenance

---

## Recommendations for Use

### For Analysis
1. Use the standardized column names in your scripts: `Object_Date`, `Object_Number`, `Link_Resource`
2. Be aware that dates have multiple formats (years, centuries, approximate dates)
3. Use URL column to enrich with metadata from Museum API if needed

### For Data Storage
1. Maintain UTF-8 encoding if re-exporting
2. Keep tab delimiters (don't convert to CSV if possible)
3. Preserve LF line endings
4. Store this audit report alongside your data for versioning

### For Future Updates
1. Apply the same standardization rules to any new Met Museum data
2. Keep headers consistent: `Object_Date`, `Title`, `Object_Number`, `Link_Resource`
3. Archive both original and standardized versions

---

## Troubleshooting

### Import Issues

**Issue:** "File encoding error" when opening in Excel
- **Solution:** Ensure you're selecting UTF-8 encoding in the import dialog

**Issue:** Data appears misaligned in spreadsheet
- **Solution:** Make sure delimiter is set to TAB, not comma

**Issue:** Weird characters in titles (Chinese/Japanese text looks garbled)
- **Solution:** Verify your application is set to UTF-8 encoding

**Issue:** Python pandas error: "UnicodeDecodeError"
- **Solution:** Use `encoding='utf-8'` explicitly:
  ```python
  df = pd.read_csv('met_inventory_standardized.tsv', sep='\t', encoding='utf-8')
  ```

### Verification Issues

**Issue:** Checksum doesn't match
- **Solution:** File may have been corrupted during download; re-download and try again

**Issue:** Validation script shows errors
- **Solution:** Check that you're using the correct file; run `python3 --version` (requires Python 3.6+)

---

## Technical Specifications

### File Format (TSV)
- **RFC 4180:** Tab-Separated Values specification
- **UTF-8 Encoding:** ISO/IEC 10646 standard
- **Line Endings:** LF (U+000A) per POSIX standard
- **Delimiter:** Tab character (U+0009)

### Character Set
- ASCII (U+0000–U+007F)
- Latin Extended (U+0100–U+017F)
- Latin Extended-A (U+0100–U+0176)
- CJK Unified Ideographs (U+4E00–U+9FFF)
- Hiragana (U+3040–U+309F)
- Hangul Syllables (U+AC00–U+D7AF)

### Compatibility

✓ Python 3.6+  
✓ R (base, tidyverse)  
✓ Excel 2016+  
✓ Google Sheets  
✓ LibreOffice Calc  
✓ SQL Server  
✓ MySQL  
✓ PostgreSQL  
✓ SQLite  
✓ Apache Spark  
✓ Pandas, Polars, DuckDB  

---

## Questions?

1. **About standardization:** See Standardization_Audit_Report.md
2. **About specific objects:** Follow the URL in Link_Resource column
3. **About Metropolitan Museum:** Visit www.metmuseum.org
4. **Data validation:** Run validate_standardization.py

---

## Files Checklist

Before using these files, verify you have:

- [ ] met_inventory_standardized.tsv (the main data file)
- [ ] Standardization_Audit_Report.md (transformation documentation)
- [ ] validate_standardization.py (validation tool)
- [ ] CHECKSUMS.txt (integrity manifest)
- [ ] README.md (this file)

---

## Version Information

| Item | Value |
|------|-------|
| Standardization Version | 1.0 |
| Date | October 14, 2024 |
| Source Records | 100 |
| Data Preservation | 100% |
| Status | ✓ Ready for Production Use |

---

## License & Attribution

**Source Data:** Metropolitan Museum of Art Inventory  
**Source URLs:** http://www.metmuseum.org/art/collection/

The standardized file maintains all original data and URLs while applying format normalization for improved interoperability.

---

**Happy analyzing!**

For the most current information about these artworks, visit each object's page using the Link_Resource URLs.

---

*Last updated: October 14, 2024*