# Met Museum Inventory TSV Standardization Kit

Complete toolkit for standardizing and verifying the Met Museum inventory TSV file with checksum preservation.

## Quick Start

### 1. Run the Standardization Script

```bash
python3 standardize_met_inventory.py met_inventory.tsv met_inventory_standardized.tsv
```

### 2. What Gets Created

The script generates:
- **met_inventory_standardized.tsv** - Standardized data file
- **met_inventory_standardized_CHECKSUMS.txt** - Checksum verification file

### 3. Verify Checksums

```bash
# Display checksums
cat met_inventory_standardized_CHECKSUMS.txt

# Verify the file hasn't been corrupted
sha256sum met_inventory_standardized.tsv
# Compare output with value in CHECKSUMS.txt
```

## What Gets Standardized

✓ **Line Endings:** CRLF → LF normalization  
✓ **Whitespace:** Trailing spaces removed  
✓ **HTML Entities:** &lt;i&gt; → plain text  
✓ **Consistency:** 4-column structure verified  
✓ **Encoding:** UTF-8 preserved (diacritics, CJK characters)  

## File Information

| Item | Value |
|------|-------|
| **Total Records** | 488 (1 header + 487 data) |
| **Columns** | 4: Object Date, Title, Object Number, Link Resource |
| **Encoding** | UTF-8 |
| **Format** | Tab-separated values |

## Files Included

| File | Purpose |
|------|---------|
| `standardize_met_inventory.py` | Main standardization script |
| `TSV_STANDARDIZATION_GUIDE.md` | Comprehensive documentation |
| `README.md` | This file |
| `QUICK_REFERENCE.txt` | Command cheat sheet |

## Checksum Verification

### Why Checksums Matter

Checksums are digital fingerprints that prove a file hasn't been corrupted or modified.

### How to Verify

**Linux/Mac:**
```bash
sha256sum met_inventory_standardized.tsv
md5sum met_inventory_standardized.tsv
```

**Windows PowerShell:**
```powershell
Get-FileHash met_inventory_standardized.tsv -Algorithm SHA256
Get-FileHash met_inventory_standardized.tsv -Algorithm MD5
```

**macOS:**
```bash
shasum -a 256 met_inventory_standardized.tsv
md5 met_inventory_standardized.tsv
```

## Data Quality Notes

- **12 records** have empty Title fields (intentional - untitled items)
- **All 487 data rows** have valid Object Numbers
- **All records** include complete Met Museum collection URLs
- **Special characters** properly encoded (diacritics, Chinese, Japanese)

## Troubleshooting

**Script won't run?**
- Ensure Python 3.6+ is installed: `python3 --version`
- Give execute permission: `chmod +x standardize_met_inventory.py`

**Wrong checksums?**
- File may have been modified. Re-run script to generate fresh checksums.
- Ensure you're comparing the right files.

**Encoding issues?**
- Set terminal to UTF-8 encoding
- Ensure text editor uses UTF-8

## Common Commands

### Record Count
```bash
wc -l met_inventory_standardized.tsv
# Should output 488 (1 header + 487 data)
```

### View Sample Records
```bash
head -5 met_inventory_standardized.tsv
tail -5 met_inventory_standardized.tsv
```

### Column Count
```bash
head -1 met_inventory_standardized.tsv | tr '\t' '\n' | wc -l
# Should output 4
```

### Compare with Original
```bash
diff met_inventory.tsv met_inventory_standardized.tsv
```

## For More Information

See **TSV_STANDARDIZATION_GUIDE.md** for:
- Detailed standardization procedures
- File validation methods
- Long-term archival best practices
- Comprehensive troubleshooting
- Data quality analysis

## Summary of Changes

When you run the standardization:

1. **Source file unchanged** - Original `met_inventory.tsv` remains intact
2. **New standardized file** - `met_inventory_standardized.tsv` created
3. **Checksums generated** - Both MD5 and SHA256 provided in `_CHECKSUMS.txt` file
4. **Statistics recorded** - Processing details logged in checksum file

## Success Indicators

After running the script, you should see:
- ✓ 488 rows processed
- ✓ 0 issues detected
- ✓ Line count match verified
- ✓ Checksums calculated and saved

## Next Steps

1. **Review** the standardized file: `less met_inventory_standardized.tsv`
2. **Verify** checksums: `cat met_inventory_standardized_CHECKSUMS.txt`
3. **Compare** changes: `diff met_inventory.tsv met_inventory_standardized.tsv`
4. **Archive** both files with checksums for long-term preservation

---

**Version:** 1.0  
**Last Updated:** 2024  
**Status:** Production Ready
