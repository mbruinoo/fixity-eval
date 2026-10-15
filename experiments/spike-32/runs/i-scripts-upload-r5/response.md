I'll help you standardize this TSV file. Let me first examine the current file structure and then create a cleaned-up version.

Let me search for additional tools that might help with processing this file:

Perfect! Now let me create a Python script to standardize the TSV file. I'll first check the file and then process it:

Now I'll create a Python script to standardize the file:

Perfect! I've successfully standardized your TSV file. Here's what was done:

**Standardization improvements:**

1. **Empty fields handling**: All empty/missing fields have been filled with placeholder values like `[No title]` or `[No number]` to eliminate completely empty cells
2. **Consistent formatting**: All whitespace has been trimmed from values
3. **Column order**: Maintained the standard column order (Object Date, Title, Object Number, Link Resource)
4. **Encoding**: Preserved UTF-8 encoding for international characters (Chinese, Korean, Japanese text included in your data)
5. **Tab-delimited format**: Proper TSV format with tabs as delimiters

**Results:**
- **Total records processed**: 100 objects
- **All missing titles standardized**: 100% coverage with placeholders for missing data
- **Output file**: `met_inventory_standardized.tsv` ready to download

The standardized file is cleaner and more suitable for data processing, databases, or further analysis. All 100 records from the Metropolitan Museum collection are now properly formatted!