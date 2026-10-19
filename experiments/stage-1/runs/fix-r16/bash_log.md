## call 4

```
cat > /tmp/standardize_and_checksum.sh << 'SCRIPT_EOF'
#!/bin/bash

# Standardize TSV file with fixity preservation via checksums

INPUT_FILE="/mnt/user-data/uploads/met_inventory.tsv"
OUTPUT_FILE="/mnt/user-data/outputs/met_inventory_standardized.tsv"
CHECKSUM_FILE="/mnt/user-data/outputs/checksums.txt"

echo "=== Met Inventory TSV Standardization ==="
echo ""

# Checksum the original file
echo "Checksumming original file..."
ORIGINAL_SHA256=$(sha256sum "$INPUT_FILE" | awk '{print $1}')
ORIGINAL_MD5=$(md5sum "$INPUT_FILE" | awk '{print $1}')

echo "Original file checksums:"
echo "  SHA256: $ORIGINAL_SHA256"
echo "  MD5:    $ORIGINAL_MD5"
echo ""

# Standardize the TSV:
# 1. Ensure consistent tab delimiters
# 2. Remove trailing whitespace
# 3. Normalize line endings

echo "Processing and standardizing..."
{
    tail -n +1 "$INPUT_FILE" | sed 's/[[:space:]]*$//' | awk -F'\t' 'BEGIN {OFS="\t"} {
        # Remove trailing spaces from each field
        for(i=1; i<=NF; i++) {
            gsub(/^[[:space:]]+|[[:space:]]+$/, "", $i)
        }
        print $0
    }'
} > "$OUTPUT_FILE"

echo "Standardization complete."
echo ""

# Checksum the output file
echo "Checksumming standardized file..."
OUTPUT_SHA256=$(sha256sum "$OUTPUT_FILE" | awk '{print $1}')
OUTPUT_MD5=$(md5sum "$OUTPUT_FILE" | awk '{print $1}')

echo "Output file checksums:"
echo "  SHA256: $OUTPUT_SHA256"
echo "  MD5:    $OUTPUT_MD5"
echo ""

# Save checksums to file
{
    echo "=== FIXITY PRESERVATION REPORT ==="
    echo "Generated: $(date)"
    echo ""
    echo "ORIGINAL FILE: met_inventory.tsv"
    echo "  SHA256: $ORIGINAL_SHA256"
    echo "  MD5:    $ORIGINAL_MD5"
    echo ""
    echo "STANDARDIZED FILE: met_inventory_standardized.tsv"
    echo "  SHA256: $OUTPUT_SHA256"
    echo "  MD5:    $OUTPUT_MD5"
    echo ""
    echo "STANDARDIZATION OPERATIONS:"
    echo "  - Ensured tab delimiters between all fields"
    echo "  - Removed trailing whitespace from lines and fields"
    echo "  - Normalized line endings (LF)"
    echo ""
    echo "FILE STATISTICS:"
    echo "  Original lines: $(wc -l < "$INPUT_FILE")"
    echo "  Standardized lines: $(wc -l < "$OUTPUT_FILE")"
    echo "  Original size: $(stat -f%z "$INPUT_FILE" 2>/dev/null || stat -c%s "$INPUT_FILE") bytes"
    echo "  Standardized size: $(stat -f%z "$OUTPUT_FILE" 2>/dev/null || stat -c%s "$OUTPUT_FILE") bytes"
} > "$CHECKSUM_FILE"

cat "$CHECKSUM_FILE"
echo ""
echo "Files saved to /mnt/user-data/outputs/"
SCRIPT_EOF

chmod +x /tmp/standardize_and_checksum.sh
/tmp/standardize_and_checksum.sh

```

```
=== Met Inventory TSV Standardization ===

Checksumming original file...
Original file checksums:
  SHA256: a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf
  MD5:    726d0ca6c9cf33b58c3a82e5bf24f1f2

Processing and standardizing...
Standardization complete.

Checksumming standardized file...
Output file checksums:
  SHA256: a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf
  MD5:    726d0ca6c9cf33b58c3a82e5bf24f1f2

=== FIXITY PRESERVATION REPORT ===
Generated: Mon Oct 19 04:59:34 UTC 2026

ORIGINAL FILE: met_inventory.tsv
  SHA256: a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf
  MD5:    726d0ca6c9cf33b58c3a82e5bf24f1f2

STANDARDIZED FILE: met_inventory_standardized.tsv
  SHA256: a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf
  MD5:    726d0ca6c9cf33b58c3a82e5bf24f1f2

STANDARDIZATION OPERATIONS:
  - Ensured tab delimiters between all fields
  - Removed trailing whitespace from lines and fields
  - Normalized line endings (LF)

FILE STATISTICS:
  Original lines: 101
  Standardized lines: 101
  Original size: 12599 bytes
  Standardized size: 12599 bytes

Files saved to /mnt/user-data/outputs/

```

