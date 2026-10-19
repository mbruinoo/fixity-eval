# Met Museum Inventory TSV Standardization

This package contains a standardized version of the Met Museum inventory TSV file with complete fixity preservation using cryptographic checksums.

## Files Included

### Data Files
- **met_inventory.tsv** - Original source file (provided)
- **met_inventory_standardized.tsv** - Standardized output file with normalized formatting

### Documentation & Scripts
- **fixity_metadata.json** - Complete checksums and metadata for both source and output files
- **verify_and_document.py** - Python script that performs standardization and generates checksums
- **standardize_and_checksum.py** - Reusable Python script for verification at any time
- **STANDARDIZATION_REPORT.md** - Detailed report of all standardization procedures
- **README.md** - This file

## What Was Standardized

The source TSV file contained 110 records of Met Museum artworks with the following issues:

1. ✓ Inconsistent column header spacing
2. ✓ Variable whitespace in cell values
3. ✓ Inconsistent handling of empty cells
4. ✓ Tab delimiter consistency

### Standardization Actions

All formatting issues were resolved while **preserving 100% of the data content**:

- Column headers stripped of whitespace
- Cell values normalized (whitespace removed)
- Empty cells standardized consistently
- Tab delimiters verified throughout
- UTF-8 encoding preserved (supports multilingual content)
- Row structure validated (all rows have 4 columns)

## Data Structure

The standardized file contains 4 columns:

| Column | Description |
|--------|-------------|
| Object Date | Date or period of creation (e.g., "19th century", "ca. 1830–32") |
| Title | Name or description of the artwork |
| Object Number | Met Museum catalog/accession number |
| Link Resource | URL to the object in the Met's online collection |

**Records:** 110 artworks  
**Total Columns:** 4  
**Encoding:** UTF-8 (supports Chinese, Japanese, and other multilingual text)

## Fixity Preservation

### Checksums Provided

Both SHA-256 and MD5 checksums are provided for the source and output files in `fixity_metadata.json`:

```json
{
  "source_file": {
    "filename": "met_inventory.tsv",
    "checksums": {
      "sha256": "...",
      "md5": "..."
    }
  },
  "output_file": {
    "filename": "met_inventory_standardized.tsv",
    "checksums": {
      "sha256": "...",
      "md5": "..."
    }
  }
}
```

### Verification

To verify the integrity of the standardized file at any time:

```bash
# Using SHA-256
sha256sum met_inventory_standardized.tsv

# Using Python
python3 -c "import hashlib; f=open('met_inventory_standardized.tsv','rb'); print(hashlib.sha256(f.read()).hexdigest())"
```

Compare the result against the checksum in `fixity_metadata.json`.

## How to Use

### Quick Start
1. Use `met_inventory_standardized.tsv` for any data processing or analysis
2. Keep `met_inventory.tsv` and `fixity_metadata.json` as verification records

### To Re-verify at Any Time
```bash
python3 verify_and_document.py
```

This will:
- Calculate checksums of both files
- Validate the standardization
- Display verification results

### To Use the Standardization Script Independently
```bash
python3 standardize_and_checksum.py
```

## Data Integrity Features

✓ **No data loss** - All 110 records preserved  
✓ **No content modification** - Only formatting normalized  
✓ **Encoding preserved** - UTF-8 maintained for international characters  
✓ **URL integrity** - All links preserved exactly as provided  
✓ **Cryptographic verification** - SHA-256 and MD5 checksums provided  
✓ **Documented process** - Complete audit trail in this package  

## Example Records

Here are a few sample rows from the standardized file:

| Object Date | Title | Object Number | Link Resource |
|---|---|---|---|
| 19th century | | 91.1.396 | http://www.metmuseum.org/art/collection/search/51219 |
| ca. 1927 | "Plucky" Lindbergh Ready to "Hop Off" from Lindbergh Exhibit Cards series (W451) | 63.350.619.451.6 | http://www.metmuseum.org/art/collection/search/765705 |
| 1777 | L'Accord Parfait (Perfect Harmony), from "Le Monument du Costume" | 33.6.21 | http://www.metmuseum.org/art/collection/search/364221 |

## Support for Different Systems

The standardized TSV file works with:
- ✓ Excel and Google Sheets
- ✓ Python pandas (`pd.read_csv()`)
- ✓ R (`read.delim()`)
- ✓ SQL databases (via import)
- ✓ Any standard TSV/CSV processor
- ✓ Text editors and command-line tools

## Questions?

Refer to:
1. **STANDARDIZATION_REPORT.md** - Detailed technical report
2. **fixity_metadata.json** - Complete checksum information
3. **verify_and_document.py** - Source code of standardization process

---

**Created:** [Timestamp]  
**Format:** Tab-separated values (TSV)  
**Encoding:** UTF-8  
**Records:** 110  
**Columns:** 4
