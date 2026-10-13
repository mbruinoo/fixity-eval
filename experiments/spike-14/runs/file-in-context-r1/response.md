I'll analyze this TSV file and standardize it for you.

Now I can see the issues. The main standardization problems are:

1. **Missing Title values** - Many rows have empty titles
2. **HTML encoding** - `&lt;i&gt;` should be `<i>` 
3. **Inconsistent spacing** - Some titles have extra spaces
4. **Missing Object Date values** - Several rows have empty dates

Let me create a standardized version:

Now let me create a standardized version with the following improvements:

1. Decode HTML entities (`&lt;` → `<`, `&gt;` → `>`)
2. Clean up extra whitespace
3. Keep all columns consistent
4. Maintain data integrity

Perfect! Let me verify the output looks correct:

Excellent! Let me verify one more section to ensure the HTML entities were properly decoded:

Perfect! ✅ **Your TSV file has been standardized!**

## Summary of Changes:

1. **✓ Decoded HTML entities** - `&lt;i&gt;` → `<i>`, `&lt;/i&gt;` → `</i>`
2. **✓ Normalized whitespace** - Removed extra spaces while preserving single spaces between words
3. **✓ Maintained data integrity** - All 301 lines preserved, no data loss
4. **✓ Consistent formatting** - Tab-separated values properly aligned

The standardized file is ready for download: **`met_inventory_standardized.tsv`**

The file now has consistent formatting and proper character encoding, making it suitable for data analysis, imports to databases, or other processing workflows.

I'll create a comprehensive data standardization package with procedural script, checksums, and all files for archival.

Now I'll create the transformation script:

Now let's run the script:

I need to copy the input file first:

Perfect! Now let's view the log file and verify the output:

Excellent! Now let's create a comprehensive README and manifest file:

Now let's create a detailed manifest file:

Perfect! Now let's update the checksums file with all files and create a final verification:

Excellent! Now let's verify everything works and create a final summary document: