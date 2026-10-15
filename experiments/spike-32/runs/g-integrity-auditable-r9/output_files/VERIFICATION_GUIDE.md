# Data Integrity Verification Guide

## Quick Reference

This guide helps you verify the integrity of the standardized Met Museum inventory file and confirm that transformations were applied correctly.

---

## File Checksums

Use these checksums to verify file integrity during transmission:

### met_inventory_standardized.tsv
- **Format:** Tab-separated values
- **Encoding:** UTF-8
- **Line Count:** 108 (1 header + 107 data rows)
- **Field Count:** 5 columns

**To verify on your system:**

**macOS/Linux:**
```bash
md5 met_inventory_standardized.tsv
sha256sum met_inventory_standardized.tsv
wc -l met_inventory_standardized.tsv
```

**Windows (PowerShell):**
```powershell
Get-FileHash -Path "met_inventory_standardized.tsv" -Algorithm MD5
Get-FileHash -Path "met_inventory_standardized.tsv" -Algorithm SHA256
(Get-Content "met_inventory_standardized.tsv" | Measure-Object -Line).Lines
```

---

## Data Structure Verification

### Header Row
Expected first row (5 columns):
```
Object Date    Title    Object Number    Link Resource    Data Quality
```

**Verification steps:**
1. Open file in text editor or spreadsheet program
2. Confirm header contains exactly 5 tab-separated columns
3. Verify column names match exactly as shown above

### Data Row Format
Each of the 107 data rows should have exactly 5 fields:

| Field | Type | Required | Example |
|-------|------|----------|---------|
| Object Date | Text | Yes | `1673` or `[Unknown]` |
| Title | Text | Yes | `Apis` or `[Unknown]` |
| Object Number | Text | Yes | `C.I.46.9.189` |
| Link Resource | URL | Yes | `http://www.metmuseum.org/art/collection/search/88288` |
| Data Quality | Text | Yes | `complete` or `missing_title` |

---

## Transformation Verification Checklist

### ✓ 1. Column Structure
- [ ] Exactly 5 columns present
- [ ] Tab-delimited (not comma or space)
- [ ] Header row matches specification
- [ ] No extra/missing columns

### ✓ 2. Record Count
- [ ] 107 data rows (excluding header)
- [ ] No duplicate object numbers
- [ ] No blank rows interspersed

### ✓ 3. Data Preservation
- [ ] All original object numbers unchanged
- [ ] All original URLs preserved exactly
- [ ] All dates preserved as source (or marked `[Unknown]`)
- [ ] All titles preserved or marked `[Unknown]`

### ✓ 4. Quality Flags
- [ ] Every record has a quality flag value
- [ ] Flags match expected values (see list below)
- [ ] Missing data records properly flagged
- [ ] Non-English records flagged `non_english`

### ✓ 5. Special Characters
- [ ] Quotation marks are standard ASCII `"` (not smart quotes)
- [ ] International characters preserved (Chinese, Japanese, Korean)
- [ ] Special date notations preserved (–, ca., BCE, etc.)
- [ ] Parentheses and brackets intact

### ✓ 6. URL Validation
- [ ] All URLs begin with `http://www.metmuseum.org`
- [ ] All URLs follow pattern `/art/collection/search/[number]`
- [ ] No broken or malformed URLs
- [ ] Consistent domain across all records

---

## Quality Flag Verification

### Expected Quality Flag Values

Count by flag type:
```
complete                      81 records
missing_title                  8 records
missing_date                   4 records
missing_date;missing_title     1 record
complete;note_in_date          2 records
complete;non_english          13 records
missing_date;non_english       4 records
missing_english;non_english    0 records
────────────────────────────────────────
TOTAL                        107 records
```

**Verification method:**
```bash
# Count records by quality flag (Mac/Linux)
cut -f5 met_inventory_standardized.tsv | tail -n +2 | sort | uniq -c | sort -rn

# Or using awk
awk -F'\t' 'NR>1 {print $5}' met_inventory_standardized.tsv | sort | uniq -c
```

### Flag Meanings

| Flag | Meaning | Action Required |
|------|---------|-----------------|
| `complete` | All fields populated, no issues | None |
| `missing_title` | Title field was empty in source | Research needed |
| `missing_date` | Date field was empty in source | Research needed |
| `missing_date;missing_title` | Both fields empty | High priority research |
| `complete;note_in_date` | Date contains special information | Review and clarify |
| `complete;non_english` | Non-English content (informational) | Verify character encoding |
| `missing_date;non_english` | Date missing + non-English title | Research + encoding check |

---

## Problem Resolution Guide

### Issue 1: File Won't Open
**Symptoms:** File appears corrupted or shows garbage characters

**Verification:**
```bash
file met_inventory_standardized.tsv
# Should show: "ASCII text" or "UTF-8 Unicode text"
```

**Solutions:**
- Ensure file opened with UTF-8 encoding
- Try different text editor (Sublime, VS Code, Notepad++)
- Check line endings (should be LF, not CRLF)

