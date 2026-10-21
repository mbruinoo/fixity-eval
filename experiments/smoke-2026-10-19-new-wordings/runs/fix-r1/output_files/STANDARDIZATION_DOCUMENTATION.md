# TSV Standardization with Fixity Preservation

## Overview
This documentation describes the standardization process applied to `met_inventory.tsv` from the Metropolitan Museum of Art collection catalog, with complete fixity preservation through SHA-256 checksums.

## Files Included

1. **met_inventory.tsv** - Original source file
2. **met_inventory_standardized.tsv** - Standardized output file
3. **standardize_tsv.py** - Python script implementing standardization logic
4. **run_standardization.sh** - Bash script to execute standardization with checksum verification
5. **fixity_report.json** - Detailed report with all checksums and statistics
6. **STANDARDIZATION_DOCUMENTATION.md** - This file

## Standardization Steps Applied

### 1. Tab Delimiter Normalization
- All delimiters verified to be consistent tab characters (U+0009)
- No spaces or other whitespace used as delimiters
- Ensures proper column parsing

### 2. Line Ending Normalization
- All line endings converted to LF (Line Feed, \n)
- Removes any CR/LF or CR inconsistencies
- Ensures cross-platform compatibility

### 3. Trailing Whitespace Trimming
- Removed leading and trailing whitespace from each cell
- Preserves internal spacing within cell content
- Prevents parsing artifacts from hidden whitespace

### 4. Column Structure Validation
- Verified consistent column count across all rows
- Padded rows with missing columns (empty strings)
- Truncated rows with excess columns
- Header: 4 columns (Object Date, Title, Object Number, Link Resource)

### 5. Empty Row Removal
- Removed completely empty rows
- Preserved rows with at least one non-empty cell
- Cleaned data reduces file size and improves processing efficiency

## Data Structure

### Columns
| Column | Content | Notes |
|--------|---------|-------|
| Object Date | Temporal dating information | Can include centuries, specific dates, ranges |
| Title | Object title/description | May be empty for some objects |
| Object Number | Museum catalog number | Unique identifier |
| Link Resource | Direct URL to museum collection page | HTTP/HTTPS links |

### Statistics
- **Total rows (including header):** See fixity_report.json
- **Data rows:** See fixity_report.json
- **Columns:** 4
- **Character encoding:** UTF-8
- **Date range covered:** 4th century BCE to 20th century
- **Languages represented:** English, French, Italian, Chinese, Japanese, Korean

## Fixity Preservation

### What is Fixity?
Fixity refers to the property of a digital object remaining unchanged. In digital preservation, fixity checking ensures that files haven't been corrupted, altered, or tampered with.

### Checksum Verification

#### SHA-256 Hash Algorithm
- Cryptographic hash function producing 256-bit (64-character hexadecimal) output
- Deterministic: same input always produces same hash
- Collision-resistant: extremely unlikely two different files produce same hash
- Widely accepted in digital preservation standards

#### How to Verify Integrity

**Command line verification:**
```bash
# Verify source file
sha256sum met_inventory.tsv
# Compare output with "checksum_sha256" in fixity_report.json

# Verify output file
sha256sum met_inventory_standardized.tsv
# Compare output with "checksum_sha256" in fixity_report.json

# Verify report itself
sha256sum fixity_report.json
```

**Python verification:**
```python
import hashlib

def verify_checksum(filepath, expected_checksum):
    with open(filepath, 'rb') as f:
        actual = hashlib.sha256(f.read()).hexdigest()
    return actual == expected_checksum
```

### Fixity Report Contents

The `fixity_report.json` file includes:

```json
{
  "timestamp": "ISO 8601 datetime of standardization operation",
  "operation": "TSV Standardization",
  "input_file": {
    "path": "path to original file",
    "checksum_sha256": "hex string of source hash",
    "size_bytes": "file size in bytes"
  },
  "output_file": {
    "path": "path to standardized file",
    "checksum_sha256": "hex string of output hash",
    "size_bytes": "file size in bytes"
  },
  "statistics": {
    "total_rows": "number including header",
    "columns": 4,
    "data_rows": "number excluding header"
  },
  "standardization_applied": [
    "list of normalization steps"
  ]
}
```

## Quality Assurance

### Data Integrity Checks Performed
- ✓ Column count consistency verified
- ✓ No accidental data loss during trimming
- ✓ Unicode characters preserved (Chinese, Japanese, Korean, French accents)
- ✓ URL links remain intact and functional
- ✓ Special characters and punctuation preserved
- ✓ Quotation marks and apostrophes maintained

### Before vs. After
- **Before:** Potentially inconsistent delimiters, variable line endings, trailing spaces
- **After:** Consistent tab delimiters, uniform LF line endings, trimmed whitespace, validated structure

## Usage Examples

### Opening in Spreadsheet Applications
```
LibreOffice Calc, Excel, Google Sheets
- File > Open > Select met_inventory_standardized.tsv
- Encoding: UTF-8
- Delimiter: Tab
```

### Command Line Processing
```bash
# View first 10 rows
head -10 met_inventory_standardized.tsv

# Count data rows
wc -l met_inventory_standardized.tsv

# Extract specific column (e.g., Object Numbers)
cut -f3 met_inventory_standardized.tsv

# Convert to CSV for compatibility
sed 's/\t/,/g' met_inventory_standardized.tsv > met_inventory.csv
```

### Python Processing
```python
import csv

with open('met_inventory_standardized.tsv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        print(row['Object Number'], row['Title'])
```

## Standards Compliance

### Standards Referenced
- **RFC 4180:** Common Format and MIME Type for Comma-Separated Values (CSV) Files
  - Adapted for TSV with tab delimiter
- **UTF-8 (RFC 3629):** Character encoding standard
- **NISO Z39.19:** Guidelines for the Construction, Format, and Management of Monolingual Controlled Vocabularies
- **ISO/IEC 27002:** Information security standards for preservation

### Best Practices Applied
- Platform-independent line endings (LF)
- UTF-8 encoding (international character support)
- Consistent delimiter usage
- Whitespace normalization
- Cryptographic integrity verification

## Recommendations for Long-Term Preservation

1. **Store checksums separately** - Keep fixity_report.json in a different location
2. **Verify periodically** - Run checksum verification on a regular schedule
3. **Document provenance** - Maintain records of standardization process
4. **Back up** - Create multiple copies in different storage systems
5. **Monitor technology** - Stay informed about standards evolution
6. **Test restoration** - Periodically verify you can successfully process the file

## Further Information

### Digital Preservation Resources
- NIST Digital Preservation Guidelines
- Library of Congress Recommended Format Specifications
- OAIS Reference Model (ISO 14721)
- BitCurator Digital Preservation Tools

### TSV Format References
- https://tools.ietf.org/html/rfc4180 (CSV/TSV standards)
- https://en.wikipedia.org/wiki/Tab-separated_values

## Support & Maintenance

### Script Features
- Error handling for malformed input
- UTF-8 encoding validation
- Automated checksum generation
- Detailed reporting
- Cross-platform compatibility (Windows, macOS, Linux)

### Known Considerations
- Empty Title cells are preserved (museum data characteristic)
- Object dates maintain original format variance for historical accuracy
- URLs preserved exactly as provided by museum
- Special characters preserved in all languages

---

**Document Version:** 1.0  
**Last Updated:** [See fixity_report.json timestamp]  
**Standardization Method:** Automated Python script with SHA-256 verification
