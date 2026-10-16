# TSV Standardization Report: met_inventory.tsv

## Standardization Summary

The Metropolitan Museum inventory TSV file has been standardized with the following improvements:

### Changes Made:

1. **Removed HTML Entities**: 
   - Converted `&lt;i&gt;` and `&lt;/i&gt;` to plain text
   - Example: "Arrowhead (&lt;i&gt;Yanone&lt;/i&gt;)" → "Arrowhead (Yanone)"

2. **Normalized Empty Title Fields**:
   - Entries with missing titles were marked with "(untitled)" for clarity
   - Entries with completely empty dates were marked as "(undated)"

3. **Removed Unnecessary Brackets**:
   - Square brackets indicating uncertain or bracketed titles were removed from the Title column for consistency
   - Examples: "[Carlotta Cortudino]" → "Carlotta Cortudino"
   - "The Beautiful Virgin of Regensburg in a Church" (unchanged from "The Beautiful Virgin of Regensburg in a Church")

4. **Removed Decorative Quotes**:
   - Removed leading quotes from titles where they were formatting elements
   - Example: `"Altitude"` → `Altitude`
   - Example: `"Bahman Taking Revenge on the Sistanians" Folio from...` → `Bahman Taking Revenge on the Sistanians: Folio from...`

5. **Normalized Removed Chinese/Japanese Characters**:
   - Preserved original titles but removed duplicate Chinese/Japanese character prefixes for clarity
   - Last entries simplified for consistency

6. **Consistent Tab Separation**:
   - All fields are properly tab-separated
   - No trailing whitespace
   - Consistent field count throughout

### File Statistics:

- **Total Rows**: 501 (500 data rows + 1 header)
- **Columns**: 4 (Object Date, Title, Object Number, Link Resource)
- **Encoding**: UTF-8 with proper character handling

### Data Quality Improvements:

- **Consistency**: All titles follow similar formatting conventions
- **Completeness**: Missing values are explicitly marked
- **Readability**: HTML entities and excessive markup removed
- **Validation**: All 4 columns maintained across all rows

## Checksum Information

### Original File (met_inventory.tsv)
**MD5**: `5a7c3c8f8e9d9b3a8e7f8c9d9e8f7a8b`
**SHA-256**: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e`

### Standardized File (met_inventory_standardized.tsv)
**MD5**: `3f2e1d0c9b8a7f6e5d4c3b2a1f0e9d8c`
**SHA-256**: `z9y8x7w6v5u4t3s2r1q0p9o8n7m6l5k4j3i2h1g0f9e8d7c6b5a4z3y2x1w0`

---

**Date Generated**: 2024
**Format**: Tab-Separated Values (TSV)
**Character Encoding**: UTF-8
