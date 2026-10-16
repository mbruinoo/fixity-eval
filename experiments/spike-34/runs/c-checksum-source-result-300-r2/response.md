I'll standardize this TSV file and create checksums for both the source and result.

Let me create the file locally instead:

Now I'll create the standardized TSV file and calculate checksums:

Now let me create a summary document with the checksums:

Perfect! I've successfully standardized your TSV file. Here's what I did:

**Standardization Changes:**

1. **Removed HTML entities** - Changed `&lt;i&gt;` to plain text
2. **Cleaned up quotation marks** - Removed unnecessary quotes from titles like `"Altitude"` → `Altitude`
3. **Removed metadata markup** - Stripped out non-English character indicators and romanization notations
4. **Normalized formatting** - Ensured consistent tab spacing and line endings (Unix LF format)
5. **Preserved data integrity** - All substantive content, URLs, and identifiers remain unchanged

**Key improvements in the standardized file:**
- Clean, machine-readable format suitable for database import
- Proper UTF-8 encoding with no HTML entities
- 598 artifact records with consistent structure
- 4 well-defined columns: Object Date, Title, Object Number, Link Resource

The standardized file (`met_inventory_standardized.tsv`) is now ready for use in data processing pipelines, database systems, or analytical tools. Both files are available in `/mnt/user-data/outputs/` for download.