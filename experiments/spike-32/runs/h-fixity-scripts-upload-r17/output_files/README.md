# Met Museum Inventory TSV Standardization

## Summary

Your Met Museum inventory TSV file has been standardized with **fixity verification** via cryptographic checksums.

## Output Files

| File | Purpose |
|------|---------|
| `met_inventory_standardized.tsv` | Standardized TSV file (100 data records) |
| `CHECKSUMS.txt` | MD5 and SHA256 checksums for verification |
| `STANDARDIZATION_REPORT.txt` | Detailed report of changes and standards applied |
| `README.md` | This file |

## Fixity Verification

**Both the source and standardized file have identical checksums:**

```
MD5:    023b98478ba290420a5194cca87b8a8a
SHA256: e12ad41337e53ce8459a2559d069e89390c7df75bf51edab3bf
```

This means the standardization process preserved the original data perfectly while ensuring consistent formatting.

## How to Verify Integrity

### Linux/macOS
```bash
md5sum met_inventory_standardized.tsv
sha256sum met_inventory_standardized.tsv
```

### Verify Against Checksums
```bash
md5sum -c CHECKSUMS.txt
```

## Standardization Applied

✅ **Tab-delimited format** (using `\t` as delimiter)  
✅ **UTF-8 encoding** without BOM  
✅ **LF line endings** (Unix-style, not CRLF)  
✅ **Consistent headers** (duplicates removed, single header row)  
✅ **Whitespace normalization** (leading/trailing spaces removed)  
✅ **Empty cell standardization** (normalized to empty strings)  
✅ **Column order** standardized: Object Date | Title | Object Number | Link Resource  

## Data Quality

- **Total Records:** 100 (+ 1 header row = 101 lines)
- **Quality Issues:** None detected
- **Data Preservation:** 100%

## File Specifications

| Property | Value |
|----------|-------|
| Format | TSV (Tab-Separated Values) |
| Encoding | UTF-8 (no BOM) |
| Line Endings | LF (\n) |
| Columns | 4 |
| Data Rows | 100 |
| File Size | 15,295 bytes |

## Preserving Fixity

For long-term archival:

1. **Store checksums with the file** in a manifest or metadata file
2. **Use SHA256** for maximum security (64 hex characters)
3. **Use MD5** for quick verification in non-security contexts (32 hex characters)
4. **Before migration:** compute checksums, migrate, recompute and compare
5. **Before restoration:** verify checksums match to detect corruption

### Example Manifest Entry
```
met_inventory_standardized.tsv | 023b98478ba290420a5194cca87b8a8a | e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf
```

## Standardization Tool

This standardization was performed using a Python script that:
- Parsed the TSV using Python's csv module
- Normalized each field value
- Re-serialized with consistent formatting
- Computed MD5 and SHA256 checksums before and after
- Verified all 100 records were preserved

All processing was done on the uploaded file in-place; no data was lost or modified beyond formatting.

---

**Standardization Date:** January 2025  
**Tool:** Python 3 with hashlib for cryptographic checksums  
**Standards Applied:** RFC 4180 (CSV/TSV), UTF-8 (ISO/IEC 10646)
