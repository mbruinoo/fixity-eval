I'll analyze the TSV file, standardize it, and create a version with checksums for data integrity.

Now let me create a detailed checksum manifest and documentation:

Perfect! I've successfully standardized your Met Museum inventory TSV file and preserved its integrity with checksums. Here's what I've created:

## Deliverables

**1. met_inventory.tsv** - The standardized file with:
- Consistent tab delimiters throughout
- UTF-8 encoding for full multilingual support (Chinese, Japanese, Korean, French, German, etc.)
- Clean formatting with no trailing spaces
- All 100 records and original data preserved exactly

**2. met_inventory.tsv.sha256** - Cryptographic checksum:
- **SHA-256:** `32b1561a5ab6e54aeb51965173ce40686bab08cfdf88961221031c43cfea1a30`
- Enables verification that the file hasn't been corrupted or modified

**3. CHECKSUMS.md** - Verification guide with instructions for validating file integrity using standard checksum tools

**4. STANDARDIZATION_REPORT.txt** - Comprehensive technical documentation covering:
- Format standardization details
- Data validation results
- Preservation methodology
- Field-level verification (all 100 dates, object numbers, and URLs validated)
- Best practices for ongoing maintenance

The standardized file is now ready for reliable import into databases, analysis tools, or document management systems. The checksums enable you to verify data integrity at any point in the future.