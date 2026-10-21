I'll help you standardize this TSV file while preserving fixity through checksums. Let me first work with the uploaded file and document my process.

Now let me view the original file to get its full content and create a standardization script:

Now I'll create a Python script to standardize the TSV file and compute checksums:

Now I'll create a shell script to run the standardization and verify checksums:

Now let me execute the standardization:

Perfect! Now let me verify the output and show you the results:

Excellent! Let me also verify the standardized file looks good:

Perfect! Let me create one final verification document:

Perfect! Let me create one more verification to double-check everything:

Perfect! Here's your complete summary:

## ✅ Standardization Complete with Fixity Verification

Your Met Museum inventory TSV file has been successfully standardized with full integrity verification. Here's what was delivered:

### **Output Files** (ready to download)

1. **met_inventory_standardized.tsv** — The clean, standardized data file
   - 100 data rows + 1 header row (101 lines total)
   - 4 columns maintained: Object Date | Title | Object Number | Link Resource
   - All data preserved exactly, whitespace normalized

2. **CHECKSUMS.txt** — Cryptographic integrity verification
   - Input SHA256: `a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf`
   - Output SHA256: `81783da84538cbaa1ced2514f557ca3da6d51484fdf1aa8cdcd152af5aeb397f`

3. **standardization_report.txt** — Detailed processing report (0 issues found)

4. **STANDARDIZATION_SUMMARY.md** — Comprehensive documentation

5. **standardize_met_inventory.py** — Reusable Python script for reproducibility

6. **run_standardization.sh** — Bash wrapper for automation

### **What Was Standardized**

- ✅ Whitespace normalization (leading/trailing spaces removed)
- ✅ Empty cells standardized to consistent empty strings
- ✅ All 4 columns verified present in every row
- ✅ UTF-8 encoding and special characters preserved (French accents, Chinese characters, em-dashes)
- ✅ All URLs, object numbers, and data values intact
- ✅ Zero data loss or corruption

### **Fixity Verification**

- Both source and output files checksummed with SHA256
- Row counts verified: 100 records + header maintained
- Column structure validated
- All data integrity checks passed

You can verify the output file after download by running:
```bash
sha256sum met_inventory_standardized.tsv
```
Should match: `81783da84538cbaa1ced2514f557ca3da6d51484fdf1aa8cdcd152af5aeb397f`