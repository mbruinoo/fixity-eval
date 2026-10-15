# TSV Standardization & Checksum Preservation Toolkit

## Overview

This comprehensive toolkit standardizes your Met Museum inventory TSV file while maintaining **complete data integrity** through SHA-256 checksums and detailed verification protocols.

## What's Included

### Core Scripts

1. **standardize_tsv.py** ⭐ Main standardization engine
   - Cleans and normalizes all TSV data
   - Ensures consistent column structure
   - Sorts records by Object Number
   - Generates SHA-256 checksums for both files
   - Logs all operations with timestamp

2. **standardize.sh** ⭐ User-friendly wrapper
   - Orchestrates the entire standardization process
   - Automatically verifies checksums
   - Generates human-readable verification reports
   - Provides colored, informative output

3. **validate_tsv.py** Quality assurance tool
   - Analyzes source and output files
   - Compares standardization results
   - Detects issues and inconsistencies
   - Provides detailed statistical analysis

4. **verify_checksums.sh** Data integrity verifier
   - Re-verifies files at any time
   - Checks for file corruption or modification
   - Generates HTML reports (optional)
   - Works with stored checksums

### Documentation

- **QUICKSTART.md** - Get started in 30 seconds
- **README.md** - Complete technical documentation
- **00_OVERVIEW.md** - This file, system overview

## Why Checksums Matter

**Data Integrity in Research & Archives:**

In academic and archival contexts, checksums are critical for:

✓ **Verification** - Prove files haven't been corrupted  
✓ **Audit Trail** - Document when standardization occurred  
✓ **Reproducibility** - Verify results at any future date  
✓ **Compliance** - Meet archival best practices  
✓ **Trust** - Demonstrate data hasn't been tampered with  

Your checksums are stored in `checksums.json` and can be verified anytime.

## Quick Start

### Option 1: Automatic (Recommended)

```bash
chmod +x standardize.sh
./standardize.sh met_inventory.tsv
```

Output:
- ✓ `met_inventory_standardized.tsv` - Your standardized file
- ✓ `checksums.json` - Integrity verification data
- ✓ `verification.txt` - Detailed report

### Option 2: Manual with Python

```bash
python3 standardize_tsv.py met_inventory.tsv met_inventory_standardized.tsv
```

Then verify:
```bash
python3 validate_tsv.py met_inventory.tsv met_inventory_standardized.tsv
```

## What Gets Standardized

| Problem | Solution |
|---------|----------|
| Inconsistent whitespace | All fields trimmed and normalized |
| Missing columns | All rows padded to match header |
| Extra columns | All rows truncated to match header |
| Tab delimiters | Standardized throughout file |
| Unsorted data | Sorted by Object Number for consistency |
| Encoding issues | Verified UTF-8 throughout |
| Special characters | Properly handled (Chinese, Japanese, Korean) |

### Before Standardization
```
Object Date | Title                    | Object # | Link
late 19th...  [spaces]    C.I.46.9.189  http://...
19th c.     [mixed]      81.1.379      [missing col]
```

### After Standardization
```
Object Date	Title	Object Number	Link Resource
19th century		38.25.136	http://www.metmuseum.org/art/collection/search/58999
19th century		81.1.377a, b	http://www.metmuseum.org/art/collection/search/59638
19th century		81.1.379	http://www.metmuseum.org/art/collection/search/59814
```

*Note: Records are sorted by Object Number for easy reference*

## Checksum System

### How It Works

1. **Before Processing**
   ```
   Source file → SHA-256 checksum calculated
   ```

2. **During Processing**
   ```
   Standardization applied
   Output file created
   ```

3. **After Processing**
   ```
   Output file → SHA-256 checksum calculated
   Both checksums → Logged to checksums.json
   ```

4. **Verification (Anytime)**
   ```
   Current file → SHA-256 checksum calculated
   Compare with → Logged checksum
   Result → Match ✓ or Mismatch ✗
   ```

### Checksum Log Format

```json
{
  "timestamp": "2025-01-15T10:30:45.123456",
  "source_file": "met_inventory.tsv",
  "source_checksum_sha256": "a1b2c3d4e5f6...",
  "output_file": "met_inventory_standardized.tsv",
  "output_checksum_sha256": "f6e5d4c3b2a1...",
  "algorithm": "SHA-256"
}
```

## Typical Workflow

### Day 1: Standardization

```bash
# 1. Run standardization
./standardize.sh met_inventory.tsv

# Output:
# ✓ met_inventory_standardized.tsv (100 records, 4 columns)
# ✓ checksums.json (integrity data)
# ✓ verification.txt (human-readable report)
```

### Day 30: Verification

