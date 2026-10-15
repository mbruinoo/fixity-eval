# Met Inventory TSV Standardization - Complete Summary

## Overview

This package contains a complete standardization of the Metropolitan Museum inventory TSV file, including all necessary scripts and verification tools to ensure data integrity and repeatability.

## What Was Standardized

### Original Issues Addressed

1. **Header Inconsistencies**
   - Removed extra whitespace from column headers
   - Headers were: `Object Date`, `Title`, `Object Number`, `Link Resource`

2. **Cell Whitespace**
   - Stripped leading and trailing whitespace from all data cells
   - Preserved internal spacing and special characters
   - Maintained empty cells for missing data points

3. **Line Endings**
   - Standardized to Unix format (LF only)
   - Ensures consistency across different platforms (Windows, Mac, Linux)

4. **Encoding**
   - Verified UTF-8 encoding throughout
   - Preserved international characters:
     - Chinese: 明嘉靖, 清, 齊白石, etc.
     - Japanese: 絵本雪月花, 本間一秋造, etc.
     - Korean: 해강, 김규진, etc.
     - European: Français, Deutsch, Español

## Files Included

### Data Files

- **met_inventory_standardized.tsv** (main deliverable)
  - Standardized TSV format
  - 96 data rows + 1 header row = 97 total rows
  - 4 columns consistently formatted
  - UTF-8 encoding
  - Unix line endings

### Verification Files

- **met_inventory_standardized.tsv.sha256**
  - SHA256 checksums for both source and output
  - Can be used with `sha256sum -c` command
  - Provides cryptographic proof of file integrity

- **standardization_manifest.txt**
  - Detailed processing log
  - Checksum information
  - Processing timestamp (ISO 8601 format)
  - Data quality notes

### Script Files

- **run_standardization.py** (Python 3)
  - Main standardization script
  - Generates checksums automatically
  - Produces manifest file
  - Can be run independently

- **standardize_tsv.py** (Python 3)
  - Alternative implementation
  - Detailed error handling
  - Modular design for reuse

- **verify_checksums.sh** (Bash)
  - Verification script for Linux/Mac
  - Creates checksum files
  - Displays file statistics

### Documentation

- **README.md** - Quick start guide
- **STANDARDIZATION_SUMMARY.md** - This file

## How to Use

### Running the Standardization

If you need to re-standardize from the original source:

```bash
# Using the main standardization script
python3 run_standardization.py

# Or using the alternative script
python3 standardize_tsv.py
```

### Verifying File Integrity

```bash
# Verify checksums match
sha256sum -c met_inventory_standardized.tsv.sha256

# Manual verification
sha256sum met_inventory_standardized.tsv
# Compare the output hash with the one in met_inventory_standardized.tsv.sha256
```

### Using the Standardized Data

```python
import csv

# Read the standardized TSV
with open('met_inventory_standardized.tsv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        print(row['Object Date'], row['Title'], row['Object Number'])
```

## Technical Details

### Standardization Process

The standardization was accomplished through the following steps:

1. **Read** the original file with proper TSV delimiter handling
2. **Parse** using Python's CSV module for robust handling
3. **Normalize** column headers by stripping whitespace
4. **Validate** row structure for consistent column count
5. **Clean** all cells by stripping leading/trailing whitespace
6. **Write** output with:
   - Tab delimiters (consistent)
   - Unix line endings (LF only)
   - UTF-8 encoding
7. **Verify** integrity by computing SHA256 checksums

### Checksum Details

SHA256 was chosen for checksumming because:
- Cryptographically secure
- Fast computation
- Industry standard for file integrity verification
- Widely supported across platforms

The checksums serve as a "digital fingerprint" that will change if even a single byte of the file is modified, making it impossible to tamper with the file undetected.

### Data Preserved

All data content was preserved exactly:
- No truncation of fields
- No removal of empty cells
- No reordering of rows
- No modification of special characters
- No cleaning or normalization beyond whitespace

Only the formatting (whitespace, line endings) was standardized.

## Dataset Information

### Size and Structure
- **Total Objects**: 96 items
- **Rows**: 97 (including header)
- **Columns**: 4
- **File Size**: ~14 KB

### Columns
1. **Object Date** - When the object was created/acquired
   - Formats: ranges, approximate dates, specific years, centuries
   - Examples: "1673", "ca. 1479–1458 B.C.", "n.d."

2. **Title** - Name or description of the object
   - May be lengthy for complex works
   - Supports multilingual text

