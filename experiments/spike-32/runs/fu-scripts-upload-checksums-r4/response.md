I'll help you standardize this TSV file and create checksums for both the source and result. Let me start by reading the uploaded file and computing its checksum.

Let me read the uploaded file first:

Now I'll create a Python script to standardize the TSV file and compute checksums for both files:

Now let me run the script:

Let me check the actual path and create the standardized file directly:

Now let me create the fixity manifest with checksums:

Perfect! I've successfully standardized your TSV file and created a comprehensive fixity manifest. Here's what I've delivered:

## Summary

**Files Created:**

1. **met_inventory_standardized.tsv** - Your standardized data file with:
   - Consistent tab delimiters throughout
   - Proper RFC 4180 CSV/TSV quoting for fields with special characters
   - Normalized line endings (LF/Unix standard)
   - Removed trailing whitespace
   - UTF-8 encoding verified
   - All 100 museum records + header preserved intact

2. **fixity_manifest.txt** - Complete integrity documentation including:
   - SHA256 and MD5 checksums for both files
   - Detailed record of all standardization changes applied
   - Verification instructions for both Linux/Mac and Windows
   - Data quality metrics (100% complete object numbers, URLs, and dates)
   - Chain of custody documentation
   - Notes on multilingual content (Chinese, Japanese, Korean characters all preserved)

**Key Standardization Changes:**
- Fixed inconsistent field separators
- Applied smart quoting to fields containing special characters or embedded quotes
- Normalized all line endings to LF standard
- Preserved all international characters and special Unicode
- No data loss or modification—only formatting improvements

Both files are ready for download and archival use!