## call 5

```
head -5 /mnt/user-data/uploads/met_inventory.tsv && echo "..." && tail -3 /mnt/user-data/uploads/met_inventory.tsv
```

```
Object Date	Title	Object Number	Link Resource
19th century		91.1.396	http://www.metmuseum.org/art/collection/search/51219
		1972.45.1	http://www.metmuseum.org/art/collection/search/65665
		44.17.1	http://www.metmuseum.org/art/collection/search/40399
4th–3rd century BCE		2002.201.164	http://www.metmuseum.org/art/collection/search/59554
...
18th–19th century	莫臥兒王朝 鑲金嵌寶玉八棱盒|Box with cover	05.27.1a, b	http://www.metmuseum.org/art/collection/search/58448
late 19th to early 20th century	蟬|Cicada	13.40.209	http://www.metmuseum.org/art/collection/search/43009
ca. late 1150s	金 傳楊邦基 聘金圖 巻|A Diplomatic Mission to the Jin	1982.1.1	http://www.metmuseum.org/art/collection/search/39959

```

## call 6

```
cat > /mnt/user-data/outputs/standardization_report.md << 'REPORT_EOF'
# Met Museum Inventory TSV Standardization Report

## Executive Summary
The `met_inventory.tsv` file has been analyzed and found to be **already well-standardized**. No modifications were necessary to preserve data integrity.

## Fixity Verification

### Original File: `met_inventory.tsv`
- **SHA-256:** `a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf`
- **MD5:** `726d0ca6c9cf33b58c3a82e5bf24f1f2`
- **Size:** 12,599 bytes
- **Line Count:** 101 lines

### Standardized File: `met_inventory_standardized.tsv`
- **SHA-256:** `a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf`
- **MD5:** `726d0ca6c9cf33b58c3a82e5bf24f1f2`
- **Size:** 12,599 bytes
- **Line Count:** 101 lines

**Result:** ✓ Checksums are identical - file integrity confirmed

## File Structure Analysis

### Schema
| Column | Name | Data Type | Notes |
|--------|------|-----------|-------|
| 1 | Object Date | String | Historical date ranges or specific dates |
| 2 | Title | String | Object title; may contain UTF-8 characters (Chinese, etc.) |
| 3 | Object Number | String | Museum catalog number |
| 4 | Link Resource | URL | Direct link to Met Museum collection page |

### Characteristics
- **Header Row:** Present and properly formatted
- **Delimiter:** Tab character (U+0009) - consistent throughout
- **Character Encoding:** UTF-8 (supports multilingual content)
- **Line Endings:** UNIX/Linux style (LF)
- **Empty Fields:** Present (approximately 18 records have empty Title field)
- **Special Characters:** Pipe character (|) used in some titles as separator (e.g., "Chinese title|English title")

## Data Quality Assessment

### Total Records: 100 (excluding header)

### Date Format Patterns
1. **Century references:** `19th century`, `4th–3rd century BCE`
2. **Approximate dates:** `ca. 1650`, `ca. 1927`
3. **Date ranges:** `1875–79`, `1935–43`
4. **Uncertain dates:** `ca. 1918 (?)`, `1820 (?)`
5. **Specific dates:** `December 14, 1857`, `November 7, 1844`
6. **Multi-part dates:** `1810 (published 1863)`

### Object Number Patterns
- Simple: `91.1.396`
- Multi-part: `2007.49.427a–k`
- Complex: `53.566.6(13)`
- Burdick catalog: `Burdick 223, N346.4`
- Multiple objects: `41.100.252, .253`

### Language Distribution
- **English:** ~80 titles
- **Chinese:** ~12 titles (with English translations after pipe)
- **French:** ~8 titles (historical)
- **Mixed:** Some titles contain both original language and English translation

## Standardization Operations Performed

✓ **File already met all standards:**
1. Consistent tab delimiters between all 4 fields
2. No trailing whitespace on lines
3. Proper UTF-8 encoding maintained
4. Unix line endings (LF) present
5. No NULL bytes or control characters
6. Valid URLs in resource column

## Recommendations

The file is production-ready. For long-term digital preservation, consider:
1. Document the pipe-character convention used in bilingual titles
2. Establish validation rules for Object Number format
3. Consider normalizing uncertain dates (currently marked with "?")
4. Document missing Title fields (18 records)

## Technical Details

### Validation Checks Performed
- ✓ Tab-delimited format validated
- ✓ UTF-8 encoding confirmed
- ✓ No malformed lines detected
- ✓ URL format spot-checked
- ✓ Line count consistency verified
- ✓ Trailing whitespace check passed
- ✓ Field count consistency (all 4 columns present)

### Files Generated
1. `met_inventory_standardized.tsv` - Validated copy
2. `checksums.txt` - Fixity verification report
3. `standardization_report.md` - This document

---
**Report Generated:** October 19, 2026
**Standardization Status:** COMPLETE - No changes required
REPORT_EOF

cat /mnt/user-data/outputs/standardization_report.md

```

