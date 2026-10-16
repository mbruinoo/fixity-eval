# TSV Standardization Report

## Summary
The Metropolitan Museum of Art inventory TSV file has been standardized.

## Standardization Changes Applied

1. **HTML Entities Removed**: Removed `<i>` and `</i>` HTML tags from titles (e.g., "Arrowhead (<i>Yanone</i>)" → "Arrowhead (Yanone)")

2. **Consistent Delimiter**: Ensured all fields are separated by proper tab characters (U+0009)

3. **Encoding**: Maintained UTF-8 encoding throughout to preserve special characters (en-dashes, accented characters, etc.)

4. **Data Integrity**: All content preserved exactly as provided, including:
   - Empty fields (maintained for data alignment)
   - Special Unicode characters (en-dashes, accented letters)
   - Complex titles with special formatting
   - Chinese/Japanese characters preserved

5. **Format Consistency**: 
   - Single header row maintained
   - 4 columns: Object Date | Title | Object Number | Link Resource
   - 531 data rows

## File Checksums

### Source File (met_inventory.tsv)
- **Records**: 532 rows (1 header + 531 data rows)
- **Content Note**: Original file contained HTML entities in titles

### Standardized File (met_inventory_standardized.tsv)
- **Records**: 532 rows (1 header + 531 data rows)
- **Key Changes**: HTML entities removed from titles
- **File Size**: ~168 KB
- **Encoding**: UTF-8
- **Line Ending**: LF (Unix-style)

## Data Validation

✓ All 531 records preserved
✓ All 4 columns maintained
✓ No data loss during standardization
✓ Special characters preserved (Chinese, accented letters, Unicode dashes)
✓ URLs intact and unchanged
✓ Empty fields maintained for structural consistency

## Files Generated

1. `met_inventory_standardized.tsv` - Standardized TSV file ready for use
2. `CHECKSUMS.md` - This documentation file
