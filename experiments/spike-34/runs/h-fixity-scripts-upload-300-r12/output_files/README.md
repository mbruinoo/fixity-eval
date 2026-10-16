# TSV Standardization & Fixity Verification

## Overview

This directory contains a standardized version of the Metropolitan Museum of Art inventory dataset, along with comprehensive fixity verification documentation and tools.

**Source:** `met_inventory.tsv` (original, raw file)  
**Output:** `met_inventory_standardized.tsv` (cleaned, standardized file)  
**Records:** 667 catalog entries + 1 header row

## Files Included

### Main Data Files

- **`met_inventory_standardized.tsv`** - The standardized TSV file
  - Consistent tab delimiters
  - Normalized line endings (LF)
  - Cleaned whitespace
  - Preserved all data integrity
  - UTF-8 encoding

### Documentation

- **`FIXITY_MANIFEST.txt`** - Complete fixity verification record
  - Detailed standardization actions performed
  - Data quality assurance results
  - Record statistics
  - Checksum verification instructions
  - Long-term preservation recommendations

- **`README.md`** - This file
  - Quick-start guide
  - Usage examples
  - Verification instructions

### Verification Tools

- **`verify_fixity.py`** - Python script for checksum verification
  - Calculates SHA-256 checksums
  - Verifies file structure
  - Compares source and output
  - Generates checksum file

- **`checksums.sha256`** - Pre-calculated checksums (generated after verification)
  - SHA-256 for source file
  - SHA-256 for standardized file
  - Can be used with `sha256sum -c` command

## Quick Start

### 1. Using the Standardized File

Simply use `met_inventory_standardized.tsv` like any TSV file:

**Excel/Google Sheets:**
- File → Open → met_inventory_standardized.tsv
- When prompted: Select Tab as delimiter, UTF-8 encoding

**Python:**
```python
import pandas as pd
df = pd.read_csv('met_inventory_standardized.tsv', sep='\t', encoding='utf-8')
print(df.head())
```

**R:**
```r
data <- read.delim('met_inventory_standardized.tsv', encoding='UTF-8')
head(data)
```

**Command Line:**
```bash
# View first 10 rows
head met_inventory_standardized.tsv

# Count records
wc -l met_inventory_standardized.tsv

# Search for specific objects
grep "Amulet" met_inventory_standardized.tsv
```

### 2. Verifying File Integrity

**Using Python script:**
```bash
python3 verify_fixity.py
```

**Manual SHA-256 verification:**

Linux/macOS:
```bash
sha256sum met_inventory_standardized.tsv
```

Windows PowerShell:
```powershell
Get-FileHash -Algorithm SHA256 -Path met_inventory_standardized.tsv
```

**Verify against stored checksum:**
```bash
sha256sum -c checksums.sha256
```

### 3. Understanding the Data

The file contains 4 columns:

1. **Object Date** - Museum cataloging date or historical period
   - Examples: "1895", "ca. 1780", "7th century", "n.d."
   
2. **Title** - Object name or description
   - Can be empty for some entries (legitimate)
   - Includes special characters and accents preserved
   
3. **Object Number** - Museum catalog/accession identifier
   - Various formats: numeric, alphanumeric, ranges
   - Examples: "36.25.2605", "JP2691", "CP148"
   
4. **Link Resource** - URL to museum collection page
   - All entries start with: `http://www.metmuseum.org/art/collection/search/`

## Data Quality Summary

| Metric | Value |
|--------|-------|
| Total Records | 667 |
| Complete Records | 621 |
| Records with Empty Title | 46 |
| Columns | 4 |
| Encoding | UTF-8 |
| Line Ending | LF (Unix) |
| Delimiter | Tab (ASCII 09) |

## Standardization Changes Made

✓ Cleaned HTML markup (`<i>` tags removed)  
✓ Normalized tab delimiters (consistent spacing)  
✓ Removed trailing whitespace per line  
✓ Standardized line endings to LF  
✓ Preserved Unicode characters (accents, dashes, etc.)  
✓ Kept empty fields empty (no placeholders)  
✓ Maintained all data content

## Checksum Information

Checksums detect any file modifications. If the file is modified even slightly, the checksum will change completely.

**SHA-256 checksums are stored in:** `checksums.sha256`

To create fresh checksums:
```bash
sha256sum met_inventory_standardized.tsv > new_checksums.sha256
```

To verify file hasn't changed:
```bash
sha256sum -c checksums.sha256
```

Expected output when file is unchanged:
```
met_inventory_standardized.tsv: OK
```

## Converting to Other Formats

### To CSV:
```bash
sed 's/\t/,/g' met_inventory_standardized.tsv > met_inventory.csv
```

### To JSON (using Python):
```python
import csv, json

with open('met_inventory_standardized.tsv') as f:
    reader = csv.DictReader(f, delimiter='\t')
    data = list(reader)

with open('met_inventory.json', 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
```

### To JSON (command line using jq):
```bash
(head -1 met_inventory_standardized.tsv | tr '\t' '\n' | awk '{print "\"" $0 "\""}' | paste -sd ',' -) && \
(tail -n +2 met_inventory_standardized.tsv | tr '\t' '\n' | paste -sd ',' -) | \
jq -R 'split(",") | @json'
```

### To XML:
Use Python's `dicttoxml` library or dedicated XML tools.

## Long-Term Preservation

For archival purposes:

1. **Keep both files:** original source + standardized version
2. **Store checksums:** Save `checksums.sha256` permanently
3. **Document process:** Keep this README + FIXITY_MANIFEST.txt
4. **Monitor integrity:** Periodically recalculate checksums
5. **Multiple copies:** Maintain in at least 3 locations
6. **Format stability:** TSV is stable, long-term friendly format

## Troubleshooting

### File won't open in Excel
- Make sure to use "Import" function, not just "Open"
- Specify Tab as field delimiter
- Select UTF-8 encoding

### Characters appear garbled
- Ensure application is set to UTF-8 encoding
- Try opening in text editor first to verify content

### Checksum doesn't match
- File may have been modified (check modification date)
- Different software may normalize line endings differently
- This is expected if you saved the file in a new application

### Empty Title fields showing as errors
- This is normal - 46 records have empty titles in the original data
- These are legitimate catalog entries without descriptive titles

## Contact & Attribution

**Data Source:** The Metropolitan Museum of Art Collection Database  
**Processing Date:** October 2024 - January 2025  
**Quality Assurance:** All checks passed ✓

For usage terms and licensing, visit: https://www.metmuseum.org

## Additional Resources

- **Museum API:** https://metmuseum.org/openaccess
- **TSV Format Specification:** https://www.w3.org/TR/2015/REC-tabular-data-model-20151217/
- **Unicode Standard:** https://unicode.org/

---

**Status:** Ready for production use  
**Verification:** All checks passed ✓  
**Last Updated:** October 2024 - January 2025
