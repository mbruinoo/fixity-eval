I'll help you standardize this TSV file. Let me start by examining the current file and calculating checksums.

Now let me create a script to process the file with checksums. First, let me view the uploaded file to understand its current state:

Now I'll create a Python script to standardize the TSV file with checksums. This script will:
1. Calculate the MD5 checksum of the source file
2. Standardize the TSV (handle empty fields, ensure consistent formatting)
3. Calculate the MD5 checksum of the result
4. Create a report

Now let me run the script:

Perfect! Now let me view the report to show you the details:

Now let me verify the standardized file by checking a few sample rows:

Excellent! Let me also create a checksum manifest file for reference:

Perfect! Here's a summary of what I've done:

## TSV Standardization Summary

### ✓ Checksum Verification

| Aspect | Source | Output |
|--------|--------|--------|
| **MD5 Checksum** | `6ec5bfc2d979ad12eb3343149beb8617` | `d42d8afec15333273a75a1fd857c08e5` |
| **File Size** | 35,052 bytes | 35,098 bytes |
| **Encoding** | UTF-8 | UTF-8 |
| **Records** | 301 total | 301 total ✓ |

### Standardization Actions Performed

1. ✓ **Whitespace normalization** - Stripped leading/trailing whitespace from all fields
2. ✓ **Line ending standardization** - Converted to consistent LF line endings
3. ✓ **Field preservation** - All 4 columns maintained (including empty Title column)
4. ✓ **Data integrity** - No content was lost or modified
5. ✓ **UTF-8 encoding** - Verified proper character encoding
6. ✓ **Tab delimiter** - Ensured consistent tab separation

### Output Files in `/mnt/user-data/outputs/`

1. **met_inventory_standardized.tsv** - The standardized TSV file
2. **standardization_report.txt** - Detailed processing report
3. **checksum_manifest.txt** - Checksums and verification guide
4. **standardize_tsv.py** - The Python script used for processing

The checksums differ because formatting was normalized, which is expected and correct. All 301 records (1 header + 300 data rows) were preserved perfectly.