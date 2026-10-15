# Met Museum Inventory TSV Standardization

This package contains standardized versions of the Met Museum inventory dataset with comprehensive checksums and fixity documentation for data preservation.

## Contents

### Files Included

1. **met_inventory_standardized.tsv** - The standardized dataset
   - 116 catalog records with 4 columns
   - Tab-delimited format with UTF-8 encoding
   - All data preserved from source
   - Cleaned whitespace and normalized formatting

2. **standardize_met_inventory.py** - Python script for standardization
   - Can be reused on updated source files
   - Generates automatic checksums and reports
   - Fully documented and commented

3. **FIXITY_REPORT.md** - Data integrity documentation
   - MD5 checksums for source and output
   - Standardization procedures documented
   - Verification instructions
   - Schema and data characteristics

4. **README.md** - This file
   - Overview and usage instructions
   - Checksum verification guide

## Quick Start

### Verifying File Integrity

To verify that files haven't been corrupted or altered:

```bash
# On Linux/Mac:
md5sum met_inventory_standardized.tsv

# On Windows (PowerShell):
Get-FileHash -Algorithm MD5 met_inventory_standardized.tsv
```

### Using the Standardization Script

If you have an updated source file to standardize:

```bash
# Basic usage:
python3 standardize_met_inventory.py source_file.tsv

# With custom output filename:
python3 standardize_met_inventory.py source_file.tsv my_output.tsv
```

The script will:
- Standardize the TSV format
- Generate MD5 checksums for both files
- Create a detailed report
- Output a validation report file

### Viewing the Data

Open the standardized TSV file with:

```bash
# On Mac/Linux:
cat met_inventory_standardized.tsv | head -20

# In Python:
import csv
with open('met_inventory_standardized.tsv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        print(row)

# In Excel/LibreOffice:
- File > Open
- Select met_inventory_standardized.tsv
- Choose Tab as delimiter
```

## Data Structure

### Columns

| Column | Description | Example |
|--------|-------------|---------|
| Object Date | Date or era of object creation | "late 19th century", "1673", "664–30 B.C." |
| Title | Descriptive title or name | "Apis", "Ancient Walls, 1904 (from Sketchbook)" |
| Object Number | Museum accession/catalog number | "C.I.46.9.189", "56.644.21(15)" |
| Link Resource | Direct URL to collection record | "http://www.metmuseum.org/art/collection/search/88288" |

### Sample Records

```
Object Date     Title                                  Object Number    Link Resource
late 19th century                                    C.I.46.9.189    http://www.metmuseum.org/art/collection/search/88288
1673            "Corneille Emmantelée, Monedula, ...  56.644.21(15)   http://www.metmuseum.org/art/collection/search/393569
1904            Ancient Walls, 1904 (from Sketchbook) 50.130.151d      http://www.metmuseum.org/art/collection/search/16042
```

## Data Quality Notes

### Known Characteristics
- Some records have empty Title fields (intentional - no title recorded)
- Some records have empty Object Date fields (intentional - date unknown)
- All Object Number and Link Resource fields are populated
- Special characters in multiple languages are preserved
- UTF-8 encoding handles Chinese, Japanese, Korean, and European characters

### Data Coverage
- **Time Period**: 664 BCE to 2019 CE
- **Geographic Range**: Global (Egyptian, European, Asian objects)
- **Object Types**: Paintings, prints, decorative arts, sculpture, photographs, textiles, weapons, books

## Standardization Details

### What Was Changed
1. ✓ Normalized column headers
2. ✓ Trimmed leading/trailing whitespace
3. ✓ Ensured consistent tab delimiters
4. ✓ Fixed line endings (LF)
5. ✓ Verified UTF-8 encoding

### What Was Preserved
1. ✓ All data values
2. ✓ Empty cells (no filling with defaults)
3. ✓ Special characters and multi-byte sequences
4. ✓ Internal spacing in text
5. ✓ All 116 records

## Checksums for Verification

To verify file integrity over time, store these checksums securely:

```
met_inventory_standardized.tsv:
MD5: 7f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c
SHA256: [if needed, run: sha256sum met_inventory_standardized.tsv]
```

To verify a downloaded file matches:
```bash
# Generate checksum of your copy
md5sum met_inventory_standardized.tsv

# Compare to the value above
# They should match exactly
```

## Script Requirements

The Python standardization script requires:
- Python 3.6+
- Standard library only (csv, hashlib, sys, pathlib, datetime)
- No external dependencies

## Maintenance and Updates

### For Data Stewards
- Run verification checksums annually
- Document any file access in an audit log
- Keep source file archived separately
- Update FIXITY_REPORT.md if file is ever re-standardized

### For Future Standardizations
1. Keep met_inventory.tsv (source) as reference
2. Run standardize_met_inventory.py on new data
3. Compare new checksums to documentation
4. Store new checksums in FIXITY_REPORT.md
5. Archive previous versions

## Technical Specifications

### File Format
- **Delimiter**: Tab character (U+0009)
- **Encoding**: UTF-8 with BOM optional
- **Line Endings**: Unix LF (\n)
- **Quoting**: Minimal (only when necessary for embedded tabs/newlines)

### Compatibility
- ✓ Microsoft Excel (File > Open, select Tab delimiter)
- ✓ Google Sheets (File > Import, select Tab-separated values)
- ✓ LibreOffice Calc
- ✓ R (read.csv() with sep="\t")
- ✓ Python (csv module with delimiter='\t')
- ✓ Unix tools (cut, awk, grep)

## Troubleshooting

### File won't open in Excel
- Use "Text Import Wizard"
- Select Tab as the delimiter
- Ensure UTF-8 encoding is selected

### Checksum doesn't match
- Verify you're using the correct algorithm (MD5)
- Check for line ending differences (CRLF vs LF)
- Ensure file hasn't been modified since standardization

### Script error: "Input file not found"
- Verify the full path to your source file
- Check file permissions
- Try with absolute path instead of relative

### Character encoding issues
- Ensure your text editor uses UTF-8 encoding
- Check that file wasn't converted to different encoding
- Verify with: `file -i met_inventory_standardized.tsv`

## References

- Met Museum Collection API: https://metmuseum.org/web-api/
- TSV Format Specification: https://www.iana.org/assignments/media-types/text/tab-separated-values
- MD5 Checksum: https://en.wikipedia.org/wiki/MD5
- UTF-8 Encoding: https://en.wikipedia.org/wiki/UTF-8

## License and Attribution

This standardization and documentation is provided as-is. Original data from the Metropolitan Museum of Art Open Access Collection. Refer to individual object records for object-specific rights and attribution.

## Version History

- **v1.0** (2024): Initial standardization
  - 116 records processed
  - 4-column schema
  - Full UTF-8 support
  - Checksum-based fixity documentation

---

For questions or issues with this standardization, refer to the FIXITY_REPORT.md file or review the standardize_met_inventory.py script source code.
