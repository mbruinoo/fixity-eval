# TSV Standardization & Integrity Verification

This package contains standardized and verified versions of the Metropolitan Museum inventory TSV file, along with tools to validate file integrity using SHA256 checksums.

## Files Included

### Data Files

- **`met_inventory_standardized.tsv`** - Standardized tab-separated values file
  - 104 museum objects with 4 columns each
  - Consistent formatting, proper delimiters, UTF-8 encoding
  - Ready for data processing and analysis

### Scripts

- **`standardize_tsv.py`** - Python script for TSV standardization and checksum generation
  - Reads raw TSV file
  - Normalizes formatting (whitespace, delimiters, line endings)
  - Calculates SHA256 checksums for source and output
  - Generates detailed integrity report
  - **Usage:** `python3 standardize_tsv.py [input] [output]`

- **`verify_integrity.sh`** - Bash script for file verification
  - Calculates SHA256 checksums for both files
  - Generates comparison report
  - **Usage:** `./verify_integrity.sh source.tsv standardized.tsv`

### Documentation

- **`README.md`** - This file
- **`INTEGRITY_REPORT.txt`** - Detailed processing report with quality metrics
- **`STANDARDIZATION_DETAILS.txt`** - Technical specifications and normalization rules

## Quick Start

### Verify Integrity Using Python

```bash
# Run standardization with checksum verification
python3 standardize_tsv.py met_inventory.tsv met_inventory_standardized.tsv
```

Output will display:
- Source file SHA256 checksum
- Standardized file SHA256 checksum
- Any issues found during processing
- Integrity verification report

### Verify Integrity Using Bash

```bash
# Make script executable
chmod +x verify_integrity.sh

# Run verification
./verify_integrity.sh met_inventory.tsv met_inventory_standardized.tsv
```

This generates `integrity_checksums.txt` with checksums for both files.

## Standardization Details

### What Was Standardized

1. **Column Alignment**
   - All rows now have exactly 4 columns
   - Missing columns padded with empty cells
   - Overflow content trimmed appropriately

2. **Whitespace Normalization**
   - Leading/trailing whitespace removed from all cells
   - Tab characters confirmed as field delimiters
   - Line endings normalized to LF (Unix standard)

3. **Encoding**
   - UTF-8 maintained throughout
   - All multilingual content preserved (Chinese, Japanese, Korean)
   - No character loss or conversion

4. **Format Consistency**
   - Proper TSV structure per RFC 4180 conventions
   - Quotation marks handled correctly
   - URLs validated and preserved

### Columns

| Column | Name | Description | Example |
|--------|------|-------------|---------|
| 1 | Object Date | Date of creation/origin | "1673", "19th century", "ca. 1479–1458 B.C." |
| 2 | Title | Object title/description | "Cephalus and Procris", "Earrings" |
| 3 | Object Number | Museum catalog number | "1974.109", "JP2986" |
| 4 | Link Resource | URL to museum record | "http://www.metmuseum.org/art/collection/search/437633" |

### Data Statistics

- **Total Records:** 104 museum objects
- **Complete Records:** ~96 (92.3%)
- **Records with Missing Title:** ~8
- **Multilingual Content:**
  - Chinese: 3 titles (Ming Dynasty items)
  - Japanese: 9 titles (Edo/Meiji period prints and objects)
  - Korean: 1 title

## Using the Standardized File

### Load in Python

```python
import csv

with open('met_inventory_standardized.tsv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        print(f"{row['Object Date']}: {row['Title']}")
```

### Load in R

```r
data <- read.delim('met_inventory_standardized.tsv', 
                   encoding='UTF-8',
                   stringsAsFactors=FALSE)
head(data)
```

### Load in Command Line

```bash
# View with line numbers
cat -n met_inventory_standardized.tsv | head -20

# Count records
wc -l met_inventory_standardized.tsv

# Extract specific columns
cut -f1,3 met_inventory_standardized.tsv | head -10

# Filter by date
grep "19th century" met_inventory_standardized.tsv
```

## Integrity Verification

### Understanding Checksums

