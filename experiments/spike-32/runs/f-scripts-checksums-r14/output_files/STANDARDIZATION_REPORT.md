# Met Inventory TSV Standardization Report

## Overview

This report documents the standardization of `met_inventory.tsv`, a tab-separated values file containing metadata from the Metropolitan Museum of Art's collection inventory system.

## Standardization Process

### Files Generated

1. **met_inventory_standardized.tsv** - The standardized data file
2. **standardize_tsv.py** - Python script to replicate the standardization
3. **CHECKSUMS.json** - Metadata and checksum information
4. **STANDARDIZATION_REPORT.md** - This documentation

## Data Structure

### Column Definitions

| Column | Description | Data Type |
|--------|-------------|-----------|
| Object Date | Temporal dating of the artifact | Text (variable format) |
| Title | Name/description of the object | Text (often empty) |
| Object Number | Museum catalog/accession number | Text (variable format) |
| Link Resource | URL to collection entry | URL |

### Statistics

- **Total Records**: 104 rows (excluding header)
- **Total Columns**: 4
- **Encoding**: UTF-8
- **Delimiter**: Tab character (ASCII 0x09)
- **Line Ending**: LF (Unix, ASCII 0x0A)

## Standardization Rules Applied

### 1. Character Encoding
- **Before**: Mixed encoding (likely UTF-8 with potential encoding issues)
- **After**: Pure UTF-8 without BOM
- **Rationale**: UTF-8 is the modern standard for text data; ensures compatibility across systems

### 2. Line Endings
- **Before**: Potentially mixed (CR/LF or LF)
- **After**: LF only (Unix standard)
- **Rationale**: Consistent line endings prevent issues in version control and cross-platform tools

### 3. Delimiter Consistency
- **Before**: Tab characters (may have varied representation)
- **After**: ASCII tab (0x09) consistently applied
- **Rationale**: Ensures proper parsing by TSV processors

### 4. Whitespace Handling
- **Header fields**: Leading/trailing whitespace removed
- **Data fields**: Leading/trailing whitespace removed (preserves internal spacing)
- **Rationale**: Improves data quality and query accuracy

### 5. Quoting Style
- **Method**: QUOTE_MINIMAL (RFC 4180 compliant)
- **Application**: Quotes applied only to fields containing special characters (tabs, newlines, quotes)
- **Rationale**: Minimal quoting improves readability while maintaining parsibility

### 6. Field Consistency
- **Empty fields**: Represented as truly empty (no spaces or special characters)
- **Special characters**: Properly escaped or quoted as needed
- **Ordering**: Column order preserved from original

## Data Characteristics

### Content Analysis

- **Languages**: English, French, Italian, Chinese (Traditional), Japanese, Korean
- **Date formats**: Variable (ranging from specific years to "n.d." for undated items)
- **Object numbers**: Multi-part identifiers with letters, numbers, dots, and dashes
- **URLs**: All resources point to metmuseum.org collection database

### Notable Entries

- **Oldest artifact**: 664–30 B.C. (Apis, Object 04.2.486)
- **Most recent**: 1989 (Koshare/Tewa Ritual Clowns)
- **Multilingual records**: ~30 entries with non-Latin text
- **Missing titles**: ~12 entries have empty Title field

## Fixity and Verification

### Checksum Preservation

Checksums are calculated using SHA-256, a cryptographic hash function that:
- Produces a 256-bit (64-character hexadecimal) hash
- Is virtually impossible to reverse-engineer the original content
- Changes completely if any byte is modified
- Allows verification of file integrity over time

### How to Verify Integrity

1. **Calculate source checksum** (before standardization):
   ```bash
   sha256sum /mnt/user-data/uploads/met_inventory.tsv
   ```

2. **Calculate output checksum** (after standardization):
   ```bash
   sha256sum /mnt/user-data/outputs/met_inventory_standardized.tsv
   ```

3. **Compare with recorded checksums** in CHECKSUMS.json

4. **Verify the script** (optional):
   ```bash
   python3 /mnt/user-data/outputs/standardize_tsv.py
   ```

## ISO 14721 OAIS Compliance

This standardization process follows best practices from ISO 14721 (Reference Model for an Open Archival Information System):

- **Representation Information**: Documented in this report
- **Fixity**: Preserved through SHA-256 checksums
- **Authenticity**: Traceable to source with checksums
- **Format**: Standard TSV (RFC 4180 compliant)

## Recommendations for Use

1. **Data Import**: Most tools will accept this standardized format:
   - Python: `pandas.read_csv(file, sep='\t', encoding='utf-8')`
   - Excel: Open directly or use Data → From Text/CSV
   - SQL: Use LOAD DATA INFILE with tab delimiter

2. **Preservation**: 
   - Store CHECKSUMS.json alongside the data file
   - Periodically verify checksums against saved values
   - Maintain backup copies with original format

3. **Future Updates**:
   - Re-run standardize_tsv.py to maintain consistency
   - Compare new checksums to detect modifications
   - Document any schema changes in CHECKSUMS.json

## Technical Details

### CSV Processing Configuration

```python
delimiter = '\t'          # Tab character
quoting = QUOTE_MINIMAL   # RFC 4180
lineterminator = '\n'     # Unix line ending
encoding = 'utf-8'        # Unicode
escapechar = None         # Standard CSV escaping
```

### File Size Comparison

| Metric | Source | Output | Change |
|--------|--------|--------|--------|
| Size | Original | Standardized | Varies |
| Rows | 104 | 104 | No change |
| Columns | 4 | 4 | No change |

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-10-14 | Initial standardization |

## Questions and Support

For questions about this standardization:
1. Consult the embedded comments in standardize_tsv.py
2. Review RFC 4180 for CSV/TSV standards
3. Check CHECKSUMS.json for metadata

---

*Report generated: 2025-10-14*
*Standardization method: Python 3 with csv module*
