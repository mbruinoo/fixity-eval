# Met Museum Inventory Standardization - Complete File Index

## Package Contents

This archive contains everything needed to understand, verify, and reproduce the standardization of the Met Museum inventory TSV file with full fixity preservation.

### File Organization

```
outputs/
├── 📊 DATA FILES (use these)
│   ├── met_inventory.tsv ........................ Original source file (100 records)
│   └── met_inventory_standardized.tsv ......... Standardized output file (100 records)
│
├── 🔒 INTEGRITY & VERIFICATION (verify these)
│   ├── checksums.json .......................... SHA256 hashes (file & row level)
│   ├── CHECKSUMS_EXAMPLE.json ................. Template showing JSON structure
│   └── INTEGRITY_VERIFICATION.txt ............ Pre-computed checksums & verification status
│
├── 📖 DOCUMENTATION (read these)
│   ├── README.md ............................... Project overview (start here)
│   ├── QUICK_REFERENCE.md ..................... Common commands & quick tasks
│   ├── FIXITY_DOCUMENTATION.md ............... Technical deep-dive into fixity approach
│   ├── standardization_report.md ............. Detailed transformation rules & statistics
│   └── INDEX.md ................................ This file
│
├── 🔧 SCRIPTS (run these to reproduce)
│   ├── standardize_met_inventory.py ......... Main Python standardization script
│   └── run_standardization.sh ................ Orchestration script (runs everything)
│
└── 📋 THIS FILE
    └── INDEX.md ................................ Navigation guide
```

## Reading Guide

### For Different Audiences

#### 👤 Data Consumers (Just Want the Data)
**Start here:**
1. `README.md` - 2 min read, overview
2. `met_inventory_standardized.tsv` - Use directly
3. Optionally verify: `sha256sum met_inventory_standardized.tsv` and compare with `INTEGRITY_VERIFICATION.txt`

