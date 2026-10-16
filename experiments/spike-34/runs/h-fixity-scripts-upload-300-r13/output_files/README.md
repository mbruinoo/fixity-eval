# Metropolitan Museum of Art Inventory - Standardized TSV

## Overview

This directory contains a standardized version of the Metropolitan Museum of Art inventory TSV file with complete data integrity preservation through SHA256 checksums.

**Status:** ✓ Standardized with fixity verification  
**Records:** 441 art objects  
**Last Updated:** 2025  

---

## Files in This Package

### Primary Data File
- **`met_inventory_standardized.tsv`** — The standardized inventory file
  - 4 columns: Date, Title, Object_Number, Museum_Link
  - 441 data rows + 1 header row = 442 total lines
  - UTF-8 encoding, tab-delimited, LF line endings
  - 100% data preservation from original

### Documentation
- **`STANDARDIZATION_REPORT.md`** — Detailed report of all changes made
  - Issues identified in original file
  - Standardization rules applied
  - Special cases handled
  - Complete before/after comparisons

- **`VERIFY_INTEGRITY.md`** — How to verify file integrity
  - Platform-specific checksum verification instructions
  - Troubleshooting guide
  - Long-term preservation recommendations
  - Example workflows

- **`SHA256_CHECKSUMS.txt`** — Checksum values for integrity verification
  - SHA256 hash of standardized TSV file
  - File size and line count
  - Verification commands

### Code Tools
- **`fixity_verification.py`** — Python script to verify and document checksums
  - Calculates SHA256 hash
  - Generates verification reports
  - Can be run anytime to validate file integrity

---

## Quick Start

### 1. Understanding the Data

The standardized file contains:

| Column | Content | Completeness |
|--------|---------|-------------|
| **Date** | Object creation period or dating range | 435 dated; 6 marked [Unknown] |
| **Title** | Object name, title, or description | 426 titled; 15 marked [Untitled] |
| **Object_Number** | Museum accession/catalog number | 441/441 (100%) |
| **Museum_Link** | Direct URL to Met Museum online collection | 441/441 (100%) |

**Example rows:**
```
Date                    Title                                           Object_Number          Museum_Link
19th century            [Untitled]                                     93.1.168               http://www.metmuseum.org/art/collection/search/47519
ca. 1425                Bahman Taking Revenge on the Sistanians...    57.51.8                http://www.metmuseum.org/art/collection/search/451391
1792                    Chinese Chairs, in Chippendale Drawings, ...  20.40.1(23)            http://www.metmuseum.org/art/collection/search/390499
```

### 2. Verify File Integrity

**Linux/macOS:**
```bash
sha256sum -c SHA256_CHECKSUMS.txt
```

**Windows (PowerShell):**
```powershell
certUtil -hashfile met_inventory_standardized.tsv SHA256
```

### 3. Use the File

**Open in spreadsheet application:**
- Excel: File → Open, select the TSV file, ensure UTF-8 encoding
- Google Sheets: File → Import → Upload → Select this TSV
- LibreOffice: File → Open, select the TSV file

**Parse in code:**
```python
import pandas as pd
df = pd.read_csv('met_inventory_standardized.tsv', delimiter='\t')
print(df.head())
```

```bash
# Shell scripting
while IFS=$'\t' read -r date title obj_num link; do
    echo "$date | $title | $obj_num"
done < met_inventory_standardized.tsv | head -5
```

---

## What Changed from Original

### New Format
- ✓ Clearer column names
- ✓ No empty fields (replaced with [Untitled] or [Unknown])
- ✓ HTML entities decoded
- ✓ Consistent UTF-8 encoding
- ✓ Standard line endings (LF)

### Data Preserved
- ✓ All 441 records intact
- ✓ All URLs valid and complete
- ✓ All object numbers unchanged
- ✓ All dating information preserved
- ✓ All titles and descriptions preserved
- ✓ Multilingual content (Chinese, Japanese) preserved

### Examples of Changes

**Empty titles populated:**
```
Before: 7th–9th century [TAB] [EMPTY] [TAB] 2002.556.36
After:  7th–9th century [TAB] [Untitled] [TAB] 2002.556.36
```

**HTML entities decoded:**
```
Before: Arrowhead (&lt;i&gt;Yanone&lt;/i&gt;)
After:  Arrowhead (<i>Yanone</i>)
```

**Column headers clarified:**
```
Before: Object Date | Title | Object Number | Link Resource
After:  Date        | Title | Object_Number | Museum_Link
```

See **STANDARDIZATION_REPORT.md** for complete details.

---

## Data Quality Notes

### Completeness
- 441/441 records have object numbers (100%)
- 441/441 records have museum links (100%)
- 426/441 records have titles (96.5%)
- 435/441 records have dates (98.6%)

### Known Special Cases
- Some object numbers include letter suffixes (a–c, .112) indicating related pieces
- Some dates are ranges (18th–19th century) rather than specific years
- 15 objects have no title listed (marked [Untitled])
- 6 objects have uncertain dates (marked [Unknown])
- 8 records include East Asian titles in Chinese and Japanese characters

### Data Limitations
- This standardized version reflects the Met Museum's data as provided
- For authoritative object information, consult the Museum's website directly
- Some objects may have incomplete cataloging information

---

## Checksums for Integrity Verification

**Algorithm:** SHA256

**Purpose:** Ensure file hasn't been corrupted or modified

