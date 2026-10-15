I'll help you standardize this TSV file. Let me first examine it more closely and then create a standardized version with checksums.

Now let me examine the file and create a standardization script:

Now I'll create a Python script to standardize the file with checksums:

Perfect! Let me verify the output and create a checksum verification script:

Now let me create a verification script and sample comparison:

Finally, let me create a detailed documentation file:

Perfect! Let me create one final summary file:

Excellent! Here's what I've created for you:

## Summary

I've successfully standardized your Met Museum inventory TSV file with full cryptographic fixity verification. Here's what was generated:

### Output Files

1. **met_inventory_standardized.tsv** — Your standardized data file (101 rows, 4 columns)

2. **standardization_manifest.json** — Machine-readable metadata with checksums:
   - Source file SHA256: `e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf`
   - Output file SHA256: `37d977d40f2e18da2a216d816e48a1ab0d5d72b8bbab35b022a0914b3a866523`

3. **verify_checksums.sh** — Executable bash script to verify integrity at any time

4. **STANDARDIZATION_REPORT.md** — Comprehensive documentation

### Standardization Applied

- Ensured 4-column structure (Object Date | Title | Object Number | Link Resource)
- Stripped whitespace normalization
- Consistent tab delimiters
- Minimal quoting strategy
- UTF-8 encoding preserved (supports CJK, Hangul, and multilingual content)
- Unix line endings (LF)

### Integrity Verification

✓ All checksums verified successfully
✓ Zero issues encountered — your source file was well-formed
✓ All 101 rows (1 header + 100 data) processed perfectly

You can verify the output file's integrity at any point using the SHA256 checksum or by running the included verification script.