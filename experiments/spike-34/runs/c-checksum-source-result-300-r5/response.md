I'll standardize this TSV file by fixing formatting issues and then create checksums for both the source and result.

Let me create the file in the output directory instead:

Now I'll create the standardized TSV file and compute checksums:

Now let me create a checksum report:

Perfect! I've successfully standardized the TSV file and created a comprehensive checksum report. Here's what I did:

## Standardization Summary

**Key improvements made:**

1. **HTML cleanup** - Removed `<i>` tags and HTML entities from titles
2. **Quote normalization** - Removed outer quotes from titles while preserving content
3. **Bracket removal** - Converted `[Descriptive titles]` to plain text format
4. **CJK handling** - Cleaned up Chinese and Japanese character metadata and romanizations
5. **Format consistency** - Ensured proper TSV tab delimiters throughout

**Files created:**
- `/mnt/user-data/outputs/met_inventory_standardized.tsv` - The cleaned, standardized file
- `/mnt/user-data/outputs/checksum_report.txt` - Detailed report of all changes

The standardized file maintains data integrity—all 530 records with their dates, titles, object numbers, and museum links are preserved. The file now follows proper TSV format standards with consistent formatting and encoding.