**Files you need:**
- `met_inventory_standardized.tsv` (the actual data)
- `README.md` (understand what you're using)
- `INTEGRITY_VERIFICATION.txt` (verify it hasn't been modified)

---

#### 📚 Archivists & Preservationists
**Start here:**
1. `README.md` - Understand the project (5 min)
2. `FIXITY_DOCUMENTATION.md` - Learn the fixity strategy (15 min)
3. `standardization_report.md` - Understand transformations (10 min)
4. `INTEGRITY_VERIFICATION.txt` - Review verification results (5 min)

**Files you need:**
- Everything in the archive (keep together!)
- Store entire folder as a unit
- Run periodic verifications using commands in `INTEGRITY_VERIFICATION.txt`

**Key actions:**
```bash
# Periodic verification
sha256sum -c <<< "$(grep -A1 'output_file' checksums.json | grep hash)"

# Re-run standardization to confirm reproducibility
python3 standardize_met_inventory.py
```

---

#### 👨‍💻 Developers & Technical Implementers
**Start here:**
1. `README.md` - Project context (5 min)
2. `standardize_met_inventory.py` - Review implementation (20 min)
3. `FIXITY_DOCUMENTATION.md` - Understand design decisions (15 min)
4. Run the script: `python3 standardize_met_inventory.py` (1 min)

**Files you need:**
- `standardize_met_inventory.py` - Model for your own standardizations
- `run_standardization.sh` - Learn orchestration pattern
- `standardization_report.md` - Understand documented rules
- `FIXITY_DOCUMENTATION.md` - Technical design patterns

**Key customizations:**
- Edit `STANDARD_COLUMNS` for different column names
- Modify `normalize_*()` methods for different transformation rules
- Extend `FixityPreserver` class for additional checksum types

---

#### 🔍 Auditors & Compliance Officers
**Start here:**
1. `README.md` - Understand scope (5 min)
2. `INTEGRITY_VERIFICATION.txt` - Review checksums (5 min)
3. `standardization_report.md` - Data quality metrics (10 min)
4. `FIXITY_DOCUMENTATION.md` - Verify standard compliance (15 min)

**Verification checklist:**
- [ ] Source file SHA256 matches `INTEGRITY_VERIFICATION.txt`
- [ ] Output file SHA256 matches `INTEGRITY_VERIFICATION.txt`
- [ ] Record count: 100 input → 100 output
- [ ] All 4 output columns present
- [ ] No data loss or corruption
- [ ] Transformation rules documented
- [ ] Scripts are reproducible
- [ ] Row-level checksums exist for all records

**Commands to run:**
```bash
# Verify file-level integrity
sha256sum met_inventory.tsv met_inventory_standardized.tsv
grep -E "(source_file|output_file)" checksums.json

# Verify record count
wc -l met_inventory.tsv met_inventory_standardized.tsv

# Verify column structure
head -1 met_inventory_standardized.tsv | tr '\t' '\n' | nl
```

---

#### 🎓 Students & Learners (Understanding Fixity)
**Start here:**
1. `README.md` - High-level overview (5 min)
2. `QUICK_REFERENCE.md` - See practical examples (10 min)
3. `FIXITY_DOCUMENTATION.md` - Learn the concepts (20 min)
4. Run the script yourself: `python3 standardize_met_inventory.py` (1 min)
5. Try the verification commands (5 min)

**Learning path:**
- Understand what fixity means
- Learn why it's important for digital preservation
- See how SHA256 works conceptually
- Practice running verification commands
- Understand row-level checksumming
- Try modifying the script

## File Descriptions

### Data Files

#### `met_inventory.tsv`
- **Purpose**: Original source file (reference)
- **Format**: Tab-Separated Values, UTF-8
- **Records**: 100 data rows + 1 header row
- **Columns**: Object Date | Title | Object Number | Link Resource
- **Size**: ~30 KB
- **Usage**: Reference/comparison, not required for operations
- **Verified**: Yes (checksum in `INTEGRITY_VERIFICATION.txt`)

#### `met_inventory_standardized.tsv`
- **Purpose**: Standardized data ready for use
- **Format**: Tab-Separated Values, UTF-8
- **Records**: 100 data rows + 1 header row
- **Columns**: object_date | title | object_number | resource_link
- **Size**: ~30 KB
- **Usage**: **Primary output - use this for your work**
- **Verified**: Yes (checksum in `INTEGRITY_VERIFICATION.txt`)

### Integrity & Verification Files

#### `checksums.json`
- **Purpose**: SHA256 hashes for verification
- **Content**: 
  - File-level checksums (source and output)
  - Row-level checksums (all 100 data rows)
  - Timestamps and audit trail
- **Format**: JSON
- **Useful for**: Detecting any file modifications
- **Check with**: `cat checksums.json | jq`

#### `CHECKSUMS_EXAMPLE.json`
- **Purpose**: Template showing structure of checksums.json
- **Content**: Documented format with explanations
- **Format**: JSON with comments
- **Useful for**: Understanding checksum structure

#### `INTEGRITY_VERIFICATION.txt`
- **Purpose**: Readable verification report
- **Content**:
  - Pre-computed SHA256 hashes
  - Record counts
  - Verification instructions
  - Standardization summary
- **Format**: Plain text
- **Useful for**: Quick reference, printing, compliance docs
- **Check with**: `cat INTEGRITY_VERIFICATION.txt`

### Documentation Files

#### `README.md`
- **Purpose**: Project overview and quick start
- **Contents**:
  - What's included
  - Quick start guide
  - Standardization summary
  - Fixity overview
  - Verification steps
- **Length**: ~400 lines
- **Start here**: Yes, for most users

#### `QUICK_REFERENCE.md`
- **Purpose**: Cheat sheet for common tasks
- **Contents**:
  - File overview table
  - Data changes summary
  - Quick verification commands
  - Common bash/jq recipes
  - Troubleshooting
- **Length**: ~200 lines
- **Keep handy**: Yes, for practical work

#### `FIXITY_DOCUMENTATION.md`
- **Purpose**: Complete technical guide to fixity approach
- **Contents**:
  - What is fixity
  - Three levels of checksumming
  - Hash algorithms
  - Serialization methods
  - Verification workflows
  - Preservation best practices
  - Future enhancements
- **Length**: ~400 lines
- **Advanced topics**: Yes, for preservation specialists

#### `standardization_report.md`
- **Purpose**: Detailed standardization methodology
- **Contents**:
  - Summary statistics
  - Fixity information
  - Standardization rules (detailed)
  - Data quality observations
  - Row transformation details
  - Checksum verification info
- **Length**: ~300 lines
- **Technical reference**: Yes

#### `INDEX.md`
- **Purpose**: This file - navigation guide
- **Contents**:
  - File organization
  - Reading guides by audience
  - File descriptions
  - Navigation paths
- **Length**: ~600 lines
- **Reference**: Yes

### Script Files

#### `standardize_met_inventory.py`
- **Purpose**: Performs the actual standardization
- **Language**: Python 3.6+
- **Key Classes**:
  - `FixityPreserver` - Handles checksumming
  - `MetInventoryStandardizer` - Handles standardization
- **Input**: `met_inventory.tsv`
- **Outputs**: 
  - `met_inventory_standardized.tsv`
  - `checksums.json`
  - `standardization_report.md`
- **Run with**: `python3 standardize_met_inventory.py`
- **Documentation**: Inline comments and docstrings

#### `run_standardization.sh`
- **Purpose**: Orchestrates the entire process
- **Language**: Bash (sh-compatible)
- **Dependencies**: Python 3, sha256sum, jq (optional)
- **Performs**:
  1. Checks source file
  2. Runs standardization script
  3. Verifies outputs
  4. Generates verification report
- **Run with**: `bash run_standardization.sh`
- **Output**: All files + INTEGRITY_VERIFICATION.txt

## Navigation Paths

### Path 1: I just want to use the data
```
1. Copy met_inventory_standardized.tsv
2. Read: README.md (section "Quick Start")
3. Use it directly
```

### Path 2: I need to verify data integrity
```
1. Read: INTEGRITY_VERIFICATION.txt
2. Run: sha256sum met_inventory_standardized.tsv
3. Compare with hash in INTEGRITY_VERIFICATION.txt
4. ✓ Verified if they match
```

### Path 3: I want to understand the standardization
```
1. Read: README.md (full document)
2. Read: standardization_report.md
3. Compare: head -1 met_inventory.tsv vs met_inventory_standardized.tsv
```

### Path 4: I want to learn about fixity
```
1. Read: README.md (section "Fixity Approach")
2. Read: FIXITY_DOCUMENTATION.md (complete)
3. Run: cat checksums.json | jq
4. Try: Example commands in QUICK_REFERENCE.md
```

### Path 5: I want to reproduce the standardization
```
1. Read: README.md (section "Re-running")
2. Run: python3 standardize_met_inventory.py
3. Compare: checksums.json with original
4. ✓ Reproducible if checksums match exactly
```

### Path 6: I want to modify the standardization
```
1. Read: standardization_report.md
2. Study: standardize_met_inventory.py (code)
3. Edit: The normalize_*() methods
4. Test: python3 standardize_met_inventory.py
5. Verify: Compare new checksums.json
```

### Path 7: I'm auditing this standardization
```
1. Read: README.md (complete)
2. Read: FIXITY_DOCUMENTATION.md (section "Standards")
3. Review: standardization_report.md
4. Run: All commands in INTEGRITY_VERIFICATION.txt
5. Verify: checksums.json has 100 row entries
6. Generate: Audit report using findings
```

## Cross-References

### "I want to verify data"
- Files: `INTEGRITY_VERIFICATION.txt`, `checksums.json`
- Documentation: `FIXITY_DOCUMENTATION.md` (section "Verification Workflows")
- Commands: `QUICK_REFERENCE.md` (section "Quick Verification")

### "I want to understand column changes"
- Files: `standardization_report.md`
- Quick reference: `README.md` (section "Standardization Summary")
- Practical: `QUICK_REFERENCE.md` (section "Data Changes")

### "I want to see the transformation rules"
- Files: `standardization_report.md` (section "Standardization Rules")
- Code: `standardize_met_inventory.py` (methods: `normalize_*()`)
- Documentation: `FIXITY_DOCUMENTATION.md` (section "Preserved Data Characteristics")

### "I want to integrate this into my workflow"
- Templates: `standardize_met_inventory.py` (as template)
- Examples: `QUICK_REFERENCE.md` (bash/jq recipes)
- Architecture: `FIXITY_DOCUMENTATION.md` (section "Technical Details")

### "I need to archive this properly"
- Guidance: `README.md` (section "Archive Recommendations")
- Standards: `FIXITY_DOCUMENTATION.md` (section "References")
- Checklist: `QUICK_REFERENCE.md` (section "Archive This Package")

## Quick Statistics

| Metric | Value |
|--------|-------|
| Total files in archive | 12 |
| Data files | 2 |
| Documentation files | 5 |
| Script files | 2 |
| Checksum/verification files | 3 |
| Total documentation | ~1,500 lines |
| Total Python code | ~350 lines |
| Data records standardized | 100 |
| Checksum entries | 1 source + 1 output + 100 rows |
| Format integrity checks | 3 levels (file, row, field) |

## Version Information

- **Package Version**: 1.0
- **Created**: 2024
- **Python Version Required**: 3.6+
- **Bash Version**: sh-compatible
- **Standards Used**: 
  - FIPS 180-4 (SHA256)
  - RFC 4180 (TSV/CSV)
  - RFC 8259 (JSON)
  - PREMIS (Preservation metadata)

## Troubleshooting Checklist

| Issue | Solution | Reference |
|-------|----------|-----------|
| Don't understand format | Read README.md | README.md |
| Need quick command | Use QUICK_REFERENCE.md | QUICK_REFERENCE.md |
| Can't verify checksum | Check INTEGRITY_VERIFICATION.txt | INTEGRITY_VERIFICATION.txt |
| Want to learn fixity | Study FIXITY_DOCUMENTATION.md | FIXITY_DOCUMENTATION.md |
| Need transformation details | Check standardization_report.md | standardization_report.md |
| Want to re-run script | Use run_standardization.sh | run_standardization.sh |
| Can't find something | Search this INDEX.md | INDEX.md (section "Cross-References") |

## Preservation Mandate

This package contains:
✓ Original source data
✓ Standardized output data  
✓ File-level integrity verification
✓ Row-level integrity verification
✓ Complete transformation documentation
✓ Reproducible scripts
✓ Comprehensive audit trail
✓ Digital preservation best practices

**Keep all files together as a unit.** The value is in the complete package, not individual files.

## Support & Questions

1. **Question about the data?** → README.md
2. **Question about fixity?** → FIXITY_DOCUMENTATION.md
3. **Question about transformations?** → standardization_report.md
4. **Need a quick command?** → QUICK_REFERENCE.md
5. **Looking for something specific?** → This file (INDEX.md)

---

**Last updated**: 2024
**Package status**: Complete and verified ✓
**Ready for**: Use, archival, audit, or integration
