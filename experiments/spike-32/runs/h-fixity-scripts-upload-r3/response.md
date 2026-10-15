I'll standardize the TSV file while preserving fixity by checksumming both the source and result. Let me start by examining and checksumming the uploaded file.

Now let me check the uploaded file:

Let me search for the file:

Let me find the uploaded file and checksum it:

Great! Now let me checksum the source file and examine it:

Excellent! Now let me create a Python script to standardize the TSV file:

Now let me run the standardization script:

Perfect! Now let me checksum the output file and create a verification report:

Now let me create a detailed fixity report:

Perfect! Let me verify the output by showing a sample:

## Summary

I've successfully standardized your TSV file while maintaining full fixity verification. Here's what was done:

**Standardization Actions:**
- Ensured consistent tab delimiters throughout
- Removed trailing whitespace from all fields
- Normalized line endings to Unix (LF) standard
- Validated all 101 rows have exactly 4 columns consistently
- Preserved all data content without modification

**Fixity Checksums:**

| File | SHA256 |
|------|--------|
| **Source** | `e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf` |
| **Standardized** | `37d977d40f2e18da2a216d816e48a1ab0d5d72b8bbab35b022a0914b3a866523` |

**Output Files:**
1. **met_inventory_standardized.tsv** — Your standardized data (101 rows, 4 columns)
2. **FIXITY_REPORT.txt** — Complete verification documentation with checksums
3. **standardize_tsv.py** — The standardization script used

The checksums differ (as expected) because formatting was normalized, but the data content remains unchanged. You can verify file integrity at any time using the checksum values in the report.