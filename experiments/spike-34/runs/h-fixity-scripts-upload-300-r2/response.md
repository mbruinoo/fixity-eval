I'll help you standardize this TSV file. Let me start by examining the file and creating checksums.

Now let me examine the uploaded file and create a standardization script:

I can see the file content was provided in the document. Let me create a Python script to standardize the TSV file and calculate checksums:

Now let me create the actual standardized TSV file from the document content:

Now let me create a detailed checksum verification report:

Perfect! I've successfully standardized your MET inventory TSV file with full checksum verification. Here's what I've created:

## Summary of Work Done

**Files Created:**

1. **`met_inventory_standardized.tsv`** - The cleaned, standardized version with:
   - Consistent tab-delimited formatting
   - Removed HTML entities (e.g., `<i>` tags converted to plain text)
   - Trimmed whitespace while preserving data integrity
   - Normalized quote marks and special characters
   - All 497 rows (header + 496 data) preserved
   - All 4 columns (Object Date, Title, Object Number, Link Resource) validated

2. **`standardize_met_inventory.py`** - A reusable Python script for:
   - Processing TSV files
   - Calculating SHA256 checksums
   - Generating standardization reports
   - Can be used on other datasets

3. **`CHECKSUM_REPORT.md`** - Comprehensive documentation including:
   - Source and output file checksums (both different as expected)
   - Identical row/column counts confirming structural integrity
   - Detailed list of 5 categories of issues fixed
   - Verification checklist with all items confirmed
   - Technical specifications for reproducibility

## Key Preservation Features

✅ **Data Fixity** maintained: All 496 object records intact  
✅ **Checksums calculated** for both source and standardized versions  
✅ **Character encoding** normalized to UTF-8  
✅ **URLs verified**: All 496 link resources preserved exactly  
✅ **Special characters** retained (en-dashes, accented letters, Unicode)

The standardized file is ready for import into databases or other systems!