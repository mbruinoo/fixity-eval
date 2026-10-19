# Standardization Package - Complete Index

## 📑 Navigation Guide

### Quick Links by Use Case

**🚀 I just want to use the data:**
1. Open `met_inventory_standardized.tsv`
2. Use in Excel, Python, or any TSV application
3. Done! ✓

**🔐 I want to verify integrity:**
1. Read: `README.md` (verification section)
2. Run: `python3 verify_fixity.py`
3. Check: `fixity_manifest.json` for details

**📚 I want to understand the standardization:**
1. Read: `README.md` (overview)
2. Read: `STANDARDIZATION_EXAMPLE.md` (concrete examples)
3. Read: `STANDARDIZATION_REPORT.md` (technical details)

**🔧 I want to re-run or modify the process:**
1. Review: `standardize_and_checksum.py` (well-commented)
2. Run: `python3 standardize_and_checksum.py`
3. Verify: `python3 verify_fixity.py`
4. Archive: Keep old checksums for history

---

## 📋 File Descriptions

### DATA FILES

#### `met_inventory_standardized.tsv`
- **Purpose**: The standardized Met Museum inventory data
- **Format**: Tab-Separated Values (UTF-8, Unix line endings)
- **Records**: 126 artifact entries
- **Columns**: Object Date, Title, Object Number, Link Resource
- **Sorting**: By date (chronologically) then by object number
- **Status**: Ready for immediate use
- **Contains**: All original data with normalized formatting

#### `met_inventory_source.tsv` *(created during standardization)*
- **Purpose**: Source file before standardization (for reference/backup)
- **Format**: Tab-Separated Values (UTF-8)
- **Records**: 126 artifact entries
- **Note**: May contain whitespace inconsistencies relative to output

---

### DOCUMENTATION FILES

#### `README.md` ⭐ **START HERE**
- **Best for**: First-time users
- **Contents**:
  - Quick start guide (3 options)
  - Feature summary
  - Data statistics
  - Usage examples
  - FAQ
- **Read time**: 5-10 minutes
- **Links to**: STANDARDIZATION_REPORT.md, STANDARDIZATION_EXAMPLE.md

#### `STANDARDIZATION_REPORT.md`
- **Best for**: Technical users and archivists
- **Contents**:
  - Detailed transformation specifications
  - Data preservation guarantees
  - Quality checks performed
  - Statistics and metrics
  - Reproducibility information
  - Recommendations for long-term use
- **Read time**: 10-15 minutes
- **Contains**: All technical specifications

#### `STANDARDIZATION_EXAMPLE.md`
- **Best for**: Understanding what changed
- **Contents**:
  - Before/after comparison examples
  - 7 concrete standardization examples
  - Special character handling examples
  - Verification checklist
- **Read time**: 5-10 minutes
- **Visual**: Easy-to-follow examples

#### `PACKAGE_CONTENTS.txt`
- **Best for**: Overview of all files
- **Contents**:
  - Complete package inventory
  - File purposes and descriptions
  - Transformations summary
  - Statistics
  - Use cases
  - Recommendations
- **Read time**: 5 minutes
- **Format**: Plain text with structured sections

#### `INDEX.md` *(this file)*
- **Purpose**: Navigation guide for the package
- **Contains**: This file you're reading now
- **Use**: Find what you need quickly

---

### SCRIPT FILES

#### `standardize_and_checksum.py`
- **Purpose**: Main standardization script
- **Language**: Python 3.6+
- **Dependencies**: Standard library only (no external packages)
- **Run**: `python3 standardize_and_checksum.py`
- **Does**:
  - Reads source TSV
  - Applies all standardization transformations
  - Calculates SHA-256 checksums
  - Generates fixity manifest
  - Writes standardized output
- **Output files created**:
  - `met_inventory_standardized.tsv`
  - `fixity_manifest.json`
- **Time to complete**: < 1 second
- **Code quality**: Well-commented, readable

#### `verify_fixity.py`
- **Purpose**: Integrity verification script
- **Language**: Python 3.6+
- **Dependencies**: Standard library only
- **Run**: `python3 verify_fixity.py`
- **Does**:
  - Loads fixity manifest
  - Calculates current file checksums
  - Compares against manifest values
  - Reports detailed verification status
  - Detects corruption or unauthorized changes
- **Output**: Detailed report with pass/fail indicators
- **Exit codes**: 0=success, 1=failure
- **Time to complete**: < 1 second

#### `run_standardization.sh`
- **Purpose**: Bash wrapper for standardization with reporting
- **OS**: Linux/macOS (Bash required)
- **Run**: `bash run_standardization.sh`
- **Does**:
  - Executes standardization
  - Displays statistics
  - Shows manifest contents
  - Compares row counts
  - Displays sample data
- **Output**: Comprehensive text report
- **Time to complete**: ~2 seconds

---

### METADATA FILES

#### `fixity_manifest.json`
- **Purpose**: Checksum and transformation audit trail
- **Format**: JSON
- **Contains**:
  - Standardization timestamp
  - Source file metadata:
    - Path
    - Size in bytes
    - SHA-256 hash
  - Output file metadata:
    - Path
    - Size in bytes
    - SHA-256 hash
  - List of transformations applied
  - Algorithm information (SHA-256)
- **Use**: Verification and audit trail
- **Machine-readable**: Yes
- **Human-readable**: Yes
- **Verify against**: Use `verify_fixity.py` script

---

## 🗺️ Decision Tree: Which File Do I Need?

