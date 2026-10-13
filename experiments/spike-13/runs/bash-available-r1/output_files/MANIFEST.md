# Metropolitan Museum Inventory Data Standardization

## Project Overview
This archive contains the input data, transformation script, output data, and documentation for standardizing the Met Museum inventory TSV file.

## Files Included

### 1. Input Data
- **met_inventory.tsv**
  - Original Metropolitan Museum inventory data
  - 300 records, 4 columns
  - Columns: Object Date | Title | Object Number | Link Resource
  - MD5 Checksum: `6ec5bfc2d979ad12eb3343149beb8617`

### 2. Transformation Script
- **standardize_met_inventory.py**
  - Procedural Python 3 script for data standardization
  - Fully documented with docstrings
  - Includes fixity checking via MD5 checksums
  - Executable with command-line arguments
  - Can be version controlled and re-run on the same input to verify reproducibility

### 3. Output Data
- **met_inventory_standardized.tsv**
  - Standardized version of the input data
  - Same row count (300 records) and column count (4) as input
  - All transformations applied consistently
  - MD5 Checksum: `ea7849011acfd1def02051dbefcb64db`

### 4. Documentation
- **MANIFEST.md** (this file) - Project overview and file descriptions
- **CHECKSUMS.txt** - Checksum verification file for archival fixity

## Transformations Applied

### 1. Missing Value Handling
- **Object Date**: Empty values → `Unknown` (11 records affected)
- **Title**: Empty values → `Untitled` (25 records affected)

### 2. Text Encoding
- Decoded HTML entities (e.g., `&lt;` → `<`, `&gt;` → `>`)
- Removed HTML tags (e.g., `<i>`, `</i>`)

### 3. Date Standardization
| Original | Standardized |
|----------|--------------|
| B.C. | BCE |
| BC | BCE |
| A.C. | CE |
| A.H. | AH |
| circa | ca. |
| Circa | ca. |

### 4. Character Normalization
- En-dashes (–) → standard hyphens (-)
- Em-dashes (—) → standard hyphens (-)
- Multiple spaces → single spaces
- Leading/trailing whitespace → removed

### 5. Column Name Standardization
| Original | Standardized |
|----------|--------------|
| Object Date | Object_Date |
| Title | Title |
| Object Number | Object_Number |
| Link Resource | Link_Resource |

(Changed to snake_case format for database/programming compatibility)

## Fixity Verification

To verify the integrity of the archived files, use the provided checksums:

```bash
# Verify input file integrity
md5sum -c <<EOF
6ec5bfc2d979ad12eb3343149beb8617  met_inventory.tsv
EOF

# Verify output file integrity
md5sum -c <<EOF
ea7849011acfd1def02051dbefcb64db  met_inventory_standardized.tsv
EOF

# Verify both files
md5sum -c CHECKSUMS.txt
```

## How to Re-run the Transformation

### Prerequisites
```bash
pip install pandas
```

### Execute the Script
```bash
python3 standardize_met_inventory.py met_inventory.tsv met_inventory_standardized.tsv
```

### Expected Output
The script will:
1. Read the input TSV file
2. Apply all transformations step-by-step
3. Write the standardized output file
4. Calculate and display MD5 checksums for both files
5. Provide a summary report

The output checksums should match the original checksums if the input file has not been modified.

## Data Quality Notes

### Before Standardization
- 11 missing Object Date values (3.7%)
- 25 missing Title values (8.3%)
- Inconsistent date notation (B.C., BC, circa, Circa)
- Mixed dash characters (en-dash, em-dash, hyphen)
- HTML entities in titles
- Inconsistent whitespace

### After Standardization
- 0 missing critical values (all filled with meaningful defaults)
- Consistent date notation across all records
- Uniform dash characters (standard hyphen)
- Clean, readable titles
- Standardized whitespace
- Professional column naming conventions

## Archival Information

**Execution Date/Time**: 2024-10-13T21:13:47.351523 UTC  
**Python Version**: 3.9+ (pandas 1.0+)  
**Script Author**: Data Standardization Pipeline  
**Purpose**: Ensure data consistency and quality for downstream analysis  
**Reproducibility**: Fully reproducible - re-running the script on the same input will produce identical output

## How to Use This Archive

1. **Verification**: Use CHECKSUMS.txt to verify data integrity
2. **Documentation**: Refer to this MANIFEST for transformation details
3. **Reproducibility**: Run standardize_met_inventory.py to regenerate output
4. **Version Control**: Archive all three files (input, script, output) together
5. **Future Processing**: Use met_inventory_standardized.tsv as input for analysis pipelines

## Contact & Support

For questions about the transformations applied, see the detailed documentation in the script header and function docstrings.

---
*Archive created for data preservation and reproducibility*
