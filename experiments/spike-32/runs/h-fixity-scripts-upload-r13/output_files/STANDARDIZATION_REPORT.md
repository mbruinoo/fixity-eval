# Met Museum Inventory TSV Standardization Report

## Overview
This report documents the standardization of `met_inventory.tsv` with full fixity verification through cryptographic checksums.

## Source File Information
- **Filename**: met_inventory.tsv
- **Records**: 101 rows (1 header + 100 data rows)
- **Columns**: 4 (Object Date, Title, Object Number, Link Resource)
- **Encoding**: UTF-8
- **SHA256 Checksum**: `e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf`

## Standardization Operations Performed

### 1. **Consistent Tab Delimiters**
   - Verified all fields are separated by single tab characters (`\t`)
   - Removed any inconsistent delimiter patterns
   - Pattern: `\t` (U+0009)

### 2. **Whitespace Normalization**
   - Stripped leading and trailing whitespace from all fields
   - Preserved internal spaces within field values
   - Empty fields standardized to explicit empty strings

### 3. **Empty Cell Handling**
   - Normalized all missing/empty cells consistently
   - Empty fields represented as empty strings between delimiters
   - Example: `row_data\t\tvalue` (empty Title field)

### 4. **Encoding Standardization**
   - All content standardized to UTF-8 encoding
   - Preserved special characters: em-dashes (–), accented characters, CJK characters, Hangul
   - Verified byte-level consistency

### 5. **Line Ending Standardization**
   - Converted all line endings to Unix format (LF only, `\n`)
   - Removed any carriage returns or mixed line endings
   - Each row ends with single newline character

## Output File Information
- **Filename**: met_inventory_standardized.tsv
- **Records**: 101 rows (1 header + 100 data rows)
- **Columns**: 4 (Object Date, Title, Object Number, Link Resource)
- **Encoding**: UTF-8
- **Line Endings**: LF (Unix)
- **SHA256 Checksum**: `37d977d40f2e18da2a216d816e48a1ab0d5d72b8bbab35b022a0914b3a866523`

## Fixity Verification

### Checksum Comparison
| Metric | Value |
|--------|-------|
| Source SHA256 | e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf |
| Output SHA256 | 37d977d40f2e18da2a216d816e48a1ab0d5d72b8bbab35b022a0914b3a866523 |
| Algorithm | SHA-256 |

**Note**: The checksums differ because the standardization process modified the file's content format (whitespace removal, consistent delimiters, line ending normalization). Both checksums are valid records of their respective file states.

### Verification Method
To verify file integrity at any time, run:
```bash
sha256sum met_inventory_standardized.tsv
# Should output: 37d977d40f2e18da2a216d816e48a1ab0d5d72b8bbab35b022a0914b3a866523
```

## Data Quality Notes

### Preserved Elements
- All object data intact
- Special characters preserved (em-dashes, accented characters, CJK, Hangul)
- URL structures maintained
- Object numbers in original format

### Content Observations
- Some entries have empty Title fields (rows 2-9, others)
- Some entries have empty Object Date fields (rows 8, 87, 90, 98-99)
- Multilingual content: English, French, German, Italian, Chinese, Japanese, Korean
- Date formats vary: years, date ranges, periods, descriptions ("n.d.", "ca.", "probably", etc.)

## Files Generated

1. **met_inventory_standardized.tsv** - The standardized TSV file
2. **CHECKSUMS.txt** - Checksum verification record
3. **standardize_tsv.py** - Python standardization script (reproducible)
4. **run_standardization.sh** - Bash wrapper script
5. **STANDARDIZATION_REPORT.md** - This documentation

## Reproducibility

The standardization process is fully reproducible using the provided Python script:

```bash
python3 standardize_tsv.py
```

The script:
- Reads the original TSV with proper UTF-8 handling
- Applies standardization rules consistently
- Generates checksums for both source and output
- Creates a fixity report

## Best Practices Applied

✓ Cryptographic checksums for integrity verification  
✓ Lossless transformation (all data preserved)  
✓ Unicode normalization (UTF-8)  
✓ Consistent delimiter usage  
✓ Reproducible processing (script provided)  
✓ Complete documentation  
✓ Separate fixity verification record  

---

Generated: 2024
Report Version: 1.0
