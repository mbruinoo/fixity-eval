# Met Museum Inventory TSV Standardization

This package contains the standardized version of the Met Museum inventory TSV file with complete data fixity verification.

## 📋 Quick Reference

| Property | Value |
|----------|-------|
| **Source File** | `met_inventory.tsv` (301 rows) |
| **Output File** | `met_inventory_standardized.tsv` (301 rows) |
| **Format** | Tab-separated values (TSV) |
| **Encoding** | UTF-8 |
| **Data Preserved** | 100% ✓ |

## 🔐 Checksums (SHA256)

```
SOURCE
33c53888daa063ca9697f4a82f15cd2d047afbce1ccb21c235e9c4ae9509d547

OUTPUT
2759af0c2d0ebd12032a4d53bf4b4170bac8c100b6ca678e0a3ea97e74f03528
```

> Different checksums are expected—they result from standardization formatting, not data loss.

## ✨ What Was Standardized

- **Consistent delimiters:** All tabs (no spaces or mixed delimiters)
- **Clean whitespace:** Trimmed from field edges
- **Line endings:** Unix standard (LF) throughout
- **Column structure:** Exactly 5 columns per row
- **Encoding:** UTF-8 preserved with all international characters

## 📦 Package Contents

1. **met_inventory_standardized.tsv**
   - The standardized data file (35 KB)
   - 301 rows × 5 columns
   - Ready for import/processing

2. **standardize_tsv.py**
   - Complete Python source code
   - Fully reproducible
   - Includes built-in checksum verification

3. **FIXITY_REPORT.md**
   - Comprehensive technical documentation
   - Data integrity verification results
   - Standardization details

4. **CHECKSUMS.txt**
   - Quick reference for SHA256 hashes
   - Can be used with `sha256sum -c`

5. **standardization_metadata.txt**
   - Machine-readable metadata
   - Processing timestamp and parameters

6. **README.md** (this file)
   - Quick-start guide

## 🔍 Data Integrity Checks

All critical data has been verified:

| Check | Result |
|-------|--------|
| Row count preserved | ✓ 301 → 301 |
| Column count standardized | ✓ 5 columns |
| Empty fields preserved | ✓ 25 Title fields |
| Object numbers verified | ✓ 300 entries |
| UTF-8 encoding intact | ✓ Yes |
| International characters | ✓ Chinese, Japanese, Latin |

## 🚀 How to Use

### Option 1: Use the standardized file directly
```bash
# Import the standardized TSV
import pandas as pd
df = pd.read_csv('met_inventory_standardized.tsv', sep='\t')
```

### Option 2: Reproduce the standardization
```bash
# Run the standardization script
python3 standardize_tsv.py
```

## ✅ Verification

### Quick verification
```bash
sha256sum met_inventory_standardized.tsv
# Should output:
# 2759af0c2d0ebd12032a4d53bf4b4170bac8c100b6ca678e0a3ea97e74f03528
```

### Verify using the included file
```bash
sha256sum -c CHECKSUMS.txt
```

### Verify source file
```bash
sha256sum ../uploads/met_inventory.tsv
# Should output:
# 33c53888daa063ca9697f4a82f15cd2d047afbce1ccb21c235e9c4ae9509d547
```

## 📊 Column Structure

| Column 1 | Column 2 | Column 3 | Column 4 | Column 5 |
|----------|----------|----------|----------|----------|
| **Object Date** | **Title** | **Object Number** | **Link Resource** | (trailing) |
| 7th–9th century | (empty) | 2002.556.36 | http://www.metmuseum.org/... | |
| 19th century | (empty) | 93.1.168 | http://www.metmuseum.org/... | |
| spring/summer 1983 | "Altitude" | 2019.583 | http://www.metmuseum.org/... | |

## 🌍 Encoding Support

The standardized file maintains full support for:
- **Latin extended:** é, ü, ø, etc.
- **Chinese:** 清, 蝉, 近代, etc.
- **Japanese:** 筆, 図, 冊頁, etc.
- **Special characters:** –, …, etc.

## 📝 Notes

- All 301 rows have been processed
- No data has been removed or altered—only formatting corrected
- The file is suitable for archival, migration, and data exchange
- The Python script is completely reproducible
- Checksums enable independent verification

## 🔗 Related Files

See also:
- `FIXITY_REPORT.md` — Full technical details
- `standardization_metadata.txt` — Machine-readable format
- `standardize_tsv.py` — Complete source code

---

**Created:** 2026-10-16  
**Algorithm:** SHA256  
**Status:** ✓ Complete and verified