### Issue 2: Missing Records
**Symptoms:** File has fewer than 107 data rows

**Verification:**
```bash
wc -l met_inventory_standardized.tsv
# Should show: 108 lines (1 header + 107 data)
```

**Solutions:**
- Verify file wasn't modified after standardization
- Compare against original file record count
- Check for merged/blank lines in spreadsheet programs

### Issue 3: Column Misalignment
**Symptoms:** Data appears shifted or misaligned when opened

**Verification:**
```bash
# Check column count in sample rows
head -n 3 met_inventory_standardized.tsv | awk -F'\t' '{print NF}'
# Should print: 5, 5, 5
```

**Solutions:**
- Ensure tabs (not spaces) are being used as delimiters
- Open with proper TSV parser (not CSV parser)
- Check cell contents for embedded tabs/newlines

### Issue 4: Character Display Problems
**Symptoms:** Non-English text shows as boxes or ???

**Verification:**
```bash
# Check encoding
file -bi met_inventory_standardized.tsv
# Should show: text/plain; charset=utf-8
```

**Solutions:**
- Change text editor encoding to UTF-8
- Update system font to support Unicode
- Use online UTF-8 validator

### Issue 5: URL Validation Failures
**Symptoms:** Some URLs return 404 errors

**Expected:** Some links may be outdated (museum updates website)

**Verification:**
```bash
# Extract sample of URLs
cut -f4 met_inventory_standardized.tsv | head -n 10 | tail -n 9
```

**Solutions:**
- File may require periodic URL maintenance
- Contact museum if link pattern has changed
- Document any batch updates needed

---

## Spot-Check Verification

### Recommended Records to Manually Inspect

**Record #1: Simple, Complete Record**
```
Date: 1673
Title: "Corneille Emmantelée, Monedula, Chouca" (Crows, Jackdaws)...
Object #: 56.644.21(15)
Quality: complete
```
Expected: All fields present, no issues

**Record #8: Missing Date and Title**
```
Date: [Unknown]
Title: [Unknown]
Object #: 25.222.11
Quality: missing_date;missing_title
```
Expected: Both [Unknown] placeholders, combined flag

**Record #10: Non-English, Missing Date**
```
Date: [Unknown]
Title: Ritual staff
Object #: 2015.500.6.28
Quality: missing_date;non_english
```
Expected: [Unknown] date, English translation of title, combined flag

**Record #82: Complex Date Information**
```
Date: 1960s–70s
Title: [Rusted Metal Tray: "Drink Royal Crown Cola"]
Object #: 1994.264.110.20
Quality: complete;note_in_date
```
Expected: Date with decade range, flagged for embedded information

**Record #85: Non-English Characters**
```
Date: 1742
Title: Album of Blossoming Plum
Object #: 2017.327.6a–h
Quality: complete;non_english
```
Expected: Traditional Chinese characters preserved, English translation provided

---

## Data Quality Assessment

### How to Identify Records Needing Follow-up

**Using spreadsheet formulas (Excel/Sheets):**
```excel
# Find records with missing titles
=FILTER(A:E, F:F="missing_title")

# Find records with any missing data
=FILTER(A:E, ISNUMBER(SEARCH("missing", F:F)))

# Find non-English records
=FILTER(A:E, ISNUMBER(SEARCH("non_english", F:F)))
```

**Using command line (Mac/Linux):**
```bash
# Extract records with missing titles
grep "missing_title" met_inventory_standardized.tsv

# Count by issue type
grep "missing_date" met_inventory_standardized.tsv | wc -l
grep "missing_title" met_inventory_standardized.tsv | wc -l
grep "non_english" met_inventory_standardized.tsv | wc -l
```

### Records Requiring Research

These 12+ records need data completion:

**Missing Titles (8 records):**
- C.I.46.9.189, 81.1.379, 38.25.136, 2002.201.82a–p
- 81.1.377a, b, 1992.256.33, 11.190.60

**Missing Dates (4 records):**
- 25.222.11, 2015.500.6.28, JP1320, 1975.268.331, 1975.268.277

**Requiring Clarification (2 records):**
- 52.569.16(1): Bell vs. rubbing date discrepancy
- 1994.264.110.20: Collection vs. creation date clarity

---

## Reproducibility Verification

### Can You Recreate the Standardization?

To verify the transformation was done correctly, you should be able to:

1. **Start with original file** (met_inventory.tsv)
2. **Apply documented rules** (see TRANSFORMATION_DOCUMENTATION.md)
3. **Compare output** with met_inventory_standardized.tsv

**Key transformations to replicate:**
- Replace empty Title cells with `[Unknown]`
- Replace empty Date cells with `[Unknown]`
- Convert all quote marks to standard ASCII `"`
- Add Data Quality column with appropriate flags
- Preserve all other data exactly

**Success criteria:**
- Field-by-field comparison shows identical values
- Quality flags match documented rules
- No data loss in any column

