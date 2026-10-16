# Metropolitan Museum of Art Inventory - Standardization Report

## Data Fixity Verification

### Source File
- **SHA-256**: `1f487d12804e5cbd285ff6cf9f1d560595731455546be9230f887b7611e7860e`
- **MD5**: `1c2323177f9fb869f2df32f5cb85e7a6`

### Output File
- **SHA-256**: `d29688f6cfe8b8821f88dc78fff57bd32bf3555fb3a43cf7a4315f4143ea4853`
- **MD5**: `40a44e788343362f9b0ba4a619480414`

## Changes Made

1. **Structure**: Standardized to 4 columns (Object Date, Title, Object Number, Link Resource)
2. **Headers**: Ensured proper header row
3. **Encoding**: UTF-8 encoding throughout
4. **Line Endings**: Normalized to LF (Unix-style)
5. **Whitespace**: Stripped trailing spaces from all fields
6. **Quoting**: Applied CSV minimal quoting strategy

## Output Statistics

- **Total Records**: 300
- **Columns**: 4
- **Format**: Tab-separated values (TSV)

## Files Generated

- `met_inventory_standardized.tsv` - The standardized data file
- `fixity_report.json` - Structured checksum verification report
- `README.md` - This documentation file
- `standardize_met_inventory.py` - Processing script for reproducibility

## Verification

To verify data integrity:

```bash
# Check SHA-256
sha256sum met_inventory_standardized.tsv
# Should match: d29688f6cfe8b8821f88dc78fff57bd32bf3555fb3a43cf7a4315f4143ea4853

# Check MD5
md5sum met_inventory_standardized.tsv
# Should match: 40a44e788343362f9b0ba4a619480414
```
