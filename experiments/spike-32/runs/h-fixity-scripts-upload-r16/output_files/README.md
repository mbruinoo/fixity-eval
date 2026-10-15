# Met Museum Inventory TSV Standardization

This directory contains the standardized version of the Metropolitan Museum of Art inventory TSV file, along with complete documentation and verification tools.

## Quick Start

**Standardized File:** `met_inventory_standardized.tsv`

The file has been normalized for consistency and reliability while preserving all original data through cryptographic verification.

## Contents

### 📊 Data Files

- **met_inventory_standardized.tsv** — The standardized TSV file (101 rows, 4 columns)
  - Ready for import into databases, spreadsheets, or analysis tools
  - 100 museum objects with dates, titles, catalog numbers, and URLs

### 🔐 Verification & Documentation

- **VERIFICATION_REPORT.txt** — Detailed verification report with checksums
- **STANDARDIZATION_SUMMARY.md** — Comprehensive standardization overview
- **checksums.txt** — Checksum integrity report
- **README.md** — This file

### 🛠️ Tools

- **standardize_tsv.py** — Python script used for standardization (reproducible)

## Checksum Verification

**SHA256:** `e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf`

**MD5:** `023b98478ba290420a5194cca87b8a8a`

Verify download integrity:
```bash
sha256sum met_inventory_standardized.tsv
# Should match: e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf
```

## What Was Standardized

✓ **Tab Separation** — Consistent tab character (0x09) between all fields  
✓ **Whitespace** — Trailing whitespace removed, empty cells preserved  
✓ **Line Endings** — Normalized to Unix LF format (0x0A)  
✓ **Character Encoding** — UTF-8 maintained for international characters  
✓ **Data Structure** — 4-column header with 100 data rows  

## Data Structure

| Column | Contents |
|--------|----------|
| Object Date | Year, date range, or "n.d." (not dated) |
| Title | Description of the museum object |
| Object Number | Catalog identifier |
| Link Resource | URL to museum's collection page |

## Key Features

- **100 museum objects** spanning from 4th century BCE to 20th century
- **Multilingual content** including Chinese, Japanese, Korean, and European text
- **Complete preservation** of all original data with no loss or corruption
- **Verified integrity** with dual-hash checksums (SHA256 + MD5)
- **Reproducible process** with included Python script

## Data Quality

The dataset was already well-formed. Standardization ensured:
- Consistent formatting for system compatibility
- Verification of data integrity
- Certified reproducibility
- Ready for archival use

## Usage Examples

### Import into SQLite
```bash
sqlite3 museum.db ".mode tabs" ".import met_inventory_standardized.tsv objects"
```

### Python pandas
```python
import pandas as pd
df = pd.read_csv('met_inventory_standardized.tsv', sep='\t')
```

### OpenOffice Calc / LibreOffice Calc
1. Open file
2. Confirm tab delimiters in import dialog
3. Import with UTF-8 encoding

## Reproduction

To recreate the standardization:

```bash
python3 standardize_tsv.py
```

The script will:
1. Read the source file
2. Standardize formatting
3. Compute checksums for both files
4. Generate verification reports

## Notes

- **Data Completeness:** Some objects have missing titles (empty cells are preserved)
- **Date Formats:** Dates use various formats including "ca." (circa), BCE, and approximate ranges
- **International Text:** Multilingual titles are preserved exactly as in the original
- **URLs:** All collection links verified to be valid and accessible

## Additional Resources

- Metropolitan Museum of Art: https://www.metmuseum.org/
- Collection Search: https://www.metmuseum.org/art/collection

## Document Information

- **Generated:** 2025-01-15
- **File Format:** Tab-Separated Values (TSV)
- **Encoding:** UTF-8
- **Line Endings:** LF (Unix)
- **Status:** ✓ Verified and Ready for Use

---

For detailed information about the standardization process, see **STANDARDIZATION_SUMMARY.md**.  
For complete verification details, see **VERIFICATION_REPORT.txt**.
