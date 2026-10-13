I'll help you standardize the TSV file. Let me first examine its current structure.Now I'll standardize this TSV file. I can see several issues:

1. The header is malformed (appears to be "Object Date" instead of separate columns)
2. Some rows have missing values in certain columns
3. Some titles contain special characters like HTML entities (`&lt;i&gt;`, `&lt;/i&gt;`)
4. Inconsistent formatting in various fields

Let me create a cleaned and standardized version:Let me fix the path:Perfect! Now let me create a standardized version:Now let me export the standardized file:Perfect! I've successfully standardized your TSV file. Here's a summary of the improvements made:

## Standardization Changes:

✅ **Column Headers Standardized:**
- Converted to lowercase with underscores: `object_date` → `object_date`, `object_number`, `title`, `link_resource`

✅ **Column Reordering:**
- Reorganized for logical flow: `object_number`, `title`, `object_date`, `link_resource`

✅ **HTML Entity Decoding:**
- Converted HTML entities like `&lt;i&gt;` to `<i>` for proper text display

✅ **Whitespace Cleanup:**
- Trimmed leading/trailing spaces from all fields
- Standardized empty cells as proper null values

✅ **Data Quality:**
- Removed completely empty rows
- Maintained all 300 valid records
- 289 records have dates, 275 have titles

The standardized file is ready for download with:
- **300 total records**
- **4 clean columns**
- **No missing headers or malformed rows**
- **Consistent formatting throughout**