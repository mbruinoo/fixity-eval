# Metropolitan Museum Inventory Standardization Archive

## 📦 Quick Start

This archive contains everything needed to understand, verify, and reproduce the data standardization process.

### Files at a Glance

| File | Purpose | Size |
|------|---------|------|
| **met_inventory.tsv** | Input data (original) | 35 KB |
| **met_inventory_standardized.tsv** | Output data (standardized) | 37 KB |
| **standardize_met_inventory.py** | Transformation script | 7.9 KB |
| **CHECKSUMS.txt** | MD5 checksums for fixity | 947 B |
| **MANIFEST.md** | Detailed documentation | 4.6 KB |
| **README.md** | This file | - |

## ✅ Verify Data Integrity

All files in this archive are protected by MD5 checksums for long-term preservation:

```bash
# Verify all files at once
md5sum -c CHECKSUMS.txt

# Expected output:
# met_inventory.tsv: OK
# met_inventory_standardized.tsv: OK
# ✓ All checksums verified successfully!
```

**Checksums:**
- Input: `6ec5bfc2d979ad12eb3343149beb8617`
- Output: `ea7849011acfd1def02051dbefcb64db`

## 🔄 Re-run the Transformation

To regenerate the standardized file from the original:

```bash
# Install dependencies (if needed)
pip install pandas

# Run the transformation
python3 standardize_met_inventory.py met_inventory.tsv met_inventory_standardized.tsv
```

The output checksums should match the originals if the input file hasn't changed.

## 📊 What Changed

### Data Issues Fixed
- ✓ 11 missing dates → filled with "Unknown"
- ✓ 25 missing titles → filled with "Untitled"
- ✓ HTML entities decoded (e.g., `&lt;i&gt;` → removed)
- ✓ Date notation standardized (B.C. → BCE, circa → ca.)
- ✓ Dashes normalized (en-dash/em-dash → hyphen)
- ✓ Whitespace cleaned up
- ✓ Column names standardized (spaces → underscores)

### Data Quality Metrics
| Metric | Before | After |
|--------|--------|-------|
| Missing Dates | 11 (3.7%) | 0 (0%) |
| Missing Titles | 25 (8.3%) | 0 (0%) |
| Date Notation Variants | Multiple | Consistent |
| HTML Artifacts | Present | Removed |
| Whitespace Issues | Multiple | Normalized |

## 📝 Column Changes

```
Before                  After
Object Date       →     Object_Date
Title             →     Title
Object Number     →     Object_Number
Link Resource     →     Link_Resource
```

## 🔍 Detailed Documentation

See **MANIFEST.md** for:
- Complete list of transformations
- Detailed data quality notes
- How to verify individual files
- Archival best practices
- Full script documentation

## 🗂️ Archival Best Practices

This archive follows reproducible data processing standards:

1. **Input preservation**: Original file included unchanged
2. **Process documentation**: Complete script with comments
3. **Fixity verification**: MD5 checksums for all data files
4. **Reproducibility**: Script can re-generate output from input
5. **Metadata**: Full documentation of all transformations

## 💾 For Long-Term Storage

Recommended directory structure for archival:
```
met_inventory_standardization/
├── input/
│   └── met_inventory.tsv
├── output/
│   └── met_inventory_standardized.tsv
├── script/
│   └── standardize_met_inventory.py
├── metadata/
│   ├── CHECKSUMS.txt
│   ├── MANIFEST.md
│   └── README.md
└── checksum_verification_record.txt
```

## 🔐 Verification Record

To create a timestamped verification record:

```bash
# Save current date and verification results
echo "Checksum Verification - $(date)" > checksum_verification_record.txt
md5sum -c CHECKSUMS.txt >> checksum_verification_record.txt 2>&1
```

## 📚 Script Details

**Language**: Python 3  
**Dependencies**: pandas  
**Execution Time**: ~1 second  
**Memory Usage**: ~50 MB  

**Key Features**:
- Step-by-step transformation logging
- Input/output checksum calculation
- File existence verification
- Comprehensive error handling
- Detailed execution summary

## ❓ Common Questions

**Q: Can I re-run the script?**  
A: Yes! As long as the input file matches the original checksum, you'll get identical output.

**Q: Why are the output and input files different sizes?**  
A: The output file includes quotes around fields for safety (per TSV best practices), adding ~2 KB.

**Q: How do I know the standardization is correct?**  
A: Check the checksums match. The script output shows exactly what was changed. Review MANIFEST.md for detailed transformation rules.

**Q: What if my checksum doesn't match?**  
A: Your file may have been modified. This is expected during normal use. The checksum helps you detect changes over time.

---

**Archive Created**: 2024-10-13  
**Processing Reproducible**: ✓ Yes  
**Data Integrity Verified**: ✓ Yes  
**Ready for Long-Term Archival**: ✓ Yes
