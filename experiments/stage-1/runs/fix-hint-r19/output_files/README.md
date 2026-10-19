# Met Museum Inventory - Standardized Dataset with Fixity Preservation

## Overview

This package contains a standardized version of the Met Museum inventory TSV file with comprehensive checksum-based fixity preservation. All 100 records have been processed through standardization rules and paired with cryptographic checksums for complete data integrity verification.

## Quick Start

### Files Included

1. **met_inventory_standardized.tsv** - The standardized dataset
   - 100 records with 7 fields each
   - Consistent field names and formatting
   - Includes SHA-256 checksums for verification

2. **met_inventory_checksums.tsv** - Checksum manifest
   - Row-level checksums for quick spot-checking
   - Maps source → standardized checksums
   - Format: row_number | object_number | source_checksum | std_checksum

3. **met_inventory_manifest.json** - Complete metadata
   - Full standardization specification
   - Data quality report with statistics
   - Transformation audit trail
   - Usage guidelines and technical notes

4. **standardize_met_inventory.py** - Reproducible script
   - Complete Python implementation
   - Checksum calculation and verification
   - Can be run independently for validation
   - Well-documented for extension

5. **STANDARDIZATION_REPORT.md** - Detailed analysis
   - Standardization rules explained
   - Data quality observations
   - Verification instructions with examples
   - Technical notes and recommendations

6. **README.md** - This file

## Standardization Summary

### Field Changes

| Original | Standardized | Type |
|----------|--------------|------|
| Object Date | date | Text |
| Title | title | Text |
| Object Number | object_number | Text (unique) |
| Link Resource | url | URL |

### Data Enhancements

- **row_number**: Sequential ID for tracking (1-100)
- **source_checksum**: SHA-256 of original data
- **std_checksum**: SHA-256 of standardized data

### Normalization Applied

✓ Whitespace trimmed from all fields  
✓ Empty values standardized  
✓ Consistent field ordering  
✓ UTF-8 encoding maintained  
✓ Tab-separated format (TSV)  

## Data Quality

### Completeness by Field

| Field | Complete | Missing | % |
|-------|----------|---------|---|
| date | 97 | 3 | 97% |
| title | 91 | 9 | 91% |
| object_number | 100 | 0 | 100% |
| url | 100 | 0 | 100% |

### Key Observations

- **Object Number**: Universal primary key (100% complete)
- **URLs**: All records have collection database links
- **Dates**: Various formats (specific years, ranges, eras, approximate)
- **Titles**: Some items lack titles in the original data
- **Unicode**: Full UTF-8 support for Chinese, French, and special characters

## Checksum Verification

### SHA-256 Algorithm

Each row is checksummed independently:

```
Source Checksum = SHA-256(Date ⊤ Title ⊤ Object # ⊤ URL)  [original]
Std Checksum    = SHA-256(Date ⊤ Title ⊤ Object # ⊤ URL)  [standardized]
```

### Verification Methods

**Automated (using Python script):**
```bash
python3 standardize_met_inventory.py
```

**Manual (for single record):**
1. Extract row data from standardized TSV
2. Reconstruct tab-separated format
3. Calculate SHA-256 hash
4. Compare with recorded std_checksum

**Spot-check (using checksums file):**
```bash
# Look up row 50
grep "^50" met_inventory_checksums.tsv
```

## File Statistics

### Standardized TSV
- **Format**: Tab-Separated Values (TSV)
- **Encoding**: UTF-8
- **Records**: 100 + 1 header
- **Fields**: 7
- **Lines**: 101

### Checksums TSV
- **Format**: Tab-Separated Values (TSV)
- **Records**: 100 + 1 header
- **Fields**: 4
- **Purpose**: Verification reference

### Manifest JSON
- **Format**: JSON (human-readable)
- **Size**: ~50 KB
- **Contains**: Full metadata and specifications
- **Purpose**: Complete documentation

## Usage Examples

### Load the standardized data

Python:
```python
import csv

with open('met_inventory_standardized.tsv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        print(f"{row['object_number']}: {row['title']} ({row['date']})")
```

Pandas:
```python
import pandas as pd

df = pd.read_csv('met_inventory_standardized.tsv', sep='\t')
print(df.info())
print(df.head())
```

### Verify a specific record

```bash
# Find record for object number "1976.609.1"
grep "1976.609.1" met_inventory_standardized.tsv

# Get its checksums
grep "1976.609.1" met_inventory_checksums.tsv
```

### Understand the data

- **manifest.json**: Technical specification
- **STANDARDIZATION_REPORT.md**: Human-readable details
- **standardize_met_inventory.py**: Implementation reference

## Preservation Strategy

This package implements **multi-level fixity preservation**:

| Level | Method | Evidence |
|-------|--------|----------|
| 1 | Record checksums | source_checksum, std_checksum |
| 2 | Field tracking | Individual values preserved exactly |
| 3 | Transformation audit | Field mapping documented |
| 4 | Reproducibility | Python script for verification |
| 5 | Documentation | Manifest + reports + comments |

## Recommendations

### For Archival/Preservation

- Store all files together (TSV, checksums, manifest, script, reports)
- Verify checksums monthly to detect data drift
- Keep source checksums to compare with original file
- Version any future modifications

### For Data Analysis

- Use standardized field names for consistency
- Reference object_number as primary key
- Filter by date/title completeness as needed
- Resolve URLs to access Met Museum database

### For Data Exchange

- Share standardized TSV with recipients
- Include manifest.json to explain schema
- Provide checksums for recipients to verify integrity
- Document any modifications from this version

## Troubleshooting

### Checksum Mismatch

If calculated checksum doesn't match recorded value:

1. **Verify file wasn't corrupted** - Re-download files
2. **Check encoding** - Ensure UTF-8 with no BOM
3. **Check line endings** - Should be LF (Unix), not CRLF
4. **Verify checksum calculation** - Use script provided

### UTF-8 Issues

Chinese characters and accented letters require UTF-8 encoding:

- **Python**: Use `encoding='utf-8'` when opening files
- **Excel**: Save as "CSV UTF-8" or import with UTF-8
- **Text editors**: Configure for UTF-8 (most do by default)

### TSV Format Issues

Tab-separated format requires special handling:

- **Tabs in data**: None in this dataset
- **Line breaks in fields**: None in this dataset  
- **Empty fields**: Represented as consecutive tabs (standard TSV)

## Support and Validation

### Validate the complete package

```bash
# 1. Verify all files exist
ls -la met_inventory_*.* standardize_* *.md

# 2. Run Python verification script
python3 standardize_met_inventory.py

# 3. Spot-check 5 random rows
for i in 1 15 42 67 99; do
  echo "Row $i:"
  grep "^$i" met_inventory_standardized.tsv
done
```

### Generate new checksums (if needed)

```bash
python3 standardize_met_inventory.py
```

This will regenerate all checksums and verify integrity.

## License and Attribution

- **Source**: Met Museum Collections Database
- **Processing Date**: January 19, 2025
- **Standardization**: SHA-256 checksumming for fixity
- **Format**: TSV/JSON/Python

## Version Information

| Component | Version |
|-----------|---------|
| Dataset | 1.0 |
| Standardization | 1.0 |
| Python Script | 1.0 |
| Report | 1.0 |

---

**Last Updated**: January 19, 2025  
**Total Records**: 100  
**Verification Status**: Ready for validation

For complete technical details, see STANDARDIZATION_REPORT.md and met_inventory_manifest.json
