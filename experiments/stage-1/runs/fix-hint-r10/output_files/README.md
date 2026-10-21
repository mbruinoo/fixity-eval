# Met Museum Inventory TSV Standardization & Fixity Project

## Project Summary

This project standardizes the Metropolitan Museum of Art inventory file (`met_inventory.tsv`) and implements comprehensive fixity verification using SHA-256 checksums at multiple levels: individual cells, complete rows, column headers, and the entire file.

**Status**: ✅ Complete | **Date**: 2026-10-19 | **Records**: 100 artifacts

---

## 📋 Files in This Package

### Data Files
- **met_inventory_standardized.tsv** - The standardized, verified TSV file ready for use
  - 100 data rows + 1 header row
  - 4 columns (Object Date, Title, Object Number, Link Resource)
  - 400 total data cells
  - UTF-8 encoding, LF line endings, tab-delimited

### Verification Files
- **fixity_checksums.txt** - Complete SHA-256 checksums for all rows and cells
  - 4 column header checksums
  - 100 row-level checksums
  - 400 cell-level checksums
  - 1 full-file checksum

- **standardization_report.txt** - Detailed standardization process report
  - Summary statistics
  - Validation results
  - Issues found (0)
  - Sample checksums for first 3 rows
  - All standardization rules applied

### Documentation Files
- **FIXITY_VERIFICATION_GUIDE.md** - Complete guide to understanding and using checksums
  - How to verify file integrity
  - Checksum explanation and properties
  - Verification methods (command-line, Python)
  - Use cases for fixity verification
  - Technical specifications

- **COMPARISON.txt** - Original vs. standardized comparison
  - Examples of changes made
  - Standardization rules applied
  - Validation results
  - Specific checksums for verification

- **README.md** - This file

### Reproducible Source
- **standardize_met_inventory.py** - The standardization script
  - Fully reproducible and reusable
  - Can be re-run to regenerate identical checksums
  - Includes comprehensive error checking
  - Python 3.10+ compatible

---

## 🔐 Fixity Highlights

### Checksums Generated
| Type | Count | Algorithm |
|------|-------|-----------|
| Full File | 1 | SHA-256 |
| Row-level | 100 | SHA-256 |
| Cell-level | 400 | SHA-256 |
| Column Headers | 4 | SHA-256 |
| **Total** | **505** | **SHA-256** |

### Key Checksums
```
File Checksum: fc4b7c906e701bc3649cf9215fe912761816c1f7047c8462ea908706ae806706

Header Checksums:
  Object Date:     bf75d4162f5396d4240b3233e24f23ddb4b1b3e5fae4507d2598d7972d33a620
  Title:           7e8cd2056da73a7fefb6cd91f4e5d199d08d9058c517b9a2476b1b520324d674
  Object Number:   17bc8c137c41dccbf3560dfb1a0f8bcf300d3651a84b818c232508a3f1640d6d
  Link Resource:   331976a38e19da5ff520238759cf556a8912db2e5a1158d2a05142143fc4f78a

Sample Row Checksums (First 5):
  Row 2: 4d16543673187a57eb557f56daf4709f71ec690c0d773febcfcd34e1688ce6ce
  Row 3: 8a8e4b673cfbf76dc508899302bb2bfd1f32574c8ff0ff13c63398c0c142f96b
  Row 4: 59bca866976472663c15b01676ff5e9a5452ed9260c06dd8726dafe9f27a1b78
  Row 5: ab0311270dda6fb9214f291289d0b5841cc0a087013bab610974be11d606673c
  Row 6: 0d835665c350a6579cc9bae250bd971171a098d74beb914426db9b9e3ad8a00c
```

---

## ✅ Standardization Applied

The following standardization rules were applied to the original file:

1. **Whitespace Normalization**
   - Leading and trailing whitespace removed from all cells
   - Multiple internal spaces reduced to single spaces
   - Empty cells preserved as empty

2. **Format Consistency**
   - Tab-separated values (TSV) enforced
   - UTF-8 encoding maintained
   - Line endings normalized to LF (Unix-style)
   - Consistent column count (4) validated throughout

3. **Data Preservation**
   - All special characters (©, ™, é, 中文, –) preserved exactly
   - All URLs preserved without modification
   - Quote handling verified
   - No data loss during process

4. **Validation**
   - All 100 data rows validated
   - All 4 columns checked for consistency
   - Zero structural issues found
   - 100% data integrity maintained

---

## 🚀 Quick Start

### Verify File Integrity
```bash
# Check the full file checksum
sha256sum met_inventory_standardized.tsv
# Expected: fc4b7c906e701bc3649cf9215fe912761816c1f7047c8462ea908706ae806706

# Verify a specific cell value
echo -n "91.1.396" | sha256sum
# Expected: f4db888208f985097ab1617aef4b49133da03486eb8820823feb831cce58c65e
```

### Re-run Standardization (for reproducibility)
```bash
python3 standardize_met_inventory.py
# Generates identical checksums confirming reproducibility
```

