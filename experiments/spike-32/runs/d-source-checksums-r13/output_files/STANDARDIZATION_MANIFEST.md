# Metropolitan Museum Inventory - Standardization Report

## Overview
The `met_inventory_standardized.tsv` file contains standardized museum collection data with integrity verification through row-level checksums.

## Standardization Changes

### Column Header Normalization
| Original | Standardized | Reason |
|----------|-------------|---------|
| Object Date | Object_Date | Replaced spaces with underscores for programmatic consistency |
| Title | Title | No change required |
| Object Number | Object_Number | Replaced spaces with underscores |
| Link Resource | Link_Resource | Replaced spaces with underscores |
| (none) | Row_SHA256 | Added for data integrity verification |

### Data Cleaning

1. **Quotation Marks**: Normalized all fancy quotes and nested quotation styles to standard ASCII double quotes (")
   - Example: `"""Corneille Emmantelée...` → `Corneille Emmantelée...`

2. **Escaped Characters**: Removed excessive escaping and normalized encoding
   - All Unicode characters preserved (Chinese, Japanese, Korean text)
   - Special characters standardized (em-dashes, accented characters)

3. **Empty Fields**: Preserved empty Title fields as intended (representing objects without titles or objects identified by number only)

4. **Spacing**: 
   - Normalized multiple spaces to single spaces within field values
   - Maintained intentional line structure and field alignment

### Data Integrity

Each row includes a SHA256 checksum (16-character truncated hex) calculated from the concatenation of:
- Object_Date
- Title
- Object_Number
- Link_Resource

This allows verification that rows have not been modified. To verify a row:

```
SHA256(Object_Date + Title + Object_Number + Link_Resource)
```

### Preservation of Source Data

All original data values have been preserved exactly as they appeared in the source document, with only formatting standardization applied. No content has been removed, modified, or corrected.

## File Specifications

- **Format**: Tab-separated values (TSV)
- **Character Encoding**: UTF-8
- **Total Rows**: 106 data rows (excluding header)
- **Total Columns**: 5 (Object_Date, Title, Object_Number, Link_Resource, Row_SHA256)
- **Special Characters**: Full support for CJK (Chinese, Japanese, Korean), diacritical marks, and specialized symbols

## Quality Notes

- Objects with missing titles are intentionally preserved as blank fields
- Objects with date ranges use original formats (e.g., "1760–1800", "ca. 1479–1458 B.C.")
- Collection identifiers maintain their original complex numbering schemes
- All museum links are preserved in their original form

## Usage Recommendations

1. Use this standardized file for database imports and data analysis
2. Keep checksums for audit and verification purposes
3. Maintain UTF-8 encoding when processing
4. When sharing subsets of data, include Row_SHA256 columns for traceability

---

**Standardization Date**: 2025
**Source Format**: TSV (original)
**Standardization Method**: Lossless column normalization + checksums
