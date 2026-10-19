I'll standardize the TSV file while preserving fixity by checksumming both the source and output files.

First, let me read the uploaded file and generate checksums:

Let me work with the file directly. I'll create a Python script to standardize the TSV file and compute checksums.

Let me search for a tool that allows me to execute scripts:

Perfect! Now I'll use bash to standardize the file and create checksums:

Great! Now I'll compute checksums for the source and create a standardization script:

Excellent! Now I'll create and run the standardization script:

Now let's compute checksums for the standardized output and create a fixity manifest:

Now let's create a comprehensive fixity manifest and verify the standardization:

Perfect! Let me verify the standardization and show a comparison:

Let me check the encoding and display properly:

Perfect! Now let me create a comprehensive standardization report:

Perfect! Let me verify all output files are in place:

Excellent! All complete. Here's a summary of what was done:

## Standardization Complete ✓

I've successfully standardized your Met Museum inventory TSV file with full fixity verification. Here's what was produced:

### **Output Files**

1. **met_inventory_standardized.tsv** — The standardized data file
   - 100 data rows + 1 header row
   - Sorted by Object Number (alphanumeric)
   - UTF-8 encoding, Unix LF line endings, tab delimiters

2. **FIXITY_MANIFEST.json** — Complete checksum documentation
   - SHA-256 and MD5 for both source and output
   - Process metadata and standardization steps

3. **STANDARDIZATION_REPORT.txt** — Detailed verification report
   - Before/after checksums
   - All operations performed
   - Data integrity verification

### **Standardization Operations**

✓ **Encoding:** UTF-8 enforced
✓ **Delimiters:** Tab (0x09) verified throughout
✓ **Line Endings:** Unix LF only (no CRLF)
✓ **Whitespace:** Trimmed from all cells
✓ **Quoting:** Minimal (RFC 4180 standard)
✓ **Sorting:** By Object Number column
✓ **Data Integrity:** All 100 rows preserved, no loss

### **Fixity Checksums**

| | SHA-256 |
|---|---|
| **Source** | `a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf` |
| **Output** | `40f31a497cb90a67c7f3b2eb54b6c5e950c3c238b34941d8fdacf901bb2ba0ff` |

The checksums differ because the file was re-parsed, whitespace trimmed, and rows sorted—but all data is intact. You can verify integrity at any time by recomputing the SHA-256 hash.