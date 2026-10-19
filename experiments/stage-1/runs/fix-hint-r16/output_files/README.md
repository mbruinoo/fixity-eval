# Metropolitan Museum Inventory TSV Standardization & Fixity Package

## Package Contents

This package contains a complete standardization of the Metropolitan Museum collection inventory data with comprehensive checksums for long-term data integrity verification.

### Data Files
- **met_inventory_standardized.tsv** - The standardized TSV file (100 rows of data + header)
- **met_inventory_checksums.json** - Complete checksums for both source and standardized files

### Scripts
- **standardize_met_inventory.py** - Python script to standardize the TSV and generate checksums
- **verify_met_inventory.py** - Python script to verify file integrity against checksums
- **met_inventory_verification_report.json** - Latest verification results

### Documentation
- **README.md** - This file
- **STANDARDIZATION_DOCUMENTATION.md** - Detailed documentation of standardization methodology
- **FIXITY_VERIFICATION_GUIDE.md** - Guide to understanding and using checksums for long-term preservation

## Quick Summary

| Aspect | Details |
|--------|---------|
| **Original File** | 101 lines (1 header + 100 data rows) |
| **Standardized File** | 101 lines (1 header + 100 data rows) |
| **Format** | Tab-separated values (TSV) |
| **Encoding** | UTF-8 without BOM |
| **File Hash (SHA256)** | a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf |
| **Row Count** | 100 object records |
| **Columns** | 4 (Object Date, Title, Object Number, Link Resource) |
| **Standardization Status** | ✓ Complete & Verified |

## What Was Standardized

### Formatting Improvements
1. **Consistent Delimiters** - Ensured all field separators are tabs
2. **Whitespace Normalization** - Removed leading/trailing whitespace from cells
3. **Empty Cell Handling** - Standardized representation of empty cells
4. **Encoding Validation** - Verified UTF-8 encoding throughout
5. **Line Endings** - Standardized to LF (Unix style)
6. **Header Standardization** - Applied consistent, descriptive column names

### Data Preservation
- **No content modification** - All original data values preserved exactly
- **Multilingual support** - All international characters and scripts preserved
- **Special characters** - Diacritics, punctuation, and symbols maintained
- **Structure preserved** - Column order and data organization unchanged

## Getting Started

### Verify the Standardized File

**Option 1: Quick command-line verification**
```bash
sha256sum met_inventory_standardized.tsv
# Should output: a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf
```

**Option 2: Automated verification script**
```bash
python3 verify_met_inventory.py
```

Expected output:
```
✓ File integrity verified (SHA256 and SHA512 match)
✓ All 100 data rows verified successfully
✓ VERIFICATION PASSED - All files and rows are valid
```

### Re-standardize (if needed)

```bash
python3 standardize_met_inventory.py
```

This will:
1. Process the original file
2. Generate new standardized output
3. Create fresh checksums
4. Verify integrity

## Data Structure

### Columns

| Column | Name | Type | Description |
|--------|------|------|-------------|
| 1 | Object Date | String | Date or date range (e.g., "ca. 1650", "1875–79", "19th century (?)") |
| 2 | Title | String | Object title or description (may be empty for some records) |
| 3 | Object Number | String | Unique catalog/accession number |
| 4 | Link Resource | URL | Direct link to object in Met Museum online collection |

### Data Characteristics

**Date Field Examples:**
- Simple dates: "1896"
- Date ranges: "1875–79", "1814–21/2"
- Approximate dates: "ca. 1650", "ca. 1927"
- Uncertain dates: "1820 (?)", "ca. 4500–4000 B.C. (?)"
- Periods: "19th century", "mid-20th century"
- Complex dates: "early 19th century, crystal bust possibly 17th or 18th century"

**Object Number Examples:**
- Standard format: "91.1.396", "79.2.447"
- Compound numbers: "C.I.64.69.2", "63.350.619.451.6"
- Range notation: "21.175.224a, b", "36.120.598a, b"
- Alternative formats: "JP1328", "Burdick 223, N346.4"
- Dated references: "17.50.17-371(88)"

**Multilingual Content:**
- Entries 90-101 contain Chinese/Japanese text with English translations
- Format: Foreign text | English translation
- Examples: "东周 玉璜|Arc-shaped pendant (Huang)"

## Checksums and Fixity

### Understanding Checksums

Checksums are digital fingerprints that enable verification of file integrity. The package includes:

1. **File-level SHA256 & SHA512** - For verifying entire file hasn't changed
2. **Row-level SHA256** - For identifying which specific rows changed
3. **Metadata** - Including standardization date, methodology, and field definitions

### Verification Methods

See **FIXITY_VERIFICATION_GUIDE.md** for detailed information on:
- How to verify file integrity
- Understanding checksum results
- Detecting modifications
- Long-term preservation strategies
- Legal and archival considerations

## Technical Specifications

