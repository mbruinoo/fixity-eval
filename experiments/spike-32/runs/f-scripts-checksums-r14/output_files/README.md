# Met Inventory TSV Standardization Kit

## Quick Start

This kit contains a standardized version of the Metropolitan Museum's inventory data along with tools to verify its integrity.

## Files Included

### Data Files
- **met_inventory_standardized.tsv** - The standardized inventory data (104 records, 4 columns)

### Documentation
- **STANDARDIZATION_REPORT.md** - Detailed report on standardization process
- **README.md** - This file

### Tools & Metadata
- **standardize_tsv.py** - Python script to standardize TSV files (reusable)
- **CHECKSUMS.json** - File integrity metadata

## Quick Verification

To verify the standardized file hasn't been corrupted:

```bash
# Calculate the SHA-256 checksum
sha256sum met_inventory_standardized.tsv

# Compare with the value in CHECKSUMS.json["output_checksum_sha256"]
```

## Using the Data

### Python (Pandas)
```python
import pandas as pd
df = pd.read_csv('met_inventory_standardized.tsv', sep='\t', encoding='utf-8')
print(df.head())
```

### Command Line (View)
```bash
# Display first 10 rows
head -10 met_inventory_standardized.tsv

# Count records
wc -l met_inventory_standardized.tsv
```

### Excel/Sheets
Simply open the file - most spreadsheet applications recognize TSV format automatically.

## Standardization Summary

| Aspect | Standard Applied |
|--------|------------------|
| Encoding | UTF-8 |
| Line Endings | LF (Unix) |
| Delimiter | Tab (ASCII 0x09) |
| Quoting | Minimal (RFC 4180) |
| Whitespace | Trimmed from headers and edges |

## Data Structure

```
Object Date │ Title │ Object Number │ Link Resource
─────────────┼───────┼───────────────┼────────────────
late 19th    │       │ C.I.46.9.189  │ http://www...
century     │       │               │
```

**Columns:**
1. **Object Date** - When the object was made (e.g., "1890", "ca. 1500–1450 B.C.", "n.d.")
2. **Title** - Object name (often empty for inventory items)
3. **Object Number** - Museum catalog number
4. **Link Resource** - URL to the full record at metmuseum.org

## Integrity & Fixity

All files use SHA-256 checksums to preserve integrity:

- Source checksum stored in CHECKSUMS.json
- Output checksum stored in CHECKSUMS.json
- Re-verify anytime: `sha256sum met_inventory_standardized.tsv`

If the checksum changes, the file content has been modified (which may be intentional or indicate corruption).

## Replicating the Standardization

To standardize a similar file:

```bash
python3 standardize_tsv.py
```

The script will:
1. Read the original TSV
2. Calculate source checksum
3. Apply standardization rules
4. Generate output file
5. Calculate output checksum
6. Create verification files
7. Generate a detailed log

## Data Characteristics

- **Records**: 104 museum objects
- **Languages**: English, French, Italian, Chinese, Japanese, Korean
- **Date Range**: 664 BCE to 1989 CE
- **All URLs**: Point to metmuseum.org collection database

## Questions?

Refer to **STANDARDIZATION_REPORT.md** for detailed information about:
- Standardization rules
- Data analysis
- ISO 14721 OAIS compliance
- Best practices for use and preservation

---

**Created**: 2025-10-14  
**Format Version**: 1.0  
**Checksum Algorithm**: SHA-256
