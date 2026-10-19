# Met Museum Inventory Standardization - File Index

## Quick Start

1. **Read the standardized data:** `met_inventory_standardized.tsv`
2. **Verify integrity:** Run `python3 verify_checksums.py`
3. **Understand the process:** Read `STANDARDIZATION_REPORT.md`

---

## Output Files

### Data Files

| File | Purpose | Format |
|------|---------|--------|
| **met_inventory_standardized.tsv** | Standardized inventory with normalized columns | TSV (Tab-Separated Values) |
| **met_checksums.json** | Complete SHA-256 checksum manifest | JSON |

### Documentation

| File | Purpose | Content |
|------|---------|---------|
| **STANDARDIZATION_REPORT.md** | Comprehensive standardization details | Markdown report with technical information |
| **CHECKSUMS_SUMMARY.txt** | Quick reference for checksums and integrity | Plain text summary |
| **BEFORE_AND_AFTER.txt** | Comparison of original vs standardized | Plain text comparison |
| **INDEX.md** | This file | Navigation guide |

### Scripts

| File | Purpose | Language |
|------|---------|----------|
| **verify_checksums.py** | Verify output file integrity | Python 3 |
| **standardize_met.py** | Original standardization script (reproducible) | Python 3 |

---

## Fixity Preservation Summary

### Checksums

```
Source file (original):        a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf
Standardized output:           165c313b08027723576ccce9e0eb1ccad4394cb6668ae0962be5b16feaf2bd8d
Algorithm:                     SHA-256
All 100 rows individually checksummed:  ✓ YES
Verification status:           ✓ PASSED
```

### Integrity Guarantee

✓ Every data row has both source and output checksums  
✓ File-level integrity is verifiable  
✓ Row-level integrity is verifiable  
✓ Process is reproducible and deterministic  
✓ Any modification will be detected  

---

## How to Use

### View the Standardized Data

```bash
head -20 met_inventory_standardized.tsv
```

### Verify File Integrity

```bash
python3 verify_checksums.py
```

Expected output:
```
✓ VERIFIED
Status: ✓ ALL ROWS VERIFIED
```

### Reproduce the Standardization

```bash
# If you have the original file:
python3 standardize_met.py
```

### Check Individual Row Hashes

See `met_checksums.json` for the complete manifest of all 100 rows.

---

## Standardization Details

### Transformations Applied

1. **Column names:** Normalized to lowercase with underscores
   - "Object Date" → "object_date"
   - "Title" → "title"
   - "Object Number" → "object_number"
   - "Link Resource" → "link_resource"

2. **Whitespace:** Leading/trailing spaces removed from all fields

3. **Encoding:** UTF-8 standardized (Unicode characters preserved)

4. **Column order:** Fixed to: object_date, title, object_number, link_resource

### Data Preservation

✓ All 100 rows preserved  
✓ All field values preserved  
✓ All URLs intact  
✓ All special characters and Unicode preserved  
✓ Empty fields preserved  

---

## Data Statistics

- **Total rows:** 100
- **Total fields:** 4 per row
- **Date range:** 4th–3rd century BCE to 1960s
- **Character encoding:** UTF-8 (with Unicode characters)
- **File size (original):** ~12.5 KB
- **File size (standardized):** ~12.5 KB

---

## Files at a Glance

```
/mnt/user-data/outputs/
├── met_inventory_standardized.tsv     ← START HERE (standardized data)
├── met_checksums.json                  ← Checksum manifest
├── verify_checksums.py                 ← Verification tool
├── standardize_met.py                  ← Original script
├── STANDARDIZATION_REPORT.md           ← Full documentation
├── CHECKSUMS_SUMMARY.txt               ← Quick reference
├── BEFORE_AND_AFTER.txt                ← Comparison
└── INDEX.md                            ← This file
```

---

## Technical Information

### Checksum Methodology

Each row is checksummed as the tab-delimited concatenation of its values. This detects:
- Field reordering
- Data modifications
- Formatting changes
- Data corruption

### Reproducibility

The standardization process is deterministic. Re-running on the source file produces:
- Identical TSV output
- Identical row checksums
- Identical file-level checksum

### Security

SHA-256 provides:
- Collision resistance
- One-way function (cannot be reversed)
- Tamper detection capability
- Industry-standard security level

---

## Recommendations

1. **Keep files together:** Maintain TSV, checksums, and verification script together
2. **Periodic verification:** Run verification script occasionally to detect corruption
3. **Archive checksums separately:** Store `met_checksums.json` in a safe location
4. **Preserve this documentation:** Keep INDEX.md and STANDARDIZATION_REPORT.md with data

---

## Contact & Support

For questions about this standardization:
- Review STANDARDIZATION_REPORT.md for technical details
- Review CHECKSUMS_SUMMARY.txt for quick answers
- Run `python3 verify_checksums.py` to confirm integrity

---

*Generated: 2026-10-19*  
*Algorithm: SHA-256*  
*Status: ✓ All checksums verified*
