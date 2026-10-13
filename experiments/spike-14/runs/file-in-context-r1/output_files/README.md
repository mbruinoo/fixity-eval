# MET Museum Inventory TSV Standardization Project

## Overview

This archive contains a complete data standardization workflow for the Metropolitan Museum of Art inventory TSV file, including the input data, processing script, output data, and verification logs.

## Project Structure

```
met_inventory_standardization/
├── README.md                              (This file)
├── MANIFEST.txt                           (File manifest with checksums)
├── met_inventory.tsv                      (Original input file)
├── standardize_met_inventory.py           (Transformation script)
├── met_inventory_standardized.tsv         (Standardized output file)
├── standardization_log.txt                (Processing log and statistics)
└── checksums.txt                          (MD5 checksums for fixity verification)
```

## File Descriptions

### Input Data
- **met_inventory.tsv** - Original MET Museum inventory data (301 lines, 300 data rows + 1 header)
  - MD5: `6ec5bfc2d979ad12eb3343149beb8617`
  - Format: Tab-separated values
  - Columns: Object Date | Title | Object Number | Link Resource
  - Issues addressed: HTML entity encoding, inconsistent whitespace

### Processing Script
- **standardize_met_inventory.py** - Python 3 procedural transformation script
  - Executable Python script with detailed documentation
  - Includes comprehensive logging and error handling
  - Performs fixity verification (MD5 checksums)
  - Generates detailed processing statistics
  - Self-documenting with inline comments and docstrings

### Output Data
- **met_inventory_standardized.tsv** - Standardized output file (301 lines, 300 data rows + 1 header)
  - MD5: `c18503f8f274ac7e9500ebf3635017f1`
  - Format: Tab-separated values (UTF-8 encoded)
  - All transformations applied consistently

### Verification & Documentation
- **standardization_log.txt** - Detailed processing log including:
  - Timestamp of execution
  - Input/output file paths and MD5 checksums
  - Processing statistics
  - Warning counts and data quality metrics
  - Fixity verification summary

- **checksums.txt** - MD5 checksums for all files
  - Used to verify data integrity during archival and retrieval

## Transformation Rules Applied

The standardization script applies the following transformations:

### 1. HTML Entity Decoding
- `&lt;` → `<`
- `&gt;` → `>`
- `&amp;` → `&`
- `&quot;` → `"`
- `&apos;` / `&#39;` → `'`

**Example**: `Arrowhead (&lt;i&gt;Yanone&lt;/i&gt;)` → `Arrowhead (<i>Yanone</i>)`

### 2. Whitespace Normalization
- Collapse multiple consecutive spaces to single space
- Trim leading and trailing whitespace
- Applied to Title column only

**Example**: `Title with  multiple   spaces` → `Title with multiple spaces`

### 3. Data Preservation
- All empty cells preserved (no assumption of values)
- Tab-separated structure maintained
- Column order unchanged
- UTF-8 encoding enforced throughout

### 4. Quality Assurance
- Column count validation (4 columns expected)
- No rows dropped or modified inappropriately
- Comprehensive logging of all operations
- MD5 checksums for input and output files

## Processing Statistics

| Metric | Value |
|--------|-------|
| Total lines processed | 301 |
| Data rows processed | 300 |
| Header rows | 1 |
| Rows with warnings | 0 |
| HTML entities decoded | 4 |
| Encoding issues | 0 |
| Processing status | ✓ SUCCESSFUL |

## Fixity Verification

This archive includes MD5 checksums to verify data integrity:

```
Input:   6ec5bfc2d979ad12eb3343149beb8617  met_inventory.tsv
Output:  c18503f8f274ac7e9500ebf3635017f1  met_inventory_standardized.tsv
```

To verify file integrity:
```bash
md5sum -c checksums.txt
```

## How to Use

### Running the Transformation Script

```bash
# Navigate to project directory
cd met_inventory_standardization/

# Run the standardization script
python3 standardize_met_inventory.py
```

The script will:
1. Verify the input file exists and calculate MD5
2. Read all lines from input file
3. Process each row according to transformation rules
4. Write standardized output to new file
5. Calculate MD5 checksum of output
6. Generate detailed log file with statistics

### Verifying Output

```bash
# Check file integrity using stored checksums
md5sum -c checksums.txt

# View processing log
cat standardization_log.txt

# Compare input and output (shows transformations)
diff met_inventory.tsv met_inventory_standardized.tsv
```

### Columns in Output File

| Column | Description | Example |
|--------|-------------|---------|
| Object Date | Date or date range | "ca. 1425", "1890s–1900s", "3rd–2nd century BCE" |
| Title | Title or description of artwork | "Arrowhead (<i>Yanone</i>)" |
| Object Number | Museum catalog number | "57.51.8", "2019.583" |
| Link Resource | URL to museum collection | "http://www.metmuseum.org/art/collection/search/451391" |

## Data Quality Notes

- Some rows have empty Title fields (original data structure)
- Object Numbers use museum's internal cataloging system
- Dates range from ancient times (BCE) to contemporary (2020s)
- All 4 HTML entities in original data have been properly decoded
- No data loss during transformation

## Archival Notes

This package is suitable for long-term archival because:

1. **Reproducibility**: The transformation script is included, allowing reprocessing
2. **Verification**: MD5 checksums enable integrity verification over time
3. **Documentation**: Comprehensive logs and README describe all changes
4. **Format**: Standard tab-separated values (universal compatibility)
5. **Encoding**: UTF-8 encoding (standard for text data)
6. **Version Control**: Processing timestamp and statistics recorded

## Technical Specifications

- **Script Language**: Python 3
- **File Format**: Tab-Separated Values (TSV)
- **Character Encoding**: UTF-8
- **Line Endings**: Unix (LF)
- **Execution Time**: ~0.5 seconds
- **Dependencies**: Python standard library only (no external packages)

## Author & Date

- **Process**: Automated Data Standardization Pipeline
- **Execution Date**: 2026-10-13
- **Execution Time**: 2026-10-13T21:17:52.530153 (ISO 8601)

## License & Rights

This package contains:
- Original data from the Metropolitan Museum of Art (public domain collection data)
- Processing script created for standardization purposes
- Documentation and logs from the standardization process

## Questions & Support

For questions about this standardization:
- Review the `standardization_log.txt` for processing details
- Check the `standardize_met_inventory.py` script documentation
- Examine the differences between input and output files
- Verify MD5 checksums for data integrity

---

*Generated as part of automated data processing and archival workflow*
