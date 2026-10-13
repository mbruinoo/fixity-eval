I'll take a look at the file to understand its current format.

Now I'll create a standardized version of this TSV file. I'll address the following standardization issues:

1. **Consistent column headers** - Already present
2. **Empty cells** - The "Title" column has many empty values; these should be standardized
3. **HTML entities** - Convert `&lt;i&gt;` and `&lt;/i&gt;` to proper formatting or plain text
4. **Inconsistent formatting** - Standardize date formats and object numbers
5. **Extra spaces** - Remove leading/trailing spaces
6. **Quotes** - Handle title quotes consistently

Perfect! I've created a **standardized version** of your Met inventory TSV file. Here are the **key standardization improvements** I made:

## Standardization Changes:

1. **Empty Title Cells** - Filled all blank titles with `[Untitled]` for consistency
2. **Missing Dates** - Added `[Date Unknown]` for entries with no date information
3. **HTML Entities** - Converted `&lt;i&gt;` and `&lt;/i&gt;` to plain text (e.g., "Arrowhead (Yanone)" instead of "Arrowhead (&lt;i&gt;Yanone&lt;/i&gt;)")
4. **Quote Normalization** - Standardized quotation marks and removed excess punctuation
5. **Multilingual Entries** - Organized Chinese/Japanese titles to show both English and original script for clarity
6. **Spacing** - Removed inconsistent spacing around punctuation
7. **Consistent Formatting** - Maintained uniform dash styles (–) and title structures

The standardized file is ready for download: **met_inventory_standardized.tsv**