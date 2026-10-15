# Complete File Index

Your TSV standardization toolkit includes everything needed to standardize data and preserve integrity.

## 📋 Documentation Files

### Start Here
- **00_OVERVIEW.md** - System overview and key concepts (~5 min read)
- **QUICKSTART.md** - Get started in 30 seconds
- **INDEX.md** - This file, complete guide

### Complete Reference
- **README.md** - Full technical documentation with all options
- **EXAMPLES.md** - 15 real-world usage examples with outputs

## 🔧 Executable Scripts

### Main Workflow
- **standardize.sh** - Primary script for standardization
  - Usage: `./standardize.sh [input] [output]`
  - Features: Standardizes file, generates checksums, verifies integrity
  - Output: TSV file, checksums.json, verification.txt

- **standardize_tsv.py** - Core Python standardization engine
  - Usage: `python3 standardize_tsv.py [input] [output]`
  - Features: File standardization, checksum generation, JSON logging
  - Can be used standalone or via standardize.sh

### Quality Assurance
- **validate_tsv.py** - TSV validation and comparison tool
  - Usage: `python3 validate_tsv.py [source] [output]`
  - Features: Analyzes both files, detects issues, compares results
  - Output: Detailed statistics and quality report

### Verification
- **verify_checksums.sh** - Checksum verification utility
  - Usage: `./verify_checksums.sh [options]`
  - Features: Verifies file integrity, can generate HTML reports
  - Options: --verbose, --html, --checksum [file]

## 📊 Generated Files (After Running)

### From standardize.sh
- **met_inventory_standardized.tsv** - Your standardized TSV file
- **checksums.json** - SHA-256 checksums and metadata (JSON format)
- **verification.txt** - Human-readable verification report

### From verify_checksums.sh
- **checksum_verification_report.txt** - Verification results
- **checksum_verification_report.html** - Web viewable report (optional)

## 🚀 Quick Reference

### Most Common Commands

```bash
# Standardize your file (recommended)
./standardize.sh met_inventory.tsv

# Validate results
python3 validate_tsv.py met_inventory.tsv met_inventory_standardized.tsv

# Verify integrity (anytime)
./verify_checksums.sh

# Check checksum values
cat checksums.json | python3 -m json.tool
```

## 📖 Reading Guide

### For Newcomers
1. Read **QUICKSTART.md** (2 minutes)
2. Run `./standardize.sh met_inventory.tsv`
3. Check **verification.txt** for results
4. Read **00_OVERVIEW.md** for understanding

### For Understanding Details
1. Read **README.md** sections of interest
2. Review **EXAMPLES.md** for your use case
3. Run `python3 validate_tsv.py source.tsv output.tsv`

### For Integration
1. Review **README.md** "Technical Notes" section
2. Check **EXAMPLES.md** "Integration with Data Pipeline"
3. Examine **standardize_tsv.py** source code
4. Use validate_tsv.py for quality gates

### For Archive/Long-term Preservation
1. Read **00_OVERVIEW.md** "File Preservation Best Practices"
2. Follow directory structure in **EXAMPLES.md** Example 12
3. Use **verify_checksums.sh** periodically
4. Keep README.md with your archive

## 🎯 Task-Based Guide

### "I just want to standardize my file"
```bash
chmod +x standardize.sh
./standardize.sh met_inventory.tsv
# Done! Check met_inventory_standardized.tsv
```
📖 See: **QUICKSTART.md**

### "I need to verify data integrity"
```bash
./verify_checksums.sh
# Check the output and verification.txt
```
📖 See: **README.md** → Checksum Management

### "I want to understand what changed"
```bash
python3 validate_tsv.py met_inventory.tsv met_inventory_standardized.tsv
```
📖 See: **EXAMPLES.md** → Example 2

### "I need this for academic research"
```bash
./standardize.sh met_inventory.tsv
# Archive: original, standardized, checksums.json together
```
📖 See: **00_OVERVIEW.md** → Use Cases

### "I need to integrate this into a pipeline"
```python
# Review standardize_tsv.py for API usage
# Use validate_tsv.py as quality gate
# Embed checksum verification in your process
```
📖 See: **EXAMPLES.md** → Example 13

### "I'm archiving this long-term"
```bash
# Structure as per Example 12
# Keep all files together
# Periodically run verify_checksums.sh
```
📖 See: **EXAMPLES.md** → Example 12 & **README.md** → Data Integrity

## ✅ File Checklist

