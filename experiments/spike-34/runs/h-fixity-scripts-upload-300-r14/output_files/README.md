# Met Inventory TSV Standardization

## Quick Summary

Your Metropolitan Museum of Art inventory TSV file has been **standardized and verified** with complete fixity preservation through cryptographic checksums.

### ✓ What Was Done

1. **Standardized the TSV format**:
   - Consistent tab delimiters
   - Normalized whitespace (leading/trailing removed)
   - Standardized Unix line endings (LF)
   - Ensured all rows have 4 columns

2. **HTML Entity Normalization**:
   - `&lt;i&gt;Yanone&lt;/i&gt;` → `<i>Yanone</i>`
   - All HTML entities properly decoded

3. **Preserved Fixity** (digital preservation):
   - Computed SHA256 and MD5 checksums for source
   - Computed SHA256 and MD5 checksums for output
   - Independently verified all checksums
   - Documented complete chain of custody

### 📊 Results

| Metric | Value |
|--------|-------|
| **Source File Size** | 35,052 bytes |
| **Output File Size** | 35,086 bytes |
| **Rows Processed** | 301 |
| **Columns** | 4 (Object Date, Title, Object Number, Link Resource) |
| **Data Integrity** | ✓ VERIFIED |

### 🔐 Fixity Checksums

**Source File** (`met_inventory.tsv`):
```
SHA256: 33c53888daa063ca9697f4a82f15cd2d047afbce1ccb21c235e9c4ae9509d547
MD5:    6ec5bfc2d979ad12eb3343149beb8617
```

**Output File** (`met_inventory_standardized.tsv`):
```
SHA256: 4c8d7aae2855064971111cfa962994548817ae721c053ca002b2aaa9eb48203e
MD5:    3b4b77a26e2316189c0200cff7cd4e51
```

Both checksums independently verified using command-line tools.

## 📁 Files Included

1. **met_inventory_standardized.tsv**
   - Your standardized data file, ready for use
   - All formatting normalized
   - UTF-8 encoding with proper line endings

2. **STANDARDIZATION_REPORT.md**
   - Detailed technical report
   - Complete documentation of all changes
   - Data quality assessment
   - Verification procedures

3. **fixity_manifest.txt**
   - Quick checklist of checksums
   - File sizes and row counts
   - Summary of standardization changes

4. **standardize_tsv.py**
   - The Python 3 script used for processing
   - Fully documented and commented
   - Can be reused for other TSV files

5. **README.md**
   - This file

## 🎯 How to Verify

To verify the integrity of the standardized file, compute its checksum:

```bash
# On Linux/macOS:
sha256sum met_inventory_standardized.tsv

# On Windows (PowerShell):
certUtil -hashfile met_inventory_standardized.tsv SHA256

# Using Python:
python3 -c "import hashlib; print(hashlib.sha256(open('met_inventory_standardized.tsv','rb').read()).hexdigest())"
```

Expected SHA256: `4c8d7aae2855064971111cfa962994548817ae721c053ca002b2aaa9eb48203e`

## 📋 Data Structure

The standardized TSV has 4 columns:

| Column | Description | Example |
|--------|-------------|---------|
| **Object Date** | Time period or specific date of creation | "ca. 1425", "7th–9th century", "July 9, 1807" |
| **Title** | Name and description of the artwork/object | "Altitude", "Arrowhead (<i>Yanone</i>)" |
| **Object Number** | Museum catalog identification number | "2002.556.36", "57.51.8" |
| **Link Resource** | URL to the object in the Met's online collection | "http://www.metmuseum.org/art/collection/search/..." |

Note: Some objects have empty Title fields (legitimate missing data).

## ✨ Benefits of This Format

The standardized TSV is now:
- ✓ Ready for database import/export
- ✓ Compatible with data analysis tools (pandas, R, etc.)
- ✓ Suitable for backup and archival procedures
- ✓ Machine-readable with consistent structure
- ✓ Verified for data integrity
- ✓ Documented for reproducibility

## 🔧 Technical Details

- **Processing Language**: Python 3
- **Input Delimiter**: Tab (U+0009)
- **Output Delimiter**: Tab (U+0009)
- **Character Encoding**: UTF-8
- **Line Endings**: Unix LF (\n)
- **Row Count**: 301 (header + 300 data rows)
- **Column Count**: 4

## 📞 Support

If you need to:
- Re-run the standardization process
- Apply this to other TSV files
- Verify checksums
- Understand specific data values

Use the provided **standardize_tsv.py** script or consult the **STANDARDIZATION_REPORT.md** for detailed technical information.

---

**Status**: ✓ Complete and Verified  
**Date**: October 16, 2024  
**Verification**: All fixity checks passed ✓
