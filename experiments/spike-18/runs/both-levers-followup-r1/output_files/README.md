# Met Museum Inventory Standardization Archive

## Overview
This archive contains the raw data, transformation script, and standardized output for the Met Museum inventory TSV file, including fixity checks for data integrity verification.

## Files Included

### 1. **met_inventory_raw.tsv**
- The original input file with inconsistencies
- Contains 100 rows of museum object records
- Issues present:
  - Missing titles (empty cells)
  - Missing dates (empty cells)
  - Bilingual titles (Chinese|English format requiring parsing)
  - Inconsistent column formatting

**MD5 Checksum:** `cb2dcc47c640a8d9ddd885dff70de81f`

### 2. **standardize_met_inventory.py**
- Python 3 transformation script
- Performs the following operations:
  - Fills missing date values with `[Unknown Date]`
  - Fills missing title values with `[Unknown]`
  - Extracts English titles from bilingual entries (removes Chinese text)
  - Ensures all rows have exactly 4 tab-separated columns
  - Removes quote marks from titles where present
  - Adds fixity check headers to output

**Features:**
- Comprehensive error handling
- UTF-8 encoding support (preserves special characters)
- Logging of MD5 checksums for both input and output
- Timestamp of transformation
- Detailed docstrings and comments

**Usage:**
```bash
python3 standardize_met_inventory.py <input_file> <output_file>
```

### 3. **met_inventory_standardized.tsv**
- The standardized output file
- Contains 100 rows plus header with fixity information
- All rows now have complete, consistent data
- Bilingual titles converted to English only
- Ready for data processing and analysis

**MD5 Checksum:** `c32374791023d4dbe9d01e9d24d351e7`

## Fixity Information

The output file includes a header with checksums for verification:

```
# Met Museum Inventory - Standardized
# Generated: 2026-10-14T00:52:17.110613
# Input File MD5:  cb2dcc47c640a8d9ddd885dff70de81f
# Output File MD5: c32374791023d4dbe9d01e9d24d351e7
```

**To verify integrity:**

```bash
# Verify input file
md5sum -c <<< "cb2dcc47c640a8d9ddd885dff70de81f  met_inventory_raw.tsv"

# Verify output file (note: includes header comments in checksum)
md5sum -c <<< "c32374791023d4dbe9d01e9d24d351e7  met_inventory_standardized.tsv"
```

## Data Transformations Applied

### Missing Values
- Empty date cells → `[Unknown Date]`
- Empty title cells → `[Unknown]`

### Title Parsing
Bilingual entries formatted as `Chinese Text|English Title` are converted to English only:
- Input: `东周 玉璜|Arc-shaped pendant (Huang)`
- Output: `Arc-shaped pendant (Huang)`

### Format Normalization
- All rows standardized to 4 tab-separated columns
- Removed enclosing quotes from titles
- Preserved all special characters and Unicode

## Column Structure

| Column | Description |
|--------|-------------|
| Object Date | When the object was created/dated (century ranges, specific dates, or "n.d."/unknown) |
| Title | Name/title of the artwork or object (now standardized and complete) |
| Object Number | Met Museum catalog number |
| Link Resource | URL to the object's entry on metmuseum.org |

## Row Count
- **Input:** 100 rows (data only)
- **Output:** 100 rows (data only) + 1 header row + 4 comment lines

## Recommendations for Use

1. **Data Import:** The standardized file is compatible with most data analysis tools (Excel, R, Python pandas, databases, etc.)

2. **Verification:** Always verify checksums before processing:
   ```bash
   md5sum met_inventory_*.tsv
   ```

3. **Archival Storage:** Keep all three files together for complete documentation of the transformation process

4. **Further Processing:** The script can be modified and rerun if additional transformations are needed

## Technical Details

- **Encoding:** UTF-8
- **Delimiter:** Tab character (\t)
- **Line Endings:** Unix-style (LF)
- **Python Version:** 3.6+
- **Dependencies:** None (uses only Python standard library)

## Reproducibility

The script is deterministic and reproducible. Running the same script on the same input file will always produce the same output, verifiable by the MD5 checksums.

## Questions or Issues?

For questions about the transformation logic, refer to the detailed docstrings in `standardize_met_inventory.py`.
