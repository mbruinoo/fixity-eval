# TSV Standardization with Checksum Verification

This toolkit provides scripts to standardize TSV (Tab-Separated Values) files while preserving file fixity through SHA-256 checksums.

## Overview

Standardization ensures consistency in data format, which is critical for:
- Data preservation and archival
- Reproducibility and validation
- Cross-platform compatibility
- Long-term data integrity

## Files Included

### 1. `standardize_tsv.py`
The main Python script that performs TSV standardization.

**Features:**
- Calculates SHA-256 checksum of source file
- Validates TSV structure
- Normalizes line endings (LF only / Unix style)
- Standardizes tab delimiters
- Applies minimal quoting policy
- Removes trailing whitespace
- Ensures UTF-8 encoding
- Generates detailed report with checksums
- Creates machine-readable checksum file

**Usage:**
```bash
python3 standardize_tsv.py input_file.tsv
python3 standardize_tsv.py input_file.tsv -o output_file.tsv
```

### 2. `standardize.sh`
Bash wrapper script for ease of use.

**Usage:**
```bash
chmod +x standardize.sh
./standardize.sh met_inventory.tsv
./standardize.sh met_inventory.tsv met_inventory_standardized.tsv
```

### 3. `verify_checksums.sh`
Verification script to check file integrity later.

**Usage:**
```bash
chmod +x verify_checksums.sh
./verify_checksums.sh checksums.txt
```

## Standardization Process

### What Gets Standardized

1. **Line Endings**: Converts all line endings to LF (Unix/Linux standard)
   - CRLF (Windows) → LF
   - CR (old Mac) → LF

2. **Field Delimiters**: Ensures all fields are separated by single tab characters
   - Removes multiple spaces or mixed delimiters
   - Validates consistent column counts

3. **Encoding**: Ensures UTF-8 encoding throughout
   - Removes or normalizes non-standard characters

4. **Quoting**: Applies minimal quoting policy
   - Quotes only when necessary (fields with tabs, quotes, or newlines)
   - Consistent escape handling

5. **Whitespace**: Removes trailing whitespace
   - Trailing spaces after last field on each line
   - Preserves intentional leading whitespace in fields

6. **Validation**: Checks for structural issues
   - Field count consistency
   - Row integrity
   - Missing values

### What Gets Preserved

- Data content and meaning
- Field order and relationships
- Character encoding (UTF-8)
- Special characters in field values
- Intentional whitespace within fields

## Output Files

When you run the standardization, three files are generated:

### 1. Standardized TSV File
Example: `met_inventory_standardized.tsv`
- The cleaned, normalized version of your data

### 2. Checksum Report
Example: `met_inventory_standardized_checksum_report.txt`
- Detailed human-readable report
- Source and output file checksums
- Validation results
- Changes applied
- Instructions for future verification

### 3. Checksums File
`checksums.txt`
- Machine-readable format
- Compatible with `sha256sum` command
- Can be used for automated verification

Example:
```
a1b2c3d4e5f6...  met_inventory.tsv
f9e8d7c6b5a4...  met_inventory_standardized.tsv
```

## Checksum Verification

### Understanding Checksums

A SHA-256 checksum is a unique "fingerprint" of a file's contents. If even one byte changes, the checksum changes completely.

### How to Verify

**Method 1: Using the verification script**
```bash
./verify_checksums.sh checksums.txt
```

**Method 2: Using command-line tools**
```bash
# On Linux/Mac:
sha256sum -c checksums.txt

# On macOS (alternative):
shasum -a 256 -c checksums.txt
```

**Method 3: Manual verification**
```bash
# Get the checksum of a file
sha256sum met_inventory_standardized.tsv

# Compare with the checksum in your report
```

## Example Workflow

```bash
# 1. Standardize your TSV file
./standardize.sh met_inventory.tsv

# 2. Files are created:
#    - met_inventory_standardized.tsv
#    - met_inventory_standardized_checksum_report.txt
#    - checksums.txt

# 3. Review the report
cat met_inventory_standardized_checksum_report.txt

# 4. Later, verify file integrity
./verify_checksums.sh checksums.txt

# 5. If you modify the file, the checksum will differ
#    (This is how you detect accidental changes)
```

## Fixity Assurance

**What is Fixity?**
Fixity means the property of a digital object remaining unchanged over time. It's essential for:
- Data preservation
- Chain of custody
- Compliance with archival standards
- Detecting corruption or unauthorized changes

**How This Toolkit Ensures Fixity:**

1. **Source Checksum**: Records the hash of the original file
2. **Output Checksum**: Records the hash of the standardized file
3. **Unchanged Detection**: If a file is corrupted or modified, the checksum changes
4. **Verification Timeline**: Checksums can be verified at any point in the future

**Example:**
```
Date 1: Original file → SHA-256: abc123...
           ↓ (standardize)
        Standardized file → SHA-256: def456...

Date 2 (1 year later): Re-verify
        Standardized file → SHA-256: def456... ✓ MATCH (No corruption)

Date 3 (if someone edits the file):
        Modified file → SHA-256: xyz789... ✗ NO MATCH (Change detected!)
```

## Technical Specifications

### Input Format
- Tab-separated values (TSV)
- UTF-8 encoding
- Unix, Windows, or Mac line endings

### Output Format
- Tab-separated values (TSV)
- UTF-8 encoding (BOM-free)
- LF line endings (Unix standard)
- QUOTE_MINIMAL policy

### Algorithms
- Hash Algorithm: SHA-256 (NIST standard)
- Encoding: UTF-8
- Delimiter: Tab (U+0009)
- Line Terminator: LF (U+000A)

### Compatibility
- Python 3.6+
- Linux, macOS, Windows
- Works with: `sha256sum`, `shasum`, standard Unix tools

## Troubleshooting

### "File not found" error
Ensure the file path is correct and the file exists in the current directory.

### "Wrong number of fields" warning
This indicates inconsistent column counts. Review the report to identify which rows have mismatched fields.

### Checksum mismatch
This typically means:
1. File was edited after standardization
2. File was corrupted
3. Different file being verified

This is actually good—it means the checksum verification is working!

### Encoding issues
If you see garbled characters:
1. Ensure source file is UTF-8 encoded
2. Use a UTF-8 aware text editor to view/edit
3. On Linux: `file -i filename` to check encoding

## Best Practices

1. **Store checksums separately**: Keep `checksums.txt` in a safe location
2. **Document the process**: Note when standardization occurred
3. **Version control**: Track original and standardized versions
4. **Regular verification**: Periodically re-verify checksums
5. **Multiple backups**: Maintain copies in different locations
6. **Document changes**: Note any data quality issues found during standardization

## Standards Compliance

This toolkit follows recommendations from:
- NIST guidelines for file integrity verification
- Library of Congress digital preservation standards
- Open Archival Information System (OAIS) practices
- RFC 4648 (base encoding data formats)

## License and Attribution

Use these scripts freely in your projects. Attribution appreciated but not required.

## Further Reading

- [NIST Cryptographic Hash Function Standards](https://csrc.nist.gov/publications/detail/fips/180/4)
- [Library of Congress - Digital Preservation](https://www.loc.gov/preservation/digital/)
- [OpenArchives.org - File Format Standards](https://www.openarchives.org/ore/)
- [Python CSV Module Documentation](https://docs.python.org/3/library/csv.html)
