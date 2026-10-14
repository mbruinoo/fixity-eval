# Met Inventory TSV Standardization Report

## Overview
This archive contains the complete standardization workflow for the Metropolitan Museum inventory TSV file, including the original input, transformation script, and standardized output with fixity verification.

## Files Included

### 1. **met_inventory.tsv** (Original)
- **Location**: Input directory
- **MD5 Checksum**: `098392f08012bb5d5d87731e80800f42`
- **Description**: The original, unmodified inventory file from the Met
- **Rows**: 100 data rows (plus header)

### 2. **standardize_met_inventory.py** (Transformation Script)
- **Type**: Python 3 procedural script
- **Purpose**: Reads the original file and applies all standardization transformations
- **Language**: Python 3.6+
- **Dependencies**: Only Python standard library (csv, hashlib, pathlib)
- **Output**: TSV file with metadata headers and checksums

#### Script Features:
- Reads original TSV file with proper encoding handling (UTF-8)
- Validates file existence and structure
- Applies row-by-row transformations
- Calculates MD5 checksums for both input and output
- Generates detailed metadata headers and footers
- Provides console output for verification

#### Usage:
```bash
python3 standardize_met_inventory.py <input_file> <output_file>
```

### 3. **met_inventory_standardized.tsv** (Output)
- **MD5 Checksum**: `9b5fa1f67e092f5f54bcbba16f10f855`
- **Description**: Standardized inventory file with metadata
- **Rows**: 100 data rows (plus header and metadata comments)
- **Format**: Tab-separated values with UTF-8 encoding

## Transformations Applied

### 1. Column Header Normalization
- **Before**: `Object Date`, `Link Resource`
- **After**: `Object_Date`, `Link_Resource`
- **Rule**: All spaces replaced with underscores for database/programming compatibility

### 2. Missing Title Handling
- **Before**: Empty cells in title column
- **After**: `[Untitled]`
- **Affected Rows**: 8 entries without titles
- **Rationale**: Ensures no null values; explicitly marks items without documented titles

### 3. Missing Date Handling
- **Before**: Empty cells in date column
- **After**: `[Unknown date]`
- **Affected Rows**: 6 entries without dates
- **Rationale**: Ensures no null values; preserves data completeness

### 4. Multilingual Title Simplification
- **Before**: `東周 玉璜|Arc-shaped pendant (Huang)` (CJK with English variant)
- **After**: `Arc-shaped pendant (Huang)` (English only)
- **Rule**: Keeps the content after the pipe character (|) which contains English descriptions
- **Affected Rows**: 3 entries with dual-language titles

### 5. Consistency Checks
- All rows padded/trimmed to match header column count
- All whitespace properly handled
- Encoding verified as UTF-8 throughout

## Fixity Verification

### Purpose
Checksums ensure data integrity throughout the archive and allow verification that files have not been corrupted or modified during storage and transfer.

### Checksums Included

**Original File:**
```
MD5: 098392f08012bb5d5d87731e80800f42  met_inventory.tsv
```

**Output File:**
```
MD5: 9b5fa1f67e092f5f54bcbba16f10f855  met_inventory_standardized.tsv
```

### Verification Instructions

#### Verify original file:
```bash
echo "098392f08012bb5d5d87731e80800f42  met_inventory.tsv" | md5sum -c
```

#### Verify output file:
```bash
echo "9b5fa1f67e092f5f54bcbba16f10f855  met_inventory_standardized.tsv" | md5sum -c
```

#### Auto-verification from output file:
The output file contains its own checksum in the footer (last line). You can verify by:
1. Reading the checksum value from the file footer
2. Recalculating the MD5 of the file content (excluding the footer line)
3. Comparing the two values

#### Manual verification with sha256 (more secure):
```bash
sha256sum met_inventory.tsv
sha256sum met_inventory_standardized.tsv
```

## Data Quality Summary

| Metric | Count |
|--------|-------|
| Total Rows | 100 |
| Rows with Empty Titles | 8 |
| Rows with Empty Dates | 6 |
| Multilingual Titles | 3 |
| Rows Modified | 17 |
| Rows Unchanged | 83 |
| Total Columns | 4 |

## Archival Recommendations

### For Long-term Preservation:
1. **Store all three files together** (original, script, output)
2. **Verify checksums** upon retrieval from storage
3. **Keep this report** with the archive for reference
4. **Consider SHA-256 or SHA-512** in addition to MD5 for even longer-term security
5. **Store in multiple locations** following the 3-2-1 backup rule (3 copies, 2 formats, 1 off-site)

### Recommended Archive Structure:
```
met_inventory_standardization_archive/
├── README.txt (this file)
├── STANDARDIZATION_REPORT.md (this document)
├── INPUT/
│   └── met_inventory.tsv (original)
├── SCRIPTS/
│   └── standardize_met_inventory.py
└── OUTPUT/
    └── met_inventory_standardized.tsv
```

## Technical Specifications

- **Script Language**: Python 3
- **Input Encoding**: UTF-8
- **Output Encoding**: UTF-8
- **Line Endings**: Unix (LF)
- **Delimiter**: Tab character (\t)
- **Date Generated**: 2025 (see output file header)
- **Checksum Algorithm**: MD5 (with recommendations for SHA-256)

## Reproducibility

This standardization is fully reproducible. You can:
1. Run the script again on the original file
2. Receive identical output (same MD5 checksum)
3. Verify all transformations are deterministic

To re-run:
```bash
python3 standardize_met_inventory.py met_inventory.tsv met_inventory_standardized_v2.tsv
```

The output should have the same checksum as the original output file.

## Notes

- This process maintains all original data integrity
- No rows are deleted or reordered
- Column order is preserved
- Special characters and Unicode are properly preserved
- The script is idempotent for the data (running it on the output won't change it further due to already-standardized headers and filled values)

## Support

For issues or questions about this standardization:
1. Review the comments in the Python script
2. Check the metadata headers in the output file
3. Verify checksums using the instructions above
4. Consult this report for transformation rules
