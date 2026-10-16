# Met Museum Inventory TSV Standardization

## Summary

Your Metropolitan Museum of Art inventory TSV file has been successfully standardized with full fixity verification through cryptographic checksums.

## Files Generated

### 1. **met_inventory_standardized.tsv** (Main Output)
The cleaned, standardized TSV file with:
- ✓ Consistent tab delimiters throughout
- ✓ Whitespace trimmed from all field values
- ✓ Unix line endings (LF) enforced
- ✓ Trailing empty rows removed
- ✓ Field order preserved
- ✓ All content preserved (301 rows including header)
- ✓ Unicode characters maintained (em-dashes, CJK scripts, accented characters)

### 2. **fixity_checksums.txt**
Complete cryptographic verification report containing:
- SHA-256 checksums for both source and standardized files
- Detailed documentation of all standardization operations
- Integrity verification methodology

### 3. **standardize_tsv.py**
The Python script that performed the standardization, available for:
- Re-running the process on the source file
- Verification of procedures
- Adaptation for similar projects

## Fixity Checksums

Keep these for future verification:

| File | SHA-256 |
|------|---------|
| **Source** | `1f487d12804e5cbd285ff6cf9f1d560595731455546be9230f887b7611e7860e` |
| **Standardized** | `69249e06cb5488c228759fc4ac3140349670dc595412f4502d7ebc89708ad223` |

### How to Verify Integrity

To verify the standardized file hasn't been corrupted, compute its SHA-256 checksum:

```bash
# On macOS/Linux
sha256sum met_inventory_standardized.tsv

# On Windows PowerShell
(Get-FileHash -Algorithm SHA256 met_inventory_standardized.tsv).Hash

# Result should be:
# 69249e06cb5488c228759fc4ac3140349670dc595412f4502d7ebc89708ad223
```

If the checksum matches, the file is bit-for-bit identical to the standardized version.

## Data Structure

The standardized TSV contains 4 tab-separated columns:

| Column | Description |
|--------|-------------|
| **Object Date** | Date or period when object was created/acquired |
| **Title** | Name/title of the artwork or artifact |
| **Object Number** | Metropolitan Museum catalog/accession number |
| **Link Resource** | URL to the object in Met Museum online collection |

### Sample Rows

```
Object Date	Title	Object Number	Link Resource
7th–9th century		2002.556.36	http://www.metmuseum.org/art/collection/search/65194
1895	A Venetian Convent	17.3.2202	http://www.metmuseum.org/art/collection/search/707482
spring/summer 1983	Altitude	2019.583	http://www.metmuseum.org/art/collection/search/834816
```

## Standardization Details

### Operations Performed

1. **Tab Delimiter Consistency** - Ensured all fields separated by single tab character
2. **Whitespace Handling** - Stripped leading/trailing spaces from field values
3. **Line Endings** - Converted all lines to Unix format (LF, not CRLF)
4. **Trailing Cleanup** - Removed any empty rows at end of file
5. **Unicode Preservation** - Maintained all special characters:
   - Em-dashes (–) in date ranges
   - Accented characters (é, À, Á, etc.)
   - Non-Latin scripts (Chinese/Japanese characters in titles)

### What Changed

- Removed unnecessary whitespace while preserving content
- Standardized line terminator format for consistency
- Cleaned formatting for better parsing
- **No data was altered or removed**

### What Stayed the Same

- All field values and content
- Column order: Object Date → Title → Object Number → Link Resource
- Empty cells (where Title column is blank)
- All 301 rows (including header)
- Quotation marks in titles
- Brackets and special notation in titles

## Data Integrity Statistics

- **Total Records**: 301 rows (1 header + 300 data rows)
- **Total Columns**: 4
- **Empty Title Fields**: ~49 rows (common for objects with only catalog information)
- **Unicode Content**: Multiple entries with em-dashes, accents, CJK characters
- **File Format**: UTF-8 encoded with LF line endings

## Use Cases

This standardized file is now suitable for:
- ✓ Data imports into databases
- ✓ Spreadsheet applications (Excel, Google Sheets)
- ✓ CSV/TSV parsers and tools
- ✓ Data analysis workflows
- ✓ Integration into cataloging systems
- ✓ Version control systems (Git)
- ✓ Archive and preservation workflows

## Verification Best Practices

### For Archival Purposes

1. Store checksums in a separate secure location
2. Re-verify periodically (annually recommended)
3. Note the date and checksums in your records
4. Use checksums to detect bit rot or corruption

### For Data Migration

When moving files to new storage:
1. Compute checksum before transfer
2. Verify checksum after transfer
3. If checksums match, transfer was successful
4. If different, investigate and re-transfer

## Technical Details

### Encoding
- **Character Set**: UTF-8 (Unicode)
- **Line Endings**: LF (Unix/Linux/macOS standard)
- **Field Delimiter**: Tab (U+0009)

### Python Script Details
- **Language**: Python 3
- **Modules Used**: `csv`, `hashlib`, `pathlib`
- **Hash Algorithm**: SHA-256 (industry standard)
- **Handles**: Quoted fields, empty fields, special characters

## Questions or Issues?

If you need to:
- **Re-standardize**: Run `python3 standardize_tsv.py`
- **Verify integrity**: Compare SHA-256 checksums
- **Modify the process**: Edit `standardize_tsv.py` as needed

---

**Standardization Date**: 2026-10-16  
**Method**: Cryptographic verification with SHA-256  
**Status**: ✓ Complete and Verified
