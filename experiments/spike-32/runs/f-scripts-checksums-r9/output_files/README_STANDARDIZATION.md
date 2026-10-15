# TSV Standardization Process with Integrity Verification

This package contains scripts to standardize a Museum of Metropolitan Art inventory TSV file while maintaining data integrity through cryptographic checksums.

## Overview

The standardization process applies consistent formatting rules to ensure the TSV file follows best practices for data preservation and interoperability. All changes are documented and verified using MD5 and SHA256 checksums.

## Files Included

### Scripts

1. **standardize_tsv.py** - Main standardization script
   - Reads the source TSV file
   - Applies standardization rules
   - Generates checksums for source and output
   - Creates a JSON manifest with metadata

2. **run_standardization.sh** - Bash wrapper script
   - Orchestrates the standardization process
   - Creates an audit log of all operations
   - Validates the output
   - Provides human-readable reporting

3. **verify_integrity.py** - Verification script
   - Checks output file against manifest checksums
   - Validates TSV structure
   - Reports any discrepancies

### Output Files

After running the scripts, you'll have:

1. **met_inventory_standardized.tsv** - The standardized data file
2. **met_inventory_manifest.json** - Checksums and metadata
3. **standardization_audit.log** - Complete audit trail

## Standardization Rules Applied

The following rules were applied to standardize the file:

1. **Header Normalization** - Removed extra whitespace from column headers
2. **Consistent Delimiters** - Ensured all fields are separated by tabs
3. **Encoding** - UTF-8 encoding with Unix line endings (LF)
4. **Value Trimming** - Removed leading and trailing whitespace from values
5. **Structure Preservation** - Maintained internal content structure and formatting
6. **Validation** - Identified rows with missing required fields

## How to Use

### Running the Standardization

```bash
chmod +x run_standardization.sh
./run_standardization.sh
```

Or run the Python script directly:

```bash
python3 standardize_tsv.py /path/to/source.tsv /path/to/output.tsv /path/to/manifest.json
```

### Verifying Integrity

```bash
python3 verify_integrity.py /path/to/output.tsv /path/to/manifest.json
```

## Understanding the Manifest

The manifest file (`met_inventory_manifest.json`) contains:

### Source File Information
```json
{
  "source_file": {
    "path": "/full/path/to/input/file",
    "size_bytes": 12345,
    "checksums": {
      "md5": "abc123...",
      "sha256": "def456..."
    }
  }
}
```

### Output File Information
```json
{
  "output_file": {
    "path": "/full/path/to/output/file",
    "size_bytes": 12345,
    "checksums": {
      "md5": "abc123...",
      "sha256": "def456..."
    }
  }
}
```

### Statistics
```json
{
  "statistics": {
    "total_rows": 100,
    "total_columns": 4,
    "columns": ["Object Date", "Title", "Object Number", "Link Resource"],
    "issues_found": 0
  }
}
```

## Data Quality Issues

The standardization script identifies the following types of data quality issues:

- Missing values in required fields (Object Date, Title, Object Number)
- Records with incomplete data
- Structural inconsistencies

All issues are logged in the manifest for manual review and correction.

## Integrity Verification Workflow

The integrity verification process ensures data hasn't been corrupted:

1. **File Size Check** - Verifies the output file size matches the recorded size
2. **MD5 Verification** - Checks MD5 checksum against manifest
3. **SHA256 Verification** - Checks SHA256 checksum against manifest
4. **Structure Validation** - Confirms valid TSV format and row/column counts

If all checks pass, the file integrity is confirmed. If any check fails, investigate the cause before using the file.

## Example Manifest Output

```json
{
  "timestamp": "2024-01-15T10:30:45.123456",
  "source_file": {
    "path": "/mnt/user-data/uploads/met_inventory.tsv",
    "size_bytes": 87543,
    "checksums": {
      "md5": "a1b2c3d4e5f6...",
      "sha256": "0a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t..."
    }
  },
  "output_file": {
    "path": "/mnt/user-data/outputs/met_inventory_standardized.tsv",
    "size_bytes": 87432,
    "checksums": {
      "md5": "x9y8z7w6v5u4...",
      "sha256": "1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t..."
    }
  },
  "standardization_rules": [
    "Normalized headers (stripped whitespace)",
    "Consistent tab delimiters throughout",
    "UTF-8 encoding with Unix line endings (LF)",
    "Values trimmed of leading/trailing whitespace",
    "Preserved internal structure and content"
  ],
  "statistics": {
    "total_rows": 100,
    "total_columns": 4,
    "columns": ["Object Date", "Title", "Object Number", "Link Resource"],
    "issues_found": 0
  },
  "issues": "None"
}
```

## Audit Trail

The audit log (`standardization_audit.log`) provides:

- Timestamp of processing
- Files processed
- Detailed output from each script
- Validation results
- File size comparisons
- Structure validation results

## Technical Details

### Checksums

The process uses two cryptographic hash algorithms:

- **MD5** - Fast, legacy support (used for quick verification)
- **SHA256** - Cryptographically secure (primary verification method)

Both checksums are computed and stored to provide redundant integrity verification.

### File Processing

The standardization process:

1. Reads the input file as UTF-8
2. Parses using Python's csv module with tab delimiter
3. Normalizes headers and values
4. Writes output in UTF-8 with Unix line endings
5. Computes checksums on binary data
6. Creates a machine-readable manifest

### Dependencies

- Python 3.x
- Standard library only (csv, hashlib, json, etc.)
- Bash shell (for the wrapper script)
- No external packages required

## Quality Assurance

The standardization process includes:

- ✓ Checksum verification for source and output
- ✓ TSV structure validation
- ✓ Row and column count confirmation
- ✓ Data quality issue identification
- ✓ Audit trail logging
- ✓ Manifest generation for documentation

## Troubleshooting

### Script Permissions
```bash
chmod +x run_standardization.sh
chmod +x standardize_tsv.py
chmod +x verify_integrity.py
```

### Python Version
Ensure Python 3.x is installed:
```bash
python3 --version
```

### File Encoding Issues
If you encounter encoding errors, verify the input file is UTF-8:
```bash
file -b --mime-encoding met_inventory.tsv
```

### Checksum Mismatches
If verification fails, check:
1. That the manifest file hasn't been modified
2. That the output file hasn't been corrupted
3. That you're using the correct file paths
4. File permissions

## References

- [RFC 3394 - Checksums](https://tools.ietf.org/html/rfc3394)
- [Python CSV Module Documentation](https://docs.python.org/3/library/csv.html)
- [SHA-2 Hash Function](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.180-4.pdf)

## Support

For issues or questions:

1. Check the audit log for detailed operation information
2. Review the manifest for data quality issues
3. Run the verification script to confirm integrity
4. Consult the troubleshooting section above

## License

These scripts are provided as-is for data standardization and preservation purposes.
