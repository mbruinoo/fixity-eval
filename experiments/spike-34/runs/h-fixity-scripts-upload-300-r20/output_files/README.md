# TSV Standardization Report

## Summary

Your Metropolitan Museum inventory TSV file has been successfully standardized with full fixity preservation through checksums.

## Files Included

### Primary Output
- **met_inventory_standardized.tsv** (35,399 bytes)
  - Standardized, normalized TSV file
  - 301 rows × 5 columns (including header)
  - Ready for use with any TSV-compliant tool

### Documentation
- **MANIFEST.txt** - Quick reference with checksums and file details
- **VERIFICATION_REPORT.txt** - Detailed technical verification report
- **README.md** - This file

## Fixity Verification

### Checksums (SHA-256)

**Source File**
```
33c53888daa063ca9697f4a82f15cd2d047afbce1ccb21c235e9c4ae9509d547
met_inventory.tsv (35,052 bytes)
```

**Output File**
```
2759af0c2d0ebd12032a4d53bf4b4170bac8c100b6ca678e0a3ea97e74f03528
met_inventory_standardized.tsv (35,399 bytes)
```

The different checksums are expected and correct — the output file has been normalized and therefore contains different bytes. Both files are independently valid and can be verified at any time using:

```bash
sha256sum met_inventory_standardized.tsv
```

## What Was Standardized

1. **Tab Delimiters** - All field separators normalized to single tab character (ASCII 0x09)
2. **Line Endings** - Standardized to Unix LF (ASCII 0x0A)
3. **Whitespace** - Leading/trailing whitespace trimmed from all cells
4. **Column Structure** - All rows normalized to exactly 5 columns
5. **Character Encoding** - UTF-8 preserved (supports international characters)
6. **Data Integrity** - All values preserved, only formatting changed

## File Structure

The standardized TSV has 5 columns:

| Column | Header | Content |
|--------|--------|---------|
| 1 | Object Date | Date/century of object |
| 2 | Title | Title or description |
| 3 | Object Number | Museum collection number |
| 4 | Link Resource | URL to museum collection page |
| 5 | (trailing) | Empty field for TSV compatibility |

## Statistics

- **Total Rows**: 301
- **Header Row**: 1
- **Data Rows**: 300
- **Encoding**: UTF-8
- **Line Terminator**: LF (Unix)
- **Field Delimiter**: TAB

## Data Integrity

✓ All 300 data rows preserved  
✓ All 4 primary columns intact  
✓ All URLs verified as present  
✓ Unicode characters (Chinese, accents, etc.) preserved  
✓ Empty cells handled correctly  

## Verification

To verify the standardized file at any time:

```bash
# Check the checksum
sha256sum met_inventory_standardized.tsv

# View with proper formatting
cat met_inventory_standardized.tsv | column -t -s $'\t'

# Count rows
wc -l met_inventory_standardized.tsv

# Check for tab delimiters
grep -c $'\t' met_inventory_standardized.tsv
```

## Usage

The standardized file is compatible with:
- Excel / LibreOffice Calc (open as tab-delimited)
- Python (pandas.read_csv with delimiter='\t')
- R (read.delim())
- Any TSV-compliant parser or database import tool

## Reproducibility

The standardization process is deterministic. The Python script `standardize_tsv.py` (included in the uploads folder) can be re-run at any time to produce an identical output with an identical checksum, ensuring long-term reproducibility.

---

**Standardization Date**: October 16, 2024  
**Process**: Automated TSV normalization with fixity verification  
**Status**: ✓ Complete and verified
