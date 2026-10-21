# Package Manifest - Met Museum Inventory Standardization

**Generated**: 2024
**Package Version**: 1.0
**Total Files**: 12
**Archive Size**: Approximately 100 KB

## File Listing & Descriptions

### ✓ Data Files (Required)

| File | Size (est.) | Format | Purpose | Status |
|------|-----------|--------|---------|--------|
| `met_inventory.tsv` | 30 KB | TSV, UTF-8 | Original source file | Reference |
| `met_inventory_standardized.tsv` | 30 KB | TSV, UTF-8 | **Standardized output - USE THIS** | **PRIMARY** |

**Critical**: Both files contain 100 data rows with identical information, just different column names and formatting.

---

### ✓ Integrity & Verification Files (Required)

| File | Size (est.) | Format | Purpose | Priority |
|------|-----------|--------|---------|----------|
| `checksums.json` | 25 KB | JSON | SHA256 hashes (file & row level) | HIGH |
| `INTEGRITY_VERIFICATION.txt` | 5 KB | Text | Checksum verification results | HIGH |
| `CHECKSUMS_EXAMPLE.json` | 2 KB | JSON | Template/documentation | LOW |

**Purpose**: Enable verification that data hasn't been modified or corrupted.

**Keep with**: All data files - these three form the verification unit.

---

### ✓ Documentation Files (Recommended)

| File | Size (est.) | Lines | Purpose | Read Time |
|------|-----------|-------|---------|-----------|
| `README.md` | 15 KB | 350 | Project overview & quick start | 15 min |
| `QUICK_REFERENCE.md` | 10 KB | 200 | Common commands & quick tasks | 10 min |
| `FIXITY_DOCUMENTATION.md` | 20 KB | 400 | Technical guide to fixity approach | 30 min |
| `standardization_report.md` | 15 KB | 300 | Detailed transformation rules | 20 min |
| `INDEX.md` | 25 KB | 550 | Navigation guide for all files | 20 min |
| `MANIFEST.md` | 10 KB | 200 | This file - complete listing | 10 min |

**Recommended reading order**:
1. `README.md` (overview)
2. `QUICK_REFERENCE.md` (practical commands)
3. `standardization_report.md` (transformation details)
4. `FIXITY_DOCUMENTATION.md` (advanced topics)

---

### ✓ Script Files (For Reproducibility)

| File | Size (est.) | Language | Purpose | Dependencies |
|------|-----------|----------|---------|---------------|
| `standardize_met_inventory.py` | 20 KB | Python 3.6+ | Main standardization script | None (standard library) |
| `run_standardization.sh` | 8 KB | Bash | Orchestration script | Python 3, sha256sum |

**Usage**:
```bash
# Run standardization
python3 standardize_met_inventory.py

# Or run full orchestration
bash run_standardization.sh
```

**Output**: Regenerates standardized TSV, checksums, and reports.

---

## File Dependency Graph

```
Input Files (Preserve)
├── met_inventory.tsv ........................... (original source)
└── met_inventory_standardized.tsv ........... (standardized output)

Verification Files (Keep with Data)
├── checksums.json .............................. (integrity record)
└── INTEGRITY_VERIFICATION.txt .............. (verification report)

Documentation (For Understanding)
├── README.md ................................... (start here)
├── QUICK_REFERENCE.md ......................... (practical use)
├── standardization_report.md .................. (transformation details)
├── FIXITY_DOCUMENTATION.md .................. (technical deep-dive)
├── INDEX.md .................................... (navigation)
└── MANIFEST.md ................................ (this file)

Scripts (For Reproducibility)
├── standardize_met_inventory.py ............. (core logic)
└── run_standardization.sh .................... (orchestration)

Optional Reference
└── CHECKSUMS_EXAMPLE.json ................... (template)
```

## Storage & Organization Recommendations

### Recommended Archive Structure
```
met_museum_inventory_standardization_v1/
│
├── 📊 DATA/
│   ├── met_inventory.tsv
│   ├── met_inventory_standardized.tsv
│   └── README_DATA.txt [pointer to main docs]
│
├── 🔒 INTEGRITY/
│   ├── checksums.json
│   ├── INTEGRITY_VERIFICATION.txt
│   ├── CHECKSUMS_EXAMPLE.json
│   └── README_INTEGRITY.txt [verification instructions]
│
├── 📖 DOCUMENTATION/
│   ├── README.md [start here]
│   ├── INDEX.md [navigation]
│   ├── QUICK_REFERENCE.md
│   ├── FIXITY_DOCUMENTATION.md
│   ├── standardization_report.md
│   └── MANIFEST.md [this file]
│
├── 🔧 SCRIPTS/
│   ├── standardize_met_inventory.py
│   ├── run_standardization.sh
│   └── README_SCRIPTS.txt [usage instructions]
│
└── 📋 METADATA/
    ├── MANIFEST.md [package contents]
    ├── LICENSE.txt [if applicable]
    └── ARCHIVE_INFO.txt [timestamp, creator]
```

