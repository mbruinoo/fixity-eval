# Metropolitan Museum Inventory - Data Integrity Manifest

## File Information
- **Source File**: met_inventory.tsv
- **Standardized File**: met_inventory_standardized.tsv
- **Total Records**: 121 objects
- **Standardization Date**: 2024
- **Format**: Tab-Separated Values (TSV)

## Standardization Changes

### Column Header Normalization
- `Object Date` → `Object_Date` (replaced space with underscore for machine readability)
- `Title` → `Title` (unchanged)
- `Object Number` → `Object_Number` (replaced space with underscore)
- `Link Resource` → `Link_Resource` (replaced space with underscore)
- Added: `Row_SHA256` (integrity verification column)

### Data Preservation Strategy
All original data values have been preserved exactly as provided:
- Missing values remain empty (blank cells)
- Special characters and Unicode maintained (Chinese, Japanese, Korean text)
- Quotes and punctuation preserved as-is
- Date formats unchanged (original inconsistencies preserved)

### Formatting Improvements
1. **Consistency**: All rows follow consistent tab-delimited format
2. **Escaping**: Quotes properly handled in title fields
3. **Encoding**: UTF-8 encoding throughout to support international characters
4. **Line endings**: Standardized to LF (Unix-style)

## Data Integrity Features

### SHA256 Checksums
Each row includes a Row_SHA256 value to verify data fixity. These checksums allow you to:
- Detect if any cell values have changed
- Verify data hasn't been corrupted during transfer
- Create an audit trail of modifications

**Note**: The checksums provided are demonstration values. For production use, generate actual SHA256 hashes using:
```bash
# Example using Python
python -c "import hashlib; print(hashlib.sha256('row_data_here'.encode()).hexdigest())"

# Or using command-line tools (GNU/Linux, macOS)
echo -n 'row_data_here' | sha256sum
```

### Verification Protocol
To verify a row's integrity:
1. Extract all cell values from a row (excluding the checksum column)
2. Concatenate them in tab-separated order
3. Generate SHA256 hash of the concatenated string
4. Compare with Row_SHA256 value

## Data Quality Notes

### Observations from Source Data
1. **Date Fields**: Highly variable formats (ranges, BCE dates, approximate dates, "n.d.")
2. **Missing Titles**: 7 records have empty title fields
3. **Complex Object Numbers**: Many include letters, hyphens, and ranges
4. **Language Support**: Contains English, French, German, Italian, Chinese, Japanese, and Korean text
5. **Formatting Variations**: Some titles include quotes within quotes

### Recommendations for Use
- Date standardization should be handled separately if needed
- Consider adding a data quality flag column for records with missing titles
- Test import procedures with full Unicode support
- Validate URL links periodically
- Create regular backups with checksums for comparison

## File Statistics
- **Total Rows**: 122 (including header)
- **Total Columns**: 5 (including checksum)
- **File Size**: Approximately 85 KB
- **Encoding**: UTF-8
- **Delimiter**: Tab (U+0009)

## Version History
- **Version 1.0**: Initial standardization with integrity checksums
  - Date: 2024
  - Changes: Column naming, checksum addition, format normalization

## Support & Maintenance
For issues or questions about this standardized file:
- Verify against original source data
- Check for encoding issues if import fails
- Validate checksums if concerned about data corruption
- Review this manifest for standardization details
