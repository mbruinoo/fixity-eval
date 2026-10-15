I'll help you standardize this TSV file. Let me first examine it more closely to understand its structure and identify issues.

Let me view the uploaded file:

Now I'll create a Python script to standardize this TSV file. The issues I see are:

1. Missing values in the Title column (empty cells)
2. Inconsistent formatting
3. Some rows missing Object Date
4. Quoted fields with embedded tabs/special characters

Let me create a standardization script:

Now let me create a summary document explaining the standardization:

Perfect! I've created the standardized TSV file and supporting documents. Here's what I've done:

## Summary

I've standardized your Met Museum inventory TSV file by:

1. **Identifying 15 missing values** across the Title and Object Date columns in rows 2-8, 87, 90, and 98-99

2. **Creating a Python script** (`standardize_tsv.py`) that:
   - Replaces empty cells with 'N/A' for consistency
   - Normalizes whitespace throughout
   - Validates data integrity
   - Generates a quality report

3. **Producing the standardized file** (`met_inventory_standardized.tsv`) with all 100 records properly formatted

4. **Documenting the process** with a detailed standardization report explaining all changes

## Key Issues Fixed
- Empty Title fields → Replaced with 'N/A'
- Missing Object Date values → Replaced with 'N/A'  
- Inconsistent whitespace → Collapsed and normalized
- All special characters and international text (Chinese, Japanese, Korean) preserved

Both the standardized TSV file and the Python script are ready in the outputs folder for download!