Essential files:
- ✓ standardize_tsv.py
- ✓ standardize.sh
- ✓ validate_tsv.py
- ✓ verify_checksums.sh
- ✓ README.md

Highly recommended:
- ✓ QUICKSTART.md
- ✓ 00_OVERVIEW.md
- ✓ EXAMPLES.md

Reference:
- ✓ INDEX.md (this file)

## 🔐 Understanding Checksums

### What are checksums?
Mathematical fingerprints of files using SHA-256 algorithm.
- Same file always produces same checksum
- Different file produces different checksum
- Impossible to forge without changing file

### Why do I need them?
- **Verify** files haven't been corrupted
- **Detect** if files were modified
- **Document** processing history
- **Enable** reproducibility
- **Satisfy** archival requirements

### Where are they stored?
In `checksums.json` file (created automatically).

### How do I use them?
```bash
# Verify anytime
./verify_checksums.sh

# They tell you:
# ✓ Files match → No corruption
# ✗ Mismatch → File changed or corrupted
```

📖 See: **00_OVERVIEW.md** → Checksum System

## 🛠️ Requirements

### System Requirements
- **Python**: 3.6+ (for standardize_tsv.py)
- **Bash**: 4.0+ (for .sh scripts)
- **Utilities**: sha256sum (standard on Linux/Mac)

### Optional
- **jq**: For advanced JSON parsing
- **column**: For pretty output

### Installation
```bash
# Linux/Ubuntu
sudo apt-get install python3 coreutils

# macOS
brew install python3

# Windows
# Install Git Bash or WSL
# Or use Python via MSYS2/MinGW
```

## 📞 Support & Troubleshooting

### Common Questions

**Q: Where do I put my TSV file?**
A: Same directory as standardize.sh, or provide full path

**Q: Can I use this on Windows?**
A: Yes! Use Git Bash, WSL, or run Python scripts directly

**Q: What if standardization fails?**
A: Check validation_output and verify file isn't corrupted

**Q: How often should I verify?**
A: At least quarterly for archives, after any file transfer

See **README.md** Troubleshooting section for more.

### Getting Help
1. Check **README.md** for your issue
2. Run `python3 validate_tsv.py` to diagnose
3. Review generated reports (verification.txt, etc.)
4. Inspect checksums.json for details

## 📊 File Size Reference

Typical file sizes for 100 records:
- Original TSV: ~18-20 KB
- Standardized TSV: ~18-20 KB (similar)
- checksums.json: ~200 bytes
- verification.txt: ~1-2 KB

## 🎓 Learning Path

**Beginner**
1. QUICKSTART.md (2 min)
2. Run standardize.sh (1 min)
3. Review output files (2 min)

**Intermediate**
1. README.md → What Gets Standardized
2. EXAMPLES.md → Example 1-3
3. Run validate_tsv.py (3 min)

**Advanced**
1. README.md → All sections
2. EXAMPLES.md → Examples 13-15
3. Read Python/Bash source code
4. Integrate into your workflow

## 📁 Directory Structure (Recommended)

```
project/
├── met_inventory.tsv (original - keep safe)
├── standardize.sh (this toolkit)
├── standardize_tsv.py
├── validate_tsv.py
├── verify_checksums.sh
├── README.md
├── QUICKSTART.md
└── outputs/ (generated)
    ├── met_inventory_standardized.tsv
    ├── checksums.json
    └── verification.txt
```

## ⚡ Performance Notes

Processing time for ~100 records:
- Standardization: < 1 second
- Checksum calculation: < 1 second
- Validation: < 2 seconds
- Total: < 5 seconds

All scripts are optimized for performance.

## 📝 License & Attribution

These tools are provided as-is for archival and research purposes.
Suitable for academic institutions, museums, and archives.

---

## 🎯 Next Steps

1. **Choose your path:**
   - Quick start? → Read QUICKSTART.md
   - Understand system? → Read 00_OVERVIEW.md
   - See examples? → Read EXAMPLES.md
   - Need details? → Read README.md

2. **Run your first standardization:**
   ```bash
   chmod +x standardize.sh
   ./standardize.sh met_inventory.tsv
   ```

3. **Verify results:**
   ```bash
   cat verification.txt
   cat checksums.json
   ```

4. **Explore further:**
   - Try validation: `python3 validate_tsv.py ...`
   - Try verification: `./verify_checksums.sh`
   - Read examples: Open EXAMPLES.md

---

**Happy standardizing! Your data integrity journey starts now.** ✓

For quick reference, keep this INDEX.md handy!
