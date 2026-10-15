# TSV Standardization Package - Metropolitan Museum Inventory

## Quick Start

This archive contains the standardized version of the Met's inventory TSV file along with verification scripts and documentation.

**Main File**: `met_inventory_standardized.tsv`

## Package Contents

### Data File
- **met_inventory_standardized.tsv** (15 KB)
  - The standardized inventory file
  - 101 rows (1 header + 100 museum objects)
  - 4 tab-delimited columns
  - UTF-8 encoding with Unix line endings

### Documentation
- **VERIFICATION_SUMMARY.txt** - Quick verification checklist and results
- **STANDARDIZATION_REPORT.md** - Comprehensive standardization details
- **README.md** - This file

### Scripts & Checksums
- **standardize_tsv.py** - Python script that performs the standardization
- **checksum_source.py** - Python script to verify file integrity
- **checksums.txt** - SHA-256 checksums for source and output files
- **source_checksum.txt** - Source file checksum reference

## File Structure

The standardized TSV contains:

| Column | Description |
|--------|-------------|
| Object Date | Date or period (e.g., "1673", "ca. 1479–1458 B.C.", "19th century") |
| Title | Object title or description (may be empty for some entries) |
| Object Number | Museum catalog number (e.g., "C.I.46.9.189") |
| Link Resource | URL to object in Met's online collection |

### Sample Rows:
```
Object Date	Title	Object Number	Link Resource
1673	"Corneille Emmantelée, Monedula, Chouca"...	56.644.21(15)	http://www.metmuseum.org/art/collection/search/393569
19th century		81.1.379	http://www.metmuseum.org/art/collection/search/59814
1756	Leopold Mozart playing the violin	01.2.63	http://www.metmuseum.org/art/collection/search/371966
```

## Checksums

For data integrity verification:

**Source File (Original)**
```
SHA-256: e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf
```

**Standardized File**
```
SHA-256: 6dacf89c79b4322e0a21c34c379671ec614bbd5501a20729ac72d8e806f629dd
```

### Verify Checksums
```bash
# On Linux/Mac:
sha256sum met_inventory_standardized.tsv

# On Windows (PowerShell):
certUtil -hashfile met_inventory_standardized.tsv SHA256
```

## Using the Standardized File

### Import into Excel/Sheets
1. Open the TSV file directly (most spreadsheet applications recognize tab delimiters)
2. Or use File → Import with delimiter set to Tab

### Import into Python
```python
import pandas as pd

df = pd.read_csv('met_inventory_standardized.tsv', sep='\t', encoding='utf-8')
print(df.head())
print(f"Total objects: {len(df)}")
```

### Import into SQLite
```bash
sqlite3 museum.db
.mode tabs
.import met_inventory_standardized.tsv museum_inventory
```

### Process with Command Line Tools
```bash
# Count rows
wc -l met_inventory_standardized.tsv

# Extract specific column (e.g., all URLs)
cut -f4 met_inventory_standardized.tsv

# Find entries by date
grep "1756" met_inventory_standardized.tsv
```

## Standardization Details

### What Was Standardized
✓ Tab-delimited format validation  
✓ Whitespace normalization  
✓ Line ending standardization (Unix LF)  
✓ Column consistency (4 columns per row)  
✓ UTF-8 encoding (multilingual support)  
✓ Data integrity verification  

### What Was NOT Changed
✓ Data content (all 100 objects preserved)  
✓ Character encoding (UTF-8 maintained)  
✓ Field values (no truncation or modification)  
✓ Order of rows (original sequence preserved)  

### Languages Supported
- English
- French
- Italian
- German
- Japanese
- Chinese (Simplified & Traditional)
- Korean

## Quality Assurance

- ✓ 100% data preservation verified
- ✓ All 4 columns intact in every row
- ✓ 101 lines total (header + 100 objects)
- ✓ All URLs verified as valid references
- ✓ UTF-8 encoding confirmed
- ✓ No data loss or corruption detected

## Running the Scripts

### Re-standardize the File
```bash
python3 standardize_tsv.py
```

### Verify Source Integrity
```bash
python3 checksum_source.py
```

## Troubleshooting

### Issue: File appears corrupted in text editor
- Solution: Ensure your editor supports UTF-8 encoding
- Recommendation: Use UTF-8 compatible editor (VS Code, Sublime, vim, etc.)

### Issue: Empty cells appearing as different content
- Solution: These are genuine empty cells in the Title column
- Note: Some museum objects lack specific titles in the original data

### Issue: Special characters not displaying correctly
- Solution: Ensure file is opened with UTF-8 encoding
- Check: File encoding should be "UTF-8" not "UTF-16" or "Latin-1"

### Issue: Import errors in Excel on Windows
- Solution: Use Data → From Text/CSV and select UTF-8 encoding
- Alternative: Use LibreOffice Calc instead

## Technical Specifications

| Property | Value |
|----------|-------|
| Format | Tab-Separated Values (TSV) |
| Encoding | UTF-8 (without BOM) |
| Line Endings | LF (Unix/Linux/Mac) |
| Delimiter | Tab (U+0009) |
| Quote Character | None (original fields preserved) |
| Row Count | 101 (1 header + 100 data) |
| Column Count | 4 |
| File Size | ~15 KB |

## Version History

- **v1.0** (2025) - Initial standardization
  - Standardized encoding and line endings
  - Validated data integrity
  - Generated verification checksums

## Support & Documentation

For detailed information:
- See `STANDARDIZATION_REPORT.md` for comprehensive details
- See `VERIFICATION_SUMMARY.txt` for verification results
- Review Python scripts for implementation details

## Citation

If you use this dataset in research, please cite:
```
Metropolitan Museum of Art. (2024). Met Collection Database [Data file].
Retrieved from http://www.metmuseum.org/
Standardized TSV version prepared [2025]
```

## License

The underlying data is from the Metropolitan Museum of Art's public collection database. Please refer to the Met's usage guidelines at https://www.metmuseum.org/information/about-the-met

---

**Archive generated**: 2025  
**Standardization status**: ✓ Complete  
**Data integrity**: ✓ Verified  
**Ready for use**: ✓ Yes
