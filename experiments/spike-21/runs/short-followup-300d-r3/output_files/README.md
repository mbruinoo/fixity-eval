# MET Museum Inventory TSV Standardization

## Overview
This archive contains the original MET Museum inventory data, a Python transformation script, and the standardized output, along with checksums for verification.

## Files Included

### 1. `met_inventory_original.tsv`
- **Purpose**: Original source file (before standardization)
- **Format**: Tab-separated values (TSV)
- **Rows**: 101 (including header)
- **Size**: 11,259 bytes
- **SHA256**: `4b0d42eebae3d781563f5ff3b1b3618e60957ada95aa4a9213b9cf2cc11c8349`
- **Status**: Reference/Archive

### 2. `transform_met_inventory.py`
- **Purpose**: Python script to standardize the TSV file
- **Type**: Procedural transformation script
- **Size**: Python source code
- **SHA256**: `2a91596883ccf314351354c9984b2b73ed223398cff029b8a05ead3d9fbcc37c`
- **Requirements**: Python 3.6+
- **Dependencies**: Standard library only (csv, hashlib, pathlib, sys, datetime)

#### Transformation Logic
The script performs the following operations:

1. **Column Validation**: Ensures all rows have exactly 4 columns
   - Pads rows with fewer than 4 columns
   - Truncates rows with more than 4 columns (with issue logging)

2. **UTF-8 Encoding**: Preserves all character encoding including:
   - Accented characters (é, ç, etc.)
   - Chinese/Japanese text (東周 玉璜, 棟方志功筆, etc.)
   - Special Unicode characters (–, —)

3. **Data Preservation**: 
   - Maintains all values including empty cells
   - Preserves row count (101 rows before and after)
   - No data loss or modification

4. **Checksum Generation**: 
   - Calculates SHA256 for input, output, and script files
   - Enables verification of transformation integrity

### 3. `met_inventory_standardized.tsv`
- **Purpose**: Output file after standardization
- **Format**: Tab-separated values (TSV)
- **Rows**: 101 (including header)
- **Size**: 11,269 bytes
- **SHA256**: `f8068b3ef0a4dbc8a33c7e412df54433124cdf53fea8405d30d081523f3224b5`
- **Status**: Standardized/Production

#### Improvements Over Original
- Consistent tab delimiters across all rows
- Guaranteed 4-column structure
- Proper line endings (LF)
- UTF-8 encoding validation
- Ready for programmatic processing

### 4. `transformation_manifest.txt`
- **Purpose**: Detailed transformation record with checksums
- **Contents**:
  - File checksums (SHA256)
  - File sizes
  - Transformation timestamp
  - Verification instructions
  - Re-run instructions

## How to Use

### Run the Transformation
```bash
python3 transform_met_inventory.py \
  --input met_inventory_original.tsv \
  --output met_inventory_standardized.tsv
```

### Verify File Integrity
```bash
sha256sum -c <<EOF
4b0d42eebae3d781563f5ff3b1b3618e60957ada95aa4a9213b9cf2cc11c8349  met_inventory_original.tsv
f8068b3ef0a4dbc8a33c7e412df54433124cdf53fea8405d30d081523f3224b5  met_inventory_standardized.tsv
EOF
```

### Verify Script Integrity
```bash
sha256sum -c <<EOF
2a91596883ccf314351354c9984b2b73ed223398cff029b8a05ead3d9fbcc37c  transform_met_inventory.py
EOF
```

## Data Structure

### Column Headers
1. **Object Date**: Date or date range of the object (7th-9th century, 1836, ca. 1970, etc.)
2. **Title**: Name or description of the artwork/object (may be empty)
3. **Object Number**: Unique identifier within the Met collection
4. **Link Resource**: URL to the object in the Met's online collection

### Column Format
```
Object Date[TAB]Title[TAB]Object Number[TAB]Link Resource
```

## Verification Results

### Transformation Output
```
Original file rows: 101
Total rows processed: 101
No structural issues found
Output file rows: 101
✓ Row count verified
```

### Size Changes
- Original: 11,259 bytes
- Standardized: 11,269 bytes
- Difference: +10 bytes (0.09% increase)
  - Due to normalized line endings and structural corrections

## Technical Notes

### Character Encoding
The script handles international characters properly:
- Preserves all Unicode characters
- Maintains accented Latin characters (Béranger, Villenave, etc.)
- Supports East Asian text (Chinese and Japanese)
- UTF-8 encoding throughout

### Tab vs. Space Delimiters
- Input: Properly tab-delimited (verified by script)
- Output: Tab-delimited with standard library csv module
- Delimiter character: `\t` (U+0009)

### Empty Cells
- Preserved in standardized output
- No data loss
- Empty cells represented as empty strings between tabs

## Archive Contents Summary

| File | Type | Checksum | Purpose |
|------|------|----------|---------|
| `met_inventory_original.tsv` | TSV | 4b0d42... | Source data (before) |
| `transform_met_inventory.py` | Python | 2a9159... | Transformation logic |
| `met_inventory_standardized.tsv` | TSV | f8068b... | Standardized data (after) |
| `transformation_manifest.txt` | Text | — | Metadata & checksums |
| `README.md` | Markdown | — | This documentation |

## Questions?

For verification, consult `transformation_manifest.txt` for:
- Exact checksums of all files
- Timestamp of transformation
- Instructions for re-running the transformation
- Step-by-step verification commands

---

**Transformation Date**: 2026-10-14T02:12:11  
**Status**: Complete and Verified