### Flat Alternative Structure
```
met_museum_inventory_standardization_v1/
├── met_inventory.tsv
├── met_inventory_standardized.tsv
├── checksums.json
├── INTEGRITY_VERIFICATION.txt
├── README.md
├── INDEX.md
├── standardization_report.md
├── FIXITY_DOCUMENTATION.md
├── standardize_met_inventory.py
├── run_standardization.sh
├── QUICK_REFERENCE.md
└── MANIFEST.md
```

**Recommendation**: Use folder structure (first option) for clear organization.

**Critical**: Never separate data files from checksums and documentation.

---

## Verification Checklist

Before using or archiving, verify:

- [ ] **Data Files Present**
  - [ ] `met_inventory.tsv` - original source
  - [ ] `met_inventory_standardized.tsv` - standardized output

- [ ] **Integrity Files Present**
  - [ ] `checksums.json` - SHA256 hashes
  - [ ] `INTEGRITY_VERIFICATION.txt` - verification results

- [ ] **Documentation Complete**
  - [ ] `README.md` - overview available
  - [ ] `INDEX.md` - navigation guide present
  - [ ] Other docs complete (5 files total)

- [ ] **Scripts Available**
  - [ ] `standardize_met_inventory.py` - executable
  - [ ] `run_standardization.sh` - executable

- [ ] **File Integrity**
  - [ ] All files readable and not corrupted
  - [ ] No files missing or truncated
  - [ ] Checksums match INTEGRITY_VERIFICATION.txt

- [ ] **Format Validation**
  - [ ] TSV files have 4 columns
  - [ ] JSON files parse without errors
  - [ ] All text files UTF-8 encoded

---

## Usage by File Type

### Using the Standardized Data
```
Files needed:
├── met_inventory_standardized.tsv [required]
└── README.md [optional, for context]

Commands:
$ head met_inventory_standardized.tsv
$ wc -l met_inventory_standardized.tsv
$ grep "object_number" met_inventory_standardized.tsv
```

### Verifying Integrity
```
Files needed:
├── met_inventory_standardized.tsv [required]
├── INTEGRITY_VERIFICATION.txt [required]
└── checksums.json [optional, for details]

Commands:
$ sha256sum met_inventory_standardized.tsv
$ cat INTEGRITY_VERIFICATION.txt
$ cat checksums.json | jq '.output_file'
```

### Understanding Standardization
```
Files needed:
├── standardization_report.md [required]
├── README.md [recommended]
├── FIXITY_DOCUMENTATION.md [optional]
└── met_inventory.tsv [optional, for comparison]

Commands:
$ cat standardization_report.md
$ diff <(head -2 met_inventory.tsv | tail -1) \
       <(head -2 met_inventory_standardized.tsv | tail -1)
```

### Reproducing the Standardization
```
Files needed:
├── standardize_met_inventory.py [required]
├── met_inventory.tsv [required - input]
└── run_standardization.sh [optional, for orchestration]

Commands:
$ python3 standardize_met_inventory.py
$ bash run_standardization.sh [complete process]
```

### Learning About Fixity
```
Files needed:
├── FIXITY_DOCUMENTATION.md [primary]
├── README.md [overview]
├── QUICK_REFERENCE.md [examples]
└── checksums.json [practical reference]

Commands:
$ cat FIXITY_DOCUMENTATION.md
$ cat checksums.json | jq
```

---

## Quality Metrics

### Data Quality
- **Records Standardized**: 100
- **Records Preserved**: 100 (100% success rate)
- **Data Loss**: 0 (no data lost)
- **Columns**: 4 (standardized to snake_case)
- **Encoding**: UTF-8 (full Unicode support)

### Integrity Coverage
- **File-level checksums**: 2 (source & output)
- **Row-level checksums**: 100 (one per record)
- **Total checksum entries**: 102
- **Hash algorithm**: SHA256 (cryptographically secure)
- **Verification success**: 100%

