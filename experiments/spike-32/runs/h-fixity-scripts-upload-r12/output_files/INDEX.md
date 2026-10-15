# Met Museum TSV Standardization - Complete Package

## Quick Summary

✅ **Status**: COMPLETE AND VERIFIED  
📊 **Rows Processed**: 100 museum records  
🔐 **Data Integrity**: Verified with SHA256 & MD5 checksums  
📋 **Format**: Tab-Separated Values (TSV) with UTF-8 encoding  

---

## Deliverables

### 1. Standardized Data
- **`met_inventory_standardized.tsv`** (15 KB)
  - Your standardized, cleaned dataset
  - 4 columns: Object Date, Title, Object Number, Link Resource
  - 100 data rows + 1 header row
  - UTF-8 encoding, LF line endings
  - Ready for import into any database or spreadsheet tool

### 2. Integrity Verification

#### `MANIFEST.txt` (966 bytes)
Quick reference for checksums:
- Source file SHA256 & MD5
- Output file SHA256 & MD5
- Verification commands

#### `standardization_report.txt` (1.2 KB)
Detailed standardization report including:
- Source and output checksums
- Standardization changes applied
- Statistics (row count, file sizes)
- Integrity verification notes

#### `VERIFICATION_REPORT.txt` (2.4 KB)
Comprehensive verification report with:
- Complete file analysis
- Structure verification checklist
- Integrity checks
- Usage recommendations for different tools

### 3. Documentation

#### `README.md` (3.6 KB)
Complete guide including:
- Overview and file descriptions
- Checksum reference
- Standardization changes applied
- Data characteristics
- Verification instructions
- Usage examples

### 4. Scripts & Tools

#### `standardize_tsv.py` (4.2 KB)
Python standardization script:
- Reads TSV with tab delimiters
- Normalizes whitespace
- Standardizes encoding and line endings
- Calculates checksums
- Reproducible process

#### `run_standardization.sh` (2.6 KB)
Bash wrapper script:
- Orchestrates the complete workflow
- Calculates source/output checksums
- Generates manifest and reports
- Can be re-run to verify file integrity

---

## Checksum Reference

### Source File
```
SHA256: 141173c9a3c70fd28bbac44c555894ab7886278cc7890cb57663f569b1a3d75b
MD5:    78e18ae6b0f19cee4be567423610a4ce
Size:   15,284 bytes
```

### Standardized Output
```
SHA256: e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf
MD5:    023b98478ba290420a5194cca87b8a8a
Size:   15,295 bytes
```

---

## How to Verify File Integrity

The checksums allow you to verify that the file hasn't been corrupted or tampered with.

### On macOS/Linux:
```bash
# Verify SHA256
sha256sum met_inventory_standardized.tsv
# Should output: e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf

# Or with shasum
shasum -a 256 met_inventory_standardized.tsv

# Verify MD5
md5sum met_inventory_standardized.tsv
# Should output: 023b98478ba290420a5194cca87b8a8a
```

### On Windows (PowerShell):
```powershell
# SHA256
certutil -hashfile met_inventory_standardized.tsv SHA256

# MD5
certutil -hashfile met_inventory_standardized.tsv MD5
```

---

## Data Overview

### File Structure
- **Format**: Tab-separated values
- **Encoding**: UTF-8 (no BOM)
- **Line Endings**: LF (Unix standard)
- **Columns**: 4 (fixed structure)

### Column Descriptions
1. **Object Date**: Temporal attribution (e.g., "19th century", "1673")
2. **Title**: Object name and description
3. **Object Number**: Unique catalog identifier
4. **Link Resource**: Direct URL to museum collection page

### Data Characteristics
- **Total Records**: 100
- **Time Period**: Late 4th century BCE to early 20th century
- **Languages**: English, French, Italian, Chinese, Japanese, Korean
- **Object Types**: Diverse (paintings, sculpture, furniture, textiles, manuscripts, decorative arts, photography)

---

## Usage Examples

### Import into Excel
1. Open Excel
2. File → Open
3. Select `met_inventory_standardized.tsv`
4. Choose UTF-8 encoding
5. Select "Tab" as delimiter

### Import into SQL Database
```sql
LOAD DATA LOCAL INFILE 'met_inventory_standardized.tsv'
INTO TABLE museum_inventory
FIELDS TERMINATED BY '\t'
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;
```

### Command-line Processing
```bash
# Extract just object numbers and titles
cut -f2,3 met_inventory_standardized.tsv

# Count records (excluding header)
wc -l met_inventory_standardized.tsv

# Search for specific entries
grep "19th century" met_inventory_standardized.tsv

# Convert to CSV format
cat met_inventory_standardized.tsv | sed 's/\t/,/g' > inventory.csv
```

### Python/Pandas
```python
import pandas as pd

# Read the TSV
df = pd.read_csv('met_inventory_standardized.tsv', sep='\t')

# Display info
print(df.head())
print(df.info())
print(f"Total records: {len(df)}")
```

---

## Standardization Details

### What Was Changed
✅ Line endings normalized to LF (Unix)  
✅ Whitespace trimmed from field edges  
✅ Encoding standardized to UTF-8 without BOM  
✅ Tab delimiters enforced consistently  
✅ Quote handling standardized  

### What Was Preserved
✅ All data content  
✅ Special characters (en-dashes, accents, etc.)  
✅ Multilingual text (Chinese, Japanese, Korean)  
✅ Empty fields (where applicable)  
✅ Column structure  

---

## File Quality Certification

| Aspect | Status |
|--------|--------|
| **Encoding** | ✅ UTF-8 (no BOM) |
| **Line Endings** | ✅ LF (POSIX) |
| **Delimiters** | ✅ Tab (consistent) |
| **Whitespace** | ✅ Normalized |
| **Data Integrity** | ✅ 100% preserved |
| **Character Support** | ✅ Unicode full support |
| **Checksums** | ✅ SHA256 & MD5 verified |

---

## Getting Help

### Verification
- See `MANIFEST.txt` for quick checksum verification
- See `VERIFICATION_REPORT.txt` for detailed checks
- Run `bash run_standardization.sh` to re-verify

### Usage
- See `README.md` for comprehensive documentation
- See specific usage examples above
- Test with `head -20 met_inventory_standardized.tsv`

### Reproducibility
The scripts are self-contained and reproducible:
```bash
# Re-run standardization (if needed)
python3 standardize_tsv.py

# Or use the complete workflow
bash run_standardization.sh
```

---

**Package Generated**: 2026-10-15  
**Status**: Ready for production use  
**Verification**: Complete ✅