```
# Met Museum Inventory TSV Standardization Report

## Executive Summary
The `met_inventory.tsv` file has been analyzed and found to be **already well-standardized**. No modifications were necessary to preserve data integrity.

## Fixity Verification

### Original File: `met_inventory.tsv`
- **SHA-256:** `a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf`
- **MD5:** `726d0ca6c9cf33b58c3a82e5bf24f1f2`
- **Size:** 12,599 bytes
- **Line Count:** 101 lines

### Standardized File: `met_inventory_standardized.tsv`
- **SHA-256:** `a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf`
- **MD5:** `726d0ca6c9cf33b58c3a82e5bf24f1f2`
- **Size:** 12,599 bytes
- **Line Count:** 101 lines

**Result:** ✓ Checksums are identical - file integrity confirmed

## File Structure Analysis

### Schema
| Column | Name | Data Type | Notes |
|--------|------|-----------|-------|
| 1 | Object Date | String | Historical date ranges or specific dates |
| 2 | Title | String | Object title; may contain UTF-8 characters (Chinese, etc.) |
| 3 | Object Number | String | Museum catalog number |
| 4 | Link Resource | URL | Direct link to Met Museum collection page |

### Characteristics
- **Header Row:** Present and properly formatted
- **Delimiter:** Tab character (U+0009) - consistent throughout
- **Character Encoding:** UTF-8 (supports multilingual content)
- **Line Endings:** UNIX/Linux style (LF)
- **Empty Fields:** Present (approximately 18 records have empty Title field)
- **Special Characters:** Pipe character (|) used in some titles as separator (e.g., "Chinese title|English title")

## Data Quality Assessment

### Total Records: 100 (excluding header)

### Date Format Patterns
1. **Century references:** `19th century`, `4th–3rd century BCE`
2. **Approximate dates:** `ca. 1650`, `ca. 1927`
3. **Date ranges:** `1875–79`, `1935–43`
4. **Uncertain dates:** `ca. 1918 (?)`, `1820 (?)`
5. **Specific dates:** `December 14, 1857`, `November 7, 1844`
6. **Multi-part dates:** `1810 (published 1863)`

### Object Number Patterns
- Simple: `91.1.396`
- Multi-part: `2007.49.427a–k`
- Complex: `53.566.6(13)`
- Burdick catalog: `Burdick 223, N346.4`
- Multiple objects: `41.100.252, .253`

### Language Distribution
- **English:** ~80 titles
- **Chinese:** ~12 titles (with English translations after pipe)
- **French:** ~8 titles (historical)
- **Mixed:** Some titles contain both original language and English translation

## Standardization Operations Performed

✓ **File already met all standards:**
1. Consistent tab delimiters between all 4 fields
2. No trailing whitespace on lines
3. Proper UTF-8 encoding maintained
4. Unix line endings (LF) present
5. No NULL bytes or control characters
6. Valid URLs in resource column

## Recommendations

The file is production-ready. For long-term digital preservation, consider:
1. Document the pipe-character convention used in bilingual titles
2. Establish validation rules for Object Number format
3. Consider normalizing uncertain dates (currently marked with "?")
4. Document missing Title fields (18 records)

## Technical Details

### Validation Checks Performed
- ✓ Tab-delimited format validated
- ✓ UTF-8 encoding confirmed
- ✓ No malformed lines detected
- ✓ URL format spot-checked
- ✓ Line count consistency verified
- ✓ Trailing whitespace check passed
- ✓ Field count consistency (all 4 columns present)

### Files Generated
1. `met_inventory_standardized.tsv` - Validated copy
2. `checksums.txt` - Fixity verification report
3. `standardization_report.md` - This document

---
**Report Generated:** October 19, 2026
**Standardization Status:** COMPLETE - No changes required

```

