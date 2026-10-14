# Met Museum Inventory File - Integrity Verification

## File Checksums

**Standardized File:** `met_inventory.tsv`
- **SHA-256:** `32b1561a5ab6e54aeb51965173ce40686bab08cfdf88961221031c43cfea1a30`
- **File Size:** 56,879 bytes
- **Generated:** 2025
- **Format:** Tab-separated values (TSV)
- **Encoding:** UTF-8

## Verification Instructions

To verify file integrity:

```bash
# Using sha256sum (Linux/macOS):
sha256sum -c met_inventory.tsv.sha256

# Using shasum (alternative):
shasum -a 256 -c met_inventory.tsv.sha256

# Manual verification on macOS:
shasum -a 256 met_inventory.tsv
```

Expected output: `met_inventory.tsv: OK`

## Standardization Changes

The TSV file has been standardized to ensure:

1. **Consistent Tab Delimiters:** All field separators are proper tabs (not spaces)
2. **UTF-8 Encoding:** Full character set support for international content (Chinese, Japanese, Korean, Arabic scripts)
3. **No Trailing Spaces:** Clean row endings
4. **Proper Quoting:** Title fields with special characters properly escaped for TSV compliance
5. **Header Row:** Consistent column headers (Object Date, Title, Object Number, Link Resource)
6. **Data Integrity:** 100 records preserved without alteration to content

## File Structure

| Column | Description | Data Type | Example |
|--------|-------------|-----------|---------|
| Object Date | When the artifact was created/dated | String | "1673", "ca. 1479–1458 B.C." |
| Title | Name or description of the object | String | "Earrings", "Bowl" |
| Object Number | Museum catalog/accession number | String | "2017.113.379", "C.I.46.9.189" |
| Link Resource | URL to museum collection record | URL | "http://www.metmuseum.org/art/..." |

## Data Quality Notes

- 100 total records
- 4 columns
- Language support: English, Chinese, Japanese, Korean, French, German, Italian, Spanish
- 8 records with missing titles (empty Title field - these are intentional blank values)
- All URLs are valid Met Museum collection links
- Object numbers follow museum's hierarchical cataloging system

## Preservation Recommendations

1. Store checksums in a separate, read-only location
2. Recalculate checksums periodically to detect any file corruption
3. Maintain this checksum file alongside backups
4. Use version control to track checksum history
5. Document the standardization date and methodology

