# Met Museum Inventory TSV Standardization Report

## Fixity & Integrity Verification

### Source File
- **File**: met_inventory.tsv (original)
- **SHA256 Checksum**: `a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf`
- **Total Rows**: 101 (1 header + 100 data rows)
- **Status**: ✓ Integrity verified

### Output File
- **File**: met_inventory_standardized.tsv
- **SHA256 Checksum**: `7cf93a72687692918324a354667e0250c7de67d71041b33b8d4de0ed73f3b10d`
- **Total Rows**: 101 (1 header + 100 data rows)
- **Status**: ✓ Integrity verified

## Standardization Operations Applied

1. **Column Normalization**
   - Standardized column order: `Object Date` → `Title` → `Object Number` → `Link Resource`
   - All columns consistently present and ordered

2. **Whitespace Handling**
   - Removed leading/trailing whitespace from all fields
   - Preserved intentional spaces within field values

3. **Empty Value Standardization**
   - All missing/empty values converted to empty strings
   - Consistent representation across all fields

4. **Sorting**
   - Primary sort: Object Date (chronological order)
   - Secondary sort: Object Number (alphanumeric order)
   - Rows with empty dates appear first

5. **Format Preservation**
   - Tab-delimited format (TSV) maintained
   - Line endings: Unix (LF)
   - Character encoding: UTF-8
   - CSV quoting rules applied for complex values

## Data Quality Notes

- **Rows with no Object Date**: 4 rows (appear first in output)
- **Rows with no Title**: 7 rows
- **Complete records**: 93 rows with all four fields populated
- **Date range**: 4th–3rd century BCE to 1960s
- **Object number patterns**: Various formats including numeric, compound (letters+numbers), and multi-part identifiers

## Verification

### Using SHA256 checksums:
```bash
# Verify source
sha256sum met_inventory.tsv
# Should match: a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf

# Verify output
sha256sum met_inventory_standardized.tsv
# Should match: 7cf93a72687692918324a354667e0250c7de67d71041b33b8d4de0ed73f3b10d
```

### Using provided verification script:
```bash
bash verify_checksums.sh
```

## Files Included

1. **met_inventory_standardized.tsv** - The standardized data file
2. **standardize_met_inventory.py** - Python script used for standardization
3. **verify_checksums.sh** - Bash script to verify file integrity
4. **CHECKSUM_LOG.txt** - Detailed log of checksums and operations
5. **STANDARDIZATION_SUMMARY.md** - This file

## Reproducibility

To reproduce this standardization:
```bash
python3 standardize_met_inventory.py
```

The script will:
- Read the source TSV from `/mnt/user-data/uploads/met_inventory.tsv`
- Apply standardization operations
- Write output to `/mnt/user-data/outputs/met_inventory_standardized.tsv`
- Generate checksums and a log file
- Verify file integrity

---

*Standardization completed: 2026-10-19T02:56:12*
