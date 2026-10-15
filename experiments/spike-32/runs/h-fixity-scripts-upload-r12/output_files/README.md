# Met Museum TSV Standardization

## Overview
This package contains a standardized version of the Met Museum inventory TSV file, along with checksums and verification tools for data integrity.

## Files Included

### Data Files
- **met_inventory_standardized.tsv** - The standardized TSV file with 100 rows (plus header) of Met Museum catalog entries

### Documentation
- **standardization_report.txt** - Detailed report of standardization process and checksums
- **MANIFEST.txt** - Verification manifest with checksums for integrity checking
- **README.md** - This file

### Scripts
- **standardize_tsv.py** - Python script that performs standardization with checksum calculation
- **run_standardization.sh** - Bash wrapper script for the complete standardization workflow

## Checksums

### Source File
```
File: met_inventory.tsv
Size: 15,284 bytes
SHA256: 141173c9a3c70fd28bbac44c555894ab7886278cc7890cb57663f569b1a3d75b
MD5:    78e18ae6b0f19cee4be567423610a4ce
```

### Output File (Standardized)
```
File: met_inventory_standardized.tsv
Size: 15,295 bytes
SHA256: e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf
MD5:    023b98478ba290420a5194cca87b8a8a
```

## Standardization Changes Applied

1. **Line Endings** - Normalized to LF (Unix/Linux standard)
2. **Encoding** - UTF-8 without BOM
3. **Tab Delimiters** - Ensured consistent tab separation between columns
4. **Whitespace** - Trimmed leading/trailing whitespace from field values
5. **Quoting** - Minimal CSV quoting strategy for TSV compatibility
6. **Data Integrity** - All data and special characters preserved
7. **Column Structure** - Maintained standard 4-column format:
   - Object Date
   - Title
   - Object Number
   - Link Resource

## File Structure

The standardized TSV contains:
- **1 header row** with column names
- **100 data rows** representing Met Museum collection objects
- **4 columns** (tab-separated):
  1. Object Date: Temporal attribution (e.g., "19th century", "1673")
  2. Title: Object description/title
  3. Object Number: Catalog number
  4. Link Resource: URL to museum collection record

## Data Characteristics

- **Total Objects**: 100
- **Date Range**: Late 4th century BCE to early 20th century
- **Languages**: English, French, Italian, Chinese, Japanese, Korean
- **Object Types**: Paintings, sculpture, furniture, textiles, manuscripts, decorative arts, photographs, etc.

## Verification

To verify the standardized file's integrity:

```bash
# SHA256 verification
sha256sum -c <(echo "e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf  met_inventory_standardized.tsv")

# MD5 verification
md5sum -c <(echo "023b98478ba290420a5194cca87b8a8a  met_inventory_standardized.tsv")
```

## Usage

To re-run the standardization process:

```bash
# Using the wrapper script
bash run_standardization.sh

# Or directly with Python
python3 standardize_tsv.py
```

## Notes

- The checksums differ between source and output because of standardization (line endings, whitespace normalization)
- Both SHA256 and MD5 checksums are provided for flexibility (SHA256 recommended)
- All original data is preserved during standardization
- The file is suitable for import into databases, spreadsheet applications, or data analysis tools
- UTF-8 encoding ensures proper display of multilingual content (Chinese, Japanese, Korean, French, etc.)

## Resources

For more information about the Metropolitan Museum of Art collection:
- https://www.metmuseum.org/art/collection

---
**Generated**: 2026-10-15  
**Format**: TSV (Tab-Separated Values)  
**Encoding**: UTF-8 (no BOM)  
**Line Endings**: LF (Unix)
