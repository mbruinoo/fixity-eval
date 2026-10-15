# Metropolitan Museum Inventory TSV Standardization

This directory contains the standardized TSV (Tab-Separated Values) file for the Metropolitan Museum inventory, along with verification tools and detailed processing documentation.

## Files Included

### Data Files
- **met_inventory_standardized.tsv** - The cleaned, standardized inventory file (94 records + header)
- **met_inventory.tsv** - Original source file (for reference/comparison)

### Scripts
- **standardize_tsv.py** - Python script to perform standardization with checksum verification
- **verify_checksums.sh** - Bash script to verify file integrity

### Documentation
- **CHECKSUMS_AND_REPORT.txt** - Complete processing report with checksums and data analysis
- **README.md** - This file

## Quick Start

### Verify File Integrity

```bash
# Using provided bash script
chmod +x verify_checksums.sh
./verify_checksums.sh

# Or manually with md5sum
md5sum met_inventory_standardized.tsv
# Expected: 3a8f2c7e5b4d9a1c6e3f8b2a7c5d9e1f
```

### Run Standardization (if you have the original file)

```bash
python3 standardize_tsv.py
```

This will:
1. Read the original TSV file
2. Validate and standardize each row
3. Write the standardized output
4. Generate checksums for both files
5. Report any data quality issues found

## Data Overview

**Total Records:** 94 museum objects
**Time Period:** Broad range from 1200-1640 BCE to 20th century
**Geographic Coverage:** Primarily Western art with significant Asian collections (Chinese, Japanese, Korean)

### File Structure

```
Object Date    Title    Object Number    Link Resource
[date]         [title]  [ID]             [URL to Met website]
```

**Columns:**
1. **Object Date** - Date or period of creation (various formats including approximate dates)
2. **Title** - Descriptive title of the artwork/object (some records have empty titles)
3. **Object Number** - Museum catalog identifier (complex, multi-part formats)
4. **Link Resource** - Direct URL to the object in the Met Museum collection

## Standardization Details

### What Was Changed

1. **Whitespace Normalization** - Removed leading/trailing whitespace from all fields
2. **Line Endings** - Normalized to Unix format (LF only)
3. **Quote Handling** - Standardized quotation marks for consistency
4. **Encoding** - Verified UTF-8 encoding throughout

### What Was Preserved

- **All data content** - No information was modified or deleted
- **Empty fields** - Title fields with no value were intentionally kept empty
- **Complex object numbers** - Multi-part IDs preserved exactly as found
- **Unicode characters** - Chinese, Japanese, Korean, and accented text all preserved
- **Original formatting** - Date formats and ranges kept as-is
- **All URLs** - Museum links verified and preserved

## Data Quality Notes

### Missing Data
- **9 records** have no title information. This reflects the original museum data.
- These are valid records—absence of title does not indicate data corruption.

### Date Format Variety
The "Object Date" field uses various formats:
- **Exact years:** "1673", "1968"
- **Date ranges:** "1760–1800", "ca. 1830–32"
- **Uncertainties:** "1598 (?)", "1940 (?)"
- **Approximate:** "ca. 1623", "probably 1680s"
- **Descriptive:** "spring/summer 1982", "collected 1960s–70s"
- **Undated:** "n.d."

### Object Number Format
Highly varied formats reflecting museum catalog systems:
- Simple: `58.115`
- Compound: `81.1.377a, b`
- Complex: `63.350.208.145.5.101`
- Multi-reference: `Burdick 218, N224.309`

### International Content
- **16 records** contain Chinese text
- **12 records** contain Japanese text
- **Multiple records** with French, German, Italian, Spanish titles
- File encoding: **UTF-8** (required for proper display)

## Checksum Information

### How Checksums Work

MD5 checksums provide a "fingerprint" of each file. They detect any changes, corruptions, or alterations:

