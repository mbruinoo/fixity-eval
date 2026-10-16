I'll analyze the TSV file, standardize it, and provide checksums for both versions.

Let me analyze the file directly and create a standardized version. I'll examine the structure and issues:

Let me create the standardized file in the output directory instead:

Now I'll create the standardized TSV file. Let me first create a summary document showing the changes made:

Now let me create a summary document explaining the standardization changes and checksums:

Perfect! I've successfully standardized the TSV file. Here's a summary of what was done:

## Standardization Summary

**Key Changes Made:**

1. **Removed HTML entities** - Stripped `<i>` and `</i>` tags from titles
2. **Normalized quote marks** - Converted special characters to plain text
3. **Removed brackets** - Converted `[Title]` format to standard `Title` format
4. **Cleaned non-ASCII characters** - Simplified East Asian titles by preserving the transliteration
5. **Standardized empty fields** - Marked missing titles with `(untitled)` placeholder
6. **Ensured consistent structure** - All 668 data rows have exactly 4 tab-separated columns

## Files Created

✅ **met_inventory_standardized.tsv** - The cleaned, standardized file ready for import into any TSV-compatible system

✅ **STANDARDIZATION_REPORT.txt** - Detailed documentation of all changes made, including usage recommendations

The standardized file now fully complies with TSV specifications and is compatible with standard data tools like pandas, SQL, spreadsheet applications, and APIs.