# TSV Standardization Guide with Fixity Verification

## Overview

This package contains scripts and tools to standardize a Tab-Separated Values (TSV) file while preserving fixity through checksum verification. Fixity refers to the integrity of a digital object—ensuring it hasn't been altered or corrupted.

## Files Included

### 1. `standardize_tsv.py`
The main Python script that performs standardization and checksum verification.

**Features:**
- Parses TSV file with UTF-8 encoding
- Normalizes whitespace and field structure
- Validates column structure
- Computes SHA-256 checksums for fixity verification
- Generates detailed log file with results
- Handles edge cases and reports issues

**Usage:**
```bash
python3 standardize_tsv.py <input_file> [output_file] [log_file]
```

**Example:**
```bash
python3 standardize_tsv.py met_inventory.tsv met_inventory_standardized.tsv met_inventory_standardization.log
```

### 2. `run_standardization.sh`
Bash wrapper script that orchestrates the standardization process and checksum verification.

**Features:**
- Executes the Python standardization script
- Computes and records SHA-256 checksums
- Creates comprehensive checksum verification file
- Generates file statistics

**Usage:**
```bash
bash run_standardization.sh
```

### 3. `met_inventory.tsv`
The source TSV file extracted from the provided data.

### 4. Output Files (generated after running standardization)

#### `met_inventory_standardized.tsv`
The standardized output TSV file with:
- Consistent tab delimiters
- UTF-8 encoding
- Trimmed whitespace on field values
- Proper CSV escaping where needed

#### `met_inventory_standardization.log`
Detailed log file containing:
- Source and output file checksums (SHA-256)
- Row counts (read vs. written)
- Column validation results
- Any issues or warnings encountered
- Verification instructions

#### `CHECKSUMS.txt`
Comprehensive checksum record for fixity verification:
- SHA-256 hashes for both source and output
- File sizes and line counts
- Commands to verify file integrity

## Standardization Process

### What Gets Standardized

1. **Delimiter Consistency**: Ensures all fields are separated by tabs (\\t)
2. **Whitespace Normalization**: Trims leading/trailing spaces from field values
3. **Encoding**: Validates and maintains UTF-8 encoding
4. **Column Structure**: Verifies all rows have expected columns:
   - Object Date
   - Title
   - Object Number
   - Link Resource
5. **Escaping**: Handles quoted fields with embedded delimiters properly

### What's Preserved

- Original data values (content not modified)
- Multilingual characters (CJK, Korean, special characters)
- Intentional empty fields
- Special characters and Unicode normalization

## Fixity Verification

### Understanding Checksums

SHA-256 checksums are cryptographic hashes that:
- Create a unique fingerprint for a file
- Are deterministic (same file = same checksum)
- Are sensitive to any change, no matter how small
- Cannot be reversed to recover the original file

### Verification Steps

#### 1. After Standardization (Immediate Check)
```bash
# The script automatically computes and displays checksums
sha256sum met_inventory.tsv
sha256sum met_inventory_standardized.tsv
```

Compare these with the values in `CHECKSUMS.txt`.

#### 2. Later Verification (Integrity Check)
To verify the files haven't been modified since standardization:

```bash
# Check source file
sha256sum met_inventory.tsv
# Compare with SOURCE_SHA256 in CHECKSUMS.txt

# Check output file
sha256sum met_inventory_standardized.tsv
# Compare with OUTPUT_SHA256 in CHECKSUMS.txt
```

#### 3. Batch Verification
Create a checksum file for verification:
```bash
sha256sum met_inventory.tsv met_inventory_standardized.tsv > check.sha256
sha256sum -c check.sha256
```

## Usage Instructions

### Step 1: Prepare
Ensure the source TSV file is in the working directory:
```bash
ls -la met_inventory.tsv
```

### Step 2: Run Standardization
```bash
# Option A: Use the bash wrapper (recommended)
bash run_standardization.sh

# Option B: Run Python script directly
python3 standardize_tsv.py met_inventory.tsv met_inventory_standardized.tsv met_inventory_standardization.log
```

### Step 3: Review Results
```bash
# View the standardization log
cat met_inventory_standardization.log

# View checksums
cat CHECKSUMS.txt

# Compare file sizes
ls -la met_inventory*.tsv
```

### Step 4: Verify Integrity
```bash
# Check if files match their checksums
sha256sum -c CHECKSUMS.txt
```

## Technical Details

### Column Structure
The standardized file expects exactly 4 columns:

| Column | Description | Type |
|--------|-------------|------|
| Object Date | Date or date range | String |
| Title | Object title/description | String |
| Object Number | Museum catalog number | String |
| Link Resource | URL to museum catalog entry | String |

### Encoding
- **Input**: UTF-8 (with fallback error handling)
- **Output**: UTF-8 without BOM (Byte Order Mark)
- **Special Characters**: Fully supported (CJK characters, diacritics, etc.)

### Delimiter
- **Source**: Tab character (\\t = 0x09)
- **Output**: Tab character (\\t = 0x09)

### Line Endings
- **Output Format**: Unix-style (LF = \\n)

## Troubleshooting

### Issue: "Column mismatch" warning in log
**Cause**: Source file header doesn't match expected columns
**Solution**: Verify the source file has the correct header row

### Issue: Checksum mismatch during verification
**Cause**: File was modified after standardization
**Solution**: 
1. Do not modify files before verification
2. Re-run standardization to generate new checksums
3. Check for file corruption

### Issue: Encoding errors
**Cause**: File contains non-UTF-8 characters
**Solution**: 
1. Re-encode source file to UTF-8
2. Remove or replace problematic characters
3. Re-run standardization

### Issue: Different row count
**Cause**: Expected based on data format
**Solution**: Check log file for details about any dropped rows

## Data Quality Notes

### Known Issues in Source Data
- Some rows have empty Title fields
- Multilingual titles (Chinese, Korean, Japanese)
- Special characters and Unicode dashes (–) instead of ASCII hyphens (-)
- Quoted fields with embedded quotes and special characters

### Standardization Impact
- All special characters are preserved
- Empty fields remain empty
- No data values are modified
- Only formatting/structure is normalized

## Security Considerations

- SHA-256 is cryptographically secure for fixity verification
- Checksums prove file integrity but not authenticity
- For authentication, use digital signatures (GPG, etc.)
- Store checksums separately from files for best practice

## References

### Standards
- RFC 4180: Common Format and MIME Type for Comma-Separated Values (CSV) Files
- UTF-8: Unicode Transformation Format – 8-bit (RFC 3629)
- SHA-256: Secure Hash Algorithm 2 (FIPS 180-4)

### Tools
- `sha256sum`: GNU CoreUtils
- `python3-csv`: Python Standard Library
- `bash`: GNU Bash

## Support

For issues or questions about this standardization process:
1. Check the detailed log file: `met_inventory_standardization.log`
2. Review checksums: `CHECKSUMS.txt`
3. Compare source and output: Use diff or visual comparison tools
4. Verify Python and bash are properly installed

## Preservation Notes

This standardization workflow supports:
- **Long-term preservation**: SHA-256 checksums for fixity
- **Reproducibility**: Documented, scriptable process
- **Auditability**: Detailed logs of changes
- **Interoperability**: Standard TSV format with UTF-8 encoding

