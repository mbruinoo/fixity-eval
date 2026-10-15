# TSV Standardization Project

## Overview

This project standardizes the Met Museum inventory TSV file using automated scripts with cryptographic verification of data fixity.

## Files Included

### Output Files

1. **met_inventory_standardized.tsv** - The standardized dataset with the following improvements:
   - Headers normalized to snake_case: `object_date`, `title`, `object_number`, `link_resource`
   - Empty cells standardized to "N/A" for consistency
   - UTF-8 encoding with proper tab-separation
   - 92 data rows (plus 1 header row)

2. **standardization_report.json** - Detailed processing report containing:
   - SHA256 checksums of both source and output files
   - Processing timestamp
   - Data summary (row count, column names)
   - List of standardization changes applied

### Scripts

1. **standardize_tsv.py** - Main standardization script
   - Reads the input TSV file
   - Normalizes headers to snake_case
   - Replaces empty cells with "N/A"
   - Computes SHA256 checksums for both source and output
   - Generates a JSON report

2. **verify_checksums.py** - Verification script
   - Compares current file checksums against recorded values
   - Validates data integrity and authenticity
   - Can be run at any time to confirm files haven't been modified

## Data Fixity & Checksums

Checksums are used to ensure data integrity. If files are modified after standardization, checksums will change, alerting you to unauthorized modifications.

### Source File Checksum (SHA256)
```
93061a6c9654006447accb638ace12db0a85e1353f3e44444f976844f78452c9
```

### Standardized Output Checksum (SHA256)
```
616baa1f6dde23d1bed5edb5bf22e2ebd03dee72e6cc5957fe9c5ece3c41d9fb
```

## Standardization Changes

### Before
- **Header**: "Object Date" (with space and mixed case)
- **Empty cells**: Blank/missing values
- **Data**: Inconsistent formatting

### After
- **Header**: "object_date" (snake_case, consistent)
- **Empty cells**: Marked as "N/A" (explicit, searchable)
- **Data**: Consistent formatting with normalization applied

## How to Verify Integrity

To verify that the output files haven't been modified since processing:

```bash
python3 verify_checksums.py
```

This will compare the current files against the checksums recorded in `standardization_report.json`.

## Data Structure

### Columns (4 total)
1. **object_date** - Date or period of the object
2. **title** - Title/description of the museum object
3. **object_number** - Museum catalog/accession number
4. **link_resource** - URL to the object record in the Met's online collection

### Sample Rows
```
object_date                 title                           object_number           link_resource
late 19th century           N/A                            C.I.46.9.189            http://www.metmuseum.org/art/collection/search/88288
1673                        "Corneille Emmantelée, Mon...  56.644.21(15)          http://www.metmuseum.org/art/collection/search/393569
ca. 1479–1458 B.C.         Arrow                          36.3.225                http://www.metmuseum.org/art/collection/search/560249
```

## Processing Statistics

- **Total data rows**: 92
- **Processing timestamp**: 2026-10-15T03:22:27.062661
- **Encoding**: UTF-8
- **Delimiter**: Tab character (0x09)

## Technical Details

### Checksum Algorithm
- **Algorithm**: SHA256 (FIPS 180-4)
- **Purpose**: Ensure data integrity and detect unauthorized modifications
- **Verification**: Compare current file checksums against recorded values

### Standardization Process
1. Read TSV with Python's csv module (tab-delimited)
2. Normalize all header values to lowercase snake_case
3. Standardize data rows by trimming whitespace and marking empty cells as "N/A"
4. Compute SHA256 checksums for audit trail
5. Write standardized output with consistent formatting
6. Generate JSON report with full metadata

## Usage Examples

### Verify File Integrity
```bash
python3 verify_checksums.py
```

### Re-standardize or Apply to New Files
Edit the file paths in `standardize_tsv.py` and run:
```bash
python3 standardize_tsv.py
```

### Examine the Report
```bash
cat standardization_report.json
```

Or with formatting:
```bash
python3 -m json.tool standardization_report.json
```

## Quality Assurance

✓ All data validated against source checksums  
✓ Headers consistently normalized  
✓ Empty cells explicitly marked  
✓ UTF-8 encoding verified  
✓ Tab delimiters confirmed  
✓ Checksum integrity verified  

---

**Generated**: 2026-10-15  
**Status**: ✓ Complete and Verified
