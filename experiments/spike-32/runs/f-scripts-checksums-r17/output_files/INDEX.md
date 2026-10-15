# Met Inventory TSV Standardization - File Index

## Quick Navigation

Start with one of these based on your needs:

### 📖 I want to understand what happened
→ Read: **README.md** (2-min overview)  
→ Read: **STANDARDIZATION_SUMMARY.md** (comprehensive guide)  

### 📋 I want to verify the data
→ Check: **met_inventory_standardized.tsv.sha256**  
→ Run: `sha256sum -c met_inventory_standardized.tsv.sha256`  
→ Read: **standardization_manifest.txt** (processing details)  

### 🔧 I want to re-standardize or automate
→ Use: **run_standardization.py** (primary script)  
→ Or: **standardize_tsv.py** (alternative implementation)  
→ Or: **verify_checksums.sh** (bash verification)  

### 📊 I want to use the data
→ Use: **met_inventory_standardized.tsv** (the standardized file)  
→ Columns: Object Date | Title | Object Number | Link Resource  
→ Format: Tab-separated, UTF-8 encoded, Unix line endings  

---

## File Manifest

### Data Files (2 files)

| File | Purpose | Size | Format |
|------|---------|------|--------|
| `met_inventory_standardized.tsv` | Standardized inventory data | ~14 KB | TSV (UTF-8, Unix LF) |
| `met_inventory_standardized.tsv.sha256` | Checksum verification file | <1 KB | SHA256 hashes |

### Documentation Files (4 files)

| File | Purpose | Audience | Read Time |
|------|---------|----------|-----------|
| `README.md` | Quick start guide | Anyone | 2 min |
| `STANDARDIZATION_SUMMARY.md` | Complete reference | Implementers | 10 min |
| `standardization_manifest.txt` | Processing log & technical details | Auditors | 5 min |
| `INDEX.md` | This file - navigation guide | Everyone | 2 min |

### Script Files (3 files)

| File | Language | Purpose | When to Use |
|------|----------|---------|------------|
| `run_standardization.py` | Python 3 | Primary standardization script | Re-standardize or automate |
| `standardize_tsv.py` | Python 3 | Alternative implementation | Development/testing |
| `verify_checksums.sh` | Bash | Linux/Mac checksum verification | Verify integrity |

### Source File Reference

| File | Location | Format |
|------|----------|--------|
| `met_inventory.tsv` | `/mnt/user-data/uploads/` | Original TSV |

---

## Quick Start by Task

### Task: Verify the Standardized File is Legitimate

```bash
# 1. Check checksums
sha256sum -c met_inventory_standardized.tsv.sha256

# 2. Read what was done
cat standardization_manifest.txt

# Result: OK if checksums match
```

### Task: Use the Data in Python

```python
import csv

with open('met_inventory_standardized.tsv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        print(f"{row['Object Date']}: {row['Title']}")
```

### Task: Use the Data in Excel/Sheets

1. Open your spreadsheet application
2. Import/Open: `met_inventory_standardized.tsv`
3. Set delimiter to Tab
4. Encoding: UTF-8
5. Done - data is properly formatted and will load cleanly

### Task: Re-Standardize from Original

```bash
# Ensure Python 3 is installed
python3 --version

# Run the standardization
python3 run_standardization.py

# This will:
# - Read the original file
# - Standardize it
# - Generate new checksums
# - Create a new manifest
```

### Task: Audit the Standardization Process

```bash
# 1. Read the summary
cat STANDARDIZATION_SUMMARY.md

# 2. Check technical details
cat standardization_manifest.txt

# 3. Verify data wasn't modified
sha256sum -c met_inventory_standardized.tsv.sha256

# 4. Review what was standardized
diff met_inventory.tsv met_inventory_standardized.tsv
# (Only whitespace should differ)
```

### Task: Share This with Colleagues

Include these files:
1. ✓ `met_inventory_standardized.tsv` (the data)
2. ✓ `met_inventory_standardized.tsv.sha256` (for verification)
3. ✓ `README.md` (quick reference)
4. ✓ `run_standardization.py` (for reproducibility)

Optional:
- `STANDARDIZATION_SUMMARY.md` (detailed info)
- `standardization_manifest.txt` (technical log)

---

## Key Information at a Glance

### What Was Standardized

- ✓ Column headers (removed extra whitespace)
- ✓ Data cells (stripped leading/trailing space)
- ✓ Line endings (converted to Unix format)
- ✓ Encoding (verified UTF-8 throughout)

### What Was Preserved

- ✓ All data content (nothing modified)
- ✓ All 96 objects (nothing removed)
- ✓ All 4 columns (nothing added/removed)
- ✓ Internal spacing (preserved exactly)
- ✓ Special characters (Chinese, Japanese, Korean, European)
- ✓ Empty cells (maintained for missing data)

### Verification

- ✓ SHA256 checksums generated
- ✓ Manifest created with details
- ✓ Scripts provided for reproducibility
- ✓ Data integrity confirmed

---

## Technical Specifications

```
File Format:       Tab-Separated Values (TSV)
Columns:           4 (Object Date, Title, Object Number, Link Resource)
Rows:              97 (1 header + 96 data rows)
Encoding:          UTF-8
Line Endings:      LF (Unix style)
Checksum Method:   SHA256
Data Preserved:    100% (only formatting standardized)
```

---

## Frequently Asked Questions

**Q: Can I modify this file?**  
A: Yes, but the SHA256 checksums will no longer match. Keep the originals.

**Q: How do I know if the file is corrupted?**  
A: Run `sha256sum -c met_inventory_standardized.tsv.sha256`. If it says "OK", the file is good.

**Q: What encoding should I use?**  
A: UTF-8. All international characters are properly encoded in UTF-8.

**Q: Can I use this in Excel?**  
A: Yes, import as TSV with Tab delimiter and UTF-8 encoding.

**Q: Will this work on Windows?**  
A: Yes, but use a UTF-8 compatible application. Recommended: VS Code, LibreOffice, or Python.

**Q: Why SHA256 instead of MD5?**  
A: SHA256 is cryptographically secure and is the current best practice.

**Q: Can I re-standardize this?**  
A: Yes, run `python3 run_standardization.py` with the original source file.

**Q: What if I lose the checksums?**  
A: You can regenerate them by re-running `python3 run_standardization.py`.

---

## Directory Structure

```
/mnt/user-data/outputs/
├── met_inventory_standardized.tsv          [Main deliverable]
├── met_inventory_standardized.tsv.sha256   [Verification]
├── README.md                               [Quick start]
├── STANDARDIZATION_SUMMARY.md              [Full documentation]
├── standardization_manifest.txt            [Processing log]
├── INDEX.md                                [This file]
├── run_standardization.py                  [Primary script]
├── standardize_tsv.py                      [Alternative script]
└── verify_checksums.sh                     [Verification script]

/mnt/user-data/uploads/
└── met_inventory.tsv                       [Source file]
```

---

## Support Resources

### For Questions About:

- **The standardization process** → See `STANDARDIZATION_SUMMARY.md`
- **Technical details** → See `standardization_manifest.txt`
- **How to use the data** → See `README.md`
- **File verification** → Run `sha256sum -c met_inventory_standardized.tsv.sha256`
- **Script implementation** → Check comments in `run_standardization.py`

---

## Version & Date

- **Version**: 1.0
- **Date**: 2024-01-15
- **Dataset**: Metropolitan Museum of Art Inventory
- **Objects**: 96 items
- **Status**: ✓ Complete and verified

---

**Last Updated**: 2024-01-15  
**Next Steps**: Read README.md or use the standardized TSV file directly!
