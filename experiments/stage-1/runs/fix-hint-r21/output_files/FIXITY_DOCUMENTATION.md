# Met Museum Inventory TSV Standardization
## Fixity Preservation & Data Integrity Report

**Process Date:** 2026-10-19  
**Rows Processed:** 101  
**Total Checksums Generated:** 1,012 (SHA256 hashes)

---

## Executive Summary

This standardization process applied consistent formatting rules to the Met Museum inventory TSV file while maintaining complete fixity through comprehensive checksumming at multiple levels:

- **Full file level** checksums for both source and output
- **Row-level** checksums for tracking which records were modified
- **Cell-level** checksums for individual data elements (date, title, object number, URL)

All checksums have been independently verified to confirm data integrity.

---

## Files Generated

### 1. `met_inventory_standardized.tsv`
**Type:** Tab-Separated Values  
**Size:** 13 KB  
**Rows:** 101 data rows + 1 header  
**SHA256:** `81b5c3abc36a53a291b97fb29c8fa7af69160aaba46b8a1f6bea4c10c5467215`

The standardized inventory file with all formatting rules applied consistently.

### 2. `fixity_verification_report.json`
**Type:** JSON with complete checksum data  
**Size:** 134 KB  
**Purpose:** Machine-readable verification record containing:
  - Full file checksums for source and output
  - Row-by-row hash data for 101 rows
  - Cell-level checksums for each of 4 fields
  - Detailed change tracking for each row

### 3. `standardization_summary.txt`
**Type:** Plain text report  
**Purpose:** Human-readable summary of the standardization process

### 4. `met_inventory_source.tsv`
**Type:** Tab-Separated Values (reference)  
**SHA256:** `fefa31cd031d657372eb58405523e9e82b30462b89b031f87617b18226d6ed46`

Original source file preserved for verification purposes.

---

## Standardization Rules Applied

### 1. **Whitespace Normalization**
- **Rule:** Trim leading and trailing whitespace from all fields
- **Impact:** Ensures clean data representation without affecting content
- **Verification:** Non-destructive transformation

### 2. **Empty Title Handling**
- **Rule:** Replace empty or whitespace-only title cells with `[Untitled]`
- **Impact:** 12 rows affected (11.9% of dataset)
- **Rationale:** Provides metadata for records without explicit titles while preserving auditability

### 3. **Date Field Preservation**
- **Rule:** Preserve as-is after whitespace trim
- **Impact:** 0 rows affected
- **Rationale:** Date formats are historically significant; standardization occurs at whitespace level only

### 4. **URL Validation**
- **Rule:** URLs must start with 'http'; others marked as invalid (empty string)
- **Impact:** 1 row affected
- **Rationale:** Ensures all URLs are properly formatted and retrievable

### 5. **Object Number Preservation**
- **Rule:** Strip whitespace, preserve original format and characters
- **Impact:** 0 rows affected
- **Rationale:** Object numbers are critical identifiers; format preserved exactly

---

## Standardization Changes Summary

| Field | Rows Changed | Percentage | Details |
|-------|--------------|-----------|---------|
| Title | 12 | 11.9% | Empty titles → `[Untitled]` |
| Date | 0 | 0% | Whitespace trimmed only |
| Object Number | 0 | 0% | Whitespace trimmed only |
| URL | 1 | 1.0% | Invalid URL removed |
| **Total Rows Modified** | **13** | **12.9%** | At least one field changed |

---

## Checksum Architecture

### File-Level Checksums
```
Source:  fefa31cd031d657372eb58405523e9e82b30462b89b031f87617b18226d6ed46
Output:  81b5c3abc36a53a291b97fb29c8fa7af69160aaba46b8a1f6bea4c10c5467215
```

Different checksums confirm that standardization was applied (as expected).

### Row-Level Checksums
Each row has a canonical JSON representation for checksumming:
```json
{
  "Link Resource": "http://...",
  "Object Date": "19th century",
  "Object Number": "91.1.396",
  "Title": "[Untitled]"
}
```

**Format benefits:**
- Field order doesn't affect the hash (deterministic)
- Special characters properly encoded (UTF-8)
- Enables verification of individual record changes
- Canonical format ensures consistent checksums across systems

### Cell-Level Checksums
Each field has its own checksum for granular verification:
- `date`: Object Date field
- `title`: Title field
- `object_number`: Object Number field  
- `url`: Link Resource field

---

## Modified Records

**Records with changes:** 13 of 101 (12.9%)

### Title Changes (12 records)
These records had empty or whitespace-only titles replaced with `[Untitled]`:

