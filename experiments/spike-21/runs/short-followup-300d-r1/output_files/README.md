# Met Museum Inventory Standardization Archive

This archive contains the original inventory data, transformation script, results, and verification documentation.

## Files in this Archive

### Data Files
- **`met_inventory_original.tsv`** - Original unmodified inventory file (100 data rows + header)
- **`met_inventory_standardized.tsv`** - Standardized output file with all transformations applied

### Transformation Script
- **`standardize_met_inventory.py`** - Python 3 script performing all standardization with verification

### Documentation & Logs
- **`standardization.log.json`** - Detailed JSON log with checksums and transformation records
- **`README.md`** - This file

## Transformation Rules Applied

The standardization script performs the following transformations:

1. **Missing Titles**: Any empty or whitespace-only title fields are replaced with `[Untitled]`
2. **Missing Dates**: Any empty or whitespace-only date fields are replaced with `[Unknown]`
3. **Multilingual Titles**: Pipe-separated multilingual entries (e.g., "Chinese|English") extract only the English portion
4. **Whitespace**: Leading and trailing whitespace removed from all fields
5. **Structural Validation**: All rows verified to contain exactly 4 columns

## Verification & Checksums

### Input File Checksums
- **MD5**: `6e430765c4305e4f4ce053f5ea87cbc8`
- **SHA256**: `4b0d42eebae3d781563f5ff3b1b3618e60957ada95aa4a9213b9cf2cc11c8349`
- **Size**: As recorded in standardization.log.json

### Output File Checksums
- **MD5**: `efef65fd16677f40631055293d172e0e`
- **SHA256**: `4e91423acfd91f20e246c44a6228191beca1eed296f7cb7fd877de0ec5ba28d5`
- **Size**: As recorded in standardization.log.json

## Transformation Statistics

```
Total rows processed:           100
Rows with missing dates:        5
Rows with missing titles:       9
Rows with multilingual titles:  3
Total transformations applied:  14
Empty cells remaining:          0 ✓
```

## How to Verify Integrity

To verify that the standardized file hasn't been corrupted:

```bash
# Verify MD5 checksum
md5sum met_inventory_standardized.tsv
# Should output: efef65fd16677f40631055293d172e0e

# Verify SHA256 checksum
sha256sum met_inventory_standardized.tsv
# Should output: 4e91423acfd91f20e246c44a6228191beca1eed296f7cb7fd877de0ec5ba28d5
```

## How to Re-run the Transformation

Ensure Python 3 is installed, then:

```bash
python3 standardize_met_inventory.py
```

The script will:
1. Read the original TSV file
2. Apply all standardization rules
3. Generate the standardized output
4. Produce checksums and verification logs
5. Display transformation statistics

## Detailed Transformation Log

The `standardization.log.json` file contains:
- Timestamp of transformation
- Script version
- Input/output file paths
- Header information
- Complete list of every row transformation (original → standardized)
- Detailed statistics
- File checksums and sizes

To inspect the log:
```bash
cat standardization.log.json | python3 -m json.tool
```

## Data Changes Summary

### Rows with Missing Dates (5 rows)
These were filled with `[Unknown]`:
- Row 4: Object 1994.605.95
- Row 6: Object CP157
- Row 8: Object 14.40.171
- Row 29: "n.d." (normalized)
- Row 51: Portrait of a Man
- Row 53: Quiet Man

### Rows with Missing Titles (9 rows)
These were filled with `[Untitled]`:
- Multiple rows at the beginning with no title information

### Multilingual Titles (3 rows)
These had pipe-separated content, English extraction applied:
- Row 92: Extracted "Arc-shaped pendant (Huang)"
- Row 93: Extracted "Red and Blue, Two Attendants"
- Row 94: Extracted "Five Beauties"

## Validation Notes

- All 100 data rows verified with exactly 4 columns each
- Zero empty cells remaining after standardization
- No data loss - original values preserved in transformation log
- Checksums allow verification of file integrity at any point

## Archival Notes

This standardized dataset is suitable for:
- Database import (all fields populated)
- CSV/TSV tools (consistent structure)
- Data analysis (no missing critical fields)
- Bulk operations (predictable format)

The comprehensive logging enables:
- Audit trail of changes
- Replication of transformation
- Verification of data integrity
- Reverse lookup of original values

---

Generated: 2024
Script Version: 1.0
