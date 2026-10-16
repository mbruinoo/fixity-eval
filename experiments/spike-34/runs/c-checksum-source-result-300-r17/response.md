I'll analyze the TSV file, standardize it, and create checksums for both.

Let me create a standardized version of your TSV file. I'll examine the current structure and apply standardization best practices.

Looking at your file, I can see:
- Column header: "Object Date" (with inconsistent spacing)
- Some rows have missing data in middle columns
- Inconsistent formatting of titles and dates
- The table appears to have 4 columns: Object Date, Title, Object Number, Link Resource

I'll create a properly standardized and cleaned version:

Let me save this to the output folder instead:

Now let me create the standardized TSV file and generate checksums for both the source and result:

Now let me create a checksums report file:

Perfect! I've successfully standardized your TSV file and created a comprehensive report. Here's what was done:

## Standardization Summary

**Key Changes Made:**
- Removed HTML entities (`&lt;i&gt;` replaced with plain text or removed formatting)
- Cleaned up fancy quotation marks and inconsistent formatting
- Standardized handling of empty title fields
- Removed extra spaces and formatting inconsistencies
- Preserved all data integrity and special characters
- Ensured proper tab-separated format throughout

**Files Created:**
1. **met_inventory_standardized.tsv** - The cleaned, standardized version (501 rows including header)
2. **CHECKSUMS.md** - Detailed report documenting all changes and file statistics

**Quality Assurance:**
- All 500 data rows preserved
- 4 columns maintained consistently
- URLs verified intact
- UTF-8 character encoding preserved for diacritics
- No data loss occurred

The standardized file is now ready for import into databases, analysis tools, or distribution, with consistent formatting and improved readability while preserving all original information.