# Met Inventory TSV Standardization Report

## Executive Summary

The Metropolitan Museum's inventory TSV file has been successfully standardized with complete fixity verification through SHA-256 checksums. The file was already well-formed, requiring minimal whitespace normalization.

## Files Generated

1. **met_inventory_standardized.tsv** - The standardized data file
2. **met_inventory_checksums.json** - Complete checksum documentation with row-level granularity
3. **standardize_and_verify.py** - Reproducible Python script for verification
4. **STANDARDIZATION_REPORT.md** - This document

## Data Statistics

| Metric | Value |
|--------|-------|
| Total Rows | 101 |
| Total Columns | 4 |
| Column Headers | Object Date, Title, Object Number, Link Resource |
| Character Encoding | UTF-8 |
| Line Terminator | LF (Unix/Linux) |
| Delimiter | TAB |

## Standardization Process

### Transformations Applied

- **Whitespace Normalization**: Stripped trailing whitespace from each cell
- **Encoding Verification**: Confirmed UTF-8 encoding throughout
- **Line Endings**: Standardized to LF (Unix-style, `\n`)
- **Delimiter Consistency**: Verified consistent tab delimiters
- **Quote Handling**: Applied CSV QUOTE_MINIMAL standard (quotes only when necessary)

### Data Integrity Findings

- **File-Level Hash (Source)**:  
  `a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf`

- **File-Level Hash (Standardized)**:  
  `a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf`

**Result**: File-level hashes are identical, indicating the source file was already properly formatted with minimal trailing whitespace.

## Row-Level Checksums

### Header Row (Row 1)
- **Content**: Object Date | Title | Object Number | Link Resource
- **SHA-256**: `77d96f670aab6ef9e37444a63dfb77d475119da9ad763ab158b75a4dcde721a1`
- **Status**: Unchanged (header already properly formatted)

### Sample Rows - Verification

#### Row 2 (First Data Row)
- **Source Content**: `19th century		91.1.396	http://www.metmuseum.org/art/collection/search/51219`
- **Source SHA-256**: `4d16543673187a57eb557f56daf4709f71ec690c0d773febcfcd34e1688ce6ce`
- **Standardized SHA-256**: `4d16543673187a57eb557f56daf4709f71ec690c0d773febcfcd34e1688ce6ce`
- **Status**: Unchanged

#### Row 101 (Last Data Row)
- **Content**: `ca. late 1150s	金 傳楊邦基 聘金圖 巻|A Diplomatic Mission to the Jin	1982.1.1	http://www.metmuseum.org/art/collection/search/39959`
- **SHA-256**: `269623ce6718a7471b303b61676cd0ebde0515fa0b613a92997ddc0e4b37b1d4`
- **Status**: Unchanged

### All 101 Row Checksums

Complete row-level checksums for all 101 rows are available in `met_inventory_checksums.json`. This enables verification of:
- Individual row integrity
- Detection of any modifications to specific rows
- Granular traceability of data provenance

## Data Quality Observations

### Consistent Data Structure
- All 101 rows maintain the 4-column structure
- Headers properly labeled and distinct from data

### Content Characteristics
- **Object Dates**: Range from ancient (4th-3rd century BCE, ca. 2030–1640 B.C.) to modern (1960s)
- **Titles**: Diverse artwork, photographs, and museum collection items
- **Object Numbers**: Mix of numerical IDs and complex reference codes (e.g., `2007.49.427a–k`)
- **Links**: All URLs properly formed and consistent with museum database format

### International Content
- Chinese language titles with bilingual descriptions (Chinese | English)
- Japanese titles with transliterations
- French titles and descriptions
- Proper Unicode support for special characters

### Data Quality Issues Found
- **None**: The TSV is well-formed with minimal whitespace inconsistencies

## Fixity Verification Instructions

### How to Verify File Integrity

1. **Verify File-Level Integrity**:
   ```bash
   sha256sum met_inventory_standardized.tsv
   # Compare to: a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf
   ```

2. **Verify Specific Row** (e.g., Row 2):
   ```bash
   # Extract row 2, calculate its hash
   sed -n '2p' met_inventory_standardized.tsv | sha256sum
   # Compare to Row 2 hash in met_inventory_checksums.json
   ```

3. **Full Reproducibility**:
   ```bash
   python3 standardize_and_verify.py
   # Regenerate all checksums and compare with previous output
   ```

## Timestamp

- **Standardization Date/Time**: 2026-10-19T03:56:01.092351 UTC
- **Algorithm**: SHA-256
- **Encoding**: UTF-8

## Recommendations

1. **Archive Both Files**: Keep the original source and standardized versions for compliance records
2. **Preserve Checksums**: Store `met_inventory_checksums.json` with version control history
3. **Regular Verification**: Use provided checksums to verify file integrity during migration or storage operations
4. **Reproduction**: The standardization script can be re-run at any time to verify consistency

## Conclusion

The Met inventory data demonstrates excellent data hygiene. The standardization process confirmed that the source file adheres to proper TSV formatting standards. The comprehensive row-level checksum documentation enables granular integrity verification and supports robust digital preservation practices.

All files are ready for archival, migration, or further processing with complete provenance documentation.
