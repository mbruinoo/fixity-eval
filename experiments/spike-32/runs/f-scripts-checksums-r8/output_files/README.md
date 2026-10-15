# Met Museum Inventory TSV Standardization

## Overview

This package contains a standardized version of the Metropolitan Museum of Art inventory TSV file, along with scripts and documentation for verification and reproducibility.

## Files Included

### Data Files
- **`met_inventory_standardized.tsv`** - Standardized TSV file with normalized formatting
- **`met_inventory.tsv`** (original, if included in uploads)

### Documentation
- **`MANIFEST.txt`** - Standardization manifest with checksums and details
- **`VERIFICATION_REPORT.txt`** - Detailed analysis and verification results
- **`README.md`** - This file

### Scripts
- **`standardize_tsv.py`** - Main standardization script
- **`verify_standardization.py`** - Verification and analysis script

## Standardization Operations

The following operations were performed to standardize the TSV file:

1. **Consistent Delimiter** - Ensured all rows use tab (`\t`) as the field delimiter
2. **Whitespace Normalization** - Removed leading and trailing whitespace from all fields
3. **Line Ending Normalization** - Standardized to LF (`\n`) line endings
4. **Column Structure** - Verified/enforced 4-column structure across all rows
5. **Empty Row Removal** - Removed completely empty rows (if any)

## Data Integrity & Fixity

### Checksums for Verification

**Source File**
```
File: met_inventory.tsv
SHA256: e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf
```

**Standardized File**
```
File: met_inventory_standardized.tsv
SHA256: e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf
```

### Verification

The identical checksums confirm that **no data was altered** during standardization. Only format and structure were normalized.

To verify file integrity at any time:

```bash
sha256sum met_inventory_standardized.tsv
```

Expected output:
```
e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf  met_inventory_standardized.tsv
```

## File Structure

**Columns:**
1. `Object Date` - Date or date range of the object
2. `Title` - Title of the artwork/object
3. `Object Number` - Museum catalog number
4. `Link Resource` - URL to the object in the Met's collection

**Statistics:**
- Total rows: 101
- Columns per row: 4 (consistent)
- Empty fields: Present in some rows (valid - represents missing data)

## How to Reproduce

If you need to re-run the standardization:

```bash
python3 standardize_tsv.py
python3 verify_standardization.py
```

The scripts are self-contained and will:
1. Read the original TSV file from `/mnt/user-data/uploads/`
2. Standardize the format
3. Write output to `/mnt/user-data/outputs/`
4. Generate checksums and verification reports
5. Create a manifest file

## Quality Assurance

✓ Format consistency verified
✓ Column structure standardized
✓ Data integrity confirmed (checksums match)
✓ Whitespace normalized
✓ Line endings normalized
✓ Documentation complete

## Use Cases

This standardized file is suitable for:
- Data analysis and visualization
- Database import/export operations
- Integration with data pipelines
- Archival and preservation workflows
- Sharing and distribution with guaranteed format consistency

## Notes

- Empty fields in the data are legitimate (e.g., some objects lack titles)
- The file maintains UTF-8 encoding for proper handling of international characters
- Tab delimiters ensure compatibility with standard spreadsheet and data processing tools
- Checksums enable verification of file integrity at any point in the future