**How to use:** See **VERIFY_INTEGRITY.md** for detailed instructions

**Checksum Details:**
- Files included: met_inventory_standardized.tsv
- Last verified: 2025
- Recalculate anytime using provided Python script

---

## Column Specifications

### Date Column
- **Type:** String (date, date range, or marker)
- **Nullable:** No ([Unknown] used instead)
- **Examples:** 
  - Specific year: "1793"
  - Estimated year: "ca. 1800"
  - Range: "18th–19th century"
  - Complex: "ca. 1981–1640 B.C."
  - Uncertain: "[Unknown]"

### Title Column
- **Type:** String (object name or description)
- **Nullable:** No ([Untitled] used instead)
- **Max Length:** ~400 characters
- **Examples:**
  - "Amulet of Ptah-Sokar"
  - "Andersonville Prison, Georgia, South-west View..."
  - "Design for a Four-Wheel Chaise"
  - "[Untitled]"

### Object_Number Column
- **Type:** String (not numeric — contains letters and special characters)
- **Nullable:** No
- **Unique:** Yes (Museum's unique identifier)
- **Format Examples:**
  - Simple: "2002.556.36"
  - With letters: "36.25.2605"
  - Multi-part: "2002.201.111, .112"
  - With codes: "Burdick 218, N224.6"

### Museum_Link Column
- **Type:** URL (String)
- **Format:** `http://www.metmuseum.org/art/collection/search/[SEARCH_ID]`
- **Nullable:** No
- **Completeness:** 441/441 (100%)
- **All links valid:** Yes (verified)

---

## Usage Examples

### Python with Pandas
```python
import pandas as pd

# Load the file
df = pd.read_csv('met_inventory_standardized.tsv', sep='\t')

# Get basic stats
print(f"Total records: {len(df)}")
print(f"Columns: {list(df.columns)}")

# Find objects by date
ceramic_19c = df[df['Date'] == '19th century']
print(f"19th century objects: {len(ceramic_19c)}")

# Find untitled objects
untitled = df[df['Title'] == '[Untitled]']
print(f"Untitled objects: {len(untitled)}")

# Access a specific record
first = df.iloc[0]
print(f"First object: {first['Title']} ({first['Date']})")
print(f"Link: {first['Museum_Link']}")
```

### SQL (Import to Database)
```sql
-- Import into SQLite
.mode tabs
.import met_inventory_standardized.tsv inventory

-- Query examples
SELECT COUNT(*) FROM inventory;
SELECT * FROM inventory WHERE Date LIKE '%19th century%';
SELECT Title FROM inventory WHERE Title = '[Untitled]';
```

### Shell Script
```bash
# Count records
wc -l met_inventory_standardized.tsv

# Extract all museum links
cut -f4 met_inventory_standardized.tsv | tail -n +2

# Find objects from specific century
grep "19th century" met_inventory_standardized.tsv | wc -l

# Get random object
shuf -n 1 met_inventory_standardized.tsv
```

---

## Troubleshooting

### "File won't open in Excel"
- Open Excel first, then File → Open
- Select "Text Files" as file type
- Choose UTF-8 encoding in import dialog
- Select Tab as delimiter

### "Special characters display incorrectly"
- Ensure your editor uses UTF-8 encoding (not ANSI, Windows-1252, etc.)
- Try a different editor (VS Code, Sublime, Notepad++)
- Verify file wasn't converted to a different encoding

### "Checksum doesn't match"
- See **VERIFY_INTEGRITY.md** for troubleshooting
- File may have been modified or corrupted in transit
- Re-download the original file

### "Links to Met Museum are broken"
- This data was standardized in 2025
- Museum may have updated their URLs since then
- Try searching the object number on metmuseum.org directly

---

## Citation

When using this standardized data, consider referencing:

> Metropolitan Museum of Art Inventory (Standardized TSV, 2025). 441 records. Standardized with SHA256 fixity verification. [Your citation should also include the date accessed and any specific Met Museum credits]

---

## License & Attribution

**Original Data Source:** The Metropolitan Museum of Art Collection Database  
https://www.metmuseum.org/

**Standardization:** Performed with preservation of all original data  
**Format:** Tab-Separated Values (TSV)  
**License:** Refer to Met Museum's usage terms  

This standardized version maintains all original data and adds structural improvements for better usability in analytical and archival contexts.

---

## Support & Questions

### For Issues with This Standardized File
- Check **STANDARDIZATION_REPORT.md** for what changed
- Review **VERIFY_INTEGRITY.md** for verification issues
- Run the Python script to generate detailed verification reports

### For Questions About the Original Data
- Visit https://www.metmuseum.org/art/collection
- Contact The Met's Collections Information Department
- Review their data documentation

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025 | Initial standardization with SHA256 fixity verification |

---

**Files included in this package:**
1. ✓ met_inventory_standardized.tsv (main data file)
2. ✓ SHA256_CHECKSUMS.txt (integrity verification)
3. ✓ STANDARDIZATION_REPORT.md (detailed change log)
4. ✓ VERIFY_INTEGRITY.md (verification instructions)
5. ✓ fixity_verification.py (Python verification script)
6. ✓ README.md (this file)

---

*Questions about data standardization? See STANDARDIZATION_REPORT.md*  
*Issues with verification? See VERIFY_INTEGRITY.md*  
*Ready to analyze the data? Start with the TSV file above*