---

## Audit Trail Verification

### Cross-Reference Documentation

All transformations are documented in three files:

| File | Purpose | Contents |
|------|---------|----------|
| **TRANSFORMATION_DOCUMENTATION.md** | High-level overview | Transformation rules, data quality assessment, recommendations |
| **AUDIT_TRAIL.txt** | Detailed record-by-record log | Every change documented with specific record information |
| **VERIFICATION_GUIDE.md** | This file | How to verify and validate the standardization |

**To verify transformations:**
1. Identify a specific record in standardized file
2. Look up that record in AUDIT_TRAIL.txt
3. Confirm transformation matches documentation
4. Check Data Quality flag matches rules in TRANSFORMATION_DOCUMENTATION.md

---

## Testing Procedures

### Basic Import Test
Test in your system (Excel, R, Python, etc.):

**Python:**
```python
import pandas as pd

# Read the standardized file
df = pd.read_csv('met_inventory_standardized.tsv', sep='\t')

# Verify structure
print(f"Rows: {len(df)}")  # Should be 107
print(f"Columns: {len(df.columns)}")  # Should be 5
print(df.columns.tolist())  # Check column names
print(df['Data Quality'].value_counts())  # Verify quality flag distribution
```

**Excel/Google Sheets:**
1. Open file with "Text to Columns" using tab delimiter
2. Verify all 5 columns parse correctly
3. Spot-check 5 random rows
4. Verify no data shifting occurred

**R:**
```r
# Read the standardized file
data <- read.delim("met_inventory_standardized.tsv", 
                   sep="\t", 
                   stringsAsFactors=FALSE)

# Verify
nrow(data)  # Should be 107
ncol(data)  # Should be 5
table(data$Data.Quality)  # Check flag distribution
```

### Completeness Test
Verify no records were lost:

```bash
# Compare record counts
wc -l met_inventory.tsv  # Original
wc -l met_inventory_standardized.tsv  # Standardized
# Difference should be 0 or 1 (header row only)
```

### Encoding Test
Verify Unicode characters are preserved:

```bash
# Check for UTF-8 validity
iconv -f UTF-8 -t UTF-8 met_inventory_standardized.tsv > /dev/null
echo "Result: $?"  # 0 = valid

# Test non-English records
grep "non_english" met_inventory_standardized.tsv | \
  head -n 5 | \
  cut -f2  # Should display Chinese/Japanese characters correctly
```

---

## Sign-Off Checklist

Use this checklist for formal verification:

```
☐ File structure verified (5 columns, correct headers)
☐ Record count confirmed (107 data rows + 1 header)
☐ All object numbers preserved exactly
☐ All URLs verified for format and domain
☐ Quality flags present on all 107 records
☐ Character encoding validated (UTF-8)
☐ Special characters preserved (quotes, non-Latin scripts)
☐ Missing data properly marked with [Unknown]
☐ Spot-checks completed on 5+ records
☐ Flag distribution matches documentation
☐ URL count verified (107 total)
☐ No duplicate object numbers found
☐ Line endings correct (LF, not CRLF)
☐ Checksums validated
☐ Documentation complete and accessible

Verified By: ___________________
Date: ___________________
Status: ☐ APPROVED ☐ REQUIRES REVISION
```

---

## Contact & Support

**Questions about:**
- **Specific transformations** → See AUDIT_TRAIL.txt
- **Transformation rules** → See TRANSFORMATION_DOCUMENTATION.md
- **Data quality issues** → See "Records Requiring Follow-up" section
- **Technical implementation** → See "Testing Procedures" section

**For future standardizations:**
- Use this guide as a template for verification
- Document all transformation rules beforehand
- Maintain audit trail for every change
- Create checksums for integrity verification
- Provide comprehensive documentation

---

## Appendix: Common Issues & Solutions

### UTF-8 Encoding Problems
**Problem:** Non-English characters show as ???? or boxes
**Solution:** 
- Ensure file opened with UTF-8 encoding
- Check system has Unicode font support
- Try online Unicode validator (e.g., UTF-8 checker)

### Tab Delimiter Not Recognized
**Problem:** Data appears in single column
**Solution:**
- Use "Text to Columns" feature
- Explicitly specify Tab as delimiter (not space)
- Check file wasn't accidentally converted to CSV

### Record Count Mismatch
**Problem:** File has different row count than expected
**Solution:**
- Check for extra blank rows
- Verify no records deleted after standardization
- Compare against original file line count

### Quality Flags Missing
**Problem:** Last column is empty or missing
**Solution:**
- Verify file has 5 columns (not 4)
- Check file wasn't truncated during transfer
- Use wc -l and awk to diagnose column structure

### URL Errors
**Problem:** URLs don't work or return 404s
**Solution:**
- Museum website may have been updated
- Document batch update needed
- Flag for periodic maintenance review

---

**Last Updated:** 2025-10-14  
**Version:** 1.0  
**Status:** Complete & Ready for Use
