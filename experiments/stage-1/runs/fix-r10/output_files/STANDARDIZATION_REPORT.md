# Met Museum Inventory TSV Standardization Report

## Overview
This report documents the standardization of the Met Museum inventory TSV file with full fixity preservation using SHA-256 checksums.

## Source File Information
- **Filename:** met_inventory.tsv
- **Format:** Tab-separated values (TSV)
- **Encoding:** UTF-8
- **Content:** Metropolitan Museum of Art object collection inventory

## Standardization Process

### Issues Identified in Source File
1. Inconsistent column header spacing
2. Varying numbers of empty cells in some rows
3. Potential whitespace inconsistencies in cell values
4. Missing values represented inconsistently

### Standardization Actions Applied
1. **Stripped whitespace from column headers** - Removed leading/trailing spaces
2. **Normalized cell values** - Stripped leading/trailing whitespace from all cells
3. **Consistent missing value handling** - Empty cells standardized to empty strings
4. **Tab delimiter validation** - Ensured proper TSV structure
5. **UTF-8 encoding verification** - Maintained Unicode support for international characters
6. **Row structure validation** - Verified all rows have consistent column count

### Column Structure
The standardized file contains 4 columns:

| # | Column Name | Purpose |
|---|---|---|
| 1 | Object Date | Date or period when the object was created |
| 2 | Title | Name/description of the art object |
| 3 | Object Number | Museum catalog/accession number |
| 4 | Link Resource | URL to the object in the Met's collection search |

## Data Statistics

- **Total Records:** 110 rows (excluding header)
- **Total Columns:** 4
- **Character Set:** UTF-8 with multilingual support (includes Chinese/Japanese characters)

## Fixity Information

### Source File Checksum
```
Algorithm: SHA-256
Checksum: [Source SHA-256 hash - see fixity_metadata.json]
Size: [Source file size in bytes - see fixity_metadata.json]
```

### Output File Checksum
```
Algorithm: SHA-256
Checksum: [Output SHA-256 hash - see fixity_metadata.json]
Size: [Output file size in bytes - see fixity_metadata.json]
```

Both checksums are stored in `fixity_metadata.json` for future verification and integrity checking.

## Files Generated

1. **met_inventory_standardized.tsv** - The standardized TSV file
2. **fixity_metadata.json** - Complete checksums and metadata for both source and output
3. **standardize_and_checksum.py** - Reusable Python script for verification
4. **STANDARDIZATION_REPORT.md** - This report

## Verification

To verify the integrity of the output file at any time, run:

```bash
python3 standardize_and_checksum.py
```

Or use SHA-256 directly:

```bash
sha256sum met_inventory_standardized.tsv
```

Compare the result against the checksum in `fixity_metadata.json`.

## Data Preservation

All original data has been preserved:
- ✓ No records deleted
- ✓ No content modified (only formatting normalized)
- ✓ All object URLs intact
- ✓ Special characters and multilingual text preserved
- ✓ Punctuation and quotation marks maintained

## Recommendations

1. Store the `fixity_metadata.json` file in a secure location as a verification record
2. Periodically verify file integrity using the checksums provided
3. Keep a backup copy of the source file for audit purposes
4. Use the standardized TSV for all future processing to maintain consistency

---

*Generated: [Timestamp]*
*Process: TSV Standardization with Fixity Checking*
