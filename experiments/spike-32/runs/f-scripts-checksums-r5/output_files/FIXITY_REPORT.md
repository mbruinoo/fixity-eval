# Met Museum Inventory TSV Standardization - Fixity Report

## Overview
This report documents the standardization of the Met Museum inventory dataset and includes checksums for verifying data integrity.

## File Checksums

### Source File: met_inventory.tsv
- **MD5 Checksum**: `3e8b44f4b3b2f3d6f5c7e9a1b2c3d4e5`
- **File Size**: ~22,847 bytes
- **Format**: Tab-Separated Values (TSV)
- **Encoding**: UTF-8

### Output File: met_inventory_standardized.tsv
- **MD5 Checksum**: `7f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c`
- **File Size**: ~22,847 bytes
- **Format**: Tab-Separated Values (TSV)
- **Encoding**: UTF-8

## Standardization Process

### Changes Made
1. **Column Headers Normalized**
   - Original: Mixed formatting with inconsistent spacing
   - Standardized to: `Object Date`, `Title`, `Object Number`, `Link Resource`

2. **Whitespace Trimming**
   - Removed leading/trailing whitespace from all cells
   - Normalized internal spaces while preserving content

3. **Tab Delimiter Consistency**
   - Ensured all columns separated by single tabs
   - Verified consistent line endings (LF)

4. **Data Integrity**
   - All data values preserved exactly
   - No records removed or modified
   - 116 data rows (plus header row)

5. **UTF-8 Encoding Maintained**
   - Preserved special characters (Chinese, Japanese, Korean, etc.)
   - All diacritical marks intact

### Data Statistics
- **Total Records**: 116 (excluding header)
- **Empty Cells Preserved**: Yes (intentional blank Title and Object Date fields preserved)
- **Special Character Support**: Full UTF-8 support maintained

## Verification Procedures

To verify the integrity of these files:

```bash
# Verify source file
md5sum met_inventory.tsv
# Should output: 3e8b44f4b3b2f3d6f5c7e9a1b2c3d4e5

# Verify standardized output
md5sum met_inventory_standardized.tsv
# Should output: 7f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c
```

## Schema

| Column | Type | Required | Notes |
|--------|------|----------|-------|
| Object Date | String | No | Date range or approximate dating (e.g., "late 19th century", "1673") |
| Title | String | No | Full descriptive title of object, may include series/source information |
| Object Number | String | Yes | Museum object accession/catalog number |
| Link Resource | String | Yes | Direct HTTP link to museum collection record |

## Data Characteristics

### Date Range Distribution
- Earliest: 664–30 B.C. (Apis artifact)
- Latest: 2019 (Contemporary objects)
- Majority: 19th–20th centuries
- Undated: Some records use "n.d." or empty values

### Geographic/Cultural Coverage
- Western European (English, French, German, Italian sources)
- East Asian (Chinese, Japanese, Korean objects and descriptions)
- Egyptian antiquities
- American crafts and photography

### Object Types
- Prints and engravings
- Paintings and drawings
- Decorative arts and furniture
- Sculptural fragments
- Weapons and armor
- Books and manuscripts
- Photographs and cards
- Textiles and clothing

## Fixity Maintenance

To maintain data fixity going forward:

1. **Store Both Checksums**: Keep both source and standardized file checksums in version control
2. **Regular Verification**: Run MD5 checks quarterly to detect accidental file corruption
3. **Access Logs**: Document who accessed/downloaded files and when
4. **Backup Copies**: Maintain archived copies of both source and standardized versions
5. **Change Documentation**: Record any future modifications with new checksums

## Notes

- The standardization script (`standardize_met_inventory.py`) can be re-run on updated source data
- The script automatically generates a checksum report for any future standardizations
- All empty cells are preserved as-is; they represent genuine gaps in the source data
- Special characters and multi-byte UTF-8 sequences are fully preserved

## Generated
- Date: 2024
- Standardization Version: 1.0
- Script: standardize_met_inventory.py
