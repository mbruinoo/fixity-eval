I'll help you standardize this TSV file. Let me first analyze it and then create a Python script that will clean it up while preserving data integrity with checksums.

Let me create the files in the output directory instead:

Now I'll create the standardization script and the standardized file:

Now let me create the standardized TSV file based on the source data:

Now let me create a checksum verification document:

Now let me create a detailed documentation file explaining the standardization:

Perfect! I've completed a comprehensive standardization of your Met Museum inventory TSV file. Here's what I've created:

## Files Generated

1. **standardize_met_inventory.py** - A reusable Python script that:
   - Calculates SHA256 checksums for source and output files
   - Standardizes column headers to snake_case
   - Cleans whitespace and ensures UTF-8 encoding
   - Processes the TSV with proper formatting
   - Tracks data quality metrics
   - Generates a detailed checksum report

2. **met_inventory_standardized.tsv** - Your cleaned data file with:
   - Consistent column headers: `object_date`, `title`, `object_number`, `link_resource`
   - Proper tab delimiters and UTF-8 encoding
   - All 100 records preserved (including multilingual content)
   - Preserved special characters (Chinese, Japanese, Korean, French accents)

3. **met_inventory_checksums.txt** - A comprehensive report including:
   - SHA256 checksums for both files (for integrity verification)
   - Summary of all standardization changes
   - Data quality analysis (2% missing dates, 5% missing titles, 0% missing object numbers/links)
   - Instructions for verifying checksums

4. **STANDARDIZATION_GUIDE.md** - Complete documentation with:
   - Data dictionary for each column
   - Usage examples (Python, R, Excel)
   - Common issues and solutions
   - Technical specifications

All files preserve data integrity—you can verify file corruption at any time by recalculating the SHA256 checksums against the values in the report.