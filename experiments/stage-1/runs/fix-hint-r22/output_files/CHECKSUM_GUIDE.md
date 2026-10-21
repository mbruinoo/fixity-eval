# Museum Inventory TSV Standardization - Checksum Verification Guide

## Overview

This document explains how to verify the integrity of the standardized TSV file using checksums. All data has been preserved through cryptographic checksums at both the cell and row levels.

## Files Generated

1. **met_inventory_standardized.tsv** - The standardized inventory file (101 rows including header)
2. **checksums.json** - Complete checksum database for all cells and rows
3. **standardization_report.md** - Human-readable report of changes
4. **standardize_met_inventory.py** - Script used for standardization

## Checksum Architecture

### Three-Level Integrity Model

#### Level 1: Cell-Level Checksums
Each individual cell has a SHA-256 checksum calculated from its exact content (string value).

**Structure:**
```json
{
  "cell_checksums": {
    "2": {
      "Object Date": {"value_length": 11, "checksum": "abc123..."},
      "Title": {"value_length": 0, "checksum": "e3b0c44..."},
      "Object Number": {"value_length": 8, "checksum": "def456..."},
      "Link Resource": {"value_length": 54, "checksum": "ghi789..."}
    }
  }
}
```

**How to verify a cell:**
```python
import hashlib

# Read the cell value from row 2, column "Object Date"
cell_value = "19th century"

# Calculate its checksum
calculated_checksum = hashlib.sha256(cell_value.encode('utf-8')).hexdigest()

# Compare with checksums.json
expected_checksum = "abc123..."  # from checksums.json

assert calculated_checksum == expected_checksum, "Cell integrity compromised!"
```

#### Level 2: Row-Level Checksums
Each row is checksummed as a complete tab-delimited string.

**Formula:**
```
row_string = "Object Date\tTitle\tObject Number\tLink Resource"
row_checksum = SHA-256(row_string)
```

**Structure:**
```json
{
  "source_rows": {
    "1": {"checksum": "abc123...", "field_count": 4}
  },
  "standardized_rows": {
    "1": {"checksum": "def456...", "field_count": 4, "changed": false}
  }
}
```

**Verification:** A row checksum can be calculated by:
1. Reading all cells in a row
2. Joining them with tab characters (`\t`)
3. Computing SHA-256 of the resulting string

#### Level 3: File-Level Summary
The entire file can be verified by checking all row checksums.

## Standardization Changes

The following normalizations were applied to all rows:

### Changes Made:
1. **Whitespace Normalization**: Removed leading/trailing whitespace from all cells
2. **Delimiter Standardization**: Ensured consistent tab (0x09) delimiters
3. **Field Count Normalization**: Padded rows with empty cells to ensure 4 columns
4. **Quote Handling**: Applied RFC 4180 CSV standards (Python csv module)
5. **Encoding**: Maintained UTF-8 encoding for international characters

### What Did NOT Change:
- Content of cells (only whitespace trimmed)
- Character encoding (UTF-8 preserved)
- International characters (Chinese/Japanese text intact)
- Special characters in titles (quotes, dashes, accents)
- Empty cells (represented as empty strings between tabs)

## How to Manually Verify Integrity

### Method 1: Using the Provided Script

```bash
python3 standardize_met_inventory.py
```

This regenerates all checksums and compares with source. Any mismatches indicate corruption.

### Method 2: Spot-Check Verification

Use Python to verify specific rows or cells:

```python
import json
import hashlib
import csv

# Load checksums
with open('checksums.json', 'r') as f:
    checksums = json.load(f)

# Read standardized file
with open('met_inventory_standardized.tsv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f, delimiter='\t')
    rows = list(reader)

# Verify row 5 (example)
row_num = 5
row = rows[row_num - 1]

# Recalculate checksum
row_str = '\t'.join(row)
calculated_checksum = hashlib.sha256(row_str.encode('utf-8')).hexdigest()
expected_checksum = checksums['standardized_rows'][str(row_num)]['checksum']

if calculated_checksum == expected_checksum:
    print(f"✓ Row {row_num} integrity verified")
else:
    print(f"✗ Row {row_num} integrity compromised!")

# Verify specific cell
col_name = 'Object Date'
cell_value = row[0]  # First column
cell_checksum = hashlib.sha256(cell_value.encode('utf-8')).hexdigest()
expected_cell_checksum = checksums['cell_checksums'][str(row_num)][col_name]['checksum']

if cell_checksum == expected_cell_checksum:
    print(f"✓ Cell integrity verified: {cell_value}")
else:
    print(f"✗ Cell integrity compromised!")
```

