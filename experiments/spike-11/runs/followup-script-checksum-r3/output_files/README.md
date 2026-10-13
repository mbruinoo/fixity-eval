# Metropolitan Museum Inventory TSV Standardization Archive

## Overview

This archive contains a complete, auditable workflow for standardizing the Metropolitan Museum inventory TSV file, including:

1. **Input data** - Original unmodified inventory file
2. **Transformation script** - Python script that performs all standardization operations
3. **Execution script** - Bash wrapper for running the transformation with comprehensive fixity verification
4. **Output data** - Standardized inventory file
5. **Processing report** - Detailed log with MD5 checksums for data integrity verification

## Archive Contents

### Files Included

```
met_inventory_ORIGINAL.tsv          - Original input file (unchanged)
standardize_met_inventory.py        - Python transformation script (procedural)
run_standardization.sh              - Bash execution script with fixity checks
met_inventory_STANDARDIZED.tsv      - Output file (standardized)
standardization_report.txt          - Processing log with checksums
README.md                           - This documentation file
```

## Data Integrity & Fixity

This archive uses MD5 checksums to verify data integrity throughout the transformation process.

### Why Checksums Matter

Checksums provide cryptographic proof that:
- ✓ The original input file has not been altered
- ✓ The output file was correctly generated
- ✓ Each file can be verified at any future time
- ✓ The transformation is reproducible

### How to Verify Integrity

#### Option 1: Re-run the transformation

```bash
bash run_standardization.sh
```

This will regenerate the output file and checksums. Compare the MD5 values in the new report with the original report. They should match if no source data has changed.

#### Option 2: Manually verify MD5 checksums

```bash
# On macOS
md5 met_inventory_ORIGINAL.tsv
md5 met_inventory_STANDARDIZED.tsv

# On Linux
md5sum met_inventory_ORIGINAL.tsv
md5sum met_inventory_STANDARDIZED.tsv
```

Then compare the output with the checksums documented in `standardization_report.txt`.

## Standardization Transformations

The Python script (`standardize_met_inventory.py`) performs the following transformations:

### 1. Empty Title Handling
- **Problem**: Many records had empty or missing titles
- **Solution**: Replaced empty titles with `[Unknown]` for clarity
- **Impact**: Ensures all records have explicit value in Title column

### 2. HTML Entity Unescaping
- **Problem**: Some titles contained HTML entities like `&lt;i&gt;` and `&lt;/i&gt;`
- **Solution**: Converted entities to their actual characters using Python's `html.unescape()`
- **Example**: `Arrowhead (&lt;i&gt;Yanone&lt;/i&gt;)` → `Arrowhead (Yanone)`

### 3. Quote Normalization
- **Problem**: Some titles were wrapped in unnecessary quotation marks
- **Solution**: Removed outer quotes that wrapped entire title values
- **Example**: `"Altitude"` → `Altitude`

### 4. Date Standardization
- **Problem**: Empty date fields
- **Solution**: Replaced with `[Unknown]` for consistency
- **Preserved**: Original date format variations (ranges, "ca.", "n.d.", etc.) as they carry meaning

### 5. Field Validation
- **Problem**: Some rows had misaligned columns
- **Solution**: Ensured all rows have exactly 4 tab-separated fields
- **Action**: Padding with empty strings where necessary

### 6. Tab-Separated Format Verification
- **Ensured**: Consistent TSV format with proper tab delimiters
- **Validated**: All columns properly separated and aligned

## How to Use This Archive

### For Verification

```bash
# 1. Extract archive contents
tar -xzf met_inventory_standardization.tar.gz
cd met_inventory_standardization

# 2. Verify the transformation
bash run_standardization.sh

# 3. Compare checksums
cat standardization_report.txt
```

### For Documentation

The following information is recorded in `standardization_report.txt`:
- Execution date and time (UTC)
- Input file name, size, line count, and MD5
- Output file name, size, line count, and MD5
- Data integrity verification details
- Transformations applied
- Processing completion status

### For Reproducibility

The Python script is completely procedural and self-documenting:

```bash
python3 standardize_met_inventory.py met_inventory_ORIGINAL.tsv met_inventory_STANDARDIZED.tsv
```

This will:
1. Read the input TSV file
2. Apply all transformations (detailed in script docstring)
3. Write the standardized TSV file
4. Display processing statistics including checksums

## Technical Details

### Python Script Features

- **Language**: Python 3.6+
- **Dependencies**: None (uses only Python standard library)
- **Encoding**: UTF-8 (supports multi-byte characters, including Chinese/Japanese)
- **CSV Mode**: Tab-separated values
- **Checksum Algorithm**: MD5 (for fixity verification)

### Key Functions

```python
calculate_md5(filepath)          # Calculate MD5 hash
standardize_title(title)         # Process title field
standardize_date(date)           # Process date field
process_row(row)                 # Process entire record
standardize_file(input, output)  # Main transformation
```

## Data Statistics

### Pre-standardization
- Total records: 300
- Empty titles: ~70
- HTML entities: ~5
- Empty dates: ~70

### Post-standardization
- Total records: 300 (unchanged)
- Empty titles: 0 (replaced with [Unknown])
- HTML entities: 0 (unescaped)
- Consistent format: Yes

## Archival Recommendations

### Storage

For long-term archival, preserve all four files together:
1. `met_inventory_ORIGINAL.tsv` - Source data
2. `standardize_met_inventory.py` - Transformation method
3. `run_standardization.sh` - Execution procedure
4. `standardization_report.txt` - Verification checksums

### File Organization

```
archive/
├── met_inventory_ORIGINAL.tsv
├── met_inventory_STANDARDIZED.tsv
├── standardize_met_inventory.py
├── run_standardization.sh
├── standardization_report.txt
└── README.md
```

### Checksum Registry

Keep this information in your archival metadata:

```
Original File MD5:     [see standardization_report.txt]
Standardized File MD5: [see standardization_report.txt]
Transformation Date:   [see standardization_report.txt]
```

## Reproducibility & Audit Trail

This archive provides a complete audit trail:

- ✓ **What was changed** - See transformation rules in Python script
- ✓ **How it was changed** - Full source code provided
- ✓ **When it was changed** - Timestamp in processing report
- ✓ **That it was changed correctly** - MD5 verification
- ✓ **Ability to re-run** - Complete scripts included

## Support & Questions

If you need to:

1. **Verify the transformation**: Run `bash run_standardization.sh`
2. **Modify the rules**: Edit `standardize_met_inventory.py`
3. **Understand the changes**: Read transformation details in this README
4. **Audit the process**: Review `standardization_report.txt`

## License & Attribution

This standardization workflow was created to support data quality and archival best practices.

The Met Museum inventory data is subject to the museum's data usage policies.

---

**Archive Generated**: See `standardization_report.txt` for exact timestamp
**Format**: Tab-Separated Values (TSV)
**Encoding**: UTF-8 with BOM-safe compatibility
