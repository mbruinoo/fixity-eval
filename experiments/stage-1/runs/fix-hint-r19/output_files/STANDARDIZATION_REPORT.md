# Met Museum Inventory TSV Standardization Report

## Overview
This report documents the standardization and fixity verification of the Met Museum inventory TSV file using cryptographic checksums for data integrity preservation.

## Files Generated

### 1. **met_inventory_standardized.tsv**
- Complete standardized dataset with row-level checksums
- 100 records processed
- All checksums calculated using SHA-256 algorithm

### 2. **standardize_met_inventory.py**
- Python script for reproducible standardization
- Implements checksum calculation and verification
- Can be run independently for validation

### 3. **met_inventory_manifest.json** (to be generated)
- Complete metadata manifest with field mappings
- Records checksum mappings for all 100 rows
- Documents standardization rules applied

### 4. **met_inventory_checksums.tsv** (to be generated)
- Row-level checksums in tabular format
- Enables efficient spot-checking of data integrity
- Format: row_number | object_number | source_checksum | std_checksum

## Standardization Rules Applied

### Field Name Standardization
| Original Name | Standardized Name |
|---------------|------------------|
| Object Date | date |
| Title | title |
| Object Number | object_number |
| Link Resource | url |

### Data Normalization
1. **Whitespace Trimming**: All leading/trailing whitespace removed from field values
2. **Empty Value Handling**: Blank fields consistently represented as empty strings
3. **Field Ordering**: Consistent column order across all records
4. **Character Encoding**: UTF-8 encoding maintained throughout
5. **Quoting**: Minimal quoting applied (only when necessary for TSV compatibility)

### Metadata Additions
- **row_number**: Sequential identifier (1-100) for tracking
- **source_checksum**: SHA-256 hash of original row data (tab-separated)
- **std_checksum**: SHA-256 hash of standardized row data (tab-separated)

## Checksum Methodology

### Calculation Process
For each row:
1. **Source Checksum**: 
   ```
   SHA-256(Object Date \t Title \t Object Number \t Link Resource)
   ```
   Captures original data exactly as provided

2. **Standardized Checksum**:
   ```
   SHA-256(date \t title \t object_number \t url)
   ```
   Captures standardized data after normalization

### Fixity Preservation
- Checksums enable detection of any data corruption
- Source checksums allow verification against original file
- Standardized checksums verify transformation integrity
- Both checksums recorded for complete audit trail

## Data Quality Observations

### Missing Values
- **Title field**: 9 records have no title
- **Date field**: 3 records lack dating information
- These are preserved as-is in standardization (empty strings)

### Date Format Variations
- Precise dates: "1896", "1921"
- Date ranges: "1875–79", "20th–mid 20th century"
- Approximate dates: "ca. 1650", "probably 1878"
- Uncertain dates: "ca. 1918 (?)", "(1625)"
- Eras: "4th–3rd century BCE", "5th century BCE"

### Object Number Patterns
- Simple format: "91.1.396"
- Compound format: "21.175.224a, b" (with suffixes)
- Multi-part: "2007.49.427a–k"
- Alternative systems: "Burdick 223, N346.4"
- Unicode support required: "JP1328"

### URL Structure
All URLs follow consistent pattern:
```
http://www.metmuseum.org/art/collection/search/{ID}
```
Where {ID} is a numeric identifier independent of object_number

## Verification Instructions

### Quick Verification
Run the Python script to validate data integrity:
```bash
python3 standardize_met_inventory.py
```

### Manual Spot-Check
1. Pick a row from the standardized file
2. Look up corresponding row in met_inventory_checksums.tsv
3. Recalculate expected checksum using same data
4. Compare against recorded checksum

### Example Verification (Row 1)
```
Original: "19th century\t\t91.1.396\thttp://www.metmuseum.org/art/collection/search/51219"
Expected source_checksum: [calculated SHA-256]

Standardized: "19th century\t\t91.1.396\thttp://www.metmuseum.org/art/collection/search/51219"
Expected std_checksum: [calculated SHA-256]
```

## Statistics

| Metric | Value |
|--------|-------|
| Total Records | 100 |
| Records with Title | 91 |
| Records with Date | 97 |
| Records with Object Number | 100 |
| Records with URL | 100 |
| Checksum Algorithm | SHA-256 |
| Total Checksums | 200 (100 source + 100 std) |

## Data Integrity Chain

```
Original TSV File
        ↓
    [Record n]
        ↓
    Calculate source_checksum SHA-256(original data)
        ↓
    Apply standardization rules
        ↓
    Calculate std_checksum SHA-256(standardized data)
        ↓
    Store both checksums with record
        ↓
    Standardized TSV + Checksums
```

This chain ensures:
- **Traceability**: Every record can be traced to source
- **Integrity**: Any modification detected via checksum mismatch
- **Auditability**: Complete record of transformation applied
- **Recoverability**: Original checksums preserved for comparison

## Recommendations for Use

### For Archive/Preservation
1. Store standardized TSV alongside manifest and checksums
2. Periodically verify checksums to detect data drift
3. Keep Python script for reproducible verification
4. Document any schema changes in future versions

### For Data Analysis
- Use standardized field names for consistency
- Filter records with empty dates/titles as needed
- Reference object_number as primary key (all 100 have values)
- URLs are stable identifiers for record lookup

### For Data Exchange
- Export standardized TSV for interoperability
- Include manifest.json for recipients to understand schema
- Provide checksums for recipients to verify integrity
- Document all deviations from original for transparency

## Technical Notes

### UTF-8 Encoding
File contains characters requiring UTF-8:
- En-dashes in date ranges: "–"
- Chinese characters in titles: "東周", "冨嶽三十六景"
- French accented characters: "Côte", "Héribert"
- Special Unicode: "蛺", "琺瑯"

### TSV Format Specifics
- Tab (U+0009) used as field delimiter
- No quoting mechanism for escaped tabs (tabs don't appear in data)
- Newline (U+000A) as record delimiter
- Empty fields represented as consecutive tabs

### Checksum Considerations
- SHA-256 provides 256-bit (32-byte) hash output
- Hexadecimal representation: 64 characters per checksum
- Collision probability negligible for this dataset size
- Format: lowercase hexadecimal (consistent with common tools)

## Version Information

| Component | Version |
|-----------|---------|
| Python Script | 1.0 |
| Standardization Format | 1.0 |
| Report Date | 2025-01-19 |
| Checksum Algorithm | SHA-256 |

---

**Document Purpose**: Comprehensive documentation of data standardization and integrity verification for Met Museum inventory records.

**For Questions**: Reference the standardize_met_inventory.py script for implementation details and the embedded comments for code-level documentation.
