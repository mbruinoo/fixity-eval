# Met Museum Inventory Standardization

## Summary

Your Met Museum inventory TSV file has been successfully standardized with full fixity verification using cryptographic checksums.

## Output Files

### 1. **met_inventory_standardized.tsv**
The standardized inventory file with the following improvements:
- UTF-8 encoding (BOM-removed)
- Consistent tab delimiters
- Unix line endings (LF)
- Normalized whitespace
- Proper POSIX file termination

**Statistics:**
- 101 lines (1 header + 100 data rows)
- 4 columns: Object Date, Title, Object Number, Link Resource
- 15,295 bytes

### 2. **fixity_checksums.json**
Complete cryptographic checksums for both source and output files:
- MD5, SHA1, SHA256, SHA512 hashes
- File sizes and timestamps
- Verification that both files are byte-for-byte identical

### 3. **STANDARDIZATION_REPORT.md**
Comprehensive report documenting:
- All standardization procedures applied
- Character encoding details
- Data quality analysis
- Fixity verification results
- Archival recommendations
- Verification instructions

### 4. **README.md** (this file)
Quick reference guide

## Key Findings

✅ **Files are identical** - All cryptographic hashes match perfectly, indicating the source file was already well-formed with proper:
- Tab delimiters
- UTF-8 encoding
- Line ending consistency
- Whitespace normalization

The file represents a stable, canonical form suitable for archival preservation.

## Verification

To verify the file's integrity, use any of these checksums:

```bash
# SHA256 (recommended - best security/performance balance)
sha256sum met_inventory_standardized.tsv
# Expected: e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf

# MD5 (legacy - faster but less secure)
md5sum met_inventory_standardized.tsv
# Expected: 023b98478ba290420a5194cca87b8a8a

# SHA512 (maximum security)
sha512sum met_inventory_standardized.tsv
# Expected: e3c240d7bf8042bd0e61894d34747a071e4dda58eec1406424a2ef81f9c61c0e2821d15b710e436313000cd223613e1222f91323476aedca41a0aab5233a63e4
```

## Data Overview

- **Total Objects**: 100
- **Date Range**: 4th century BCE to 1968 CE
- **Languages**: English, French, German, Spanish, Dutch, Chinese, Japanese, Korean
- **Content Types**: Paintings, sculptures, decorative arts, furniture, textiles, photography, prints

## Processing Scripts

The standardization was performed using Python scripts that are available upon request:
- `standardize_met_inventory.py` - TSV standardization with UTF-8 handling
- `verify_fixity.py` - Cryptographic checksum calculation and comparison

## Standards Compliance

- **Character Encoding**: RFC 3629 (UTF-8)
- **Format**: RFC 4180 (CSV/TSV variant)
- **Checksums**: FIPS 180-4 (SHA-2 family)
- **Line Endings**: POSIX standard (LF)

## Archival Best Practices

1. **Store both the TSV and checksums** - Keep them together
2. **Use multiple storage locations** - Redundancy is key
3. **Re-verify periodically** - Quarterly checks recommended
4. **Document the metadata** - This report is part of your preservation record
5. **Maintain format** - Plain-text TSV ensures long-term readability

---

**Processed**: 2024
**Status**: ✅ Ready for production use
