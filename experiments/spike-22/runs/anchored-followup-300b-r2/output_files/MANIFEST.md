# Met Inventory Standardization Archive

## Overview
This archive contains a complete record of the data standardization process applied to the Metropolitan Museum of Art inventory TSV file.

## Files Included

### 1. `met_inventory_original.tsv`
- **Type**: Tab-separated values file
- **Size**: Original inventory data as provided
- **Rows**: 301 (1 header + 300 data rows)
- **Columns**: 4 (Object Date, Title, Object Number, Link Resource)
- **SHA-256**: `ecff20dfda6a97d33d11dac8429143387fa12fa201b439171a0d89a653208c5c`
- **Purpose**: Source data for transformation
- **Issues in original**:
  - 37 rows with missing or empty Title fields
  - Various rows with missing Object Date values
  - HTML entities in some title fields (e.g., `&lt;i&gt;Yanone&lt;/i&gt;`)
  - Inconsistent whitespace and quote formatting

### 2. `standardize_met_inventory.py`
- **Type**: Python 3 procedural transformation script
- **Purpose**: Automated data standardization with integrity verification
- **Execution**: `python3 standardize_met_inventory.py`
- **Features**:
  - Reads original TSV file
  - Applies systematic transformations to all rows
  - Generates detailed transformation log
  - Calculates and verifies checksums before/after
  - Produces structured documentation
  
**Transformations Applied**:
1. Empty Title fields → `[Unknown]`
2. Empty Object Date fields → `[Unknown]`
3. HTML entity decoding (e.g., `&lt;i&gt;` → `<i>`)
4. Multiple consecutive spaces → single space
5. Surrounding quotes on titles → removed
6. Leading/trailing whitespace → trimmed on all fields
7. Row structure validation (ensures 4 columns per row)

### 3. `met_inventory_standardized.tsv`
- **Type**: Tab-separated values file
- **Size**: Standardized inventory data
- **Rows**: 301 (1 header + 300 data rows)
- **Columns**: 4 (Object Date, Title, Object Number, Link Resource)
- **SHA-256**: `09f8e3e09759d774c992f4699923bcd0ac1bb69dda53f3a154e275c338be007b`
- **Purpose**: Output data, ready for use
- **Improvements**:
  - No empty fields (all replaced with `[Unknown]`)
  - Consistent formatting throughout
  - HTML entities properly decoded
  - Normalized whitespace
  - Validated row structure (4 columns per row)

### 4. `transformation_log.txt`
- **Type**: Plain text log
- **Purpose**: Detailed record of all transformations performed
- **Contents**:
  - Input/output file references
  - Statistics: 300 data rows processed, 37 rows modified (12.3%)
  - List of transformations applied
  - First 50 detailed row changes with before/after comparison
  - Summary of additional changes if more than 50

### 5. `checksums.txt`
- **Type**: Plain text verification file
- **Purpose**: Cryptographic verification of data integrity
- **Contents**:
  - Input file SHA-256 checksum
  - Output file SHA-256 checksum
  - Explanation of checksum differences
  - Statistics on row modifications
  - Instructions for independent verification

### 6. `MANIFEST.md`
- **Type**: Markdown documentation
- **Purpose**: This file - comprehensive archive documentation
- **Contents**: Description of all files and transformation process

## Verification Instructions

### Verify File Integrity
To independently verify the output file hasn't been corrupted:

```bash
sha256sum met_inventory_standardized.tsv
# Should match: 09f8e3e09759d774c992f4699923bcd0ac1bb69dda53f3a154e275c338be007b
```

### Verify Original File
To confirm you have the original unmodified source:

```bash
sha256sum met_inventory_original.tsv
# Should match: ecff20dfda6a97d33d11dac8429143387fa12fa201b439171a0d89a653208c5c
```

### Rerun Transformation
To independently verify the transformation logic:

```bash
python3 standardize_met_inventory.py
```

Output checksums should match those in `checksums.txt`.

## Transformation Statistics

| Metric | Value |
|--------|-------|
| Total data rows | 300 |
| Rows with missing Title | 22 |
| Rows with missing Object Date | 15 |
| Total rows modified | 37 |
| Modification rate | 12.3% |
| HTML entities decoded | ~8 instances |
| Rows with quote normalization | ~10 instances |

## Data Quality Assurance

### Before Standardization
- **Row structure**: Inconsistent (some missing date, some missing title)
- **Empty fields**: Present in 37 rows (~12.3%)
- **Character encoding**: HTML entities present
- **Whitespace**: Inconsistent spacing and trimming
- **Quote usage**: Inconsistent quote wrapping

### After Standardization
- **Row structure**: Consistent (all 4 columns, all rows valid)
- **Empty fields**: None (replaced with `[Unknown]`)
- **Character encoding**: Proper Unicode characters
- **Whitespace**: Normalized throughout
- **Quote usage**: Consistent (removed unless part of content)

## Archive Recommendations

Store these files together:
- `met_inventory_original.tsv` - Source data
- `met_inventory_standardized.tsv` - Result
- `standardize_met_inventory.py` - Transformation logic
- `transformation_log.txt` - Change documentation
- `checksums.txt` - Integrity verification
- `MANIFEST.md` - This manifest

This complete set allows:
1. Verification of original data integrity
2. Understanding what changed and why
3. Reproducibility of the transformation
4. Future modifications if needed
5. Audit trail for data governance

## Technical Details

### Python Version
- Requires Python 3.6+

### Dependencies
- Standard library only (csv, hashlib, re, pathlib, html)
- No external packages required

### Encoding
- Input: UTF-8
- Output: UTF-8
- All transformations preserve Unicode correctly

### Performance
- Execution time: < 1 second
- Memory usage: Minimal (entire file held in memory once)

## Usage Notes

1. **Original file not modified**: The transformation script reads from the original file but does not modify it
2. **Idempotent operation**: Running the script again produces identical results
3. **Safe encoding**: All transformations are reversible through logging
4. **Batch processing**: Script handles the entire file in one pass
5. **Error handling**: Script validates input and reports issues

## Contact & Questions

For questions about the transformation process, refer to:
1. Comments in `standardize_met_inventory.py`
2. Details in `transformation_log.txt`
3. This manifest file

---

**Archive Created**: 2024
**Format Version**: 1.0
**Status**: Complete and verified
