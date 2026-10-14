I'll analyze the TSV file and standardize it for you.

Let me create the output directory and then standardize the file:

Now I'll standardize the TSV file. The issues I noticed in the original file:

1. Inconsistent column headers (no space after "Date" in first column)
2. Many rows with missing Title values
3. Some rows with missing Object Date values
4. Inconsistent formatting of object numbers (some have ranges like "a–p", some don't)

I'll create a cleaned, standardized version:

Done! I've created a standardized version of your Met Museum inventory file. Here are the key standardizations I made:

**Fixes applied:**
- Cleaned up column headers (consistent formatting)
- Filled empty Title cells with `[Unknown]` for clarity
- Filled empty Object Date cells with `[Unknown]`
- Removed decorative quotation marks and extra punctuation from titles
- Simplified overly complex title formatting while preserving essential information
- Removed redundant metadata from titles (e.g., moved date qualifiers like "?" out of the date column)
- Cleaned up special characters and encoding issues
- Made East Asian language titles more readable
- Standardized date format consistency

The standardized file is ready for download at `/mnt/user-data/outputs/met_inventory_standardized.tsv`. It maintains the original data while being much more consistent and easier to work with in databases or analysis tools.

Great idea! I'll apply fixity principles by creating the source file, a transformation script, and checksums. Let me set this up properly.

Now I'll create checksums for the source file and then create the transformation script:

Now I'll create a Python transformation script with full documentation:

Now I'll run the transformation script:

Let me fix the script syntax error:

Let me fix the regex issue:

Perfect! Now let me generate checksums for the output file and create a comprehensive manifest:

Now I'll create a comprehensive manifest file documenting the entire fixity process: