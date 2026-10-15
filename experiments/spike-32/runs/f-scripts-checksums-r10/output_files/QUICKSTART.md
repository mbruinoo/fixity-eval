# Quick Start Guide

## 30-Second Setup

```bash
# Make scripts executable
chmod +x standardize.sh

# Run standardization
./standardize.sh met_inventory.tsv
```

That's it! You now have:
- ✓ `met_inventory_standardized.tsv` - Your standardized file
- ✓ `checksums.json` - Integrity verification
- ✓ `verification.txt` - Detailed report

## What Happened?

1. **Loaded** your original TSV file
2. **Standardized** all formatting and structure
3. **Sorted** records by Object Number
4. **Verified** data integrity with SHA-256 checksums
5. **Generated** a verification report

## Verify Later

```bash
# Verify that files haven't been corrupted
cat checksums.json

# Or re-run the validation
python3 validate_tsv.py met_inventory.tsv met_inventory_standardized.tsv
```

## What Got Fixed

| Issue | Result |
|-------|--------|
| Inconsistent whitespace | ✓ Cleaned |
| Missing/extra columns | ✓ Normalized |
| Unsorted data | ✓ Sorted by Object Number |
| Tab delimiters | ✓ Standardized |
| Encoding issues | ✓ UTF-8 verified |

## File Reference

- **standardize_tsv.py** - Core standardization logic
- **standardize.sh** - Main script to run
- **validate_tsv.py** - Detailed validation & analysis
- **checksums.json** - Your integrity checksums
- **verification.txt** - Human-readable verification report
- **README.md** - Full documentation

## Common Commands

```bash
# Standardize with custom output name
./standardize.sh met_inventory.tsv my_output.tsv

# Validate standardization results
python3 validate_tsv.py met_inventory.tsv my_output.tsv

# Check file sizes
du -h met_inventory.tsv my_output.tsv

# Count records
tail -n +2 my_output.tsv | wc -l

# View first 10 records (with headers)
head -11 my_output.tsv | column -t -s $'\t'

# Manual checksum verification
sha256sum met_inventory_standardized.tsv
# Compare with value in checksums.json
```

## If Something Goes Wrong

1. **Check the verification.txt file** for detailed issue description
2. **Run validation** to see what changed:
   ```bash
   python3 validate_tsv.py met_inventory.tsv met_inventory_standardized.tsv
   ```
3. **Re-run** with the original source file to get a fresh standardization

## Data Integrity

Your checksums are stored in `checksums.json`:

```bash
cat checksums.json | python3 -m json.tool
```

This verifies:
- ✓ Original file hasn't been corrupted
- ✓ Standardized file matches its checksum
- ✓ When standardization occurred
- ✓ Which algorithm was used (SHA-256)

## Next Steps

1. ✓ Use `met_inventory_standardized.tsv` for import/analysis
2. ✓ Keep `checksums.json` with your files for future verification
3. ✓ Archive both together for data preservation
4. ✓ Share the standardized version while keeping original

---

**Questions?** See README.md for detailed documentation.