```bash
# 1. Verify files haven't been corrupted
./verify_checksums.sh

# Output:
# ✓ Source file verified: match
# ✓ Output file verified: match
# ✓ All files verified successfully
```

### Day 365: Quality Check

```bash
# 1. Re-analyze the standardized file
python3 validate_tsv.py met_inventory.tsv met_inventory_standardized.tsv

# Output:
# ✓ Row count preserved: 100
# ✓ Column count preserved: 4
# ✓ All rows have consistent column count
# ✓ Standardization successful
```

## Use Cases

### Academic Research
- Standardize museum inventory for analysis
- Maintain data provenance and integrity
- Comply with research archive requirements
- Enable reproducible workflows

### Digital Preservation
- Archive standardized files with checksums
- Verify data hasn't corrupted over time
- Document transformation process
- Create audit trail for compliance

### Database Import
- Prepare data for clean import
- Ensure consistent structure
- Validate before bulk operations
- Keep original file with checksums

### Data Sharing
- Standardize before distribution
- Provide checksums with files
- Allow recipients to verify integrity
- Document processing method

## File Preservation Best Practices

1. **Keep Both Files**
   - Original source file (original_met_inventory.tsv)
   - Standardized output (met_inventory_standardized.tsv)
   - Use version control or backup system

2. **Store Checksums**
   - Keep checksums.json with your files
   - Never modify checksums.json
   - Back up together as a set

3. **Archive Together**
   ```
   archive/
   ├── met_inventory.tsv (original)
   ├── met_inventory_standardized.tsv (output)
   ├── checksums.json (verification data)
   └── verification.txt (processing report)
   ```

4. **Periodic Verification**
   ```bash
   # Verify files quarterly or annually
   ./verify_checksums.sh
   ```

## Technical Specifications

### Checksum Algorithm
- **Algorithm**: SHA-256 (FIPS 180-4)
- **Bit Length**: 256 bits (64 hexadecimal characters)
- **Collision Resistance**: Cryptographically secure
- **Standard**: Industry-wide adoption (blockchain, Git, etc.)

### File Format
- **Input**: Tab-separated values (.tsv)
- **Output**: Tab-separated values (.tsv)
- **Encoding**: UTF-8 throughout
- **Line Endings**: Unix style (LF)

### Data Structure
- **Columns**: 4 (Object Date, Title, Object Number, Link Resource)
- **Records**: ~100 museum inventory items
- **Special Characters**: Full Unicode support (CJK, etc.)

## Troubleshooting

### "Checksum mismatch"
File has been modified or corrupted. Possible causes:
- File was edited after standardization
- File corruption during transfer
- File moved to different system

**Solution**: Re-standardize with original source file

### "File not found"
Specify the correct path:
```bash
./standardize.sh /full/path/to/met_inventory.tsv
```

### "Python command not found"
Install Python 3.6+:
```bash
# macOS
brew install python3

# Ubuntu/Debian
sudo apt-get install python3

# Windows
# Download from python.org
```

### "Column inconsistency"
The file has rows with different column counts. After running standardize.sh:
```bash
python3 validate_tsv.py met_inventory.tsv met_inventory_standardized.tsv
```
This will show exactly which rows have issues.

## Command Reference

### Standardization
```bash
./standardize.sh SOURCE [OUTPUT]
python3 standardize_tsv.py SOURCE [OUTPUT]
```

### Validation
```bash
python3 validate_tsv.py SOURCE OUTPUT
```

### Verification
```bash
./verify_checksums.sh
./verify_checksums.sh --verbose
./verify_checksums.sh --html
./verify_checksums.sh --checksum my_checks.json
```

### Inspection
```bash
# View checksums
cat checksums.json | python3 -m json.tool

# Count records
tail -n +2 met_inventory_standardized.tsv | wc -l

# View formatted
column -t -s $'\t' met_inventory_standardized.tsv | head

# Manual verification
sha256sum met_inventory.tsv
sha256sum met_inventory_standardized.tsv
```

## Additional Resources

- **SHA-256 Explanation**: https://en.wikipedia.org/wiki/SHA-2
- **TSV Format Spec**: https://www.iana.org/assignments/media-types/text/tab-separated-values
- **Data Integrity Best Practices**: https://www.library.ca.gov/collections/preservation/

## Support & Questions

For issues or questions:

1. Check QUICKSTART.md for basic usage
2. See README.md for detailed documentation
3. Run validation to diagnose issues:
   ```bash
   python3 validate_tsv.py met_inventory.tsv met_inventory_standardized.tsv
   ```
4. Review verification reports for detailed output

## License & Attribution

These tools are provided as-is for archival and research purposes.

---

**Ready to standardize your TSV file?**

```bash
chmod +x standardize.sh
./standardize.sh met_inventory.tsv
```

**Your data integrity journey starts now!** ✓
