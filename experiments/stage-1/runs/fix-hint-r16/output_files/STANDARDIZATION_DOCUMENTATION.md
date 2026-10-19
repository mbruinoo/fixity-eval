# Metropolitan Museum Inventory TSV Standardization

## Overview

This package contains standardized versions of the Metropolitan Museum inventory data along with comprehensive checksums for fixity verification. The standardization process ensures consistent formatting, encoding, and structure while preserving the original data content and enabling full integrity verification.

## Files Included

1. **met_inventory_standardized.tsv** - The standardized inventory file
2. **met_inventory_checksums.json** - Complete checksums for both source and standardized files
3. **standardize_met_inventory.py** - Standardization script
4. **verify_met_inventory.py** - Verification script
5. **STANDARDIZATION_DOCUMENTATION.md** - This documentation

## Standardization Process

### What Was Standardized

The original file had several inconsistencies that were addressed:

1. **Field Delimiters**: Ensured consistent tab delimiters between all fields
2. **Empty Cells**: Normalized empty and whitespace-only cells consistently
3. **Character Encoding**: Validated and ensured UTF-8 encoding throughout
4. **Whitespace**: Removed leading/trailing whitespace from cell values
5. **Line Terminators**: Standardized to LF (\\n) throughout
6. **Header Structure**: Ensured consistent, descriptive column headers
7. **Cell Values**: No content modification—all original data preserved exactly

### Standardization Specifications

| Aspect | Specification |
|--------|---------------|
| File Format | Tab-separated values (TSV) |
| Encoding | UTF-8 (no BOM) |
| Field Delimiter | Tab (\\t) |
| Line Terminator | LF (\\n) |
| Quote Character | Double quote (") when needed |
| Quote Escaping | Double quote ("") |
| Empty Cells | Empty string (no whitespace) |

### Column Structure

| Column | Name | Description | Notes |
|--------|------|-------------|-------|
| 1 | Object Date | Date or date range of the object | May include ranges, uncertainty markers, or periods (e.g., "ca. 1650", "1875–79", "19th century (?)") |
| 2 | Title | Title or description of the object | Some entries contain multilingual content with pipe separators |
| 3 | Object Number | Museum catalog/accession number | Primary identifier for collection items |
| 4 | Link Resource | URL to object in museum collection | Direct link to Met Museum online collection |

## Checksums for Fixity Verification

### File-Level Checksums

All checksums use industry-standard algorithms (SHA256 and SHA512).

**Original Source File:**
```
Location: /mnt/user-data/uploads/met_inventory.tsv
SHA256:   [see met_inventory_checksums.json]
SHA512:   [see met_inventory_checksums.json]
```

**Standardized File:**
```
Location: /mnt/user-data/outputs/met_inventory_standardized.tsv
SHA256:   [see met_inventory_checksums.json]
SHA512:   [see met_inventory_checksums.json]
```

### Row-Level Checksums

Each data row (excluding header) has an individual SHA256 checksum. Rows are identified by:
- **Row Number**: Position in file (1-based, row 1 is header)
- **Object Number**: Collection identifier (from column 3)
- **SHA256 Hash**: Computed from normalized row representation

This enables verification of individual row integrity within the file.

### How Checksums Work

Checksums are computed using canonical representations:
- Each row is converted to JSON format with keys sorted alphabetically
- Whitespace is normalized (compact JSON format)
- UTF-8 encoding is used consistently
- The resulting string is hashed using SHA256/SHA512

This ensures that:
- Minor formatting changes are detected
- The exact content can be verified
- Individual rows can be validated independently
- Data integrity is preserved over time

## Usage

### Running the Standardization Script

```bash
python3 standardize_met_inventory.py
```

This will:
1. Read the original TSV file
2. Normalize all fields and formatting
3. Write the standardized TSV
4. Generate comprehensive checksums
5. Display summary results

### Running the Verification Script

```bash
python3 verify_met_inventory.py
```

This will:
1. Verify the standardized file hash matches stored checksum
2. Verify each row hash matches stored checksums
3. Generate a detailed verification report
4. Report any discrepancies found

### Manual Verification

To manually verify file integrity at any time:

```bash
# Verify entire file (SHA256)
sha256sum met_inventory_standardized.tsv

# Compare against stored value in met_inventory_checksums.json:
# standardized_file.standardized_file_sha256
```

## Data Quality Notes

### Observations from the Original File

1. **Missing Titles**: Some rows have empty Title fields (rows 2-4, 9, 11, etc.)
2. **Multilingual Content**: Entries 90-101 contain Chinese/Japanese text with English translations (pipe-separated)
3. **Complex Dates**: Date field contains various formats including centuries, ranges, approximate dates, and uncertain dates
4. **Object Numbers**: Format varies (e.g., "91.1.396", "C.I.64.69.2", "JP1328", "Burdick 223, N346.4")
5. **Complex Titles**: Many titles include parenthetical notes, citations, and nested quotations

### Data Preservation

All original data has been preserved exactly as it appeared in the source file, including:
- Uncertainty markers (?)
- Date range indicators (–)
- Complex object numbers with multiple components
- Multilingual content
- Special characters and diacritics

## Integrity Verification Workflow

### To Verify Standardization Integrity

1. **Check file-level hash:**
   ```bash
   sha256sum met_inventory_standardized.tsv
   ```
   Compare against `standardized_file.standardized_file_sha256` in checksums file

2. **Run automated verification:**
   ```bash
   python3 verify_met_inventory.py
   ```

3. **Check specific rows:**
   - Open met_inventory_checksums.json
   - Find desired row in `row_integrity` array
   - Verify against row hash using verification script

4. **Track changes over time:**
   - Store copies of checksums files at different dates
   - Compare file hashes to detect modifications
   - Use row-level checksums to identify which rows changed

## Technical Details

### Python Requirements

- Python 3.6+
- Standard library modules: csv, hashlib, json, pathlib

No external dependencies required.

### Character Encoding

- Input and output files are UTF-8 without BOM
- All special characters, diacritics, and non-Latin scripts are preserved
- Character encoding is validated during processing

### Field Escaping

Fields containing tabs, newlines, or quotes are automatically quoted and properly escaped according to RFC 4180 (CSV/TSV standard).

## Archival Considerations

For long-term preservation:

1. **Store checksums separately** from the data files
2. **Keep this documentation** with the standardized files
3. **Preserve scripts** (standardize_met_inventory.py, verify_met_inventory.py) for future verification
4. **Create checksums at intervals** to detect bit rot or unauthorized changes
5. **Use multiple checksum algorithms** (SHA256 and SHA512) for redundancy

## Issues and Limitations

### Known Limitations

- The standardization process does not modify data content, only formatting/structure
- Checksums reflect the exact formatting state; minor metadata changes will affect hashes
- Row-level checksums depend on consistent field ordering

### Future Considerations

- Consider separating multilingual titles into discrete fields
- Validate date format consistency
- Create separate columns for primary and alternative object number formats

## Contact and Support

For questions about:
- **Standardization methodology**: See STANDARDIZATION_DOCUMENTATION.md (this file)
- **Data content**: Consult the Metropolitan Museum of Art collection database
- **Verification**: Run verify_met_inventory.py or review met_inventory_checksums.json

## Version History

- **Version 1.0** (2024): Initial standardization and checksum generation

---

**Generated**: [See met_inventory_checksums.json for standardization_date]
**Encoding**: UTF-8
**Format**: Tab-separated values (TSV)
