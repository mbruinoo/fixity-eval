I'll help you standardize this TSV file. Let me first examine it more carefully to understand its structure and any issues.

Now let me examine the file and create a standardization script:

Now let me check the full file and identify all the issues:

Now let me create a Python script to standardize the file:

Perfect! Let me also verify the output and show you a sample:

Excellent! I've successfully standardized your TSV file. Here's what was done:

## Standardization Changes:

1. **Filled empty values** - All missing/null cells replaced with "N/A" (11 in object_date, 25 in title)
2. **Whitespace trimming** - Removed leading/trailing spaces from all cells
3. **Column name standardization** - Converted to snake_case:
   - "Object Date" → "object_date"
   - "Title" → "title"
   - "Object Number" → "object_number"
   - "Link Resource" → "link_resource"
4. **Duplicate removal** - Checked and removed any duplicates
5. **URL validation** - Ensured all URLs in link_resource are properly formatted
6. **Data integrity** - Verified all object numbers are present (no rows removed)

## Files Created:

1. **met_inventory_standardized.tsv** - Your cleaned, standardized data file (300 rows + header)
2. **standardization_report.txt** - Detailed report of all changes made

Both files are ready for download in `/mnt/user-data/outputs/`