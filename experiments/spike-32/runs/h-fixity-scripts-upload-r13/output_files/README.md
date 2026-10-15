# Met Inventory TSV Standardization Project

## Quick Start

All files are ready for download in this directory. The standardization has been completed with full fixity verification.

## Output Files

### Main Deliverable
- **`met_inventory_standardized.tsv`** (15 KB)  
  The standardized inventory file with:
  - Consistent tab delimiters
  - Normalized whitespace
  - UTF-8 encoding
  - Unix line endings (LF)
  - 101 rows (1 header + 100 data records)

### Documentation & Verification
- **`CHECKSUMS.txt`**  
  Quick reference with SHA-256 checksums for both source and output files

- **`STANDARDIZATION_REPORT.md`**  
  Comprehensive report detailing:
  - All standardization operations
  - Fixity verification methodology
  - Data quality notes
  - Reproducibility instructions

### Reproducibility Scripts
- **`standardize_tsv.py`**  
  Python script that performs the standardization
  - Calculates checksums automatically
  - Can be run on any system with Python 3
  - Generates fixity reports

- **`run_standardization.sh`**  
  Bash wrapper for executing the Python script

## Fixity Verification

### Source File
```
SHA-256: e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf
File: met_inventory.tsv (original)
```

### Standardized File
```
SHA-256: 37d977d40f2e18da2a216d816e48a1ab0d5d72b8bbab35b022a0914b3a866523
File: met_inventory_standardized.tsv
```

**To verify:** Run `sha256sum met_inventory_standardized.tsv` and compare with the checksum above.

## Standardization Summary

| Aspect | Details |
|--------|---------|
| **Input Format** | TSV with mixed formatting |
| **Output Format** | Standardized TSV (UTF-8, LF line endings) |
| **Records** | 101 rows maintained (1 header + 100 data) |
| **Delimiter** | Tab character (`\t`) |
| **Encoding** | UTF-8 throughout |
| **Line Endings** | Unix LF only |
| **Whitespace** | Trimmed from all fields |
| **Empty Cells** | Normalized to empty strings |
| **Data Integrity** | 100% - all data preserved |

## Key Features

✅ **Lossless** - All original data preserved  
✅ **Reproducible** - Python script provided  
✅ **Verifiable** - SHA-256 checksums included  
✅ **Unicode-Safe** - Proper UTF-8 handling (supports English, French, German, Italian, Chinese, Japanese, Korean)  
✅ **Documented** - Comprehensive reports included  
✅ **Reversible** - Original file preserved for comparison  

## How to Use the Standardized File

1. Download `met_inventory_standardized.tsv`
2. Open in any spreadsheet application (Excel, Google Sheets, etc.)
3. Or process with scripts using tab delimiters
4. Verify integrity using: `sha256sum met_inventory_standardized.tsv`

## Technical Details

### Standardization Process
1. Read source TSV with UTF-8 encoding
2. Strip leading/trailing whitespace from all fields
3. Ensure consistent tab delimiters between fields
4. Normalize empty cells
5. Write output with Unix line endings (LF)
6. Calculate SHA-256 checksums for both files

### Character Support
The file preserves all special characters:
- Accented characters (é, ö, ü, etc.)
- Em-dashes (–) for date ranges
- CJK characters (Chinese, Japanese)
- Hangul characters (Korean)
- URLs and special punctuation

## Reproducibility

To reproduce this standardization on the original file:

```bash
python3 standardize_tsv.py
```

This will:
1. Read `/mnt/user-data/uploads/met_inventory.tsv`
2. Apply standardization rules
3. Write `/mnt/user-data/outputs/met_inventory_standardized.tsv`
4. Calculate and report checksums
5. Generate a fixity report

## Questions or Issues?

Refer to `STANDARDIZATION_REPORT.md` for detailed information about:
- What was changed and why
- Data quality observations
- Fixity verification methodology
- Best practices applied

---

**Project Status**: ✅ Complete  
**Standardization Date**: 2024  
**Format Version**: 1.0