```
START
  │
  ├─→ "I just want the data"
  │    └─→ Use: met_inventory_standardized.tsv ✓
  │
  ├─→ "I want to understand what was done"
  │    ├─→ Quick overview?
  │    │   └─→ Read: README.md
  │    ├─→ See examples?
  │    │   └─→ Read: STANDARDIZATION_EXAMPLE.md
  │    └─→ Technical details?
  │        └─→ Read: STANDARDIZATION_REPORT.md
  │
  ├─→ "I want to verify the files"
  │    ├─→ Automated verification?
  │    │   └─→ Run: python3 verify_fixity.py
  │    └─→ Manual verification?
  │        └─→ Compare checksums in: fixity_manifest.json
  │
  ├─→ "I want to re-run the standardization"
  │    ├─→ Understand first?
  │    │   └─→ Read: standardize_and_checksum.py (commented code)
  │    └─→ Ready to run?
  │        └─→ Run: python3 standardize_and_checksum.py
  │
  └─→ "I need a file overview"
       └─→ Read: PACKAGE_CONTENTS.txt
```

---

## 📊 Package Statistics

| Metric | Value |
|--------|-------|
| Total Files | 9 |
| Data Files | 2 (standardized + source) |
| Documentation | 5 files |
| Scripts | 3 files |
| Metadata | 1 file |
| **Data Records** | **126** |
| **Columns** | **4** |
| **Date Range** | **4500 BCE - 1960s CE** |
| **Python Version Required** | **3.6+** |
| **External Dependencies** | **None** |

---

## ✅ Package Quality Checklist

- ✓ Complete standardization applied
- ✓ SHA-256 checksums calculated
- ✓ Fixity manifest generated
- ✓ Verification scripts included
- ✓ Comprehensive documentation provided
- ✓ Multiple usage examples included
- ✓ Data integrity preserved (126/126 records)
- ✓ Unicode/multilingual content preserved
- ✓ Ready for long-term archival
- ✓ Ready for immediate use

---

## 🚀 Quick Start Commands

```bash
# 1. Verify package integrity
python3 verify_fixity.py

# 2. View standardized data (first 10 rows)
head -n 11 met_inventory_standardized.tsv | column -t -s $'\t'

# 3. Count total records
tail -n +2 met_inventory_standardized.tsv | wc -l

# 4. Search for specific artifact
grep "19th century" met_inventory_standardized.tsv | head -5

# 5. Re-run standardization
python3 standardize_and_checksum.py

# 6. View manifest
cat fixity_manifest.json

# 7. Load in Python
python3 -c "
import csv
with open('met_inventory_standardized.tsv') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for i, row in enumerate(reader, 1):
        if i <= 3:
            print(f'{i}: {row[\"Object Number\"]} - {row[\"Object Date\"]}')"

# 8. Compare checksums (Linux/macOS)
sha256sum met_inventory_standardized.tsv
grep '"sha256"' fixity_manifest.json
```

---

## 📞 Support Reference

### If You Need To...

**...use the file immediately**
- Open: `met_inventory_standardized.tsv`
- See: `README.md` (Usage Examples section)

**...verify integrity**
- Run: `python3 verify_fixity.py`
- See: `README.md` (Verification Methods section)
- See: `STANDARDIZATION_REPORT.md` (Fixity & Verification)

**...understand transformations**
- See: `STANDARDIZATION_EXAMPLE.md` (before/after examples)
- See: `STANDARDIZATION_REPORT.md` (Standardization Details)

**...find specific records**
- Use: `grep` command (see Quick Start above)
- Open: `met_inventory_standardized.tsv` in spreadsheet
- Write: Python script using csv module

**...modify the standardization**
- Read: `standardize_and_checksum.py` (well-commented)
- See: `STANDARDIZATION_REPORT.md` (full specifications)
- Run: `python3 standardize_and_checksum.py` (after changes)

**...archive the package**
- Include: All 9 files
- Include: Verification script (`verify_fixity.py`)
- Include: Manifest (`fixity_manifest.json`)
- Include: Documentation (`README.md`, reports)
- Reference: This `INDEX.md` file

---

## 📝 Document Versions

| File | Type | Version | Purpose |
|------|------|---------|---------|
| met_inventory_standardized.tsv | Data | 1.0 | Primary output |
| README.md | Doc | 1.0 | Quick reference |
| STANDARDIZATION_REPORT.md | Doc | 1.0 | Technical specs |
| STANDARDIZATION_EXAMPLE.md | Doc | 1.0 | Usage examples |
| standardize_and_checksum.py | Script | 1.0 | Standardization engine |
| verify_fixity.py | Script | 1.0 | Verification tool |
| fixity_manifest.json | Metadata | 1.0 | Audit trail |

---

## 🎯 Summary

This package provides:

1. **A standardized TSV file** ready for immediate use
2. **Complete fixity preservation** with SHA-256 checksums
3. **Verification capabilities** to detect corruption
4. **Comprehensive documentation** for all use cases
5. **Reproducible processes** for long-term archival
6. **Zero external dependencies** - runs with Python 3.6+

**Status**: ✅ **READY FOR USE**

---

## 📖 Reading Order Recommendations

### For Data Users:
1. `README.md` (5 min)
2. Open `met_inventory_standardized.tsv`
3. Done! ✓

### For Archivists:
1. `README.md` (5 min)
2. `STANDARDIZATION_REPORT.md` (10 min)
3. `verify_fixity.py` (run verification)
4. `fixity_manifest.json` (review metadata)

### For Technical Users:
1. `README.md` (5 min)
2. `standardize_and_checksum.py` (read code)
3. Run verification
4. Review any specific sections as needed

### For Managers/Decision-Makers:
1. `PACKAGE_CONTENTS.txt` (5 min)
2. `STANDARDIZATION_REPORT.md` (overview sections)
3. Discussion with technical team

---

**Last Updated**: During standardization process  
**Package Status**: Complete and verified  
**Archive Ready**: Yes
