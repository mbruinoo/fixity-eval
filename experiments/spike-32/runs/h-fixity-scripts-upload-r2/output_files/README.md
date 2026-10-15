# Metropolitan Museum TSV Standardization Project

## Quick Start

This package standardizes a Met Museum inventory TSV file with cryptographic checksum verification for data fixity.

### Files in This Package

```
met_inventory.tsv                          - Source TSV file
met_inventory_standardized.tsv             - Output (standardized)
met_inventory_standardization.log          - Detailed standardization report
CHECKSUMS.txt                              - SHA-256 checksum record
standardize_tsv.py                         - Python standardization script
run_standardization.sh                     - Bash execution wrapper
STANDARDIZATION_GUIDE.md                   - Comprehensive documentation
README.md                                  - This file
```

## What This Does

1. **Standardizes** the TSV file by:
   - Normalizing tab delimiters
   - Trimming whitespace
   - Validating column structure
   - Ensuring UTF-8 encoding

2. **Preserves Fixity** by:
   - Computing SHA-256 checksums for source file
   - Computing SHA-256 checksums for output file
   - Recording checksums in `CHECKSUMS.txt`
   - Enabling future integrity verification

## Data Overview

The Met Museum inventory contains:
- **101 rows** of art collection metadata
- **4 columns**: Object Date, Title, Object Number, Link Resource
- **Content**: Diverse cultural artifacts spanning multiple centuries
- **Languages**: English, French, Italian, Chinese, Japanese, Korean
- **Date range**: 4th century BCE to 20th century

## How to Use

### Run Standardization
```bash
bash run_standardization.sh
```

This will:
1. Compute source file checksum
2. Run Python standardization
3. Compute output file checksum
4. Generate verification records

### Verify File Integrity
```bash
# Verify both files
sha256sum -c CHECKSUMS.txt

# Or manually check one file
sha256sum met_inventory_standardized.tsv
# Compare output with SHA-256 in CHECKSUMS.txt
```

### Review Results
```bash
# View standardization details
cat met_inventory_standardization.log

# View checksum record
cat CHECKSUMS.txt

# Compare files (if diff is empty, they're identical except formatting)
diff met_inventory.tsv met_inventory_standardized.tsv
```

## Key Features

### Data Preservation
- ✓ All original content preserved
- ✓ No data values modified
- ✓ Multilingual text support (CJK, Cyrillic, etc.)
- ✓ Special characters maintained

### Standardization
- ✓ Consistent tab delimiters
- ✓ UTF-8 encoding throughout
- ✓ Trimmed whitespace
- ✓ Validated column structure

### Fixity Verification
- ✓ SHA-256 checksums (cryptographically secure)
- ✓ Documented in CHECKSUMS.txt
- ✓ Reproducible verification
- ✓ Detailed audit trail in log file

## Checksums

### Source File
```
File: met_inventory.tsv
SHA-256: [computed by running script]
```

### Output File
```
File: met_inventory_standardized.tsv
SHA-256: [computed by running script]
```

See `CHECKSUMS.txt` for actual values after running standardization.

## Column Structure

| Column | Description | Example |
|--------|-------------|---------|
| Object Date | Date or date range | "ca. 1479–1458 B.C." |
| Title | Object title/description | "Funerary Cone of Nakht and His Wife Senhotep" |
| Object Number | Museum catalog number | "30.6.183" |
| Link Resource | URL to catalog entry | "http://www.metmuseum.org/art/collection/search/554919" |

## Data Statistics

After standardization:
- **Total Records**: 101 data rows + 1 header row
- **Total Columns**: 4
- **Encoding**: UTF-8 (no BOM)
- **Line Endings**: Unix (LF)
- **Delimiter**: Tab character (0x09)

## Quality Assurance

The standardization process:
1. Parses the entire file
2. Validates column headers
3. Normalizes each field
4. Counts rows read and written
5. Computes cryptographic checksums
6. Reports any issues or warnings
7. Generates audit trail in log file

## Long-Term Preservation

This standardization supports digital preservation by:
- Using standard, open TSV format
- Maintaining UTF-8 encoding
- Providing cryptographic fixity verification
- Creating reproducible, documented workflows
- Enabling future integrity checks

## Verification Workflow

```
Source File → SHA-256₁
                      ↓
Standardization Script
                      ↓
Output File → SHA-256₂

Record SHA-256₁ and SHA-256₂
                      ↓
Later: Compute SHA-256' on Source
       Verify SHA-256' = SHA-256₁
                      ↓
Later: Compute SHA-256' on Output
       Verify SHA-256' = SHA-256₂
```

If checksums match: ✓ Files are intact
If checksums differ: ✗ Files have been modified

## Requirements

- Python 3.x (for standardize_tsv.py)
- Bash shell (for run_standardization.sh)
- Standard Unix utilities (sha256sum)

## Support & Documentation

- See `STANDARDIZATION_GUIDE.md` for comprehensive documentation
- See `met_inventory_standardization.log` for detailed standardization report
- See `CHECKSUMS.txt` for fixity verification records

## Next Steps

1. Run the standardization script
2. Review the log file for any warnings
3. Verify checksums against CHECKSUMS.txt
4. Use met_inventory_standardized.tsv for further processing
5. Archive CHECKSUMS.txt for future integrity checks

---

**Created**: 2025
**Purpose**: Standardization and preservation of Met Museum inventory data
**Format**: Tab-Separated Values (TSV) with UTF-8 encoding
**Verification**: SHA-256 checksums for fixity assurance
