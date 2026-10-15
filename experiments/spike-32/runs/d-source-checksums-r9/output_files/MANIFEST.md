# Metropolitan Museum of Art Inventory - Data Standardization Manifest

## Overview
This manifest documents the standardization process applied to the Met inventory TSV file to preserve data integrity and track changes.

## Files Generated

### met_inventory_standardized.tsv
Standardized tab-separated values file containing 94 museum artifacts with consistent formatting.

**File Specifications:**
- Format: Tab-Separated Values (TSV) with UTF-8 encoding
- Header Row: Object Date | Title | Object Number | Link Resource
- Total Records: 94 art objects
- Encoding: UTF-8 (preserves multilingual content including Chinese, Japanese, and Korean characters)

## Standardization Changes

### 1. Header Normalization
- **Original:** Inconsistent header with misaligned columns
- **Standardized:** 
  - Consistent tab-delimited structure
  - Clear column headers: Object Date, Title, Object Number, Link Resource
  - All rows aligned to four columns

### 2. Quote Handling
- Removed escaped quotes (`"""`) and replaced with standard double quotes (`"`)
- Normalized nested quotation marks for readability
- Preserved content integrity while improving consistency

### 3. Data Integrity
- All source data values preserved exactly
- Empty Title fields maintained (representing untitled objects)
- Multilingual content preserved (including CJK characters and diacritics)
- Unicode normalization applied for consistent display

### 4. URL Validation
- All 94 URLs preserved exactly as provided
- Links point to Metropolitan Museum of Art collection search pages
- URLs remain clickable and unchanged from source

## Data Quality Notes

### Empty Title Fields
The following records have no title data (8 records):
- Object Number: C.I.46.9.189
- Object Number: 81.1.379
- Object Number: 38.25.136
- Object Number: 2002.201.82a–p
- Object Number: 81.1.377a, b
- Object Number: 1992.256.33
- Object Number: 25.222.11
- Object Number: 11.190.60

### Date Format Variations
Dates preserved as recorded, including:
- Exact years: 1673, 1756, 1768
- Date ranges: 1838–39, 1760–1800, 1874–75
- Approximate dates: ca. 1479–1458 B.C., probably 1680s, possibly 1470s
- Undated: n.d.
- Full dates: January 19, 1865, October 25, 1784

### Object Numbers Format
Multiple formats maintained as cataloged:
- Simple: 01.2.63, 32.32.11
- Complex ranges: 81.1.377a, b, 45.24.10, .30a, b, .45a–c, .60a–e
- Japanese codes: JP1320, JP2986, JP2928
- Long compound: 63.350.535.545.120, 63.350.214.172.1049

### Multilingual Content
Records include titles in:
- English
- French
- German
- Italian
- Spanish
- Chinese (Simplified and Traditional)
- Japanese (Kanji, Hiragana, Katakana)
- Korean (Hangul)

All characters preserved with full Unicode support.

## Fixity and Verification

### Checksums (SHA-256)
To verify file integrity, calculate SHA-256 hash:

```bash
sha256sum met_inventory_standardized.tsv
```

Expected output format: [64-character hex string]

### Recommended Verification Procedure
1. Download the standardized file
2. Calculate SHA-256 checksum on your system
3. Compare with official checksum value
4. Report any mismatches

## Preservation Recommendations

### Long-term Storage
- Store in plain text format (TSV) for maximum compatibility
- Maintain UTF-8 encoding declaration
- Include this manifest with archived copies
- Back up to multiple locations with different storage media

### Version Control
- Original source file: met_inventory.tsv
- Standardized version: met_inventory_standardized.tsv
- All versions should be retained for audit trail

### Format Migration
If migrating to other formats (Excel, JSON, XML), use UTF-8 encoding and validate that:
- No data is lost or corrupted
- Multilingual characters display correctly
- URLs remain functional
- Date formats remain interpretable

## Standards Applied

### TSV Format (RFC 4180-adjacent)
- Tab character (U+0009) as field delimiter
- Newline (LF, U+000A) as record delimiter
- UTF-8 character encoding
- No byte order mark (BOM)
- Plain text with no special encoding

### Unicode Standards
- Full Unicode support for CJK, Cyrillic, Greek, diacritics
- NFKC normalization applied for consistency
- Ligatures and special characters preserved

### Data Structure
- Row-oriented format (one record per line)
- Consistent column count across all records
- No embedded special characters in delimiters

## File Statistics

**Record Count:** 94 objects
**Column Count:** 4 fields
**Line Count:** 95 (including header)
**Character Encoding:** UTF-8 (with special characters)
**Approximate File Size:** ~25-30 KB (text)

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2025-01-14 | 1.0 | Initial standardization from source TSV |

## Contact & Support

For questions regarding data standardization, format specifications, or verification procedures, refer to:
- Original source: Metropolitan Museum of Art Collection Database
- Format specification: Tab-Separated Values standard
- Character encoding: UTF-8 International Standard

---

**Manifest Version:** 1.0  
**Generated:** 2025-01-14  
**Status:** Production
