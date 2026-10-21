# Met Museum Inventory - Fixity and Integrity Preservation

## Overview

This standardization process preserves **fixity** (the ability to verify that digital objects have not been altered or corrupted) through comprehensive checksumming at multiple levels of granularity.

## What is Fixity?

Fixity is a fundamental requirement in digital preservation. It ensures that:

1. **Source data** has not been inadvertently modified
2. **Transformation processes** are reproducible and auditable
3. **Output data** matches expected transformations
4. **Individual components** (rows, cells) can be verified for integrity

## Checksumming Strategy

### Level 1: Whole File Checksums (SHA256)

**Purpose**: Detect any change to the entire file

**Method**: SHA256 hash of complete file content

**Use Case**: Quick verification that a file hasn't been corrupted during transmission or storage

```bash
# Original file
sha256sum met_inventory.tsv > source.sha256

# Standardized file  
sha256sum met_inventory_standardized.tsv > output.sha256

# Verify later
sha256sum -c source.sha256
sha256sum -c output.sha256
```

### Level 2: Row-Level Checksums

**Purpose**: Detect corruption or alteration of specific records

**Method**: SHA256 of serialized JSON representation of each row

**Use Case**: Identify which records (if any) have been modified

**Row checksum format** (in `checksums.json`):
```json
{
  "row_2": {
    "original_hash": "abc123def...",
    "standardized_hash": "xyz789uvw...",
    "object_number": "91.1.396"
  }
}
```

**Key aspects**:
- Each row is converted to JSON with sorted keys for consistency
- Both pre- and post-standardization hashes are recorded
- Object number is included for easy reference
- Hashes allow verification that standardization rules were correctly applied

### Level 3: Field-Level Validation

**Purpose**: Understand what transformations were applied

**Documentation in checksums.json**:
- Tracks which rows were transformed
- Captures both source and standardized states
- Can be used to audit transformation logic

## Preserved Data Characteristics

### What Was Preserved
✓ All Unicode content (including CJK characters)
✓ Special characters and accents
✓ Complex object numbering (e.g., "36.120.598a, b")
✓ Punctuation and formatting
✓ Empty/missing values (as empty strings)
✓ Tab-delimited structure

### What Was Normalized
- Column names: Converted to lowercase with underscores
- Whitespace: Trimmed from beginning and end of fields
- Empty titles: Mapped to "[Untitled]" placeholder
- URLs: Validated to start with "http"

## Files Generated

### 1. `met_inventory_standardized.tsv`
- Standardized data file ready for use
- Tab-separated format (TSV)
- UTF-8 encoding
- Four standardized columns: object_date, title, object_number, resource_link

### 2. `checksums.json`
Complete integrity record containing:

```json
{
  "source_file": {
    "hash": "sha256_of_source",
    "timestamp": "ISO8601_timestamp"
  },
  "output_file": {
    "hash": "sha256_of_output", 
    "timestamp": "ISO8601_timestamp"
  },
  "row_transformations": {
    "row_2": {
      "original_hash": "...",
      "standardized_hash": "...",
      "object_number": "91.1.396"
    },
    ...
  }
}
```

### 3. `standardization_report.md`
- Human-readable report of standardization rules
- Data quality statistics
- Transformation summary
- Verification instructions

### 4. `INTEGRITY_VERIFICATION.txt`
- Quick-reference verification guide
- Pre-computed checksums
- Record counts
- Verification commands

### 5. `standardize_met_inventory.py`
- Reproducible Python script
- Can be re-run to verify transformations
- Extensible for additional standardization rules
- Includes detailed comments

### 6. `run_standardization.sh`
- Bash script to orchestrate the process
- Generates all outputs
- Produces integrity verification report
- Can be automated in preservation workflows

## Verification Workflows

### Quick Verification (Whole File)
```bash
# Verify source file integrity
sha256sum -c << EOF
[SHA256_from_checksums.json]  met_inventory.tsv
EOF

# Verify output file integrity
sha256sum -c << EOF  
[SHA256_from_checksums.json]  met_inventory_standardized.tsv
EOF
```

### Detailed Verification (Row Level)
```bash
# Extract and display row-level checksums
cat checksums.json | jq '.row_transformations | to_entries | .[0:5]'

# Verify specific row by object number
cat checksums.json | jq '.row_transformations | to_entries[] | select(.value.object_number == "91.1.396")'
```

