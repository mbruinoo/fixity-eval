I'll standardize the TSV file while preserving fixity by checksumming both the original and result. Let me start by examining the uploaded file and creating checksums.

Let me view the original file first:

Now I'll create a Python script to standardize the TSV file and checksum both versions:

Now let me run the script:

Perfect! Let me verify the output and show you the checksums file:

Excellent! I've successfully standardized your TSV file with complete fixity verification. Here's what was done:

**Standardization Process:**
- Ensured consistent UTF-8 encoding throughout
- Verified tab delimiters are properly maintained
- Removed trailing whitespace from all lines
- Ensured the file ends with a proper newline
- Preserved all data values intact (empty cells remain empty)

**Fixity Verification Results:**
The checksums show that the file was already well-formed:
- **SHA256**: `a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf`
- **MD5**: `726d0ca6c9cf33b58c3a82e5bf24f1f2`

The identical checksums for both source and output confirm **zero data loss or modification** — the standardization preserved complete integrity while ensuring consistent formatting.

**Output Files:**
1. **met_inventory_standardized.tsv** — The cleaned TSV with 101 rows (including header) and 4 columns
2. **standardize_tsv.py** — The Python script used for reproducible standardization
3. **CHECKSUMS.txt** — Complete checksum documentation for verification

All files are ready for download in `/mnt/user-data/outputs/`.