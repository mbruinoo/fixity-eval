# Met Museum Inventory TSV Standardization with Fixity Preservation

## Overview

This package contains a complete standardization of the Met Museum inventory TSV file with comprehensive fixity preservation through multi-level checksumming. All transformations are documented, reversible, and auditable.

## What's Included

### Data Files
- **`met_inventory.tsv`** - Original source file
- **`met_inventory_standardized.tsv`** - Standardized output file (ready to use)

### Integrity & Verification
- **`checksums.json`** - SHA256 hashes at file and row level
- **`INTEGRITY_VERIFICATION.txt`** - Verification results with pre-computed hashes

### Documentation
- **`FIXITY_DOCUMENTATION.md`** - Comprehensive technical guide to fixity approach
- **`standardization_report.md`** - Detailed transformation rules and data quality metrics
- **`QUICK_REFERENCE.md`** - Quick commands for common tasks
- **`README.md`** - This file

### Scripts
- **`standardize_met_inventory.py`** - Python 3 script that performs standardization with checksumming
- **`run_standardization.sh`** - Bash orchestration script (generates all outputs)

## Quick Start

### Using the Standardized Data
```bash
# The standardized file is ready to use
head -5 met_inventory_standardized.tsv

# View in a spreadsheet application
# or process with your tools
```

### Verifying Data Integrity
```bash
# Quick verification using stored checksums
cat checksums.json | jq '.source_file, .output_file'

# Full file verification
sha256sum met_inventory_standardized.tsv
# Compare with hash in INTEGRITY_VERIFICATION.txt
```

### Re-running the Standardization
```bash
# Requires Python 3.6+
python3 standardize_met_inventory.py

# Or with orchestration script (also generates reports)
bash run_standardization.sh
```

## Standardization Summary

### What Changed
1. **Column names** normalized to snake_case:
   - "Object Date" → "object_date"
   - "Title" → "title"
   - "Object Number" → "object_number"
   - "Link Resource" → "resource_link"

2. **Whitespace** trimmed from all fields

3. **Empty titles** mapped to "[Untitled]"

### What Was Preserved
- ✓ All Unicode content (CJK characters, accents, special symbols)
- ✓ Complex object numbering schemes
- ✓ All punctuation and formatting
- ✓ URL structure and content
- ✓ Data completeness (100 records in → 100 records out)

## Fixity Approach

### Three Levels of Verification

**Level 1: File Checksum**
- SHA256 hash of entire file
- Detects any file-level corruption
- Quick verification

**Level 2: Row Checksums**
- SHA256 hash of each individual row (as JSON)
- Can identify which specific records changed
- Enables targeted verification

**Level 3: Documentation**
- Complete record of transformations applied
- Data quality statistics
- Audit trail for compliance

### How to Verify

**Simple Check:**
```bash
sha256sum -c <<< "$(grep 'output_file' checksums.json | grep -oP '\"hash\": \"\K[^\"]+') met_inventory_standardized.tsv"
```

**Detailed Check:**
```bash
cat checksums.json | jq '.row_transformations | keys' | wc -l
# Should show: 100 (one hash per row)
```

## File Specifications

### Input File
- **Format**: TSV (Tab-Separated Values)
- **Encoding**: UTF-8
- **Columns**: 4 (Object Date, Title, Object Number, Link Resource)
- **Records**: 100 data rows
- **Special Characters**: Full Unicode support

### Output File
- **Format**: TSV (Tab-Separated Values)
- **Encoding**: UTF-8
- **Columns**: 4 (object_date, title, object_number, resource_link)
- **Records**: 100 data rows
- **Special Characters**: Full Unicode support preserved

### Checksum Format (JSON)
```json
{
  "source_file": {
    "hash": "SHA256_HASH",
    "timestamp": "ISO8601_TIMESTAMP"
  },
  "output_file": {
    "hash": "SHA256_HASH",
    "timestamp": "ISO8601_TIMESTAMP"
  },
  "row_transformations": {
    "row_2": {
      "original_hash": "...",
      "standardized_hash": "...",
      "object_number": "91.1.396"
    }
    // ... one entry per row
  }
}
```

## Use Cases

### For Data Consumers
- Use `met_inventory_standardized.tsv` for analysis, import, or processing
- Reference files by `object_number` with confidence
- Query by standardized column names

### For Archivists
- Store all files together for complete provenance
- Run periodic verification using `INTEGRITY_VERIFICATION.txt`
- Re-execute scripts to confirm reproducibility
- Maintain row-level checksums for audit purposes

### For Developers
- Use Python script as template for other standardization projects
- Extend with additional validation rules
- Integrate into automated preservation workflows
- Generate checksums for your own transformations

