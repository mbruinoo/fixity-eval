I'll standardize this TSV file by cleaning up formatting issues and ensuring consistent structure, while preserving file integrity with checksums.

Now I'll create a Python script to standardize the TSV file and compute checksums:

Now let me run the standardization script:

Perfect! Let me verify the output files and show you the results:

Excellent! Let me verify the file integrity one more time:

Perfect! I've successfully standardized your Met Museum inventory TSV file. Here's what was done:

## Summary

**Files created in `/mnt/user-data/outputs/`:**
1. **met_inventory_standardized.tsv** - The standardized data file (16 KB, 102 lines including header)
2. **checksums.txt** - Integrity checksums and processing record

**Standardization applied:**
- Ensured consistent tab delimiters throughout
- Stripped leading/trailing whitespace from all field values while preserving internal formatting
- Standardized column ordering (Object Date → Title → Object Number → Link Resource)
- Unified handling of missing values (empty fields remain empty, no changes to data content)
- Processed 101 data rows

**Fixity & Checksums (SHA-256):**
- **Source file:** `e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf`
- **Result file:** `8bd2dde1491ed1513ad54fb189ca7b75ec15b688a7b98020ea173cc29a7e11e0`

Both SHA-256 and MD5 checksums are documented in the `checksums.txt` file for verification. The script is also saved as `/mnt/user-data/standardize_tsv.py` should you need to run it again on similar files.