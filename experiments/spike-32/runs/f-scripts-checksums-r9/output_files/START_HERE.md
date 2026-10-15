# TSV Standardization with Integrity Verification - START HERE

Welcome! This package contains everything you need to standardize your Met Inventory TSV file and verify its integrity using cryptographic checksums.

## 🎯 What This Does

This system:
1. **Cleans** your TSV file (standardizes encoding, line endings, whitespace)
2. **Validates** data quality and identifies issues
3. **Verifies** integrity with MD5 and SHA256 checksums
4. **Preserves** data (nothing is lost or transformed)
5. **Documents** everything (audit log + manifest)

## ⚡ Quick Start (5 Minutes)

### 1. Run Standardization

```bash
cd /mnt/user-data/outputs
chmod +x run_standardization.sh
./run_standardization.sh
```

**Expected output:**
```
✓ Standardization complete!
✓ Checksums saved in manifest for verification
```

### 2. Verify Results

```bash
python3 verify_integrity.py
```

**Expected output:**
```
✓ VERIFICATION PASSED - File integrity confirmed
```

### 3. Review What Was Done

```bash
cat standardization_audit.log
```

## 📁 What You Get

After running, you'll have three files:

| File | Purpose | Use |
|------|---------|-----|
| **met_inventory_standardized.tsv** | Your cleaned data | Import, analyze, archive |
| **met_inventory_manifest.json** | Checksums & metadata | Verify integrity, document |
| **standardization_audit.log** | What happened | Review process, troubleshoot |

## 📖 Documentation Map

Start with the guide that matches your needs:

### 🏃 In a Hurry?
→ **QUICK_REFERENCE.txt**
- All commands on one page
- Common questions answered
- Troubleshooting guide

### 🎓 Want to Understand Everything?
→ **SUMMARY.md**
- Complete overview
- How it all works
- Key concepts explained

### 👨‍💻 Ready to Use It?
→ **IMPLEMENTATION_GUIDE.md**
- Step-by-step instructions
- Before/after comparison
- Best practices

### ✅ Need to Track Progress?
→ **CHECKLIST.md**
- Pre/post checks
- Verification steps
- Sign-off template

### 📚 Want Complete Details?
→ **README_STANDARDIZATION.md**
- Everything you need to know
- Troubleshooting section
- Advanced topics

## 🔒 About Checksums (The Key Feature)

**What?** Mathematical fingerprints of your file  
**Why?** Detect corruption or tampering  
**How?** Computed and stored in the manifest  
**When?** Verify anytime, detects any changes  

### The Checksum Promise

**Before Use:**
```bash
python3 verify_integrity.py
# ✓ Checksums match - File OK
# ✗ Checksums don't match - File corrupted
```

**After Transfer:**
```bash
python3 verify_integrity.py
# ✓ Still matches - Transfer successful
# ✗ Doesn't match - File corrupted in transit
```

**Next Year:**
```bash
python3 verify_integrity.py
# ✓ Still matches - File well preserved
# ✗ Doesn't match - File degraded
```

## 🗂️ File Structure

```
outputs/
├── START_HERE.md                   (← You are here)
├── QUICK_REFERENCE.txt             (Quick commands)
├── SUMMARY.md                      (Overview)
├── IMPLEMENTATION_GUIDE.md         (How-to guide)
├── CHECKLIST.md                    (Track progress)
├── README_STANDARDIZATION.md       (Complete docs)
├── standardize_tsv.py              (Main script)
├── run_standardization.sh          (Bash wrapper)
├── verify_integrity.py             (Verification script)
│
├── (After running:)
├── met_inventory_standardized.tsv  (Your cleaned data)
├── met_inventory_manifest.json     (Checksums & metadata)
└── standardization_audit.log       (Operation log)
```

## 🔧 System Requirements

- **Python 3.x** (included on most systems)
- **Bash shell** (for run_standardization.sh)
- **~1 MB disk space** (for scripts)
- **No external packages** (uses Python stdlib only)

