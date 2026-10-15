# Met Museum Inventory TSV Standardization

## Overview

This package contains a standardized version of the Met Museum inventory TSV file, along with cryptographic checksums for data integrity verification.

## Files Included

### Data Files
- **`met_inventory_standardized.tsv`** - The standardized, normalized TSV file (15,359 bytes)
- **`met_inventory.tsv`** - Original source file reference (15,295 bytes) 

### Verification & Documentation
- **`CHECKSUMS.sha256`** - SHA-256 checksums for integrity verification
- **`standardization_report.md`** - Detailed report of standardization process
- **`README.md`** - This file

### Scripts
- **`standardize_and_checksum.py`** - Python script used for standardization

## Checksums (SHA-256)

| File | SHA-256 Hash |
|------|--------------|
| **Source** (met_inventory.tsv) | `e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf` |
| **Standardized** (met_inventory_standardized.tsv) | `37d977d40f2e18da2a216d816e48a1ab0d5d72b8bbab35b022a0914b3a866523` |

## What Was Standardized

### 1. Tab Delimiters
- Enforced consistent single-tab field separation
- Removed irregular spacing

### 2. Column Structure  
- Normalized all rows to exactly 4 columns:
  1. **Object Date** - When the object was created/dated
  2. **Title** - Name/description of the object
  3. **Object Number** - Museum cataloging number
  4. **Link Resource** - URL to the object in Met collection
- Empty fields preserved as empty strings

### 3. Quote Handling
- Applied CSV standard quoting for fields with special characters
- Internal quotes escaped by doubling (`"` becomes `""`)
- Consistent across all records

### 4. Character Encoding
- Preserved UTF-8 for international characters
- Supports Chinese (明), Japanese (絵本), and Korean (해강) content
- Zero data loss

### 5. Line Endings
- Normalized to Unix-style (LF only)
- Cross-platform compatibility

## Data Contents

- **Total Records**: 100 objects (plus 1 header row = 101 rows total)
- **Date Range**: ca. 1850–1640 BCE to 20th century
- **International Content**: East Asian (Chinese, Japanese) and Korean artworks included
- **Coverage**: Paintings, sculptures, textiles, artifacts, and more

## How to Verify Integrity

### Using sha256sum (Linux/Mac)
```bash
# Verify the standardized file
sha256sum -c <<< "37d977d40f2e18da2a216d816e48a1ab0d5d72b8bbab35b022a0914b3a866523  met_inventory_standardized.tsv"

# Or verify both files
sha256sum -c CHECKSUMS.sha256
```

### Manual verification
```bash
# Generate checksum and compare
sha256sum met_inventory_standardized.tsv
# Should output: 37d977d40f2e18da2a216d816e48a1ab0d5d72b8bbab35b022a0914b3a866523
```

### Using Python
```python
import hashlib

with open('met_inventory_standardized.tsv', 'rb') as f:
    hash_value = hashlib.sha256(f.read()).hexdigest()
    print(hash_value)
# Should print: 37d977d40f2e18da2a216d816e48a1ab0d5d72b8bbab35b022a0914b3a866523
```

## Using the Standardized File

The standardized TSV can be imported into any tool that supports tab-delimited text:

### Excel/Google Sheets
- Open the file and select "Tab-delimited" as the delimiter
- All 4 columns will parse correctly

### Python (pandas)
```python
import pandas as pd

df = pd.read_csv('met_inventory_standardized.tsv', sep='\t')
print(df.head())
```

### Command-line tools
```bash
# View with column headers aligned
column -t -s $'\t' met_inventory_standardized.tsv | head

# Count records
wc -l met_inventory_standardized.tsv  # 101 (including header)
```

## Data Preservation

This standardization process ensures:

✓ **Lossless conversion** - All original data preserved  
✓ **Cryptographic verification** - SHA-256 checksums for integrity  
✓ **Format consistency** - Standard TSV format for portability  
✓ **Character fidelity** - UTF-8 encoding maintains international characters  
✓ **Machine readability** - Proper escaping and quoting for parsing  

## Technical Details

### Standardization Script
- **Language**: Python 3
- **Libraries**: Standard library (csv, hashlib, pathlib)
- **Encoding**: UTF-8
- **Line terminators**: LF (Unix)
- **Quote character**: `"` (double quote)
- **Escape character**: `"` (doubled for escaping)

### File Size Change
- Source: 15,295 bytes
- Standardized: 15,359 bytes  
- Difference: +64 bytes (0.4% increase)
- Reason: Added proper quoting for fields with special characters and quotes

## Questions or Issues

If you need to:
- **Verify integrity**: Use the SHA-256 checksums provided
- **Understand changes**: See `standardization_report.md`
- **Re-run standardization**: Use `standardize_and_checksum.py`
- **Access original**: Refer to the Met Museum collection API

## License & Attribution

The Met Museum inventory data is provided by The Metropolitan Museum of Art.
This standardization is provided as-is for data preservation purposes.

---

**Standardization Date**: October 15, 2024  
**Total Records**: 100 museum objects  
**Verification Method**: SHA-256 cryptographic hashing
