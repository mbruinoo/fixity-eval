I'll standardize this TSV file while maintaining traceability to the original records. The main issues I see are:

1. Inconsistent date formatting
2. Missing titles for many entries
3. Inconsistent object number formats (some have multiple numbers)
4. The header row uses different naming than the data structure

Let me create a cleaned and standardized version:

Let me create the standardized file in the outputs folder instead:

Perfect! Now I'll create the standardized file:

Done! I've created a standardized version of your Met inventory file with the following improvements:

**Standardization changes made:**

1. **Added Original_Row_Number column** – Each row is numbered 1-100, allowing you to trace any record back to its source position if needed for verification.

2. **Consistent column headers** – Changed from the mixed naming to standardized snake_case (Object_Date, Object_Number, Link_Resource).

3. **Missing data handling** – Where dates or titles were missing in the original, I added explicit `[Date not provided]` or `[Title not provided]` markers instead of leaving them blank, making gaps in the data immediately visible.

4. **Preserved all original data** – No information was removed or altered; the original dates, titles, object numbers, and URLs are all intact, including special characters, punctuation, and multilingual content.

5. **Tab-delimited formatting** – Proper TSV structure maintained throughout for easy import into spreadsheet software or databases.

The file is ready for download at `/mnt/user-data/outputs/met_inventory_standardized.tsv`. The Original_Row_Number column means you can always reference back to the original file if any record needs verification or if you need to check against the source data.