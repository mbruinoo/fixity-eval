# TSV Standardizer with Checksum Preservation

This toolset standardizes the Met Museum inventory TSV file while maintaining data integrity through SHA-256 checksums.

## Files Included

- **standardize_tsv.py** - Python script that performs the standardization
- **standardize.sh** - Bash wrapper script for execution and verification
- **README.md** - This documentation

## What Gets Standardized

The standardization process includes:

1. **Consistent Delimiters** - Ensures all fields are separated by tabs
2. **Field Cleaning** - Strips leading/trailing whitespace from each field
3. **Column Consistency** - Normalizes all rows to have the same number of columns
4. **Proper Quoting** - Handles fields with special characters using CSV/TSV standards
5. **Encoding** - Ensures UTF-8 encoding throughout
6. **Sorting** - Orders records by Object Number (column 3) for consistency

## Usage

### Using the Bash Wrapper (Recommended)

```bash
chmod +x standardize.sh
./standardize.sh [input_file] [output_file]
```

Examples:
```bash
# Using defaults (met_inventory.tsv → met_inventory_standardized.tsv)
./standardize.sh

# Custom input/output
./standardize.sh my_inventory.tsv my_output.tsv
```

### Using the Python Script Directly

```bash
python3 standardize_tsv.py <input_file> [output_file]
```

Example:
```bash
python3 standardize_tsv.py met_inventory.tsv met_inventory_standardized.tsv
```

## Checksum Management

### Automatic Checksum Generation

When you run the standardization, checksums are automatically calculated and logged:

1. **SHA-256 of source file** - Captured before processing
2. **SHA-256 of output file** - Calculated after standardization
3. **Timestamp** - Records when standardization occurred
4. **Log file** - Saved as `checksums.json`

### Checksum Log Format

```json
{
  "timestamp": "2025-01-15T10:30:45.123456",
  "source_file": "met_inventory.tsv",
  "source_checksum_sha256": "abc123...",
  "output_file": "met_inventory_standardized.tsv",
  "output_checksum_sha256": "def456...",
  "algorithm": "SHA-256"
}
```

### Verification

To verify file integrity after standardization:

```bash
# Using the bash script (automatic verification)
./standardize.sh

# Manual verification with the checksum log
sha256sum met_inventory.tsv
sha256sum met_inventory_standardized.tsv

# Compare with logged checksums in checksums.json
cat checksums.json
```

The bash wrapper automatically verifies both source and output checksums and generates a `verification.txt` report.

## Standardization Details

### Input File Analysis

- **Columns**: 4 (Object Date, Title, Object Number, Link Resource)
- **Rows**: ~100 inventory records
- **Encoding**: UTF-8
- **Issues Handled**:
  - Inconsistent whitespace
  - Missing or extra fields
  - Special characters in titles
  - Unicode content (Chinese, Japanese, Korean characters)

### Output Improvements

- All rows have consistent column count (4 columns)
- Data sorted by Object Number for easier reference
- Proper tab delimiters throughout
- Whitespace normalized
- Ready for database import or further processing

## Data Integrity Features

The checksum system ensures:

1. **Source Integrity** - Original file hasn't been corrupted or modified
2. **Output Integrity** - Standardized file matches its recorded checksum
3. **Audit Trail** - Timestamp and algorithm documented
4. **Reproducibility** - Can verify standardization at any time

## Requirements

- Python 3.6+
- bash (for the wrapper script)
- sha256sum (standard on Linux/Mac, available on Windows via Git Bash)
- jq (optional, for advanced checksum inspection on Unix systems)

## Troubleshooting

### "Input file not found"
Ensure the input file exists in the current directory or provide the full path:
```bash
./standardize.sh /path/to/met_inventory.tsv
```

### Checksum mismatch
If you see a checksum mismatch, the file may have been modified:
1. Check the verification.txt report
2. Re-run standardization with the original source file
3. Verify your source file hasn't been corrupted

### Encoding issues
If you see encoding errors, the file may not be UTF-8:
```bash
# Check file encoding
file -i met_inventory.tsv

# Convert to UTF-8 if needed
iconv -f ISO-8859-1 -t UTF-8 met_inventory.tsv > met_inventory_utf8.tsv
```

## Example Workflow

```bash
# 1. Run standardization with verification
./standardize.sh met_inventory.tsv met_inventory_standardized.tsv

# 2. Review statistics
tail -30 verification.txt

# 3. Check the checksum log
cat checksums.json | python -m json.tool

# 4. Verify later if needed
sha256sum met_inventory_standardized.tsv
# Compare with the value in checksums.json

# 5. Archive both files together
# Keep checksums.json with the files for future verification
```

## Technical Notes

### Why SHA-256?

- **Cryptographically secure** - Extremely difficult to forge
- **Industry standard** - Used in research data management
- **Widely supported** - Available on all platforms
- **Deterministic** - Same file always produces same hash

### Column Sorting

Records are sorted by Object Number for:
- Easier manual inspection
- Consistent database imports
- Faster lookups and reference
- Better version control diffs

### Why Normalize Whitespace?

- Prevents issues with data import tools
- Ensures consistent search/sort behavior
- Removes hidden characters that cause problems
- Makes diffs more meaningful for version control

## License

These tools are provided as-is for archival and data management purposes.

## Questions?

Review the generated `verification.txt` and `checksums.json` files for detailed processing information.