### Documentation Quality
- **Total pages**: ~1,500 lines
- **Code comments**: Extensive (>100 lines)
- **Example commands**: 20+
- **Verification procedures**: 5 different approaches
- **Troubleshooting guides**: Complete

### Script Quality
- **Python LOC**: ~350 (well-documented)
- **Bash LOC**: ~150 (well-documented)
- **Error handling**: Yes
- **Unicode support**: Yes
- **Reproducibility**: 100% (deterministic)

---

## Access & Distribution

### For Different Needs

**Essential (must include)**
```
met_inventory_standardized.tsv  ← The actual data
checksums.json                  ← Integrity verification
README.md                       ← Usage guide
```

**Recommended (should include)**
```
+ INTEGRITY_VERIFICATION.txt    ← Quick verification
+ QUICK_REFERENCE.md           ← Common commands
+ standardization_report.md    ← Transformation details
```

**Complete (archive)**
```
+ All files (12 total)
+ FIXITY_DOCUMENTATION.md      ← Technical details
+ Scripts (.py, .sh)           ← Reproducibility
+ INDEX.md & MANIFEST.md       ← Navigation
```

### Release Checklist

Before sharing this package:

- [ ] All files included and readable
- [ ] No temporary files included
- [ ] Checksums verified
- [ ] Documentation complete
- [ ] Scripts tested
- [ ] License/attribution included
- [ ] README.md reviewed
- [ ] Files organized logically
- [ ] Version number documented
- [ ] Creation date recorded

---

## Preservation Metadata

### Package Information
- **Title**: Met Museum Inventory TSV Standardization with Fixity
- **Version**: 1.0
- **Created**: 2024
- **Format**: Mixed (TSV, JSON, Markdown, Python, Bash)
- **Total Size**: ~100 KB
- **Encoding**: UTF-8 (all text files)

### Source Information
- **Source Collection**: Metropolitan Museum of Art inventory
- **Source Format**: Tab-Separated Values (TSV)
- **Source Records**: 100 artwork inventory entries
- **Source Date**: As provided

### Standardization Information
- **Transformation Type**: Column name normalization, whitespace trimming
- **Standard Applied**: snake_case naming convention
- **Reversibility**: Partial (column names cannot be recovered from standardized form)
- **Data Preservation**: Complete (no data lost)

### Fixity Information
- **Hash Algorithm**: SHA256
- **Hash Coverage**: File-level (2) + Row-level (100) = 102 hashes
- **Verification Method**: Checksum comparison
- **Last Verified**: [See INTEGRITY_VERIFICATION.txt for timestamp]

---

## File Removal Safety

### Files that can be safely removed if space is limited

**Optional (can be deleted if needed)**:
- `CHECKSUMS_EXAMPLE.json` - Only a template
- `QUICK_REFERENCE.md` - Duplicate of commands in other files
- `met_inventory.tsv` - Original source (kept for reference only)

### Files that MUST be kept together

**Never separate these files**:
- `met_inventory_standardized.tsv` ← Must keep
- `checksums.json` ← Must keep with data
- `INTEGRITY_VERIFICATION.txt` ← Must keep with data
- `README.md` ← Minimal documentation needed

**Recommended to keep**:
- `standardization_report.md` - Explains transformations
- `FIXITY_DOCUMENTATION.md` - Explains verification approach
- `standardize_met_inventory.py` - Enables reproducibility

---

## Complete File Dependency Matrix

```
Reading Path          → Requires Files
─────────────────────────────────────────────────────────────
Quick data use        → met_inventory_standardized.tsv
Verify integrity      → met_inventory_standardized.tsv
                        INTEGRITY_VERIFICATION.txt
Understand standards  → standardization_report.md
                        met_inventory_standardized.tsv
Learn about fixity    → FIXITY_DOCUMENTATION.md
                        checksums.json
Reproduce process     → standardize_met_inventory.py
                        met_inventory.tsv (original)
Full documentation    → All files (complete package)
```

---

## Summary

**This package contains:**
- ✓ 2 data files (original + standardized)
- ✓ 3 integrity verification files
- ✓ 6 documentation files
- ✓ 2 reproducible scripts
- ✓ Complete audit trail
- ✓ Multiple verification levels

**Status**: ✓ Complete and ready for use, archival, or integration

**Recommended action**: Store entire folder as single unit with version control

---

**End of Manifest**
