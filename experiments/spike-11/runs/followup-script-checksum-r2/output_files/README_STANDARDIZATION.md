# Metropolitan Museum Inventory Standardization

## Overview

This archive contains a complete data standardization workflow for the Metropolitan Museum inventory TSV file. It includes the original data, transformation script, standardized output, and verification documentation.

## Contents

### Files in this archive:

1. **met_inventory.tsv** (Original Input)
   - Source data from Metropolitan Museum
   - 301 rows (1 header + 300 data rows)
   - Tab-separated values format
   - Columns: Object Date | Title | Object Number | Link Resource

2. **standardize_met_inventory.py** (Transformation Script)
   - Primary transformation script (Python 3)
   - Executable: `python3 standardize_met_inventory.py`
   - Includes all normalization functions
   - Generates SHA-256 checksums for verification
   - Produces detailed execution report

3. **met_inventory_standardized.tsv** (Output)
   - Standardized version of input file
   - All transformations applied
   - Ready for database import or analysis
   - 301 rows (1 header + 300 data rows)

4. **TRANSFORMATION_LOG.txt**
   - Complete record of transformations
   - SHA-256 checksums for fixity verification
   - Data quality notes
   - Verification instructions

5. **README_STANDARDIZATION.md** (This File)
   - Documentation and usage guide

6. **CHECKSUMS.txt**
   - SHA-256 checksums for all files
   - Format compatible with `sha256sum -c` command

## Transformation Rules

### 1. Date Normalization

| Pattern | Transformation | Example |
|---------|-----------------|---------|
| "ca." | Convert to "c." | "ca. 1780" → "c. 1780" |
| "B.C." | Convert to "BCE" | "664–30 B.C." → "664–30 BCE" |
| "A.D." | Convert to "CE" | "A.D. 100" → "CE 100" |
| Empty/missing | Add placeholder | "" → "[Date Unknown]" |
| "n.d." | Convert to placeholder | "n.d." → "[Date Unknown]" |
| Dashes | Convert to en-dash | "1780-99" → "1780–99" |
| Lowercase start | Capitalize | "late 19th century" → "Late 19th century" |

### 2. Title Standardization

| Pattern | Transformation | Example |
|---------|-----------------|---------|
| Empty/missing | Add placeholder | "" → "[Untitled]" |
| Quotes | Remove surrounding quotes | ""Altitude"" → "Altitude" |
| HTML entities | Decode HTML | "&lt;i&gt;Yanone&lt;/i&gt;" → "Yanone" |
| Case | Apply title case | "amulet of ptah" → "Amulet of Ptah" |
| Whitespace | Normalize | "Title  with   spaces" → "Title with Spaces" |

**Title Case Rules:**
- Capitalize first word regardless
- Lowercase articles/prepositions: "a", "an", "the", "and", "or", "for", "to", "of", "in", "by", "from", "with", "as", "at"
- Capitalize all other words

### 3. Object Number Normalization

| Pattern | Transformation | Example |
|---------|-----------------|---------|
| Abbreviated ranges | Expand abbreviation | "2002.201.111, .112" → "2002.201.111, 2002.201.112" |
| Dashes in ranges | Convert to en-dash | "1a-c" → "1a–c" |
| Other formats | Preserve as-is | No change to standard formats |

### 4. General Cleanup

- Remove leading/trailing whitespace from all fields
- Normalize multiple spaces to single space
- Preserve URLs and special characters
- Maintain original field structure (4 columns)

## Running the Transformation

### Prerequisites

- Python 3.6 or later
- No external dependencies (uses only Python standard library)

### Basic Usage

```bash
cd /path/to/archive
python3 standardize_met_inventory.py
```

### Expected Output

The script will display:

```
======================================================================
METROPOLITAN MUSEUM INVENTORY STANDARDIZATION
======================================================================

[1/4] Reading input file: met_inventory.tsv
      Input SHA-256: abc123def456...

[2/4] Processing rows...
      Processed 300 data rows

[3/4] Writing output file: met_inventory_standardized.tsv
      Output SHA-256: xyz789uvw012...

[4/4] Transformation Summary
----------------------------------------------------------------------
Timestamp:      2024-01-15T10:30:45.123456
Input file:     met_inventory.tsv
  Size:         45,234 bytes
  SHA-256:      abc123def456...
Output file:    met_inventory_standardized.tsv
  Size:         48,567 bytes
  SHA-256:      xyz789uvw012...
Rows processed: 300

======================================================================
STANDARDIZATION COMPLETE
======================================================================
```

## Verification

### Verify File Integrity

To verify that files haven't been corrupted, use SHA-256 checksums:

```bash
# Verify all files
sha256sum -c CHECKSUMS.txt

# Verify specific file
echo "CHECKSUM_HEX  filename" | sha256sum -c -
```

### Expected Output

```
met_inventory.tsv: OK
met_inventory_standardized.tsv: OK
standardize_met_inventory.py: OK
```

### Re-generate Output

To re-run the transformation:

```bash
# Copy input file if needed
cp /path/to/original/met_inventory.tsv ./

# Run transformation
python3 standardize_met_inventory.py

# Verify output matches checksums
sha256sum -c CHECKSUMS.txt
```

## Data Quality Notes

### Coverage

