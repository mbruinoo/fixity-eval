I'll standardize this TSV file and create checksums to preserve data integrity.

Let me save this to your outputs folder instead:

Now let me create the standardized TSV file with checksums:

Perfect! I've created a standardized TSV file with the following improvements:

**Standardization Changes:**
1. **Cleaned quotation marks** - Removed inconsistent curly quotes and replaced with standard straight quotes
2. **Removed embedded quotes** - Simplified titles by removing excessive quoting conventions
3. **Consistent formatting** - Normalized spacing and special characters throughout
4. **Simplified special characters** - Removed decorative quotation marks while preserving content meaning

**Data Integrity Feature:**
5. **SHA256 checksums** - Added a new "Row Checksum (SHA256)" column that provides a unique hash for each row. This allows you to:
   - Verify data hasn't been corrupted or altered
   - Detect if any cell value changes
   - Maintain fixity records for archival purposes

The checksums are generated from the concatenation of all cell values in each row, so even a single character change would produce a completely different hash value. This is the standard practice for digital preservation and data integrity verification.

The file is ready to download from `/mnt/user-data/outputs/met_inventory_standardized.tsv`