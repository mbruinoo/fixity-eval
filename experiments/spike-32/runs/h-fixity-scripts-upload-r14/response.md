I'll standardize the TSV file and preserve fixity by checksumming both the source and result.

Let me view the uploaded file first:

Now I'll create a Python script to standardize the TSV file and compute checksums:

Now let me run the script and create the standardized file:

Perfect! Now let me create a detailed fixity report document:

Let me verify the output file looks correct:

Perfect! The output shows proper standardization (^I represents tabs, $ represents LF line endings). Let me create one more verification showing a sample comparison:

Perfect! Let me verify the final output files exist:

Excellent! Here's a summary of the completed standardization with fixity verification:

## Summary

Your Metropolitan Museum TSV inventory file has been successfully standardized with complete fixity verification. Here's what was delivered:

### Standardization Performed
- **Line endings:** Normalized to LF (Unix format)
- **Delimiters:** Standardized to literal tab characters
- **Whitespace:** Removed trailing spaces, preserved structure
- **Encoding:** UTF-8 maintained with all special characters preserved
- **Data integrity:** All 100 records verified—no data loss

### Fixity Documentation

**Source File:**
- SHA-256: `e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf`
- 101 lines (1 header + 100 records)

**Output File:**
- SHA-256: `6dacf89c79b4322e0a21c34c379671ec614bbd5501a20729ac72d8e806f629dd`
- 101 lines (1 header + 100 records)

The hash change is expected because format standardization alters the byte representation. Both hashes are deterministic and reproducible.

### Deliverables
1. **met_inventory_standardized.tsv** — Your standardized inventory file
2. **standardize_tsv.py** — Reproducible Python processing script
3. **FIXITY_REPORT.md** — Detailed fixity and standardization report
4. **VERIFICATION.txt** — Comprehensive verification report with checksums

All files are ready in `/mnt/user-data/outputs/` for download.