I'll analyze the TSV file and standardize it for you.

Now I'll create a standardized version of this file. The issues I see are:

1. Missing titles (many empty cells in the Title column)
2. HTML entities that need to be decoded (`&lt;i&gt;` should be `<i>`)
3. Inconsistent formatting and spacing
4. Some data integrity issues

Let me load the tool first:

Now let me create the standardized file:

Now let me verify the output looks good:

Let me also check a section with titles to confirm the HTML decoding worked:

Perfect! ✓ I've successfully standardized your Met Museum inventory TSV file. Here's what was done:

**Standardization changes:**
- **Whitespace cleanup**: Removed leading/trailing spaces from all fields
- **HTML entity decoding**: Converted `&lt;` to `<` and `&gt;` to `>` (visible in the "Arrowhead" entry which now shows proper italics markup)
- **Consistent formatting**: Ensured proper tab-delimited structure
- **Column preservation**: Maintained all 4 columns (Object Date, Title, Object Number, Link Resource)
- **Data integrity**: Processed 300 records while preserving empty cells where data doesn't exist

The standardized file is ready to download as **met_inventory_standardized.tsv** with consistent formatting and proper HTML entity handling throughout.