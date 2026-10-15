I'll standardize the TSV file, preserve fixity by checksumming both the source and result, and document the process.

Let me start by examining the uploaded file and calculating its checksum:

Now let me create a Python script to standardize the TSV file and calculate checksums:

Now let me run the script:

Perfect! Now let me verify the standardization by checking the output file and creating a detailed comparison report:

Excellent! Now let me create a comprehensive standardization report:

Interesting! The checksums match, which means the original file was already well-formatted. Let me create a more detailed analysis and an enhanced standardization report:

Perfect! Let me also verify the files are in the output directory:

## Summary

I've successfully standardized your Met Museum inventory TSV file with full fixity verification. Here's what was done:

### Checksum Verification Results
- **Source SHA256:** `e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf`
- **Output SHA256:** `e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf`
- **Match:** ✓ YES (Checksums are identical)

### Standardization Performed
The script validated and standardized:
- ✓ Consistent tab delimiters throughout
- ✓ Normalized all 101 rows to 4 columns (1 header + 100 data rows)
- ✓ UTF-8 encoding with proper handling of international characters (Chinese, Japanese, Korean)
- ✓ Standard Unix line endings (LF)
- ✓ Removed any trailing whitespace

### Key Finding
The original file was already well-formatted, which is why the checksums are identical. The standardization process confirmed the file's integrity rather than making changes.

### Output Files (ready to download)
1. **met_inventory_standardized.tsv** - The standardized data file
2. **STANDARDIZATION_REPORT.md** - Comprehensive report with all verification details
3. **standardization_log.txt** - Machine-readable log
4. **standardize_tsv.py** - Reusable Python script for future standardizations