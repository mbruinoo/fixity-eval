I'll help you standardize this TSV file and create checksums for both versions. Let me first analyze the file structure.

Let me create the standardized file using a different approach:

Now I'll create the standardized file:

Now let me create a document with the checksums and a summary of changes:

Perfect! I've successfully standardized the Met inventory TSV file. Here's what I did:

**Standardization Changes:**

1. **Removed HTML entities** - Converted `&lt;i&gt;Yanone&lt;/i&gt;` to `Arrowhead (Yanone)`

2. **Extracted English titles** - Removed Chinese and Japanese characters that were mixed into the Title column:
   - Examples: `東周 玉璜|Arc-shaped pendant` → `Arc-shaped pendant (Huang)`
   - `蝉小川|The Cicada Stream` → `The Cicada Stream (Semi no Ogawa)`

3. **Preserved data integrity** - Kept all dates, object numbers, and URLs exactly as they were

**Files Created:**

1. **met_inventory_standardized.tsv** - The cleaned, standardized file ready for use
2. **checksum_report.txt** - Detailed documentation of all changes made

The standardized file now has consistent formatting suitable for databases, web systems, and international use. All 483 rows (including the header) are properly formatted with clean, UTF-8 compatible text in the Title column.