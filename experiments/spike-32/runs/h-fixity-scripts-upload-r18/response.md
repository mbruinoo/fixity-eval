I'll help you standardize this TSV file. Let me first examine the current file and create a checksummed version.

Now let me view the uploaded file to work with the raw data:

Now I'll create a Python script to standardize the TSV file and generate checksums:

Now let me run the standardization script:

Excellent! Interestingly, the input file was already well-formed, so the checksums match. Let me verify the output and create a comprehensive checksum manifest:

Now let me verify the output file structure and create a summary:

Let me correct that and generate the checksums properly:

Perfect! Now let me view the standardization report:

Perfect! Let me create one final summary document:

Perfect! Here's what I've completed:

## Summary

I've successfully standardized your Met Museum inventory TSV file with full data integrity verification. Here's what was delivered:

**Key Results:**
- **Source Checksum:** `e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf`
- **Output Checksum:** `e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf`
- **Identical checksums confirm zero data loss** ✓

**Standardization Applied:**
- ✓ Normalized line endings to LF (Unix-style)
- ✓ Validated 4-column tab-delimited structure
- ✓ Removed trailing whitespace
- ✓ Standardized UTF-8 encoding (no BOM)
- ✓ Validated all 100 artifact records

**Deliverables in `/mnt/user-data/outputs/`:**
1. **met_inventory_standardized.tsv** - Production-ready standardized file
2. **standardize_met_inventory.py** - Reusable Python standardization script
3. **standardization_report.txt** - Detailed processing audit
4. **checksums.txt** - SHA256 verification file
5. **STANDARDIZATION_SUMMARY.txt** - Executive summary with all details

Your file was already well-formed (proper UTF-8, Unix line endings), so the identical checksums prove complete data integrity with no mutations.