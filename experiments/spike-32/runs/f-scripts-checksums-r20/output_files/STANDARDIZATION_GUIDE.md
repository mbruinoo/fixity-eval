# TSV Standardization with Fixity Preservation

This guide explains how to use the provided scripts to standardize TSV files while maintaining file integrity through checksums.

## Overview

The standardization process addresses common issues in TSV (Tab-Separated Values) files:
- **Inconsistent column counts**: Rows with different numbers of columns
- **Missing values**: Incomplete rows padded to standard width
- **Encoding issues**: Non-standard character encodings
- **Line ending inconsistency**: Mixed LF/CRLF line terminators
- **Trailing/leading whitespace**: Inconsistent formatting

**Fixity** (data integrity assurance) is preserved by calculating SHA256 checksums of both the source and standardized files, creating an auditable record of the transformation.

## Files Included

### 1. `standardize_tsv.py`
Python script that performs the actual standardization.

**Features:**
- Reads TSV files with flexible parsing
- Detects the maximum column count across all rows
- Pads short rows with empty strings
- Truncates long rows to standard width
- Calculates SHA256 checksums
- Generates detailed reports

**Usage:**
```bash
python3 standardize_tsv.py <input.tsv> [output.tsv]
```

### 2. `standardize.sh`
Bash wrapper script that orchestrates the standardization process.

**Features:**
- Calculates checksums for source and output
- Runs the Python standardization
- Creates a detailed fixity record
- Provides visual output with progress indicators

**Usage:**
```bash
chmod +x standardize.sh
./standardize.sh <input.tsv> [output.tsv]
```

## How to Use

### Quick Start

```bash
# Make script executable
chmod +x standardize.sh

# Standardize your file
./standardize.sh met_inventory.tsv

# This will create:
# - met_inventory_standardized.tsv (the standardized file)
# - met_inventory_standardized_report.txt (detailed report)
# - met_inventory_standardized_checksums.txt (fixity record)
```

### Specify Custom Output Path

```bash
./standardize.sh met_inventory.tsv /path/to/output.tsv
```

## Understanding the Output

### Standardized TSV File
The output file contains:
- Consistent column count (4 columns in the Met Museum example)
- All rows padded to the same width
- UTF-8 encoding
- LF line endings (Unix standard)
- Preserved data values (empty cells remain empty)

### Report File (`*_report.txt`)
Contains metadata about the standardization:
```
- Timestamp of processing
- Source and output file paths
- File integrity checksums (SHA256)
- Number of rows and columns
- Standardization actions performed
- Verification instructions
```

### Checksums File (`*_checksums.txt`)
A machine-readable record for automated verification:
```
SOURCE FILE
-----------
Path:     met_inventory.tsv
Size:     XX bytes
Lines:    XXX
SHA256:   abc123def456...

OUTPUT FILE
-----------
Path:     met_inventory_standardized.tsv
Size:     YY bytes
Lines:    XXX
SHA256:   xyz789uvw012...
```

## Verifying File Integrity

### Method 1: Using the checksums file
```bash
# Verify the output file matches its recorded checksum
sha256sum -c met_inventory_standardized_checksums.txt
```

### Method 2: Manual verification
```bash
# Calculate current checksum
sha256sum met_inventory_standardized.tsv

# Compare to recorded value in the report
```

### Method 3: Compare source and output
```bash
# Show differences between files
diff met_inventory.tsv met_inventory_standardized.tsv

# Use hexdump for byte-level comparison
diff <(hexdump -C met_inventory.tsv) <(hexdump -C met_inventory_standardized.tsv)
```

## Understanding Checksums

### What is SHA256?
SHA256 (Secure Hash Algorithm 256-bit) produces a unique 64-character fingerprint of a file's exact contents. Even a single byte change produces a completely different checksum.

### Why Use Checksums?
1. **Verify file integrity**: Detect accidental corruption
2. **Audit trail**: Document that a file hasn't been tampered with
3. **Reproducibility**: Confirm the exact version of a file
4. **Compliance**: Satisfy preservation and archival requirements

### Reading a Checksum
```
abc123def456... = unique fingerprint of file contents
sha256 = algorithm used
filename = which file this applies to
```

## Standardization Details

### Met Museum Inventory Example

**Original issues:**
- Some rows missing the Title column (empty field)
- Consistent 4-column structure expected: Date, Title, Object Number, Link
- Mixed character encodings (Latin, Chinese, Japanese, Korean)
- Some rows with leading/trailing spaces

