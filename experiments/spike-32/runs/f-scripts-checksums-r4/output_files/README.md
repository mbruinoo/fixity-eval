# Met Museum Inventory TSV Standardization

Complete workflow for standardizing the Met Museum inventory file with full integrity verification using checksums.

## Overview

This standardization process:
- **Cleans** the TSV file structure and data
- **Normalizes** column names and field formatting
- **Validates** required fields and URL formats
- **Preserves** all data through checksum verification
- **Documents** all changes with detailed reports

## Files Included

### Scripts
- `standardize_met_inventory.py` - Main Python standardization script
- `verify_integrity.py` - Post-processing integrity verification
- `run_standardization.sh` - Automated workflow orchestrator

### Data Files
- `met_inventory_source.tsv` - Original source file (reference backup)
- `met_inventory_standardized.tsv` - Cleaned and standardized output
- `standardization_report.json` - Detailed processing report
- `MANIFEST.txt` - File checksums and verification guide
- `README.md` - This file

## Standardization Changes

### Column Names
**Before:** `Object Date`, `Title`, `Object Number`, `Link Resource`  
**After:** `object_date`, `title`, `object_number`, `link_resource`

### Data Cleaning
- Removed leading/trailing whitespace from all fields
- Enforced consistent tab-separated format
- Preserved empty fields where they existed (not filled with defaults)
- Maintained original sort order

### Validation Applied
- **Required:** `object_number` must not be empty
- **Format Check:** `link_resource` URLs must begin with `http`
- **Warnings:** Missing `object_date` values noted in report

## Quick Start

### Running the Standardization

```bash
# Make scripts executable
chmod +x run_standardization.sh standardize_met_inventory.py verify_integrity.py

# Run the complete workflow
./run_standardization.sh

# Run verification independently
python3 verify_integrity.py
```

### Checking File Integrity

The `standardization_report.json` contains SHA-256 checksums for both source and output:

```bash
# Verify using provided checksums
sha256sum -c <<EOF
<source_checksum>  met_inventory_source.tsv
<output_checksum>  met_inventory_standardized.tsv
EOF
```

Or extract from report:
```bash
python3 -c "import json; r=json.load(open('standardization_report.json')); \
  print('Source:', r['source_file']['sha256_checksum']); \
  print('Output:', r['output_file']['sha256_checksum'])"
```

## Checksum Verification

### SHA-256 Checksums
The standardization process generates SHA-256 checksums for:
1. **Source file** - Calculated before processing
2. **Output file** - Calculated after processing

Both are stored in:
- `standardization_report.json` - Machine-readable report
- `MANIFEST.txt` - Human-readable verification file

### Why Checksums Matter
- **Integrity:** Detect any file corruption or tampering
- **Fixity:** Prove the file hasn't changed over time
- **Reproducibility:** Verify processing consistency

### Verifying Checksums

#### Manual verification:
```bash
sha256sum met_inventory_standardized.tsv
# Compare output with SHA-256 in standardization_report.json
```

#### Automated verification:
```bash
python3 verify_integrity.py
```

#### Using MANIFEST.txt:
```bash
cd /mnt/user-data/outputs
# The manifest contains sha256sum format checksums that can be verified:
sha256sum -c MANIFEST.txt 2>/dev/null | grep -E "(passed|failed)"
```

## Data Validation Report

The standardization process validates records and generates a report in `standardization_report.json`:

```json
{
  "processing_summary": {
    "total_records": 89,
    "validation_errors": 0,
    "standardization_applied": [...]
  },
  "validation_issues": []
}
```

### Common Validation Issues
- Missing `object_number` - Cannot process (required field)
- Invalid URL format in `link_resource` - Flagged as warning
- Missing `object_date` - Flagged but records still processed

## Understanding the Output

### Standardized TSV Structure
```
object_date		title		object_number		link_resource
late 19th century	[Title]		C.I.46.9.189		http://www.metmuseum.org/...
```

Column order:
1. `object_date` - Date or date range when object was created
2. `title` - Name/description of the object
3. `object_number` - Museum catalog number (unique identifier)
4. `link_resource` - URL to the museum's collection page

### Report Structure (standardization_report.json)
```
├── timestamp              ISO 8601 timestamp of processing
├── source_file           Source file metadata with SHA-256
├── output_file           Output file metadata with SHA-256
├── processing_summary    Statistics and standardization changes applied
└── validation_issues     Any problems detected during processing
```

## Use Cases

### 1. Data Import
The standardized file is ready for:
- Database ingestion
- CSV/spreadsheet tools
- Data analysis workflows
- XML/JSON conversion

### 2. Long-term Archival
Checksums enable:
- Periodic integrity verification
- Detecting accidental corruption
- Proving file provenance
- Compliance with data preservation standards

### 3. Comparison with Original
```bash
# See what changed
diff -u met_inventory_source.tsv met_inventory_standardized.tsv | head -50
```

## Technical Details

### Checksum Calculation
SHA-256 is calculated over the entire file byte-by-byte, making it:
- **Collision-resistant:** Virtually impossible to create a different file with same hash
- **Deterministic:** Same file always produces same checksum
- **Size-invariant:** Works for files of any size

### Python Implementation
```python
import hashlib
sha256_hash = hashlib.sha256()
with open(file, "rb") as f:
    for byte_block in iter(lambda: f.read(4096), b""):
        sha256_hash.update(byte_block)
checksum = sha256_hash.hexdigest()
```

## Troubleshooting

### Checksum Mismatch
If reported and actual checksums don't match:
1. Verify the file hasn't been modified: `ls -la met_inventory_standardized.tsv`
2. Re-run `verify_integrity.py` to recalculate
3. Check for file corruption on disk

### Missing Fields
If you see warnings about missing data:
1. Check `standardization_report.json` for specific row numbers
2. Review the original file for intentionally empty fields
3. This is normal for museum catalogs (not all fields populated for all items)

### Script Permissions
Make scripts executable:
```bash
chmod +x *.py *.sh
```

## Future Verification

To verify file integrity months or years later:

```bash
# Store this information securely
echo "Original checksum from MANIFEST.txt or standardization_report.json"
echo "SHA-256: [checksum_value]"

# Later, verify the file hasn't changed
sha256sum met_inventory_standardized.tsv
# Should match the stored checksum
```

## References

- [SHA-256 Standard](https://en.wikipedia.org/wiki/SHA-2)
- [Python hashlib Documentation](https://docs.python.org/3/library/hashlib.html)
- [Tab-Separated Values Format](https://en.wikipedia.org/wiki/Tab-separated_values)

## License & Attribution

This standardization workflow was created for the Met Museum inventory dataset.
All processing scripts are provided as-is for data preservation purposes.

---

**Last Updated:** 2024  
**Format Version:** 1.0  
**Encoding:** UTF-8
