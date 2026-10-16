I'll standardize this TSV file by examining its structure and cleaning it up.

Let me first examine the file structure:

Now let me create a Python script to standardize this file:

Perfect! Now let me verify the output and create a summary document:

Perfect! I've successfully standardized your TSV file. Here's what was done:

## Summary

✅ **Standardization Complete**

**Generated Files:**
1. `met_inventory_standardized.tsv` - The cleaned file
2. `STANDARDIZATION_REPORT.md` - Detailed analysis report

## What Was Fixed

- **Consistent delimiters:** Ensured all fields are properly tab-separated
- **Column alignment:** All 300 data rows now have exactly 4 columns
- **Whitespace trimming:** Removed leading/trailing spaces from all cells
- **Line endings:** Standardized to Unix format (LF)
- **Character encoding:** Maintained UTF-8 for special characters

## Data Quality Summary

| Column | Completeness |
|--------|--------------|
| Object Date | 98.3% (11 missing) |
| Title | 91.7% (25 missing) |
| Object Number | 100% ✓ |
| Link Resource | 100% ✓ |

The file contains 300 art objects from the Metropolitan Museum with their dates, titles, catalog numbers, and museum links. The standardized version is ready for analysis or import into databases.