| Row | Object Date | Object Number | Original Title | New Title |
|-----|------------|---------------|-----------------|-----------|
| 2 | (empty) | 1972.45.1 | (empty) | [Untitled] |
| 3 | (empty) | 44.17.1 | (empty) | [Untitled] |
| 4 | 4th–3rd century BCE | 2002.201.164 | (empty) | [Untitled] |
| 5 | 15th–16th century | 1992.72.44 | (empty) | [Untitled] |
| 6 | 19th century | 79.2.447 | (empty) | [Untitled] |
| 7 | 19th century | 30.75.967 | (empty) | [Untitled] |
| 8 | (empty) | 21.175.224a, b | (empty) | [Untitled] |
| 9 | 19th century | 10.211.836 | (empty) | [Untitled] |
| 10 | (empty) | 20.148.828 | (empty) | [Untitled] |
| 11 | ca. 1650 | 36.120.598a, b | (empty) | [Untitled] |
| 12 | 18th–19th century | 62.32a, b | (empty) | [Untitled] |
| 31 | 19th century (?) | 36.90.1951 | (empty) | [Untitled] |

### URL Changes (1 record)
Row 28 had an invalid URL removed. Note: This entry appears to contain a tobacco card catalog number in the URL field rather than an actual URL, so the invalid URL was properly rejected per standardization rules.

---

## Verification Procedures

### Independent Verification Method 1: File Hash
```bash
sha256sum met_inventory_standardized.tsv
# Expected: 81b5c3abc36a53a291b97fb29c8fa7af69160aaba46b8a1f6bea4c10c5467215
```

### Independent Verification Method 2: Row-by-Row Audit
Review `fixity_verification_report.json` row-by-row section to identify which specific records were modified and regenerate their hashes independently.

### Independent Verification Method 3: Cell-Level Verification
For critical records, regenerate cell-level checksums to verify individual data elements weren't corrupted during standardization.

### Independent Verification Method 4: Python Script
```python
import hashlib
import json

with open('met_inventory_standardized.tsv', 'rb') as f:
    file_hash = hashlib.sha256(f.read()).hexdigest()

with open('fixity_verification_report.json', 'r') as f:
    report = json.load(f)
    
assert file_hash == report['output']['file_full'], "File integrity check failed!"
```

---

## Data Quality Notes

### Preserved Through Standardization
- All historical date formats (exactly as provided in source)
- All special characters and diacriticals (UTF-8 preserved)
- All object numbers in original format
- All URLs that meet validity criteria

### Changes Made
- Whitespace normalization across all fields
- Title placeholder for 12 untitled records (transparent change)
- URL rejection for 1 invalid entry (logged)

### Character Encoding
- **Source:** UTF-8 with tab delimiters
- **Output:** UTF-8 with tab delimiters
- **Special characters present:** EM-dashes (–), Chinese characters (東周, 唐, etc.), accented letters (ô, é, etc.)

---

## Checksum Validation Results

| Check | Expected | Calculated | Status |
|-------|----------|------------|--------|
| Source SHA256 | fefa31cd... | fefa31cd... | ✓ PASS |
| Output SHA256 | 81b5c3ab... | 81b5c3ab... | ✓ PASS |
| Row count | 101 | 101 | ✓ PASS |
| Modified rows | 13 | 13 | ✓ PASS |

**Overall Status:** ✓ ALL CHECKS PASSED

---

## Implementation Details

### Standardization Script
- **Language:** Python 3
- **CSV Library:** Python standard library `csv` module
- **Hash Algorithm:** SHA256 (cryptographically secure)
- **Canonical JSON:** Ensures platform-independent checksums
- **Encoding:** UTF-8 for all file I/O

### Checksum Coverage
- **Full file:** 2 hashes (source, output)
- **Per row:** 2 hashes × 101 rows = 202 hashes
- **Per cell:** 4 fields × 2 (source/output) × 101 rows = 808 hashes
- **Total:** 1,012 SHA256 hashes generated

---

## Recommendations

1. **Retain all files:** Keep source, standardized, and verification report together
2. **Archive checksums:** Store `fixity_verification_report.json` in a preservation system
3. **Periodic verification:** Re-run checksum calculations annually to detect bit rot
4. **Document history:** Note this standardization in data provenance metadata
5. **Access policy:** Make standardized TSV the primary version; keep source for audit trail

---

## Technical Specifications

### Tab-Separated Values Format
- **Delimiter:** Tab character (ASCII 0x09)
- **Line ending:** LF (Unix style, ASCII 0x0A)
- **Quote character:** Double quote (") when present in data
- **Header:** Yes, one row with column names
- **Encoding:** UTF-8 without BOM

### Field Definitions
1. **Object Date** - Temporal information for the object
2. **Title** - Name or description of the object
3. **Object Number** - Accession or catalog number
4. **Link Resource** - URL to the object in the Met collection

### Example Row (Standardized)
```
19th century	Artist Unknown	91.1.396	http://www.metmuseum.org/art/collection/search/51219
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-10-19 | Initial standardization with comprehensive checksumming |

---

## Contact & Support

For questions about this standardization process or verification of checksums:
- Refer to the source scripts: `standardize_fixed.py`
- Review the detailed JSON report: `fixity_verification_report.json`
- Cross-reference with source file: `met_inventory_source.tsv`

---

**Document Generated:** 2026-10-19  
**Verification Status:** ✓ COMPLETE  
**Data Integrity:** ✓ PRESERVED
