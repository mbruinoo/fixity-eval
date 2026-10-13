I'll examine the TSV file first to understand its current format.

Now I'll create a standardized version of this TSV file. I'll standardize it by:

1. Ensuring proper tab-delimited formatting
2. Removing HTML entities (like `&lt;i&gt;` → `<i>`)
3. Handling consistent quote usage
4. Ensuring all rows have all columns
5. Cleaning up inconsistent spacing

Perfect! I've created a standardized version of your TSV file. Here's what I standardized:

## Key Improvements Made:

1. **Removed HTML entities** - Converted `&lt;i&gt;` to regular text for italics notation
2. **Consistent quote handling** - Removed inconsistent quotation marks around titles (keeping them as plain text or in square brackets where they were)
3. **Proper tab delimiters** - Ensured true tab separation between columns
4. **Handled empty cells** - Maintained the structure for rows with missing data in the Title column
5. **Cleaned up bracketed text** - Standardized formatting of bracketed titles
6. **Removed unnecessary quotes** - Simplified titles that were unnecessarily quoted

The standardized file maintains all 4 columns:
- **Object Date** - Date information
- **Title** - Object/artwork title
- **Object Number** - Museum catalog number
- **Link Resource** - URL to the collection

The file is ready for use and download at `/mnt/user-data/outputs/met_inventory_standardized.tsv`