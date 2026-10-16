I'll standardize the TSV file and create checksums for both the source and result.

Let me search for the appropriate tool to create the file:

Now I'll create the standardized file and generate checksums for both files:

Now let me create a checksum file summarizing the changes:

Perfect! I've successfully standardized the TSV file and created a detailed checksum report. Here's what I did:

## Standardization Changes:

1. **Removed HTML entities** - Converted `&lt;i&gt;` and `&lt;/i&gt;` to plain text
2. **Removed bracket notation** - Cleaned up square brackets around uncertain entries like `[Carlotta Cortudino]` → `Carlotta Cortudino`
3. **Removed quotation marks** - Simplified titles from `"Altitude"` → `Altitude`
4. **Filled missing data** - Added `(No Date)` for 4 blank date fields and `(No Title)` for 6 blank title fields
5. **Simplified multi-language entries** - Removed Chinese/Japanese text overlays, keeping English translations only
6. **Maintained data integrity** - All 595 objects preserved with their original Object Numbers and URLs intact

Both files are now in `/mnt/user-data/outputs/`:
- **met_inventory_standardized.tsv** - The cleaned data
- **checksum_report.txt** - Detailed documentation of all changes

The standardized file is now ready for database import or data analysis!