### File Format
- **Type**: Tab-Separated Values (TSV)
- **Delimiter**: Tab character (\\t)
- **Quote Character**: Double quote (") when needed
- **Quote Escape**: Double quote ("") when quote appears in content
- **Line Ending**: LF (\\n) - Unix style
- **Encoding**: UTF-8 (no BOM - Byte Order Mark)

### Standardization Specifications
- **Algorithm**: Canonical representation + SHA256/SHA512 hashing
- **Quoting**: Minimal (only when necessary)
- **Whitespace Handling**: Stripped from cell values, preserved in line structure
- **Empty Cells**: Represented as empty string (no whitespace)

## Scripts Reference

### standardize_met_inventory.py

Standardizes the inventory file and generates checksums.

```bash
python3 standardize_met_inventory.py
```

**Inputs:**
- `/mnt/user-data/uploads/met_inventory.tsv` (original file)

**Outputs:**
- `/mnt/user-data/outputs/met_inventory_standardized.tsv` (standardized file)
- `/mnt/user-data/outputs/met_inventory_checksums.json` (checksums and metadata)

**Process:**
1. Reads original file with UTF-8 encoding
2. Computes SHA256 and SHA512 of source file
3. Parses TSV with tab delimiters
4. Normalizes whitespace in each cell
5. Standardizes column headers
6. Computes SHA256 hash for each row
7. Writes standardized TSV with consistent formatting
8. Creates comprehensive JSON checksum document

### verify_met_inventory.py

Verifies the standardized file against stored checksums.

```bash
python3 verify_met_inventory.py
```

**Inputs:**
- `/mnt/user-data/outputs/met_inventory_standardized.tsv` (file to verify)
- `/mnt/user-data/outputs/met_inventory_checksums.json` (checksums to verify against)

**Outputs:**
- Console report showing verification status
- `/mnt/user-data/outputs/met_inventory_verification_report.json` (detailed results)

**Checks:**
1. Computes SHA256 and SHA512 of current file
2. Compares against stored file-level checksums
3. Verifies each row against stored row-level checksums
4. Reports any mismatches with specific row numbers
5. Generates detailed JSON report

## Requirements

### Python
- Python 3.6 or later
- Standard library modules only (csv, hashlib, json, pathlib)
- No external dependencies

### Supported Platforms
- Linux/Unix (macOS, Ubuntu, Debian, etc.)
- Windows (with Python installed)
- Any system with Python 3.6+

## Column Specifications

### Object Date
**Format**: String representing temporal information
**Notes**:
- May be empty for some records (especially rows 2-4, 9, 11)
- Supports various date conventions and notations
- May include uncertainty markers and date ranges

### Title
**Format**: String with descriptive information
**Notes**:
- May be empty for some records
- Can be very long with complex content
- May include quotations, parenthetical notes
- Some titles include catalog citations and cross-references

### Object Number
**Format**: String identifier
**Notes**:
- Primary key for collection items
- Varies in format but always unique
- May include letters, numbers, dots, commas, parentheses
- Some compound numbers reference multiple objects or components

### Link Resource
**Format**: HTTP/HTTPS URL
**Notes**:
- Begins with "http://www.metmuseum.org/art/collection/search/"
- Followed by numeric identifier
- Should not contain any whitespace or special URL encoding issues

## Data Quality Notes

### Completeness
- Object Date: 100/100 records (some values empty)
- Title: 76/100 records with content (24 empty)
- Object Number: 100/100 records
- Link Resource: 100/100 records

### International Content
- Records 90-101 contain East Asian (Chinese/Japanese) text
- Records maintain both original language and English translations
- All Unicode characters preserved correctly

### Accuracy
- Data sourced directly from Metropolitan Museum of Art
- No validation or correction applied during standardization
- Original formatting preserved as much as possible

## Archival and Preservation

This package is designed to support:
- **Data Integrity Verification**: Checksum-based fixity checking
- **Long-term Preservation**: Standardized format, documented methodology
- **Reproducibility**: Scripts to re-generate standardization
- **Auditability**: Detailed metadata and change tracking

See **FIXITY_VERIFICATION_GUIDE.md** for preservation best practices.

## Support and Documentation

### For Standardization Details
→ See **STANDARDIZATION_DOCUMENTATION.md**

### For Checksum/Fixity Information
→ See **FIXITY_VERIFICATION_GUIDE.md**

### For Data Content
→ Consult the Metropolitan Museum of Art collection database at www.metmuseum.org

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024 | Initial standardization and checksum generation |

## License and Attribution

**Data Source**: The Metropolitan Museum of Art, New York
- Collection: Open Access Collection
- License: The Metropolitan Museum of Art Collection API is available to the public under the Creative Commons Zero (CC0) license
- Attribution: Please credit "The Metropolitan Museum of Art, New York"

**Standardization Process**: Custom standardization with fixity verification
- Scripts: Available for reference and modification
- Documentation: Available for distribution with the data

## Key Features

✓ **Verified Standardization** - All 100 rows verified with checksums
✓ **File-level Checksums** - SHA256 and SHA512 for complete integrity
✓ **Row-level Checksums** - Individual verification of each data row
✓ **Reproducible** - Scripts available to re-standardize
✓ **UTF-8 Encoding** - Full international character support
✓ **Documented** - Comprehensive methodology and technical documentation
✓ **Preservation-Ready** - Designed for long-term archival storage
✓ **No Content Changes** - Original data values preserved exactly

## Getting Help

### Verification Status
Run: `python3 verify_met_inventory.py`

### Check File Integrity
Run: `sha256sum met_inventory_standardized.tsv`

### Review Checksums
Open: `met_inventory_checksums.json`

### Understand Methodology
Read: `STANDARDIZATION_DOCUMENTATION.md`

### Learn About Preservation
Read: `FIXITY_VERIFICATION_GUIDE.md`

---

**Package Version**: 1.0  
**Created**: 2024  
**Total Records**: 100  
**File Format**: TSV (Tab-Separated Values)  
**Encoding**: UTF-8  
**Verification Status**: ✓ Passed (all rows verified)