Check you have Python:
```bash
python3 --version
```

## 📊 What Gets Standardized

| Issue | Before | After |
|-------|--------|-------|
| **Encoding** | Mixed (UTF-8/Latin-1) | UTF-8 only |
| **Line Endings** | Mixed (CRLF/LF) | Unix LF only |
| **Headers** | Extra spaces | Normalized |
| **Values** | Inconsistent whitespace | Trimmed |
| **Delimiters** | Potentially irregular | Consistent tabs |
| **Validation** | Unknown | Quality issues identified |

**Important:** Your actual data is never changed, only formatting is cleaned.

## 🎯 Use Cases

### ✓ This System is Perfect For:

- **Museum/Archive Collections** - Preserve with verified integrity
- **Long-Term Storage** - Detect degradation over time
- **Database Imports** - Standardized format, known quality
- **Data Compliance** - Audit trail, checksum verification
- **Scientific Records** - Reproducible standardization
- **Government Records** - Documented chain of custody

## ⚠️ Important Points

### DO:
- ✓ Run verification after standardization
- ✓ Keep manifest with standardized file
- ✓ Preserve original file as reference
- ✓ Document any data issues found
- ✓ Verify annually for important files

### DON'T:
- ✗ Modify standardized file without documenting changes
- ✗ Lose the manifest (contains verification checksums)
- ✗ Trust the file without verification
- ✗ Delete the audit log (needed for verification)
- ✗ Assume file is OK without running verification

## 🚀 Common Workflows

### Workflow 1: Quick Standardization

```bash
chmod +x *.sh *.py
./run_standardization.sh
python3 verify_integrity.py
```
**Takes:** ~10 seconds  
**Result:** Standardized file ready to use

### Workflow 2: Detailed Review

```bash
./run_standardization.sh
cat standardization_audit.log
python3 -m json.tool met_inventory_manifest.json
python3 verify_integrity.py
```
**Takes:** ~2 minutes  
**Result:** Full understanding of what happened

### Workflow 3: Archival with Verification

```bash
./run_standardization.sh
python3 verify_integrity.py
# Copy to archive
cp met_inventory_* /path/to/archive/
# Verify in archive
python3 verify_integrity.py /path/to/archive/met_inventory_standardized.tsv \
                             /path/to/archive/met_inventory_manifest.json
```
**Takes:** ~1 minute  
**Result:** Verified archive copy

## ❓ Quick Q&A

**Q: Do I need to install anything?**  
A: No. Python 3 and bash come with most systems.

**Q: Will my data be changed?**  
A: Only formatting is cleaned. Actual data is preserved.

**Q: What are checksums for?**  
A: Detect if file has been corrupted or changed.

**Q: How often should I verify?**  
A: After standardization, after file transfer, annually for important files.

**Q: What if verification fails?**  
A: Don't use the file. File may be corrupted. Restore from backup.

**Q: Can I edit the standardized file?**  
A: Yes, but checksums will change. Document your edits.

**Q: Where do I get help?**  
A: See QUICK_REFERENCE.txt or README_STANDARDIZATION.md

## 🎓 Learning Path

Follow this path based on your role:

### If You're a User:
1. Read: SUMMARY.md (5 min)
2. Run: `./run_standardization.sh` (10 sec)
3. Check: `cat standardization_audit.log` (2 min)
4. Done! Use the standardized file

### If You're a Manager/Archivist:
1. Read: SUMMARY.md (5 min)
2. Read: IMPLEMENTATION_GUIDE.md (10 min)
3. Run standardization workflow (1 min)
4. Review: met_inventory_manifest.json (2 min)
5. Verify: `python3 verify_integrity.py` (10 sec)
6. Archive files together

### If You're a Developer/Admin:
1. Read: README_STANDARDIZATION.md (20 min)
2. Study: standardize_tsv.py (10 min)
3. Customize for your needs (varies)
4. Integrate into pipeline (varies)
5. Document changes

