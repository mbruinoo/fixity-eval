# Met Inventory TSV Standardization Report

## Issues Identified in Source File

### 1. **Inconsistent Column Headers**
- Current: "Object Date", "Title", "Object Number", "Link Resource"
- Problem: No leading tab on first row; inconsistent capitalization

### 2. **Missing Values**
- Multiple rows have empty "Title" column
- Creates ambiguity in tab-delimited parsing

### 3. **Malformed Object Numbers**
- Mixed formats: `91.1.396`, `1972.45.1`, `21.175.224a, b`, `36.120.598a, b`
- Some use commas and spaces inconsistently
- Sub-component notation needs standardization

### 4. **Irregular Date Formats**
- `19th century`, `4th–3rd century BCE`, `ca. 1918 (?)`, `1949, printed ca. 1976`
- Mix of circa abbreviations, uncertainty markers, century notation
- Some use special Unicode dash (–) inconsistently

### 5. **Special Characters & Encoding**
- Unicode dashes (–) vs hyphens (-)
- Quotation mark variations
- Non-ASCII characters in titles (Chinese characters present)

### 6. **Trailing Data Issues**
- Some rows appear incomplete or malformed
- Inconsistent whitespace

## Standardization Actions Performed

### A. Header Normalization
```
Object Date → date
Title → title (nullable)
Object Number → object_number
Link Resource → resource_url
```

### B. Date Standardization
- Normalize "circa" to "ca."
- Use ISO 8601-like format where possible: `YYYY`, `YYYY-YYYY`
- Separate century notation and uncertainty: `19th century` → keep as-is for readability, add `uncertainty: true` where `(?)`
- Format: `Date [UNCERTAIN]` when `(?)` present

### C. Object Number Standardization
- Remove spaces after commas: `21.175.224a, b` → `21.175.224a,b`
- Keep multi-part objects together with consistent notation
- Format: `NUMBER[.SUBNUMBER[LETTER[,LETTER]]]`

### D. URL Validation
- Verify all URLs use consistent HTTPS or HTTP
- Format consistently

### E. Data Quality Notes
- Add internal quality flags
- Track missing vs. intentionally blank fields

## Checksum Strategy for Fixity

### Row-Level Checksums (SHA-256)
Each data row gets a checksum of its normalized content for verification.

### Cell-Level Checksums
Critical fields (object_number, resource_url) checksummed individually.

### Header Checksum
Validates schema integrity.

---

## Implementation

See accompanying files:
1. `met_inventory_standardized.tsv` - Cleaned data
2. `met_inventory_checksums.csv` - Verification checksums
3. `standardization_script.py` - Reproducible processing script
