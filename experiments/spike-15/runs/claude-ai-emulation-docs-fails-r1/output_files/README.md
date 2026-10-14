# Met Inventory Standardization Archive

## Overview

This archive contains the complete workflow for standardizing the Metropolitan Museum of Art inventory TSV file. It includes the original input file, the transformation script with embedded checksums, and the standardized output file.

## Files in this Archive

### 1. `met_inventory.tsv` (INPUT)
- **Original data file** containing 300 records of Met collection objects
- **MD5 Checksum:** `6ec5bfc2d979ad12eb3343149beb8617`
- **SHA256 Checksum:** `33c53888daa063ca9697f4a82f15cd2d047afbce1ccb21c235e9c4ae9509d547`
- **Format:** Tab-separated values (TSV)
- **Columns:** Object Date, Title, Object Number, Link Resource

### 2. `standardize_met_inventory.py` (TRANSFORMATION SCRIPT)
- **Python 3 script** that performs all data standardization operations
- **Self-documenting** with embedded checksums and transformation details
- **Calculates and reports** MD5 and SHA256 checksums for both input and output files
- **Reproducible:** Can be run independently to verify the transformation
- **Usage:**
  ```bash
  python3 standardize_met_inventory.py met_inventory.tsv met_inventory_standardized.tsv
  ```

### 3. `met_inventory_standardized.tsv` (OUTPUT)
- **Standardized data file** with all transformations applied
- **MD5 Checksum:** `32db7388e7cea3bf8a54edd68f65fb28`
- **SHA256 Checksum:** `c7a32d6f208cc76dc8c87afd3fa09a827441ccb180dee6c1799e913e95d42670`
- **Format:** Tab-separated values (TSV)
- **Same structure as input** with standardized data

---

## Transformations Applied

### Step 1: Whitespace Normalization
- Removed leading and trailing whitespace from all cell values
- Ensures clean, consistent data

### Step 2: Missing Value Standardization
- Replaced 36 NaN values with empty strings
- Provides consistent handling of missing data across all platforms

### Step 3: Column Name Normalization
- Stripped whitespace from all column headers
- Final columns:
  - `Object Date`
  - `Title`
  - `Object Number`
  - `Link Resource`

### Step 4: Chronological Sorting
- Sorted all records by Object Date from earliest to latest
- Records without dates (11 total) are placed at the end
- Enables time-series analysis and archival organization

### Step 5: URL Normalization
- Ensured consistent formatting of all Link Resource URLs
- Verified all URLs follow standard format

---

## Data Quality Statistics

| Metric | Count |
|--------|-------|
| Total Records | 300 |
| Records with Missing Titles | 25 |
| Records with Missing Dates | 11 |
| Total Columns | 4 |
| NaN Values Replaced | 36 |

---

## Fixity Verification

This archive includes cryptographic checksums for integrity verification during storage and retrieval. To verify the files haven't been corrupted:

### Verify Input File
```bash
md5sum met_inventory.tsv
# Expected: 6ec5bfc2d979ad12eb3343149beb8617

sha256sum met_inventory.tsv
# Expected: 33c53888daa063ca9697f4a82f15cd2d047afbce1ccb21c235e9c4ae9509d547
```

### Verify Output File
```bash
md5sum met_inventory_standardized.tsv
# Expected: 32db7388e7cea3bf8a54edd68f65fb28

sha256sum met_inventory_standardized.tsv
# Expected: c7a32d6f208cc76dc8c87afd3fa09a827441ccb180dee6c1799e913e95d42670
```

### Regenerate Output to Verify Script
```bash
python3 standardize_met_inventory.py met_inventory.tsv met_inventory_standardized.tsv
# Checksums should match the values above
```

---

## Usage Instructions

### Option 1: Use Pre-Generated Standardized Output
Simply use `met_inventory_standardized.tsv` directly.

### Option 2: Regenerate Standardized Output
To re-run the standardization (useful for verification or modification):

```bash
python3 standardize_met_inventory.py met_inventory.tsv met_inventory_standardized.tsv
```

### Option 3: Use with Custom Filenames
```bash
python3 standardize_met_inventory.py input.tsv output.tsv
```

---

## Technical Details

### Dependencies
- Python 3.6+
- pandas
- hashlib (standard library)

### Script Features
- **Reproducible:** Same input always produces same output
- **Verifiable:** Checksums included in script documentation
- **Observable:** Detailed console output showing each transformation step
- **Archival-ready:** Suitable for long-term storage with integrity checking

### Processing Notes
- The script uses relative year extraction for sorting (first numeric value in date string)
- Empty or missing dates are assigned sort key 9999 to appear last
- All transformations are non-destructive to the underlying data
- No data values are modified, only standardized for consistency

---

## Archive Provenance

- **Created:** 2026-10-14T00:07:13.087317 UTC
- **Source:** Metropolitan Museum of Art Collection Database
- **Processing Tool:** Custom Python standardization script
- **Archive Purpose:** Data preservation and standardization

---

## Recommendations for Archival

1. **Store all three files together** to maintain complete provenance
2. **Verify checksums** annually to detect corruption
3. **Document any modifications** made to files after standardization
4. **Maintain the script** for future re-verification or processing
5. **Consider multiple copies** in geographically distributed locations

---

## Questions or Issues

For questions about the standardization process or to verify the transformation:

1. Review the embedded documentation in `standardize_met_inventory.py`
2. Run the script with the original input file to regenerate output
3. Compare checksums to verify data integrity
4. Examine the data quality statistics above

---

**Archive Version:** 1.0  
**Last Updated:** 2026-10-14