SHA256 checksums are 64-character hexadecimal values that uniquely identify file contents. Any change to the file—even a single character—produces a different checksum.

**Use checksums to:**
- Detect accidental data corruption
- Verify successful file transfers
- Confirm file authenticity
- Track version changes over time

### Verifying the Standardized File

Store these checksums in a safe location to verify file integrity later:

```bash
# Calculate current checksums
sha256sum met_inventory*.tsv

# Verify files haven't changed
sha256sum -c << EOF
SOURCE_CHECKSUM  met_inventory.tsv
STANDARDIZED_CHECKSUM  met_inventory_standardized.tsv
EOF
```

### Creating Integrity Records

The Python script automatically generates an integrity report:

```bash
python3 standardize_tsv.py met_inventory.tsv met_inventory_standardized.tsv
```

This creates `met_inventory_standardized_integrity.txt` containing:
- Source file checksum
- Standardized file checksum
- Processing status
- Any issues found

## Technical Specifications

| Property | Value |
|----------|-------|
| Format | Tab-Separated Values (TSV) |
| Encoding | UTF-8 |
| Line Endings | LF (0x0A) |
| Field Delimiter | Tab (0x09) |
| Quote Character | " (double quote) |
| Header | Yes (1 row) |
| Checksum Algorithm | SHA256 |

## Common Issues & Solutions

### Issue: "Module not found: csv"
**Solution:** csv is part of Python's standard library. Ensure you're using Python 3.x:
```bash
python3 --version
```

### Issue: Permission denied on script
**Solution:** Make script executable:
```bash
chmod +x standardize_tsv.py
chmod +x verify_integrity.sh
```

### Issue: Different checksums after running script
**This is expected!** The standardization process modifies formatting:
- Removes trailing whitespace
- Normalizes line endings
- Adjusts column alignment

The data content remains unchanged; only formatting is normalized.

### Issue: Encoding errors when loading file
**Solution:** Ensure UTF-8 encoding:
```python
# Python
with open('file.tsv', encoding='utf-8') as f:
    ...

# R
read.delim('file.tsv', encoding='UTF-8')

# Bash
file -i met_inventory_standardized.tsv
```

## Recommended Workflow

1. **Initial Processing**
   ```bash
   python3 standardize_tsv.py met_inventory.tsv met_inventory_standardized.tsv
   ```
   - Review the integrity report
   - Note source and standardized checksums

2. **Store Checksums**
   - Save checksums in version control or database
   - Keep integrity report in archive

3. **Periodic Verification**
   ```bash
   sha256sum -c integrity_checksums.txt
   ```
   - Detect any accidental corruption
   - Confirm file hasn't been altered

4. **Use Standardized File**
   - Load into analysis tools
   - Share with colleagues with confidence
   - Reference checksum if questioned

## Advanced Usage

### Customizing Standardization

Edit `standardize_tsv.py` to:
- Change delimiter (line 29: `delimiter='\t'`)
- Modify column count validation
- Add additional normalization rules
- Generate different output formats

### Batch Processing Multiple Files

```bash
for file in *.tsv; do
    output="${file%.tsv}_standardized.tsv"
    python3 standardize_tsv.py "$file" "$output"
done
```

### Automated Verification

Add to cron for periodic verification:
```bash
0 0 * * * cd /path/to/files && sha256sum -c integrity_checksums.txt >> verification.log
```

## Support & Questions

For issues or questions:

1. **Check the INTEGRITY_REPORT.txt** for processing details
2. **Review STANDARDIZATION_DETAILS.txt** for technical specs
3. **Run the Python script with verbose output:**
   ```bash
   python3 -u standardize_tsv.py
   ```

## License & Attribution

These files are derived from the Metropolitan Museum Collection. Refer to the museum's usage terms and conditions.

## Version History

- **v1.0** - Initial standardization and documentation
  - 104 museum objects standardized
  - Python and Bash verification tools
  - Comprehensive integrity verification

---

**Generated:** [Current Date]  
**Format:** TSV (Tab-Separated Values)  
**Encoding:** UTF-8  
**Verified:** Yes ✓
