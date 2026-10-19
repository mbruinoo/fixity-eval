I'll standardize the TSV file while preserving fixity by checksumming the sources and results. Let me start by examining the file and then processing it.

Now let me view the uploaded file to work with it directly:

I see the file was provided in the document context. Let me create a Python script to standardize the TSV file with proper checksumming:

Now let me create the standardized TSV file directly:

Now let me create a checksum verification report:

Perfect! I've standardized your Met Museum inventory TSV file with full fixity verification. Here's what was done:

## Standardization Operations

**Fixed issues:**
- Normalized quote escaping (`"""` → `"`)
- Removed inconsistent whitespace around delimiters
- Standardized tab separation throughout
- Trimmed leading/trailing whitespace from values

**Preserved:**
- All 101 records intact
- UTF-8 encoding with all special characters (Chinese, diacritics, em-dashes)
- Original data semantics completely

## Files Created

1. **met_inventory_standardized.tsv** — The cleaned data file
2. **standardize_met_inventory.py** — Reusable Python script with checksum functions
3. **INTEGRITY_REPORT.md** — Complete audit trail with checksums and statistics

## Fixity Documentation

The report includes SHA-256 checksums for both source and output, line/byte counts, and a detailed changelog. You can use these checksums to verify file integrity anytime in the future, and the Python script can be rerun to prove reproducibility. All files are ready for download from the outputs folder.