### Method 3: Command-Line Verification

Compare SHA-256 hashes directly:

```bash
# For the entire standardized file
sha256sum met_inventory_standardized.tsv

# For specific rows (using awk to extract)
# Extract row 5 and hash it
awk 'NR==5' met_inventory_standardized.tsv | sha256sum
```

## Checksum File Structure (checksums.json)

```json
{
  "source_rows": {
    "1": {"checksum": "...", "field_count": 4},
    "2": {"checksum": "...", "field_count": 4},
    ...
  },
  "standardized_rows": {
    "1": {"checksum": "...", "field_count": 4, "changed": false},
    "2": {"checksum": "...", "field_count": 4, "changed": false},
    ...
  },
  "cell_checksums": {
    "2": {
      "Object Date": {"value_length": 11, "checksum": "..."},
      "Title": {"value_length": 0, "checksum": "..."},
      "Object Number": {"value_length": 8, "checksum": "..."},
      "Link Resource": {"value_length": 54, "checksum": "..."}
    },
    ...
  }
}
```

## Common Use Cases

### Detecting Row Modifications

```python
row_num = 10
source_check = checksums['source_rows'][str(row_num)]['checksum']
std_check = checksums['standardized_rows'][str(row_num)]['checksum']

if source_check != std_check:
    print(f"Row {row_num} was modified during standardization")
    # Review what changed
```

### Identifying Empty Cells

Empty cells have a specific checksum (SHA-256 of empty string):

```python
empty_cell_checksum = hashlib.sha256(b'').hexdigest()
# Result: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855

# Find all empty cells in row 3:
row_3_cells = checksums['cell_checksums']['3']
for col_name, cell_info in row_3_cells.items():
    if cell_info['checksum'] == empty_cell_checksum:
        print(f"Empty cell found: {col_name}")
```

### Verifying Specific Data Integrity

To ensure a particular object number hasn't been altered:

```python
# Example: Find object number "91.1.396" and verify it
target_number = "91.1.396"

for row_num in range(2, 102):  # Skip header
    row_num_str = str(row_num)
    obj_checksum = checksums['cell_checksums'][row_num_str]['Object Number']['checksum']
    obj_length = checksums['cell_checksums'][row_num_str]['Object Number']['value_length']
    
    if obj_length == len(target_number):
        calculated = hashlib.sha256(target_number.encode('utf-8')).hexdigest()
        if calculated == obj_checksum:
            print(f"✓ Found verified object: {target_number} in row {row_num}")
```

## Technical Specifications

- **Hash Algorithm**: SHA-256 (FIPS 180-4)
- **Encoding**: UTF-8
- **Delimiter**: Tab character (0x09)
- **Line Terminator**: LF (0x0A)
- **Quoting**: RFC 4180 (as implemented by Python csv module)
- **Field Count**: 4 columns (Object Date, Title, Object Number, Link Resource)
- **Total Rows**: 101 (including header)
- **Data Rows**: 100

## Preservation of Data Integrity

- ✓ No content modification (only whitespace normalization)
- ✓ All cells checksummed before and after
- ✓ International characters preserved (UTF-8)
- ✓ Special characters in titles preserved
- ✓ Empty cells documented and checksum-verified
- ✓ Cryptographic evidence of integrity

## Limitations and Notes

1. **Checksums detect change, not intent**: If a cell is modified and the checksum is recalculated, the new checksum won't match the original. This detects *that* a change occurred but not whether it was intentional.

2. **Empty cell distinction**: Empty cells vs. cells with only whitespace are different. The standardization strips whitespace, so "  " becomes "" - this is recorded in the "changed" field.

3. **Row checksums include all columns**: A row checksum includes all four columns. If any cell changes, the row checksum changes.

4. **Value_length field**: The `value_length` field in cell checksums documents the length of the cell content. This provides additional verification that content hasn't been truncated or extended.

## Support for Verification

To verify checksums externally, you only need:
1. The standardized TSV file
2. The checksums.json file
3. A SHA-256 implementation (available in all standard libraries)

The standardization script (`standardize_met_inventory.py`) can serve as a reference implementation.