- **Total records**: 300 (plus 1 header row)
- **Records with missing dates**: ~50 → marked as "[Date Unknown]"
- **Records with missing titles**: ~25 → marked as "[Untitled]"
- **HTML entities corrected**: ~3 entries
- **Object number ranges expanded**: ~15 entries

### Special Cases

#### Multilingual Entries

Entries with Chinese or Japanese text are preserved as-is:
- Chinese titles maintain original characters
- Japanese titles (including furigana) preserved
- English translations also included where present

Example:
```
5th century BCE | Arc-Shaped Pendant (Huang) | 2009.92
1838 | The Cicada Stream (Semi No Ogawa) | 2013.787a–c
```

#### Complex Dates

Dates with uncertainty or complex notation preserved with minimal modification:

```
Before 16th century
Dated A.H. 37?/ 98 CE?
Datable to 1506–10
Published 1703 or 1712
1961, printed later
```

#### Long Titles

Long descriptive titles are preserved in full:

```
"Actresses Standing with Hands on Hips and Wearing Hats from Actresses 
(N335a) Issued by S. F. Hess & Company to Promote Long Cut Tobacco Brands"
```

### Known Limitations

1. **Abbreviations**: Museum-specific abbreviations (Vol., N335a, etc.) are preserved to maintain data fidelity.

2. **Multilingual case**: Chinese/Japanese text doesn't receive full title case transformation as English rules don't apply.

3. **Complex punctuation**: Some complex historical punctuation (e.g., "é", "Œ", "à") is preserved exactly as in source.

4. **Date ranges**: Historical date ranges with "to" (e.g., "late 19th to early 20th century") are preserved as-is, not converted to dashes.

## Technical Details

### File Format

- **Input**: Tab-Separated Values (TSV)
- **Output**: Tab-Separated Values (TSV)
- **Encoding**: UTF-8
- **Line endings**: Unix (LF)
- **CSV dialect**: Excel with tab delimiter

### Script Specifications

- **Language**: Python 3.6+
- **Encoding**: UTF-8
- **Standard library only**: No external dependencies required
- **Hash function**: SHA-256 (FIPS 180-4)

### Modules Used

```python
import csv              # TSV reading/writing
import hashlib          # SHA-256 checksums
import html             # HTML entity decoding
import re               # Regular expressions
import sys              # System operations
from pathlib import Path  # File path operations
from datetime import datetime  # Timestamps
```

## Performance

- **Processing time**: ~1-2 seconds for 300 rows
- **Memory usage**: < 10 MB
- **Output file size**: ~48 KB (TSV format)

## Troubleshooting

### Script won't run

**Error**: `ModuleNotFoundError: No module named 'csv'`

- The csv module is part of Python's standard library. Ensure Python 3.6+ is installed.

```bash
python3 --version  # Check version
python3 standardize_met_inventory.py  # Run script
```

### Checksum mismatch

**Issue**: `sha256sum` reports checksum doesn't match

**Possible causes**:
- File was modified after processing
- File was corrupted during transfer
- Windows/Unix line ending conversion occurred

**Solution**:
1. Verify file wasn't modified: `ls -la filename`
2. Check file encoding: `file filename`
3. Re-run transformation: `python3 standardize_met_inventory.py`

### Output file is empty

**Possible causes**:
- Input file not found
- Input file is not TSV format
- Permission issues

**Solution**:
```bash
# Verify input file
ls -la met_inventory.tsv
file met_inventory.tsv

# Check permissions
chmod 644 met_inventory.tsv

# Re-run script
python3 standardize_met_inventory.py
```

## Usage Examples

### Import to Database

```python
import pandas as pd

# Read standardized TSV
df = pd.read_csv('met_inventory_standardized.tsv', sep='\t')

# Filter entries by date
recent = df[df['Object Date'].str.contains('20th century')]

# Export to CSV
df.to_csv('output.csv', index=False)
```

### Validate Checksums

```bash
# Create checksum file
sha256sum met_inventory.tsv met_inventory_standardized.tsv > checksums_verify.txt

# Verify later
sha256sum -c checksums_verify.txt
```

### Archive Entire Directory

```bash
# Create archive
tar -czf met_inventory_standardization.tar.gz \
  met_inventory.tsv \
  met_inventory_standardized.tsv \
  standardize_met_inventory.py \
  README_STANDARDIZATION.md \
  TRANSFORMATION_LOG.txt \
  CHECKSUMS.txt

# Extract later
tar -xzf met_inventory_standardization.tar.gz
```

## Changelog

### Version 1.0 (Initial)

- Initial standardization implementation
- Date normalization rules
- Title case normalization
- Object number expansion
- HTML entity decoding
- SHA-256 verification checksums
- Comprehensive documentation

## License & Attribution

- **Source Data**: Metropolitan Museum of Art
- **Transformation**: Standardization script and documentation
- **Format**: Tab-Separated Values (TSV)

## Support & Questions

For issues or questions about the transformation:

1. Check **TRANSFORMATION_LOG.txt** for detailed transformation record
2. Review **README_STANDARDIZATION.md** (this file) for documentation
3. Re-run script to verify output: `python3 standardize_met_inventory.py`
4. Verify checksums: `sha256sum -c CHECKSUMS.txt`

---

**Generated**: 2024  
**Format Version**: 1.0  
**Python Version**: 3.6+
