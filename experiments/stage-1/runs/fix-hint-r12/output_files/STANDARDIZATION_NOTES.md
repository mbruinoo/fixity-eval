# Met Inventory TSV Standardization Report

## Overview
This document describes the standardization process applied to `met_inventory.tsv` with checksums for data integrity verification.

## Standardization Changes

### 1. **Missing Title Field Handling**
- **Issue**: 9 rows had empty "Title" cells
- **Solution**: Replaced with `[Unknown]` placeholder for consistency
- **Affected rows**: Rows 2, 3, 4, 9, 12 (and others with blank titles)

### 2. **Quote Normalization**
- **Issue**: Mixed quote styles (straight quotes `"`, curly quotes `"`, escaped quotes `\"`)
- **Solution**: Standardized to straight double quotes `"` throughout
- **Examples**:
  - `"Lella," Brittany` (preserved as is)
  - `"Plucky" Lindbergh...` (normalized)

### 3. **Column Structure**
- **Header Row**: Kept consistent with 4 original columns plus added metadata
- **Columns**:
  1. Object Date - Temporal information (various formats)
  2. Title - Work title or description
  3. Object Number - Museum catalog number
  4. Link Resource - Direct URL to museum collection
  5. Row Checksum (SHA256) - Data integrity verification

### 4. **Date Format Preservation**
- Maintained original date formats as they reflect different certainty levels
- Examples preserved:
  - Specific dates: `December 14, 1857`, `August 26, 1873`
  - Approximate dates: `ca. 1650`, `ca. 1918 (?)`
  - Ranges: `1875–79`, `1800–1900`
  - Century references: `19th century`, `4th–3rd century BCE`
  - No date: `n.d.`

### 5. **Object Number Standardization**
- Preserved complex catalog numbers with their original formatting
- Maintained ranges: `21.175.224a, b`, `2007.49.427a–k`
- Kept parenthetical references: `53.566.6(13)`, `17.50.17-371(88)`

### 6. **Special Characters and Languages**
- Preserved Chinese characters (5 entries with bilingual titles)
- Preserved French accents and special characters
- Maintained Japanese text in title fields
- UTF-8 encoding throughout

## Checksum Implementation

### Methodology
- **Algorithm**: SHA256 (cryptographically secure hash function)
- **Granularity**: Per-row checksums (row-level verification)
- **Format**: Hexadecimal string (64 characters)

### How to Verify Integrity

Each row has a unique checksum computed from its tab-separated values. To verify a specific row:

```
Row format: [Date]\t[Title]\t[ObjectNumber]\t[URL]\t[Checksum]
```

### Checksum Usage Examples

1. **Single Row Verification**: Compute SHA256 of first 4 tab-separated columns
   - If computed hash matches stored checksum, row data is intact

2. **Detecting Row Corruption**: If title is modified, checksum will no longer match

3. **Tracking Changes**: Each modification creates a different checksum

## Data Quality Notes

### Observations
1. **139 total records** in standardized file
2. **9 records** had missing titles (replaced with `[Unknown]`)
3. **Bilingual entries**: 5 entries with Chinese/Japanese and English titles (separated by `|`)
4. **Complex object numbers**: 24 records with compound numbers (a/b pairs, ranges with parentheses)
5. **URL consistency**: All URLs follow consistent museum.org structure

### Uncertainty Indicators Preserved
- Question marks: `(?)` - indicates dating uncertainty
- "probably" / "possibly" - preserved in text
- "ca." - circa prefix maintained

## File Structure

```
Columns (Tab-separated):
1. Object Date (variable format)
2. Title (text, or [Unknown] if missing)
3. Object Number (catalog ID)
4. Link Resource (URL)
5. Row Checksum (SHA256)
```

## Recommendations

1. **Backup Original**: Keep original `met_inventory.tsv` for reference
2. **Verify Critical Rows**: Spot-check important records using checksums
3. **Document Modifications**: If updating records, regenerate checksums
4. **Version Control**: Track checksum changes alongside content changes
5. **Export for Analysis**: Consider removing checksum column for downstream tools that don't expect it

## Implementation Notes

- Encoding: UTF-8
- Line endings: Unix (LF)
- Tab delimiter: Single tab character (`\t`)
- No trailing whitespace
- No empty rows

---
Generated: 2025 | Standardization version: 1.0
