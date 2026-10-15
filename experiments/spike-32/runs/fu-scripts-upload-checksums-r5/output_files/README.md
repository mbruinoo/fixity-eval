# TSV Standardization Report
## Metropolitan Museum of Art Inventory

### Overview
This directory contains the standardized Metropolitan Museum of Art inventory TSV file along with checksums and verification reports to ensure data integrity and fixity.

### Files Generated

#### 1. **met_inventory_standardized.tsv**
The standardized version of the original inventory file.
- **Format**: Tab-Separated Values (TSV)
- **Encoding**: UTF-8
- **Line Ending**: Unix (LF)
- **Rows**: 101 (1 header + 100 data rows)
- **Columns**: 4
  - Object Date
  - Title
  - Object Number
  - Link Resource

#### 2. **standardize_tsv.py**
Python script used to perform the standardization and checksum verification.

**Features:**
- Reads TSV with proper tab delimiter handling
- Normalizes CSV quoting rules (QUOTE_MINIMAL)
- Preserves UTF-8 encoding throughout
- Handles special characters and international text (Chinese, Japanese, Korean)
- Calculates SHA256 checksums for fixity verification
- Generates detailed audit report

**Usage:**
```bash
python3 standardize_tsv.py
```

#### 3. **checksums.txt**
Contains SHA256 checksums for both source and standardized files.

**Contents:**
```
Source File Checksum (SHA256):
/mnt/user-data/uploads/met_inventory.tsv
e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf

Standardized File Checksum (SHA256):
/mnt/user-data/outputs/met_inventory_standardized.tsv
e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf
```

**Important Note:** Both checksums are identical because the original file was already well-formed with consistent tab-delimited formatting.

#### 4. **standardization_report.txt**
Detailed human-readable report including:
- Source and output file information
- Processing statistics
- Standardization actions performed
- Fixity verification data
- Recommendations for archival

---

## Standardization Details

### Actions Performed
✓ **Tab-Delimited Format Normalization** - Ensured consistent tab delimiters throughout  
✓ **CSV Quoting Rules** - Applied QUOTE_MINIMAL for consistent field quoting  
✓ **UTF-8 Encoding** - Maintained throughout entire file  
✓ **Line Ending Normalization** - Standardized to Unix LF line endings  
✓ **Character Preservation** - Handled international text (Chinese, Japanese, Korean)  
✓ **Data Integrity** - All 100 inventory records preserved without modification  

### Data Quality Observations
- **Header Row**: Properly formatted with 4 columns
- **Empty Fields**: Present in some Title fields (lines 2-9, 87, 90, 98-99) - preserved as-is
- **Special Characters**: Extensive use of Unicode characters handled correctly
- **Field Content**: 
  - Dates: Various formats (centuries, specific years, date ranges, "n.d.", "circa")
  - Titles: Full descriptions with special characters and quotation marks
  - Object Numbers: MET catalog identifiers
  - Links: Complete HTTPS URLs to museum collection

### Character Set Coverage
- Latin characters with diacritics (French, German, Italian, Spanish)
- Chinese characters (Simplified and Traditional)
- Japanese characters (Hiragana, Kanji)
- Korean Hangul
- Special symbols (dashes, quotes, parentheses)

---

## Fixity & Verification

### What is Fixity?
Fixity is a digital preservation principle ensuring that files haven't been accidentally or maliciously altered. It's maintained through checksums—mathematical fingerprints of file content.

### SHA256 Checksums
Both files share the same SHA256 checksum:
```
e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf
```

This indicates:
1. The source file was already well-standardized
2. The standardization process preserved all content without modification
3. Both files are identical and can be verified against this checksum

### Verifying File Integrity
To verify the standardized file hasn't been corrupted:

**On macOS/Linux:**
```bash
sha256sum met_inventory_standardized.tsv
# Compare output with: e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf
```

**On Windows (PowerShell):**
```powershell
Get-FileHash -Path "met_inventory_standardized.tsv" -Algorithm SHA256
# Compare output with: e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf
```

---

## Archival Recommendations

1. **Maintain Multiple Copies**: Store at least 3 copies in geographically diverse locations
2. **Store Checksums**: Keep checksums alongside files for periodic verification
3. **Document Provenance**: Maintain this README and standardization_report.txt
4. **Periodic Verification**: Re-run checksum verification annually
5. **Format Preservation**: TSV is a stable, open format suitable for long-term archival
6. **Metadata**: Store the script and report as accompanying documentation

---

## Technical Specifications

| Property | Value |
|----------|-------|
| Format | Tab-Separated Values (TSV) |
| Encoding | UTF-8 without BOM |
| Line Endings | LF (Unix/Linux style) |
| File Size | 15,295 bytes |
| Total Rows | 101 |
| Data Rows | 100 |
| Columns | 4 |
| CSV Dialect | QUOTE_MINIMAL |
| Quote Character | Double quote (") |
| Escape Method | RFC 4180 compliant |

---

## Processing Statistics

- **Processing Time**: Seconds (minimal)
- **Rows Processed**: 101
- **Data Rows**: 100 (excluding header)
- **Fields Examined**: 400
- **Unique Object Numbers**: 100
- **International Characters**: Yes (CJK, diacritics)
- **Empty Fields**: Present (preserved as blank)
- **Error Rate**: 0%

---

## Questions?

For verification or additional standardization needs:
- Run `python3 standardize_tsv.py` to regenerate reports and checksums
- Consult the `standardization_report.txt` for detailed audit trail
- Compare checksums to verify file integrity over time

---

**Generated**: 2026-10-15 (ISO 8601 format)  
**Process**: Automated TSV standardization with SHA256 fixity verification  
**Status**: ✓ Complete and verified
