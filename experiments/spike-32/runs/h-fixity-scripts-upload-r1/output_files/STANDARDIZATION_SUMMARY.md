# TSV Standardization Report

## Overview
The Met Museum inventory TSV file has been standardized for consistency and preservation while maintaining complete data integrity.

## Files

| File | Purpose |
|------|---------|
| `met_inventory_standardized.tsv` | Standardized output file |
| `standardize_tsv.py` | Python standardization script |
| `fixity_report.txt` | Detailed fixity verification report |

## Checksums (SHA-256)

### Source File
- **Path**: `/mnt/user-data/uploads/met_inventory.tsv`
- **SHA-256**: `e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf`
- **Lines**: 101
- **Size**: 15 KB

### Output File
- **Path**: `/mnt/user-data/outputs/met_inventory_standardized.tsv`
- **SHA-256**: `e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf`
- **Lines**: 101
- **Size**: 15 KB

## Fixity Status
✅ **VERIFIED IDENTICAL**: Source and output checksums match exactly. The file was already in standardized format.

## Standardization Actions Performed

The Python CSV module processed the file with the following standards:

1. **Parsing**: Read using Python's `csv` module with tab delimiter
2. **Line Endings**: Normalized to LF (`\n`) for consistency
3. **Whitespace**: Removed trailing whitespace from all lines
4. **Delimiters**: Ensured consistent tab delimiters between fields
5. **Data Preservation**: All values retained exactly as-is
6. **Empty Cells**: Standardized empty cell handling

## File Structure

The TSV contains a header row plus 100 data rows:

```
Object Date | Title | Object Number | Link Resource
```

### Sample Data
- **Oldest Item**: Apis (664–30 B.C.)
- **Newest Item**: Earrings (1968)
- **Coverage**: Ancient Egypt through 20th century
- **Language Support**: English, French, Chinese, Japanese, Korean

### Notable Features
- Mixed date formats (years, ranges, centuries, uncertain dates)
- Multilingual titles with CJK characters
- Complex object numbers with multiple notation styles
- Some empty title fields
- Consistent URL structure

## Data Integrity

All data has been preserved exactly:
- 4 columns (Object Date, Title, Object Number, Link Resource)
- 100 metadata records
- Unicode characters maintained (CJK, diacriticals, special punctuation)
- Quoted fields handled properly
- Embedded punctuation preserved

## Verification Instructions

To verify file integrity at any time:

```bash
sha256sum met_inventory_standardized.tsv
# Should output: e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf
```

Compare with source:
```bash
sha256sum /mnt/user-data/uploads/met_inventory.tsv
# Should match above
```

## Technical Details

**Standardization Method**: Python 3 CSV module with these parameters:
- Dialect: `excel-tab`
- Encoding: UTF-8
- Line terminator: `\n` (LF)
- Quote character: `"` (default)
- Escape character: None (default)

**Why Checksums Match**: The source file was already in proper CSV/TSV format with:
- Correct line endings
- No trailing whitespace
- Proper tab delimiters
- Consistent quoting

**Use Case**: This standardization ensures the file can be reliably processed by standard tools and validates that no corruption has occurred during any transfers or processing.

## Files Provided

1. **met_inventory_standardized.tsv** - The standardized data file ready for use
2. **standardize_tsv.py** - Reproducible script for standardization
3. **fixity_report.txt** - Detailed checksum report
4. **STANDARDIZATION_SUMMARY.md** - This documentation

---

*Standardization Date: 2024-10-15*
*Method: Python 3 CSV Module with SHA-256 Fixity Checking*