### Reproducibility Test
```bash
# Re-run standardization to verify same outputs
python3 standardize_met_inventory.py

# Compare new checksums with originals
diff checksums.json checksums_new.json
```

## Preservation Best Practices

### Recommended Storage
1. **Store original file** with its checksum
2. **Store standardized file** with its checksum  
3. **Store checksums.json** separately for audit trail
4. **Store scripts** to enable re-processing
5. **Store this documentation** with the data

### Recommended Backup Strategy
```
Archive/
├── met_inventory_standardization_v1/
│   ├── Source/
│   │   ├── met_inventory.tsv
│   │   └── source.sha256
│   ├── Output/
│   │   ├── met_inventory_standardized.tsv
│   │   ├── checksums.json
│   │   └── output.sha256
│   ├── Documentation/
│   │   ├── standardization_report.md
│   │   ├── FIXITY_DOCUMENTATION.md
│   │   └── INTEGRITY_VERIFICATION.txt
│   └── Scripts/
│       ├── standardize_met_inventory.py
│       └── run_standardization.sh
```

### Periodic Verification
```bash
#!/bin/bash
# Run monthly to verify data hasn't drifted

cd /archive/met_inventory_standardization_v1/

echo "Verifying source file..."
sha256sum -c Source/source.sha256

echo "Verifying output file..."
sha256sum -c Output/output.sha256

echo "Checking for file changes..."
find . -type f -exec sha256sum {} \; > current_manifest.txt
diff original_manifest.txt current_manifest.txt || echo "Changes detected!"
```

## Technical Details

### Hashing Algorithm: SHA256
- **Algorithm**: Secure Hash Algorithm 256-bit
- **Collision resistance**: Extremely high (256-bit output)
- **Industry standard**: Approved by NIST
- **Performance**: Fast enough for large-scale verification

### Serialization for Row Hashing
Rows are converted to JSON with:
- **Sorted keys**: Ensures consistent hash regardless of field order
- **UTF-8 encoding**: Preserves all Unicode characters
- **ensure_ascii=False**: Prevents ASCII-only encoding

Example:
```python
row_json = json.dumps(
    row_dict, 
    sort_keys=True,           # Consistent ordering
    ensure_ascii=False        # Preserve Unicode
)
row_hash = hashlib.sha256(row_json.encode('utf-8')).hexdigest()
```

## Limitations and Considerations

### What Checksums Detect
✓ Accidental data corruption
✓ Unauthorized modifications
✓ Transmission errors
✓ Storage degradation

### What Checksums Cannot Detect
✗ Authorized but undocumented changes
✗ Attacks with cryptographic breaking
✗ Lost metadata about changes
✗ Version history (single point-in-time snapshot)

**Recommendation**: Combine checksums with:
- Version control systems (Git)
- Change logs
- Digital signatures for sensitive data
- Timestamps and audit trails

## Future Enhancements

1. **Cryptographic signatures**: Add digital signatures for authentication
2. **Distributed verification**: Hash tree structures (Merkle trees)
3. **Temporal records**: Track multiple versions with timestamps
4. **Automated monitoring**: Scheduled verification tasks
5. **Integration**: Embed checksums in file metadata (MIAOW headers)
6. **PREMIS compliance**: Align with digital preservation standards

## References

- **SHA256**: [FIPS 180-4 Standard](https://csrc.nist.gov/publications/detail/fips/180/4)
- **Digital Preservation**: [Library of Congress - Digital Preservation](https://www.loc.gov/preservation/about/amd.html)
- **PREMIS**: [Preservation Metadata Implementation Strategies](https://www.loc.gov/standards/premis/)
- **Fixity Checking**: [Educopia - Fixity Documentation](https://wiki.educopia.org/display/Fixity/Home)

## Support and Questions

For questions about this standardization and fixity process:

1. Review `standardization_report.md` for detailed transformation rules
2. Check `checksums.json` for specific row hashes
3. Run verification commands in `INTEGRITY_VERIFICATION.txt`
4. Re-execute `run_standardization.sh` to reproduce results
5. Examine `standardize_met_inventory.py` script for implementation details
