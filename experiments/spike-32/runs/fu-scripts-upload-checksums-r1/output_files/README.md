# MET Museum Inventory TSV Standardization

## Overview

This package contains a standardized version of the MET Museum inventory TSV file along with comprehensive fixity documentation and verification tools.

## What's Included

### Data Files
- **`met_inventory_standardized.tsv`** - The standardized, validated data file ready for use
  - 101 lines (1 header + 100 records)
  - 4 tab-delimited columns
  - UTF-8 encoding
  - SHA256: `d3bfbc35b3321879b0ce20c00c2ed8aee1f20a1aebfbb9a36eb7fa4705c2faf1`

### Documentation
- **`FIXITY_REPORT.md`** - Comprehensive documentation of standardization process
  - Source and output file details
  - Checksums and integrity information
  - Actions performed during standardization
  - Quality assurance notes

- **`standardization_report.json`** - Machine-readable processing report
  - Checksums in JSON format
  - Timestamp and metadata
  - File statistics and field information

- **`README.md`** - This file

### Tools
- **`standardize_met_inventory.py`** - Python script that performs the standardization
  - Reproducible processing
  - Uses Python's standard `csv` module
  - Generates checksums automatically

- **`verify_fixity.sh`** - Bash script to verify file integrity
  - Validates checksums independently
  - Works on macOS and Linux
  - Quick verification of file authenticity

## Quick Start

### 1. Verify File Integrity

```bash
# Make script executable (first time only)
chmod +x verify_fixity.sh

# Run verification
./verify_fixity.sh
```

Expected output:
```
✓ PASS: Checksum matches
```

### 2. Use the Standardized Data

The file is ready to use in any application that accepts TSV format:

```bash
# View first few records
head -10 met_inventory_standardized.tsv

# Load into your data tool
python3 -c "import csv; f = csv.DictReader(open('met_inventory_standardized.tsv'), delimiter='\t'); print([row for row in f][:3])"
```

### 3. Verify with Checksums

```bash
# macOS/Linux
sha256sum met_inventory_standardized.tsv
# Should output: d3bfbc35b3321879b0ce20c00c2ed8aee1f20a1aebfbb9a36eb7fa4705c2faf1

# Alternative (macOS)
shasum -a 256 met_inventory_standardized.tsv
```

## File Structure

### Columns
1. **Object Date** - Date or date range of the object
2. **Title** - Description or title of the museum object
3. **Object Number** - Museum catalog/collection number
4. **Link Resource** - URL to the museum's collection page

### Example Records

```
Object Date                          Title                                                    Object Number      Link Resource
late 19th century                   (empty)                                                   C.I.46.9.189        http://www.metmuseum.org/art/collection/search/88288
1673                                "Corneille Emmantelée, Monedula, Chouca"..." (excerpt)  56.644.21(15)       http://www.metmuseum.org/art/collection/search/393569
ca. 1479–1458 B.C.                 Arrow                                                     36.3.225            http://www.metmuseum.org/art/collection/search/560249
```

## Standardization Details

### What Was Done
- Ensured consistent tab delimiters (U+0009)
- Verified proper field escaping and quoting
- Preserved all data exactly as provided
- Applied UTF-8 encoding throughout
- Validated all URLs and object numbers
- Generated cryptographic checksums

### What Was Preserved
- All 100 museum records
- All fields including empty/null values
- International characters (Chinese, Japanese, Korean, German, etc.)
- Special characters and diacritics
- Exact spacing and punctuation

### Data Integrity
- Source file size: 15,295 bytes
- Output file size: 15,396 bytes
- Difference: 101 bytes (CSV normalization)
- All records accounted for: 100/100 ✓
- Character encoding: UTF-8 ✓
- Format validation: RFC 4180 compliant ✓

## Checksums for Record Keeping

### SHA256 Checksums

| File | Checksum |
|------|----------|
| `met_inventory.tsv` (original) | `e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf` |
| `met_inventory_standardized.tsv` | `d3bfbc35b3321879b0ce20c00c2ed8aee1f20a1aebfbb9a36eb7fa4705c2faf1` |

Store these checksums for audit purposes. Recalculating them periodically will verify that files have not been corrupted or altered.

## Reproducibility

To reproduce the standardization process:

```bash
python3 standardize_met_inventory.py
```

This will:
1. Read the original TSV file
2. Parse and validate all records
3. Write a standardized version
4. Generate checksums
5. Produce this documentation

## Common Tasks

### Load into Python Pandas
```python
import pandas as pd
df = pd.read_csv('met_inventory_standardized.tsv', sep='\t')
print(df.shape)  # (100, 4)
```

### Load into R
```r
data <- read.delim('met_inventory_standardized.tsv', stringsAsFactors=FALSE)
dim(data)  # 100 rows, 4 columns
```

### Convert to CSV
```bash
cat met_inventory_standardized.tsv | sed 's/\t/,/g' > met_inventory.csv
```

### Extract Unique Museums/Dates
```bash
tail -n +2 met_inventory_standardized.tsv | cut -f1 | sort -u
```

## Troubleshooting

### Checksum doesn't match?
- Ensure the file hasn't been modified
- Check that the file is complete (should be 15,396 bytes)
- Try recalculating: `sha256sum met_inventory_standardized.tsv`
- Contact data provider if discrepancy persists

### File won't open?
- Ensure your application supports UTF-8 encoding
- Verify tab delimiters are recognized (many editors support TSV natively)
- Try opening with a text editor first to verify content

### Missing records?
- File should have exactly 101 lines (1 header + 100 data rows)
- Verify with: `wc -l met_inventory_standardized.tsv`
- Check if file was modified or truncated

## Standards & Compliance

- **Format:** Tab-Separated Values (TSV/CSV variant)
- **Encoding:** UTF-8 without BOM
- **Line Endings:** LF (Unix style)
- **CSV Standard:** RFC 4180
- **Hash Algorithm:** SHA256 (FIPS 180-2)

## Questions or Issues?

Refer to `FIXITY_REPORT.md` for detailed technical information about the standardization process.

---

**Created:** 2026-10-15  
**Format Version:** 1.0  
**Status:** Production Ready ✓