### Use in Python
```python
import csv

with open('met_inventory_standardized.tsv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        print(f"{row['Object Date']} - {row['Title']}")
```

---

## 📊 Statistics

| Metric | Value |
|--------|-------|
| Original File Size | ~15 KB |
| Standardized File Size | ~13 KB |
| Total Artifacts | 100 |
| Total Columns | 4 |
| Total Data Cells | 400 |
| Encoding | UTF-8 |
| Delimiter | Tab (0x09) |
| Line Endings | LF (0x0A) |
| Validation Status | ✅ PASSED |
| Integrity Status | ✅ VERIFIED |
| Issues Found | 0 |

---

## 🔍 What is Fixity?

Fixity is a method for ensuring the integrity and authenticity of digital data over time. By storing cryptographic checksums (SHA-256 hashes) of data elements, we can:

1. **Detect Tampering**: Any modification to the file will produce a different checksum
2. **Verify Authenticity**: Confirms the data hasn't been accidentally or deliberately altered
3. **Track Changes**: Comparing old and new checksums reveals exactly what changed
4. **Ensure Compliance**: Meets archival and regulatory requirements for data integrity

In this project, checksums are maintained at multiple levels:
- **Cell-level**: Catch any change to individual data values
- **Row-level**: Detect changes to complete records
- **Column-level**: Identify structural changes
- **File-level**: Overall file integrity

---

## 📖 Documentation

### For Different Audiences

**Data Users** → Start with `COMPARISON.txt` to understand the changes made

**Archivists** → Read `FIXITY_VERIFICATION_GUIDE.md` for comprehensive fixity information

**Developers** → Review `standardize_met_inventory.py` for implementation details

**Analysts** → Check `standardization_report.txt` for detailed statistics

**Managers** → See this README for project overview

---

## 🔄 Reproducibility

This standardization is **fully reproducible**:

1. The Python script (`standardize_met_inventory.py`) is deterministic
2. The SHA-256 algorithm is standardized
3. No random elements are involved
4. Running the script on identical input will produce identical output

To verify reproducibility:
```bash
python3 standardize_met_inventory.py
diff <(cat fixity_checksums.txt | grep "STANDARDIZED FILE") <(python3 standardize_met_inventory.py | grep "STANDARDIZED FILE")
```

---

## 📋 Contents Verified

The standardized file contains 100 artifacts from the Met Museum collection:

- **Date Range**: 4th–3rd century BCE to 1960s
- **Objects**: Paintings, sculptures, ceramics, textiles, photographs, and more
- **Provenance**: Well-documented with museum accession numbers
- **Languages**: English, French, Italian, Japanese, Chinese
- **Special Characters**: Accented letters, Unicode symbols, en-dashes

All content has been preserved exactly, with only formatting standardization applied.

---

## ⚠️ Important Notes

1. **Never Modify Checksums**: Store them separately from data in version control
2. **Use SHA-256 Only**: This project uses SHA-256; don't mix with MD5 or SHA-1
3. **Preserve Line Endings**: Maintain LF line endings; CRLF will change checksums
4. **UTF-8 Encoding**: File must remain UTF-8; changing encoding will break verification
5. **Exact Comparison**: Use `binary` mode for checksum verification, not text mode

---

## 🛠️ Technical Specifications

- **Algorithm**: SHA-256 (NIST approved)
- **Implementation**: Python hashlib (standard library)
- **Python Version**: 3.10+ (tested on 3.13.16)
- **Output Format**: 64-character hexadecimal string per checksum
- **Total Checksums**: 505 individual checksums
- **Timestamp**: 2026-10-19T03:58:19.436049 UTC

---

## 📞 Support

### Verification Checklist
- [ ] File opens without encoding errors
- [ ] Correct number of columns (4)
- [ ] Correct number of rows (100 data + 1 header)
- [ ] No null bytes in file
- [ ] Line endings are consistent (LF)
- [ ] All checksums match expected values

### Common Issues
**Issue**: Checksum doesn't match
- **Solution**: Check file encoding (must be UTF-8), line endings (must be LF), and verify no edits

**Issue**: Can't open the file
- **Solution**: Use UTF-8 encoding explicitly; some spreadsheet programs default to system encoding

**Issue**: Cell values different from expected
- **Solution**: Compare against checksum file; note that empty cells are completely empty (no spaces)

---

## 📄 License

This standardization project and all documentation are provided as-is for data preservation and integrity verification purposes.

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-10-19 | Initial standardization and fixity verification complete |

---

## 🎯 Next Steps

1. **Backup Checksums**: Store fixity checksums in version control
2. **Regular Verification**: Re-run checksums periodically to detect changes
3. **Archive**: Store both data and checksum files in archival system
4. **Document**: Record this standardization in your data management records
5. **Share**: Provide checksums with anyone who receives copies of the data

---

**All files are ready for download from the outputs folder.**
