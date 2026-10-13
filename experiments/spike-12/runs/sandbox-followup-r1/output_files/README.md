# MET Museum Inventory Standardization Project

## Project Overview

This archive contains a complete data standardization project for the MET Museum inventory TSV file, including the original data, transformation script, standardized output, and verification documentation.

## Archive Contents

```
met_inventory_standardization/
├── README.md                           # This file
├── VERIFICATION.md                     # Checksums and data integrity report
├── INPUT/
│   └── met_inventory.tsv              # Original input file
├── OUTPUT/
│   └── met_inventory_standardized.tsv # Standardized output file
├── SCRIPTS/
│   └── standardize_met_inventory.py   # Transformation script (Python 3)
└── LOGS/
    └── standardization.log            # Detailed execution log
```

## Quick Start

### Running the Transformation

To reproduce the standardization:

```bash
python3 standardize_met_inventory.py INPUT/met_inventory.tsv OUTPUT/met_inventory_standardized.tsv LOGS/standardization.log
```

### Requirements

- Python 3.7+
- pandas library

Install dependencies:
```bash
pip install pandas
```

## Data Transformation Details

### Input File
- **Filename**: met_inventory.tsv
- **Size**: 35,052 bytes
- **Records**: 300
- **Columns**: 4 (Object Date, Title, Object Number, Link Resource)
- **Checksum (SHA256)**: `33c53888daa063ca9697f4a82f15cd2d047afbce1ccb21c235e9c4ae9509d547`

### Output File
- **Filename**: met_inventory_standardized.tsv
- **Size**: 37,470 bytes
- **Records**: 300
- **Columns**: 4 (object_number, title, object_date, link_resource)
- **Checksum (SHA256)**: `86ecd210edc5645a87a4121a14caae1ea9621fd54abaa7626329fb1e2b1582ed`

### Transformations Applied

1. **Column Name Standardization**
   - Converted column names to lowercase
   - Replaced spaces with underscores (snake_case)
   - Mapping:
     - "Object Date" → "object_date"
     - "Title" → "title"
     - "Object Number" → "object_number"
     - "Link Resource" → "link_resource"

2. **HTML Entity Decoding**
   - Decoded HTML entities in the Title field
   - Example: `&lt;i&gt;text&lt;/i&gt;` → `<i>text</i>`
   - Processed: 275 non-null title records

3. **Whitespace Normalization**
   - Removed leading/trailing whitespace from all fields
   - Converted empty strings to NULL values
   - Applied to all 4 columns

4. **Column Reordering**
   - Reordered columns for logical data presentation
   - New order: object_number, title, object_date, link_resource
   - Prioritizes unique identifier first

5. **Data Validation**
   - Validated presence of primary key (object_number)
   - Removed incomplete rows (0 rows removed)
   - All 300 records retained

### Data Quality Metrics

| Metric | Count |
|--------|-------|
| Total Records | 300 |
| Records with object_number | 300 |
| Records with title | 275 |
| Records with date | 289 |
| Records with link | 300 |
| Unique object numbers | 300 |
| Unique titles | 262 |
| Unique dates | 239 |

## File Specifications

### TSV Format
- **Delimiter**: Tab character (\t)
- **Quoting**: All fields quoted for data safety
- **Encoding**: UTF-8
- **Line endings**: POSIX (\n)

### Data Types
All columns are preserved as text/string types for maximum compatibility and to preserve any formatting nuances.

## Fixity Check

The project includes multiple layers of verification for data integrity:

1. **Input File Checksum**
   - Algorithm: SHA256
   - Hash: `33c53888daa063ca9697f4a82f15cd2d047afbce1ccb21c235e9c4ae9509d547`

2. **Output File Checksum**
   - Algorithm: SHA256
   - Hash: `86ecd210edc5645a87a4121a14caae1ea9621fd54abaa7626329fb1e2b1582ed`

3. **Verification Steps**
   - Script version tracked (1.0)
   - Execution timestamp recorded
   - Transformation counts logged
   - Row count consistency verified

To verify file integrity after download:

```bash
# Linux/macOS
sha256sum INPUT/met_inventory.tsv
sha256sum OUTPUT/met_inventory_standardized.tsv

# macOS (alternative)
shasum -a 256 INPUT/met_inventory.tsv
shasum -a 256 OUTPUT/met_inventory_standardized.tsv

# Windows PowerShell
Get-FileHash INPUT/met_inventory.tsv -Algorithm SHA256
Get-FileHash OUTPUT/met_inventory_standardized.tsv -Algorithm SHA256
```

## Using the Standardized Data

### Sample Query (with pandas)

```python
import pandas as pd

# Load standardized data
df = pd.read_csv('OUTPUT/met_inventory_standardized.tsv', sep='\t')

# Basic statistics
print(f"Total records: {len(df)}")
print(f"Records with titles: {df['title'].notna().sum()}")
print(f"Records with dates: {df['object_date'].notna().sum()}")

# View sample records
print(df.head(10))
```

### Column Access

```python
# Access specific columns
object_numbers = df['object_number']
titles = df['title']
dates = df['object_date']
links = df['link_resource']

# Filter by presence of data
with_titles = df[df['title'].notna()]
with_dates = df[df['object_date'].notna()]
```

## Script Architecture

### Main Components

1. **Checksum Calculation**
   - SHA256 hashing for data integrity verification
   - Applied to input and output files

2. **Data Input**
   - Pandas DataFrame reading with explicit string types
   - Handles tab-separated format

3. **Transformation Pipeline**
   - Modular transformation functions
   - Error handling at each stage
   - Detailed logging of operations

4. **Data Validation**
   - Row count verification
   - Field presence checks
   - Primary key validation

5. **Output Generation**
   - TSV file writing with safe quoting
   - Log file generation
   - Checksum recording

### Error Handling

The script includes comprehensive error handling for:
- Missing input files
- CSV parsing errors
- File write failures
- Encoding issues

All errors are logged with descriptive messages to aid troubleshooting.

## Reproducibility

This standardization is fully reproducible:

1. Run the script with the same input file
2. Compare output checksum: `86ecd210edc5645a87a4121a14caae1ea9621fd54abaa7626329fb1e2b1582ed`
3. If checksums match, transformation was successful
4. Review `standardization.log` for detailed execution report

## Archival Recommendations

For long-term preservation, this project should be stored with:

1. **All files together** - Maintain directory structure
2. **Checksums preserved** - Keep verification documentation
3. **Script preserved** - Enables future re-runs or audits
4. **Metadata retained** - Keep timestamps and logs
5. **Format preservation** - Store as plain text (TSV, Python, Markdown)

## License & Attribution

Original data source: The Metropolitan Museum of Art collection database

This standardization project is provided as-is for research and archival purposes.

## Support

For questions about:
- **Transformation logic**: Review `standardize_met_inventory.py` comments
- **Execution details**: See `LOGS/standardization.log`
- **Data verification**: Consult `VERIFICATION.md`

## Changelog

### Version 1.0 (2026-10-13)
- Initial standardization project
- HTML entity decoding implemented
- Column name normalization added
- Comprehensive logging and verification included

---

**Project Created**: 2026-10-13  
**Script Version**: 1.0  
**Last Modified**: 2026-10-13
