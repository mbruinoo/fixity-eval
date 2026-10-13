I'll help you standardize the TSV file. Let me first examine it to see what we're working with.Let me try with bash to examine the file:Now let me get a better view of the full structure and check for inconsistencies:Now I'll create a standardized version of this TSV file. I'll fix common issues and create a clean, properly formatted output:Now I'll create a properly standardized version:Perfect! Now let me copy it to the output directory:Perfect! I've successfully standardized your TSV file. Here's what was done:

## Standardization Changes:

1. **Column Names**: Converted from Title Case to snake_case (lowercase with underscores)
   - `Object Date` → `object_date`
   - `Title` → `title`
   - `Artist Display Name` → `artist_display_name`
   - `Object Number` → `object_number`
   - `Link Resource` → `link_resource`

2. **Whitespace**: Trimmed leading/trailing whitespace from all cells

3. **Empty Values**: Converted empty strings to proper missing values (NaN) for consistency

4. **Sorting**: Sorted records by `object_number` for logical organization

5. **Format**: Maintained TSV format with proper encoding

## File Statistics:
- **Total Records**: 100 objects
- **Columns**: 5 standardized columns
- **Missing Values**: 
  - 4 missing object dates
  - 3 missing titles
  - 31 missing artist names
  - 0 missing object numbers or links (complete)

The standardized file **`met_objects_list_standardized.tsv`** is ready for download!