# TSV Standardization & Fixity Verification Guide

## Overview

This document explains the standardization process applied to `met_inventory.tsv` and how to verify data integrity using the provided checksums.

---

## Files Generated

1. **met_inventory_standardized.tsv** - The standardized TSV file
2. **standardization_report.txt** - Comprehensive standardization report
3. **fixity_checksums.txt** - SHA-256 checksums for all rows and cells
4. **standardize_met_inventory.py** - The standardization script (reproducible)

---

## What Was Standardized

### Whitespace Normalization
- **Leading/trailing spaces** removed from all cell values
- **Multiple internal spaces** normalized to single spaces
- Empty cells preserved as empty (not deleted)

### Format Consistency
- **Delimiters**: Enforced tab-separated values (TSV)
- **Encoding**: UTF-8 preserved throughout
- **Line endings**: Normalized to LF (Unix-style)
- **Column count**: Validated (4 columns consistently)

### Validation Results
- **Total Rows**: 100 data rows + 1 header row = 101 total
- **Total Columns**: 4 (Object Date, Title, Object Number, Link Resource)
- **Structural Issues**: 0 found
- **Data Integrity**: 100% maintained

---

## Fixity Verification

Checksums preserve data integrity by creating a unique fingerprint of each data element. If even one character changes, the checksum will differ, alerting you to unauthorized modifications.

### Available Checksums

#### 1. Header Checksums (SHA-256)
Located in `fixity_checksums.txt`, each column header has a unique checksum:
```
col_0_Object Date: bf75d4162f5396d4240b3233e24f23ddb4b1b3e5fae4507d2598d7972d33a620
col_1_Title: 7e8cd2056da73a7fefb6cd91f4e5d199d08d9058c517b9a2476b1b520324d674
col_2_Object Number: 17bc8c137c41dccbf3560dfb1a0f8bcf300d3651a84b818c232508a3f1640d6d
col_3_Link Resource: 331976a38e19da5ff520238759cf556a8912db2e5a1158d2a05142143fc4f78a
```

#### 2. Row-Level Checksums (SHA-256)
Each complete row (tab-separated values) has its own checksum. Example:
```
Row 2: 4d16543673187a57eb557f56daf4709f71ec690c0d773febcfcd34e1688ce6ce
Row 3: 8a8e4b673cfbf76dc508899302bb2bfd1f32574c8ff0ff13c63398c0c142f96b
```

#### 3. Cell-Level Checksums (SHA-256)
Individual cell values are checksummed for granular verification:
```
Row 2, Col 0: e712e048610af35a517ffe1e90002d4161a5669e1029330c9a4c1a54ee1a6adb
Row 2, Col 1: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 (empty)
Row 2, Col 2: f4db888208f985097ab1617aef4b49133da03486eb8820823feb831cce58c65e
Row 2, Col 3: 935f1b4e7786d06d0d20205930236d94e0223bbd376e941b8d18439b3d879dc2
```

#### 4. Full File Checksum (SHA-256)
Complete standardized file integrity:
```
fc4b7c906e701bc3649cf9215fe912761816c1f7047c8462ea908706ae806706
```

---

## How to Verify Integrity

### Option 1: Verify Using the Script
Re-run the standardization script on the standardized file to confirm checksums:
```bash
python3 standardize_met_inventory.py
```
New checksums should match the original ones.

### Option 2: Manual Verification (Linux/Mac)
Verify individual cells using command-line tools:
```bash
# Check if a specific cell matches its checksum
echo -n "91.1.396" | sha256sum
# Expected: f4db888208f985097ab1617aef4b49133da03486eb8820823feb831cce58c65e

# Verify entire file
sha256sum met_inventory_standardized.tsv
# Should match: fc4b7c906e701bc3649cf9215fe912761816c1f7047c8462ea908706ae806706
```

### Option 3: Verify Using Python
```python
import hashlib

def verify_cell(value, expected_checksum):
    actual = hashlib.sha256(value.encode('utf-8')).hexdigest()
    return actual == expected_checksum

# Example
result = verify_cell("91.1.396", 
    "f4db888208f985097ab1617aef4b49133da03486eb8820823feb831cce58c65e")
print(f"Cell integrity verified: {result}")
```

---

## Understanding the Checksums

### SHA-256 Properties
- **Fixed length**: Always 64 hexadecimal characters
- **Unique**: Different inputs produce different hashes (with negligible collision probability)
- **One-way**: Cannot reverse a hash to get the original value
- **Deterministic**: Same input always produces the same hash
- **Sensitive**: Even changing one character creates a completely different hash

### Empty Cell Checksum
All empty cells share the same checksum:
```
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```
This is the SHA-256 hash of an empty string and is a well-known value in cryptography.

---

## Standardization Statistics

| Metric | Value |
|--------|-------|
| Total Data Rows | 100 |
| Total Columns | 4 |
| Total Cells | 400 |
| Header Checksums Generated | 4 |
| Row Checksums Generated | 100 |
| Cell Checksums Generated | 400 |
| Issues Found During Validation | 0 |

---

## Data Lineage

### Original File
- **Format**: Tab-separated values (TSV)
- **Source**: Met Museum inventory
- **Object Count**: 100 artifacts
- **Date Range**: 4th–3rd century BCE to 1960s

### Standardization Process
1. Read original file and validate structure
2. Generate fixity checksums for original content
3. Apply standardization rules
4. Generate fixity checksums for standardized content
5. Create detailed reports

### Quality Assurance
- ✓ No data loss during standardization
- ✓ All 400 cells verified
- ✓ Column structure preserved
- ✓ UTF-8 encoding maintained
- ✓ Duplicate entries preserved as-is

---

## Reproducibility

The standardization is fully reproducible:

1. **Script**: `standardize_met_inventory.py` is included
2. **Algorithm**: Python's hashlib SHA-256
3. **Parameters**: Deterministic (no random elements)
4. **Expected Result**: Running the script on the original file will regenerate identical checksums

To reproduce:
```bash
python3 standardize_met_inventory.py < met_inventory.tsv
```

---

## Common Use Cases

### 1. Verify File Hasn't Been Modified
Compare current file's checksum with stored checksum. If they differ, the file has been modified.

### 2. Detect Specific Cell Changes
Compare individual cell checksums to pinpoint exactly which cells changed.

### 3. Audit Trail
Keep checksums in version control to track data changes over time:
```
Commit 1: Full Content Checksum: fc4b7c906e701bc...
Commit 2: Full Content Checksum: a1d2e3f4b5c6... (changed)
```

### 4. Data Transfer Verification
After transferring files across systems, verify checksums match to ensure corruption-free transfer.

---

## Technical Details

### Algorithm: SHA-256
- **Type**: Cryptographic hash function
- **Output Size**: 256 bits (64 hex characters)
- **Security**: Resistant to collisions (NIST approved)
- **Library**: Python's hashlib (standard library)

### Timestamp
Generated: 2026-10-19T03:58:19.436049

### Python Version
Tested on: Python 3.13.16

---

## Support & Questions

For verification failures or questions:

1. Ensure you're using the correct checksum value
2. Verify the file encoding is UTF-8
3. Check for whitespace differences
4. Re-run the standardization script
5. Compare row by row using the row checksums

---

## References

- [SHA-256 Specification](https://en.wikipedia.org/wiki/SHA-2)
- [TSV Format Standard](https://www.iana.org/assignments/media-types/text/tab-separated-values)
- [Data Fixity (Digital Preservation)](https://en.wikipedia.org/wiki/File_format#Preservation)