### For Compliance
- SHA256 checksums meet industry standards (NIST FIPS 180-4)
- Row-level tracking supports PREMIS digital preservation standards
- Complete audit trail from scripts and documentation
- Reproducible transformations enable verification audits

## Data Quality Observations

From `standardization_report.md`:
- **Empty Titles**: 41 records (marked as "[Untitled]")
- **Missing Object Numbers**: 0 records (all preserved)
- **Missing Links**: 0 records (all valid URLs)
- **Unicode Content**: 4 records with CJK characters (preserved)

## Verification Steps

### 1. Verify File Integrity
```bash
# Check that files match their checksums
grep "source_file" checksums.json
sha256sum met_inventory.tsv

grep "output_file" checksums.json
sha256sum met_inventory_standardized.tsv
```

### 2. Verify Record Count
```bash
# Both files should have same number of records
tail -n +2 met_inventory.tsv | wc -l    # Should be 100
tail -n +2 met_inventory_standardized.tsv | wc -l  # Should be 100
```

### 3. Verify Format
```bash
# Check that output has exactly 4 columns
awk -F'\t' 'NR>1 && NF!=4 {print "Row " NR " has " NF " columns"}' met_inventory_standardized.tsv
# Should produce no output (all rows have 4 columns)
```

### 4. Verify Sample Records
```bash
# Compare a record before and after
# In met_inventory.tsv, find: 91.1.396
# In met_inventory_standardized.tsv, find: 91.1.396
# Verify other columns have same data (different column order)
```

## Archive Recommendations

For long-term preservation, archive this entire package:

```
met_museum_inventory_standardization/
├── data/
│   ├── met_inventory.tsv
│   └── met_inventory_standardized.tsv
├── integrity/
│   ├── checksums.json
│   └── INTEGRITY_VERIFICATION.txt
├── documentation/
│   ├── FIXITY_DOCUMENTATION.md
│   ├── standardization_report.md
│   ├── QUICK_REFERENCE.md
│   └── README.md
└── scripts/
    ├── standardize_met_inventory.py
    ├── run_standardization.sh
    └── README.md
```

**Never separate these files** - they form a complete unit necessary for verification and reproducibility.

## Technical Details

### Python Script Features
- Reads source TSV with proper UTF-8 encoding
- Normalizes each field according to documented rules
- Generates SHA256 hashes for all components
- Produces audit-ready checksums.json
- Includes data quality statistics

### Bash Script Features
- Orchestrates the entire standardization process
- Computes file-level checksums
- Verifies record counts before/after
- Generates human-readable verification report
- Can be scheduled for automated verification

### Reproducibility
- Scripts produce identical outputs given same input
- Checksums will match exactly on re-execution
- Transformations are deterministic
- No random elements or external dependencies

## Troubleshooting

### Checksums Don't Match
1. Verify you have the correct files
2. Check that no modifications have been made
3. Ensure using same hash algorithm (SHA256)
4. Re-run standardization script to compare

### Missing Files
1. Ensure all files in package were extracted together
2. Don't move files to different directories separately
3. Keep entire folder structure intact

### Special Character Issues
1. Verify UTF-8 encoding when opening files
2. Use `file` command: `file met_inventory_standardized.tsv`
3. Should show: "UTF-8 Unicode text"

## References

- **TSV Format**: RFC 4180 (Common Format and MIME Type for Comma-Separated Values)
- **SHA256**: FIPS 180-4 Secure Hash Standard
- **UTF-8 Encoding**: RFC 3629
- **JSON Format**: RFC 8259
- **PREMIS**: Preservation Metadata Implementation Strategies (www.loc.gov/standards/premis/)

## License & Attribution

These standardization scripts and documentation are provided as tools for data stewardship and digital preservation. The Met Museum collection metadata is subject to their usage policies.

## Support

For detailed information:
- **Quick commands**: See `QUICK_REFERENCE.md`
- **Technical details**: See `FIXITY_DOCUMENTATION.md`
- **Transformation rules**: See `standardization_report.md`
- **Verification results**: See `INTEGRITY_VERIFICATION.txt`
- **Script implementation**: Review `standardize_met_inventory.py`

## Summary

✓ **100 records** successfully standardized
✓ **4-column structure** verified
✓ **SHA256 checksums** generated at file and row level
✓ **Unicode content** preserved (CJK characters intact)
✓ **Complex numbering** preserved (e.g., "36.120.598a, b")
✓ **Complete audit trail** documented
✓ **Reproducible transformation** scripted

**Ready for use, archival, or further processing.**