### If You Need Help:
1. Check: QUICK_REFERENCE.txt
2. Search: README_STANDARDIZATION.md ("Troubleshooting")
3. Review: standardization_audit.log (for errors)
4. Run: `python3 verify_integrity.py` (diagnose)

## 🔍 Understanding the System

```
Your File
   ↓
[STANDARDIZE]  ← clean encoding, format, validate
   ↓
[CHECKSUM]     ← compute fingerprints
   ↓
[OUTPUT]       ← 3 files created
   ↓
[VERIFY]       ← confirm checksums match
   ↓
Ready to Use!
```

## 📋 The 3 Output Files Explained

### 1. met_inventory_standardized.tsv
```
Your actual data in standardized format
- UTF-8 encoding
- Tab-separated values
- Unix line endings
- Ready to use immediately
```

### 2. met_inventory_manifest.json
```
Machine-readable metadata
- File checksums (MD5, SHA256)
- File sizes
- Timestamp
- Statistics (rows, columns)
- Issues found
- Standardization rules applied
```

### 3. standardization_audit.log
```
Human-readable operation log
- When it ran
- What it did
- What it found
- Size comparisons
- Verification results
```

## ✨ Key Features

✓ **Integrity Verification** - Checksums detect corruption  
✓ **Audit Trail** - Complete record of all changes  
✓ **No Data Loss** - Original content preserved  
✓ **No Dependencies** - Python stdlib only  
✓ **Transparent** - See exactly what happened  
✓ **Reproducible** - Scripts included for repeatability  
✓ **Documented** - Multiple guides provided  
✓ **Automated** - One command runs everything  

## 🎯 Next Steps

### Right Now:
1. Read SUMMARY.md (5 minutes)
2. Run `./run_standardization.sh` (10 seconds)
3. Check results with `python3 verify_integrity.py`

### Before Using Data:
1. Review audit log
2. Check manifest for issues
3. Confirm verification passed

### For Long-Term:
1. Archive standardized file + manifest + audit log
2. Run annual verification
3. Document any issues found

## 🏁 Success Criteria

You're done when:

✓ `./run_standardization.sh` completes without errors  
✓ `python3 verify_integrity.py` shows "PASSED"  
✓ All three output files created  
✓ Audit log shows successful completion  
✓ No data quality issues, or issues documented  
✓ You understand what happened (read docs)  

## 📞 Support

**Quick answers:**
- QUICK_REFERENCE.txt (one-page guide)
- CHECKLIST.md (step-by-step)

**Detailed help:**
- README_STANDARDIZATION.md (troubleshooting section)
- IMPLEMENTATION_GUIDE.md (advanced topics)

**Immediate issues:**
- standardization_audit.log (error details)
- Check file permissions: `chmod +x *.sh *.py`

---

## 🚀 Ready? Let's Go!

```bash
# Make scripts executable
chmod +x *.sh *.py

# Run standardization
./run_standardization.sh

# Verify results
python3 verify_integrity.py

# Check what happened
cat standardization_audit.log
```

**That's it!** Your file is standardized and verified.

---

## 📚 Document Index

| Document | Best For | Read Time |
|----------|----------|-----------|
| **START_HERE.md** (you are here) | Getting oriented | 5 min |
| **QUICK_REFERENCE.txt** | Quick commands | 3 min |
| **SUMMARY.md** | Overview | 10 min |
| **IMPLEMENTATION_GUIDE.md** | How to use | 15 min |
| **CHECKLIST.md** | Progress tracking | 5 min |
| **README_STANDARDIZATION.md** | Complete reference | 30 min |

---

**Welcome to TSV Standardization with Integrity Verification!**

Choose your next step:
- **Quick Start:** Run `./run_standardization.sh`
- **Learn First:** Read `SUMMARY.md`
- **Help:** Check `QUICK_REFERENCE.txt`

Good luck! 🎉
