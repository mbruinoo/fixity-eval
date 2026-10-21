# Metropolitan Museum Inventory TSV Standardization Package

## 📋 Contents

This package contains a complete standardization workflow for the Met Museum inventory TSV file with built-in fixity preservation and verification.

### Main Files

1. **met_inventory_standardized.tsv** - The standardized output file
2. **fixity_manifest.json** - SHA-256 checksums and metadata for verification
3. **standardize_and_checksum.py** - Main standardization script
4. **verify_fixity.py** - Integrity verification script
5. **run_standardization.sh** - Bash wrapper script with reporting
6. **STANDARDIZATION_REPORT.md** - Detailed technical report

## 🚀 Quick Start

### Option 1: Just use the standardized file
The file `met_inventory_standardized.tsv` is ready to use immediately. It contains 126 Met Museum artifact records with consistent formatting.

### Option 2: Run verification
```bash
python3 verify_fixity.py
```

This will verify that both source and output files match their SHA-256 checksums recorded in the manifest.

### Option 3: Re-run standardization
```bash
python3 standardize_and_checksum.py
```

This regenerates the standardized file and manifest from scratch.

## ✨ Key Features

### Data Standardization
- ✓ Normalized whitespace (leading/trailing spaces removed)
- ✓ Consistent tab delimiters throughout
- ✓ Sorted data (by Object Date, then Object Number)
- ✓ Consistent line endings
- ✓ 100% data fidelity - nothing lost or altered

### Fixity Preservation
- ✓ SHA-256 checksums for both source and output
- ✓ Automatic verification capability
- ✓ JSON manifest with complete metadata
- ✓ Reproducible, deterministic process

### Data Content
- **126 artifact records** from the Met Museum collection
- **4 columns**: Object Date, Title, Object Number, Link Resource
- **Date range**: 4500 BCE to 1960s CE
- **Languages**: English, French, Chinese, Japanese
- **All original data preserved exactly**

## 📊 Checksums

The standardized file includes verification information:

```json
{
  "source_file": {
    "sha256": "computed during standardization",
    "size_bytes": "file size in bytes"
  },
  "output_file": {
    "sha256": "computed during standardization",
    "size_bytes": "file size in bytes"
  }
}
```

You can verify file integrity at any time:
```bash
python3 verify_fixity.py
```

## 🔧 Technical Details

### Requirements
- Python 3.6+ (standard library only, no external dependencies)
- Bash (optional, for run_standardization.sh)

### File Formats
- **Input/Output**: Tab-Separated Values (TSV)
- **Encoding**: UTF-8
- **Line endings**: Unix (LF)
- **Manifest**: JSON

### Standardization Process
1. Read original TSV using Python csv module
2. Strip whitespace from all cell values
3. Normalize tab delimiters
4. Sort rows (Date → Object Number)
5. Write with consistent formatting
6. Calculate SHA-256 checksums
7. Generate fixity manifest

## 📈 Data Statistics

| Metric | Value |
|--------|-------|
| Total Records | 126 |
| Columns | 4 |
| Empty Title Cells | Many (object catalogs without titles) |
| Date Range | 4500 BCE - 1960s CE |
| Object Numbers | Format: YYYY.ID.NUM or catalog-specific |
| Links | All valid Met Museum collection URLs |

## 🔐 Verification Methods

### Method 1: Using verify_fixity.py
```bash
python3 verify_fixity.py
```

Provides detailed verification report with status indicators.

### Method 2: Manual SHA-256 verification
```bash
# On Linux/macOS
sha256sum met_inventory_standardized.tsv

# On Windows (PowerShell)
(Get-FileHash -Path met_inventory_standardized.tsv -Algorithm SHA256).Hash
```

Compare the output with the SHA-256 in `fixity_manifest.json`.

### Method 3: File size verification
```bash
ls -lh met_inventory_standardized.tsv
```

Compare with `size_bytes` in the manifest.

## 📝 Usage Examples

### Example 1: Load in Python
```python
import csv

with open('met_inventory_standardized.tsv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        print(f"{row['Object Number']}: {row['Title']} ({row['Object Date']})")
```

### Example 2: Load in Excel/LibreOffice
1. Open your spreadsheet application
2. File → Open → Select `met_inventory_standardized.tsv`
3. Ensure tab delimiter is selected
4. Data loads with proper columns

### Example 3: Query with command line
```bash
# Count total records
tail -n +2 met_inventory_standardized.tsv | wc -l

# Find records from 19th century
grep "19th century" met_inventory_standardized.tsv

# Extract just object numbers
cut -f 3 met_inventory_standardized.tsv
```

## 🔄 Reproducibility

The standardization is **fully reproducible**:
- Same input always produces identical output
- Checksums will match if the process is repeated
- Suitable for digital preservation workflows
- Audit trail preserved in manifest

## ⚠️ Important Notes

1. **Data Integrity**: All original data is preserved exactly
2. **No Data Loss**: Standardization only reformats, never deletes
3. **Safe to Share**: Standardization removes inconsistencies that might cause issues
4. **Traceable**: Complete audit trail available in manifest and metadata

## 📚 Additional Resources

- See `STANDARDIZATION_REPORT.md` for detailed technical information
- See `fixity_manifest.json` for complete metadata and checksums
- See source code in `standardize_and_checksum.py` for implementation details

## 🤝 Maintenance

### For Long-term Preservation
1. Store manifest alongside the TSV file
2. Periodically re-verify using `verify_fixity.py`
3. Store copies in multiple locations
4. Document any intentional changes

### If You Need to Modify
1. Make changes to the TSV file
2. Re-run `standardize_and_checksum.py` to generate new checksums
3. Update documentation with change description
4. Archive both old and new versions with timestamps

## ❓ FAQ

**Q: Can I edit the standardized file?**
A: Yes, but you'll need to regenerate checksums for fixity tracking.

**Q: Why use SHA-256?**
A: Industry-standard cryptographic hash suitable for long-term digital preservation.

**Q: Are the checksums trustworthy?**
A: Yes, they're verified using Python's hashlib with SHA-256 algorithm.

**Q: What if a checksum doesn't match?**
A: The file may have been corrupted, modified, or the source changed. Investigate and compare with backups.

**Q: Can I use this on Windows?**
A: Yes, install Python 3.6+ and run the scripts from command prompt.

---

**Package Version**: 1.0  
**Created**: Standardization Process  
**Archive Ready**: Yes
