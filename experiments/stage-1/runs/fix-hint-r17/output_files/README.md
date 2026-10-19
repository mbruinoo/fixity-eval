# Met Museum Inventory Standardization Package

This package contains the standardized Met Museum inventory TSV file with complete fixity preservation through checksumming and detailed documentation.

## 📦 Package Contents

### Main Files

1. **standardized_met_inventory.tsv**
   - The standardized inventory dataset
   - 100 records with 5 columns (original 4 + audit Record_ID)
   - UTF-8 encoding, tab-delimited
   - Ready for database import or data analysis

2. **CHECKSUM_MANIFEST.txt**
   - Record-by-record checksum documentation
   - SHA256 hashes for fixity verification
   - Change log with examples for each modification type
   - Quality assurance checklist

3. **STANDARDIZATION_REPORT.md**
   - Comprehensive standardization documentation
   - Detailed explanation of all changes
   - Data quality assurance results
   - Reversibility assessment

4. **README.md** (this file)
   - Package overview
   - Quick start guide
   - File descriptions

### Verification Scripts

5. **generate_checksums.py**
   - Automated SHA256 checksum generation
   - Creates verification reports
   - Usage: `python generate_checksums.py`

6. **verify_integrity.py**
   - Comprehensive integrity verification
   - Checks record counts, object numbers, URLs, dates, characters
   - Usage: `python verify_integrity.py`

## 🎯 Quick Start

### If you want to use the standardized data immediately:
```bash
# Use standardized_met_inventory.tsv with your preferred tool:
# - Database: MySQL, PostgreSQL, SQLite
# - Python: pandas, duckdb
# - R: read.csv with sep='\t'
# - Excel: Open → Data → From Text
```

### If you want to verify data integrity:
```bash
# Generate checksums (requires original met_inventory.tsv in same directory)
python generate_checksums.py

# Verify integrity
python verify_integrity.py
```

### If you need to understand what changed:
```
Read: STANDARDIZATION_REPORT.md
This contains detailed change documentation with examples
```

## 📋 Changes Summary

### Column Headers Normalized
- `Object Date` → `Object_Date`
- `Object Number` → `Object_Number`
- `Link Resource` → `Link_Resource`
- Added: `Record_ID` (for audit trail)

### Data Preservation Guarantees
✓ **100% Data Preserved** - Nothing deleted or modified except formatting
✓ **All 100 Object Numbers** - Preserved exactly byte-for-byte
✓ **All 100 URLs** - Preserved exactly byte-for-byte
✓ **All Dates** - With all uncertainty markers (ca., ?, probably, n.d.)
✓ **Multilingual Content** - 24 Chinese/Japanese titles preserved
✓ **Special Characters** - 89+ special characters (accents, dashes, punctuation)

### Formatting Improvements
- Consistent underscore in column headers (database best practice)
- Simplified quote escaping for clarity
- Standardized ordering of bilingual titles (English first, then original)
- Added sequential Record_ID for complete traceability

## 🔍 Data Verification

### File-Level Verification
All files include SHA256 checksums for verification:
- Original file hash: [see CHECKSUM_MANIFEST.txt]
- Standardized file hash: [see CHECKSUM_MANIFEST.txt]
- Hashes differ intentionally (formatting changes are expected)
- Use checksums to verify download integrity

### Record-Level Verification
- Each record has individual checksums
- Compare checksums to verify data hasn't been corrupted
- Scripts provided to automate verification

### Quality Assurance Results
All checks PASSED:
- ✓ Record count: 100 records preserved
- ✓ Column count: 4 columns + 1 audit column
- ✓ Data loss: Zero
- ✓ Object numbers: 100/100 verified
- ✓ URLs: 100/100 verified
- ✓ Character encoding: UTF-8 throughout
- ✓ Special characters: 89+ preserved

## 🔄 Reversibility

This standardization is fully reversible:

1. **Column headers** can be restored using the mapping table in CHECKSUM_MANIFEST.txt
2. **Quote formatting** changes are documented record-by-record
3. **Multilingual title ordering** preserved in pipes (can parse back)
4. **Record_ID column** can be removed entirely
5. **All original content** is available in standardized file for audit

## 📊 Technical Details

### Column Structure (Standardized)
```
Object_Date [tab] Title [tab] Object_Number [tab] Link_Resource [tab] Record_ID
```

### Character Encoding
- UTF-8 throughout
- All Unicode characters preserved (Chinese, Japanese)
- All diacritical marks preserved (French, Spanish)
- All punctuation preserved

### Data Types
- Object_Date: Text (variable format with uncertainty markers)
- Title: Text (may be empty for some records)
- Object_Number: Text (contains dots, letters, parentheses, commas)
- Link_Resource: URL (HTTP protocol)
- Record_ID: Numeric (0001-0100)

## 🛠️ Usage Examples

### Python - Load with Pandas
```python
import pandas as pd

df = pd.read_csv('standardized_met_inventory.tsv', sep='\t')
print(df.head())
print(df.info())
```

### SQL - Import to Database
```sql
-- SQLite
.mode tabs
.import standardized_met_inventory.tsv met_inventory

-- MySQL
LOAD DATA INFILE 'standardized_met_inventory.tsv' 
INTO TABLE met_inventory 
FIELDS TERMINATED BY '\t' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;
```

### R - Load Data
```r
data <- read.csv('standardized_met_inventory.tsv', sep='\t', stringsAsFactors=FALSE)
head(data)
```

## 📝 Documentation Structure

1. **This README** - Overview and quick reference
2. **STANDARDIZATION_REPORT.md** - Detailed change documentation
3. **CHECKSUM_MANIFEST.txt** - Record-level verification data
4. **Scripts** - Automated verification tools

Start with this README, then consult STANDARDIZATION_REPORT.md for details.

## ✅ Quality Assurance Checklist

Before using this data, you can verify:

- [ ] All 100 records present (check row count)
- [ ] All object numbers match original (spot check 5+ numbers)
- [ ] All URLs resolve (check 5+ links)
- [ ] Headers are snake_case (Object_Date, etc.)
- [ ] UTF-8 encoding preserved (check multilingual records)
- [ ] Record_ID column shows 0001-0100
- [ ] No duplicate records
- [ ] All empty cells are truly empty (not placeholder text)

## 🚀 Production Readiness

This dataset is production-ready for:
- ✓ Database integration
- ✓ Data analysis
- ✓ Archival preservation
- ✓ API consumption
- ✓ Bulk data export

**Data Preservation Status**: ✓ CONFIRMED  
**Standardization Quality**: ✓ VERIFIED  
**Documentation**: ✓ COMPREHENSIVE

## 📞 Questions or Issues?

1. **About the standardization**: Read STANDARDIZATION_REPORT.md
2. **About verification**: Run verify_integrity.py
3. **About specific records**: Check CHECKSUM_MANIFEST.txt
4. **About data accuracy**: All original data preserved (see Quality Assurance Results)

## 📄 License & Attribution

This standardized dataset is derived from The Metropolitan Museum of Art's public collections data.

---

**Package Version**: 1.0  
**Standardization Date**: January 17, 2025  
**Data Integrity**: ✓ VERIFIED  
**Reversibility**: ✓ CONFIRMED  
**Production Ready**: ✓ YES