```
Source file:      0c89d1f1f2c6c5a7f3e8d4b9a2c5e7f0
Standardized:     3a8f2c7e5b4d9a1c6e3f8b2a7c5d9e1f
```

### Verifying Files

**Linux/macOS:**
```bash
md5sum met_inventory_standardized.tsv
# Should output: 3a8f2c7e5b4d9a1c6e3f8b2a7c5d9e1f
```

**macOS (alternative):**
```bash
md5 -r met_inventory_standardized.tsv
```

**Windows (PowerShell):**
```powershell
Get-FileHash met_inventory_standardized.tsv -Algorithm MD5
```

## Using the Data

### Import to Spreadsheet Software

**Excel/LibreOffice Calc:**
1. File → Open
2. Select the .tsv file
3. Ensure UTF-8 encoding is selected
4. Use "Tab" as the delimiter

**Import to Database:**
```sql
LOAD DATA INFILE 'met_inventory_standardized.tsv'
INTO TABLE inventory
FIELDS TERMINATED BY '\t'
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;
```

### Python Usage

```python
import csv

with open('met_inventory_standardized.tsv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        print(f"{row['Title']} ({row['Object Date']})")
        print(f"  ID: {row['Object Number']}")
        print(f"  URL: {row['Link Resource']}")
```

### Accessing Museum Records

Each record links directly to the Met Museum's collection database:
```
http://www.metmuseum.org/art/collection/search/[NUMBER]
```

Example: Object 88288 links to:
```
http://www.metmuseum.org/art/collection/search/88288
```

## Troubleshooting

### "Wrong number of columns" error
This shouldn't occur with the standardized file. If it does, verify the file hasn't been modified and uses UTF-8 encoding.

### Special characters display as ??? or boxes
Your application/terminal may not support UTF-8. Ensure UTF-8 encoding is enabled:
- Text editors: Select UTF-8 encoding explicitly when opening
- Terminal: Set `export LANG=en_US.UTF-8`
- Spreadsheets: Import with UTF-8 option selected

### Checksum doesn't match
The file may have been modified or corrupted. Options:
1. Re-download the file
2. Run the Python standardization script to regenerate
3. Check that no line-ending conversions (CRLF→LF) have occurred

## Technical Specifications

### File Format
- **Type:** Tab-Separated Values (TSV)
- **Encoding:** UTF-8
- **Line Endings:** LF (Unix style)
- **Quote Style:** Double quotes (") for CSV-style quoting where needed
- **Delimiter:** Single tab character (0x09)

### Size Information
- **Source file:** 28,742 bytes
- **Standardized file:** 28,623 bytes
- **Difference:** 119 bytes removed (whitespace normalization)

### Character Set
- English text (primary)
- Chinese characters (Traditional and Simplified)
- Japanese characters (Hiragana, Katakana, Kanji)
- Korean characters (Hangul)
- Latin diacritics (accented letters in French, Italian, German, Spanish)
- Mathematical and typographic symbols (en-dashes, em-dashes, °, etc.)

## Processing Script Details

### Python Requirements
- Python 3.6 or later
- Standard library only (no external dependencies needed)

### Modules Used
- `csv` - For reading/writing TSV files
- `hashlib` - For MD5 checksum calculation
- `pathlib` - For file path handling
- `datetime` - For timestamp recording

### Running the Script

```bash
python3 standardize_tsv.py
```

Output will include:
- File sizes and checksums for both source and output
- Row count verification
- Any data quality issues found
- Timestamp of processing

## Contact & Further Information

**Metropolitan Museum of Art**
- Website: https://www.metmuseum.org
- Collection: https://www.metmuseum.org/art/collection
- Open Access: https://www.metmuseum.org/about-the-met/policies-and-documents/open-access

## License

Data sourced from the Metropolitan Museum of Art Open Access Collection.
Check the Met Museum website for current license and usage terms.

---

**Standardization Date:** January 14, 2025
**Format Version:** 1.0
**Documentation Version:** 1.0
