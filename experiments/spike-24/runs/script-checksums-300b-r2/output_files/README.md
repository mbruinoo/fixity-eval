# Met Museum Inventory Standardization Archive

This archive contains the original data file, transformation script, output file, and verification documentation for standardizing the Met Museum inventory TSV file.

## Contents

### Data Files
- **met_inventory_ORIGINAL.tsv** - Original uploaded file (unmodified)
- **met_inventory_standardized.tsv** - Standardized output file

### Scripts
- **01_standardize_met_inventory.sh** - Procedural transformation script
- **00_generate_checksums.sh** - Checksum verification utility

### Documentation
- **CHECKSUMS.txt** - Verification manifest with SHA256 and MD5 checksums
- **standardization.log** - Detailed transformation log
- **README.md** - This file

## Quick Start

### To re-run the transformation:

```bash
bash 01_standardize_met_inventory.sh
```

This will regenerate `met_inventory_standardized.tsv` from the original file.

### To verify file integrity:

```bash
# Verify original hasn't been corrupted
sha256sum met_inventory_ORIGINAL.tsv
# Expected: 33c53888daa063ca9697f4a82f15cd2d047afbce1ccb21c235e9c4ae9509d547

# Verify output
sha256sum met_inventory_standardized.tsv
# Expected: 719a379093a3df7f030caf9e548b677230d299b660a8ee4a29af65410e43c242
```

## Transformation Summary

The standardization process performs the following operations:

1. **HTML Entity Decoding**
   - `&lt;` → `<`
   - `&gt;` → `>`
   - `&amp;` → `&`
   - `&quot;` → `"`

2. **Title Normalization**
   - Empty titles → `(Unknown)`
   - Removes leading/trailing brackets
   - Removes pipe-separated language prefixes (keeps English)

3. **Data Validation**
   - Ensures all rows have exactly 4 tab-separated columns
   - Verifies no data loss during transformation
   - Logs all statistics and quality metrics

## File Statistics

| Metric | Original | Standardized |
|--------|----------|--------------|
| Lines | 301 | 301 |
| Size | 35,052 bytes | 36,346 bytes |
| SHA256 | `33c53888...` | `719a3790...` |

## Reproducibility

All transformation steps use standard Unix tools (bash, sed, awk) and are fully deterministic. Running the script again will produce identical output checksums, ensuring reproducibility across different systems and time periods.

## Example Transformations

### Example 1: HTML Entity Decoding
```
Input:  ca. 1615–1868    Arrowhead (&lt;i&gt;Yanone&lt;/i&gt;)
Output: ca. 1615–1868    Arrowhead (Yanone)
```

### Example 2: Dual-Language Titles
```
Input:  5th century BCE  東周 玉璜|Arc-shaped pendant (Huang)
Output: 5th century BCE  Arc-shaped pendant (Huang)
```

### Example 3: Missing Titles
```
Input:  7th–9th century  (empty)  2002.556.36
Output: 7th–9th century  (Unknown)  2002.556.36
```

## Verification

See **CHECKSUMS.txt** for complete verification instructions and checksum values.
