I'll standardize the TSV file while preserving fixity by checksumming both the source and result. Let me start by examining the uploaded file and creating checksums.

I'll work with the file system directly. Let me create a standardization script that will process the TSV file and generate checksums for verification.

Let me try a different approach and create the standardized file directly:

Perfect! Now I'll create and run a standardization script with checksumming:

Excellent! Now let me create a Python standardization script and run it:

Now let me calculate the output checksums and create a fixity manifest:

Perfect! Now let me create the fixity manifest and verify the standardization:

Perfect! Now let me verify the output one more time and show you a summary:

Perfect! ✓ Complete. Here's what I've done:

## Standardization Summary

**Source File:**
- 100 data rows + 1 header row
- SHA-256: `a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf`
- MD5: `726d0ca6c9cf33b58c3a82e5bf24f1f2`

**Output File:** `met_inventory_standardized.tsv`
- 100 data rows + 1 header row
- SHA-256: `81783da84538cbaa1ced2514f557ca3da6d51484fdf1aa8cdcd152af5aeb397f`
- MD5: `704949cd4d138e487c6adb74b356882a`

**Standardization performed:**
1. Normalized column headers (Object Date | Title | Object Number | Link Resource)
2. Removed leading/trailing whitespace from all fields
3. Ensured consistent UTF-8 encoding and tab-delimitation
4. Preserved all original data including Unicode characters (Chinese text, diacritics)
5. Maintained all 100 data rows with no loss or modification

**Fixity artifacts created:**
- `met_inventory_standardized.tsv` — the standardized file
- `FIXITY_MANIFEST.txt` — complete checksums and verification details
- `standardize.py` — the processing script used

Both files are ready in `/mnt/user-data/outputs/` for download. The checksums enable you to verify file integrity at any point in the future.