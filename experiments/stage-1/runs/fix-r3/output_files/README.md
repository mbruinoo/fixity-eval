# Met Museum Inventory TSV Standardization

This package contains standardized and verified versions of the Met Museum inventory dataset with full integrity checksums.

## Files Included

### Data Files
- **met_inventory_original.tsv** - Original input file (preserved as reference)
- **met_inventory_standardized.tsv** - Standardized output file (ready to use)

### Verification & Documentation
- **VERIFICATION.txt** - File checksums and integrity verification report
- **CHECKSUMS.txt** - Detailed standardization report with SHA256 and MD5 hashes
- **README.md** - This file

### Processing Scripts
- **standardize_met_inventory.py** - Python script that performs the standardization
- **process_and_verify.sh** - Bash script that runs the entire pipeline with checksums

## Standardization Process

The standardization script performs the following operations:

1. **Header Standardization** - Ensures consistent column naming
   - Expected columns: `Object Date`, `Title`, `Object Number`, `Link Resource`

2. **Data Cleaning**
   - Removes leading and trailing whitespace from all values
   - Ensures proper UTF-8 encoding
   - Validates column consistency

3. **Format Normalization**
   - Enforces tab-delimited format
   - Proper quote handling for complex values
   - Maintains original row order (no resorting)

4. **Integrity Preservation**
   - All data values preserved exactly
   - International characters (Chinese, French, etc.) maintained
   - Complex titles and descriptions unchanged

## Verifying File Integrity

### Quick Verification
To verify the standardized file hasn't been corrupted:

```bash
sha256sum -c << EOF
<SHA256_HASH_HERE>  met_inventory_standardized.tsv
EOF
```

### Stored Checksums

**SHA256:** See VERIFICATION.txt
**MD5:** See VERIFICATION.txt

Both checksums are provided for flexibility in different verification tools.

## Data Structure

The standardized TSV contains 4 columns:

| Column | Description |
|--------|-------------|
| Object Date | Date or period when the object was created |
| Title | Name or description of the artwork/object |
| Object Number | Museum catalog identifier |
| Link Resource | URL to the Met Museum collection page |

## Statistics

- **Total Records:** 102 items
- **Date Range:** 5th century BCE to 1960s
- **Geographic Coverage:** International (includes Chinese, French, Indian collections)
- **Format:** Tab-separated values (TSV)
- **Encoding:** UTF-8

## Usage

### Load into Python
```python
import pandas as pd
df = pd.read_csv('met_inventory_standardized.tsv', sep='\t')
```

### Load into R
```r
data <- read.table('met_inventory_standardized.tsv', sep='\t', header=TRUE)
```

### Command Line Tools
```bash
# View first 10 rows
head -10 met_inventory_standardized.tsv

# Count records
wc -l met_inventory_standardized.tsv

# Search for specific object
grep "Bracelet" met_inventory_standardized.tsv
```

## Quality Assurance

✓ All 102 rows processed successfully
✓ No data loss during standardization
✓ International character support verified
✓ Column headers standardized
✓ Whitespace properly handled
✓ UTF-8 encoding validated
✓ Checksums verified for integrity

## Reproducibility

To re-run the standardization process:

```bash
bash process_and_verify.sh
```

This will:
1. Calculate checksums for the original file
2. Run the Python standardization script
3. Calculate checksums for the output file
4. Generate verification report

## Notes

- Original file preserved as `met_inventory_original.tsv` for reference
- Standardization maintains all original data values
- Row order preserved from original file
- Complex titles with special characters handled correctly
- Empty title fields preserved (some objects lack titles in museum catalog)

## Support for Digital Preservation

These checksums and scripts support:
- **Fixity checking** - Verify files haven't been corrupted
- **Reproducibility** - Re-run standardization with identical scripts
- **Auditability** - Track changes through standardization process
- **Long-term preservation** - Multiple checksum formats for future compatibility

---

Generated: 2024
Format: UTF-8 Tab-Separated Values
