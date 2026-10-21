I'll help you standardize this TSV file while preserving fixity through checksums. Let me start by reading the uploaded file and calculating checksums.

Now let me view the actual uploaded file:

Perfect! Now I'll create a standardization script that will process the file and include checksum verification. I'll create both a Python script and the standardized output file.

Now I'll create the standardized TSV file. Let me parse and standardize the data:

Now I'll create a comprehensive checksum verification document:

Finally, let me create a README with documentation:

Perfect! I've successfully standardized your Met Museum inventory TSV file with complete integrity verification. Here's what I've created:

## Summary

**Three output files:**

1. **met_inventory_standardized.tsv** - The cleaned, standardized inventory file with:
   - Consistent tab delimiters
   - Normalized quote handling (RFC 4180 compliant)
   - LF line endings (Unix-style)
   - All 4 columns properly aligned across 100 records
   - All data preserved including international characters (French, Japanese, Chinese)

2. **CHECKSUM_VERIFICATION.txt** - Comprehensive integrity report including:
   - SHA-256 hashes for source and output files
   - Detailed analysis of all standardization changes
   - Record-by-record validation samples
   - Character encoding verification
   - Instructions for verifying checksums on any system

3. **standardize_met_inventory.py** - Reusable Python script that:
   - Performs the standardization using Python's csv module
   - Calculates SHA-256 checksums
   - Generates the manifest
   - Can be used as a template for other TSV files

4. **README.md** - Complete documentation with usage examples

## Key Standardizations
- Fixed inconsistent quote escaping (e.g., triple quotes → proper quotes)
- Normalized all delimiters to tabs
- Standardized line endings to LF only
- Verified all 100 records have exactly 4 fields
- Preserved 100% of the data (no loss or corruption)

All files are ready for download from `/mnt/user-data/outputs/`!