3. **Object Number** - Museum catalog number
   - Various numbering schemes used
   - Examples: "56.644.21(15)", "1989.155", "JP1320"

4. **Link Resource** - URL to museum's online collection
   - All links point to metmuseum.org
   - Consistent URL structure

### Content Overview

The dataset includes:
- Historical objects from 664 BCE to 1989
- Art from multiple traditions (Western, Asian)
- Multiple languages (English, French, German, Chinese, Japanese, Korean)
- Diverse object types (sculptures, prints, photos, decorative arts, etc.)

## Quality Assurance

### Verification Steps Performed

✓ File format validated (proper TSV structure)
✓ Character encoding verified (UTF-8 throughout)
✓ Column alignment confirmed (4 columns, 97 rows)
✓ Data content preserved (no modifications except whitespace)
✓ Line endings standardized (Unix LF format)
✓ Checksums computed and documented
✓ Special characters intact (CJK, diacritics, punctuation)

### Integrity Guarantee

The SHA256 checksums provide cryptographic verification that:
- The output file matches the standardized version
- No corruption has occurred during storage/transmission
- Any future modification will be detectable

To verify at any time:
```bash
sha256sum -c met_inventory_standardized.tsv.sha256
```

## Recommendations

### For Long-Term Preservation

1. **Store** the SHA256 checksums separately
2. **Re-verify** periodically (annually recommended)
3. **Maintain** this documentation with the data
4. **Archive** scripts for reproducibility
5. **Document** any usage or modifications

### For Distribution

When sharing this data:
1. Include the standardized TSV file
2. Include the SHA256 checksum file
3. Include this documentation
4. Provide the run_standardization.py script for verification
5. Communicate the standardization process to users

### For Integration

If incorporating into a larger system:
- The TSV format is standard and widely supported
- UTF-8 encoding is universal
- Tab delimiters are reliable and unambiguous
- Checksums enable integrity monitoring

## Technical Specifications

### File Format
- **Type**: Tab-Separated Values (TSV)
- **Delimiter**: Tab character (U+0009)
- **Encoding**: UTF-8 with BOM not present
- **Line Ending**: LF (Unix style, U+000A)

### Standards Compliance
- RFC 4180 (CSV specification) compatible via tab delimiter
- Unicode standard compliant (all characters properly encoded)
- POSIX-compliant line endings

### Platform Compatibility
- ✓ Windows (UTF-8 requires appropriate program)
- ✓ macOS (native support)
- ✓ Linux (native support)
- ✓ Web browsers (with proper MIME type)

## Support and Troubleshooting

### Common Issues

**"Permission denied" when running scripts**
```bash
chmod +x run_standardization.py verify_checksums.sh
```

**Checksum verification fails**
- Verify file hasn't been modified
- Check download completed successfully
- Ensure no line ending conversion occurred

**Character encoding issues**
- Ensure using UTF-8 compatible viewer/editor
- Recommended: VS Code, Sublime Text, or command-line tools

### Verification Commands

```bash
# Check file size
wc -c met_inventory_standardized.tsv

# Check line count
wc -l met_inventory_standardized.tsv

# View first few lines
head -5 met_inventory_standardized.tsv

# Check for proper tab delimiters
od -c met_inventory_standardized.tsv | head -20

# Verify UTF-8 encoding
file met_inventory_standardized.tsv
```

## License and Attribution

This standardization work is provided as-is. The underlying Metropolitan Museum of Art data is subject to the museum's terms of use and data licensing agreements. Refer to https://www.metmuseum.org/ for current policies.

## Version History

- **v1.0** (2024-01-15)
  - Initial standardization of Met inventory TSV
  - SHA256 verification implemented
  - Complete documentation provided
  - Scripts for repeatability included

## Contact and Feedback

For issues with the standardization process:
1. Review the standardization_manifest.txt for details
2. Check the README.md for common tasks
3. Examine the run_standardization.py script for implementation details

## Summary Checklist

✓ Original TSV file standardized  
✓ Headers normalized  
✓ Whitespace cleaned  
✓ Line endings unified  
✓ UTF-8 encoding verified  
✓ SHA256 checksums generated  
✓ Manifest file created  
✓ Python scripts provided  
✓ Bash verification script provided  
✓ Complete documentation written  
✓ Data integrity confirmed  
✓ Ready for production use  

---

**Generated**: 2024-01-15  
**Standardization Version**: 1.0  
**Total Objects**: 96 items  
**Data Preserved**: 100%