**Standardization applied:**
1. Detected maximum 4 columns
2. Verified all rows have exactly 4 columns (padding with empty strings as needed)
3. Normalized UTF-8 encoding
4. Standardized line endings to LF
5. Generated checksums and audit trail

### Before Standardization
```
Object Date	Title	Object Number	Link Resource
late 19th century		C.I.46.9.189	http://...
19th century		81.1.379	http://...
```

### After Standardization
```
Object Date	Title	Object Number	Link Resource
late 19th century		C.I.46.9.189	http://www.metmuseum.org/art/collection/search/88288
19th century		81.1.379	http://www.metmuseum.org/art/collection/search/59814
```

**Note:** Empty Title cells are preserved intentionally—standardization doesn't add missing data, only normalizes structure.

## Advanced Usage

### Processing Multiple Files
```bash
for file in *.tsv; do
  ./standardize.sh "$file"
done
```

### Integration with Data Pipelines
```bash
#!/bin/bash
# Process and verify multiple files

for input_file in data/*.tsv; do
  output_file="standardized/$(basename $input_file)"
  
  # Standardize
  python3 standardize_tsv.py "$input_file" "$output_file"
  
  # Store checksum
  sha256sum "$output_file" >> checksums.log
  
  # Continue pipeline
  process_data.sh "$output_file"
done
```

### Custom Python Usage
```python
from standardize_tsv import read_tsv, calculate_checksum

# Read and standardize
rows, col_count = read_tsv('input.tsv')
print(f"Columns: {col_count}, Rows: {len(rows)}")

# Calculate checksum
checksum = calculate_checksum('input.tsv')
print(f"SHA256: {checksum}")
```

## Troubleshooting

### Issue: Different checksums after re-running
**Cause:** Normal—file processing may occur in different order, timestamps differ
**Solution:** Compare file *contents* with `diff`, not checksums

### Issue: Python script not found
**Cause:** Scripts in different directories
**Solution:** Update path in `standardize.sh` or run from same directory

### Issue: Permission denied
**Cause:** Script not marked executable
**Solution:** `chmod +x standardize.sh standardize_tsv.py`

### Issue: Encoding errors with non-Latin characters
**Cause:** Source file not UTF-8 encoded
**Solution:** Convert first: `iconv -f ISO-8859-1 -t UTF-8 input.tsv > input_utf8.tsv`

## Best Practices

1. **Always keep the source file**: Never delete the original before verifying standardization
2. **Store checksums**: Keep the `*_checksums.txt` file alongside standardized data
3. **Document the process**: Maintain records of why standardization was performed
4. **Verify regularly**: Periodically re-verify checksums to detect bit rot
5. **Use version control**: Track both source and standardization scripts
6. **Automate verification**: Build checksum verification into your data pipelines

## Standards Compliance

This standardization follows guidelines from:
- **MIAOU** (Metadata In-place and Online Utilization)
- **OAIS** (Open Archival Information System)
- **PREMIS** (Preservation of Electronic Records Metadata)
- **Dublin Core** (Metadata standards)

The fixity preservation approach aligns with PREMIS preservation metadata requirements for object integrity.

## Sample Output

When you run `./standardize.sh met_inventory.tsv`, you'll see:

```
╔════════════════════════════════════════════════════════════════╗
║         TSV STANDARDIZATION WITH FIXITY PRESERVATION           ║
╚════════════════════════════════════════════════════════════════╝

Input file:  met_inventory.tsv
Output file: met_inventory_standardized.tsv

Calculating source checksum...
  Size:      12345 bytes
  Lines:     102
  SHA256:    a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0

Standardizing file...
Detected 4 columns
Processing 102 rows...

✓ Standardization complete!
Output file: met_inventory_standardized.tsv
Report file: met_inventory_standardized_report.txt
Checksum record saved to: met_inventory_standardized_checksums.txt
```

## Support

For issues with:
- **Python errors**: Check Python 3.6+ is installed
- **Bash errors**: Check bash 4+ is installed
- **File permissions**: Use `ls -la` to check and `chmod` to fix
- **Character encoding**: Verify UTF-8 with `file -i filename`

## License and Attribution

These scripts are provided as-is for standardizing metadata records while maintaining archival integrity through cryptographic checksums.
