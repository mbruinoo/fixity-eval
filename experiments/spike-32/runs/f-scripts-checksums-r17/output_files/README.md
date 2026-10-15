# Met Inventory TSV Standardization

This directory contains scripts and documentation for standardizing the Metropolitan Museum inventory TSV file with cryptographic verification of fixity.

## Files

- **standardize_tsv.py** - Python script that standardizes the TSV file and generates SHA256 checksums
- **verify_checksums.sh** - Bash script to verify file checksums
- **standardization_manifest.txt** - Manifest containing checksums and processing details
- **met_inventory_standardized.tsv** - The standardized output file
- **met_inventory_standardized.tsv.sha256** - Checksum file for verification

## Standardization Process

The Python script performs the following operations:

1. **Reads** the original TSV file with proper delimiter handling
2. **Normalizes** column headers by stripping leading/trailing whitespace
3. **Validates** row structure to ensure consistent column count
4. **Strips** whitespace from all data cells
5. **Writes** output with consistent Unix line endings (LF)
6. **Preserves** UTF-8 encoding for international characters
7. **Calculates** SHA256 checksums for both source and output files

## Usage

### Run Standardization
```bash
python3 standardize_tsv.py
```

### Verify Checksums
```bash
bash verify_checksums.sh
```

### Manual Verification
```bash
sha256sum -c met_inventory_standardized.tsv.sha256
```

## Checksum Verification

The standardization process ensures data integrity through cryptographic checksums:

- **Source Checksum** (SHA256): Computed on original file before processing
- **Output Checksum** (SHA256): Computed on standardized file after processing
- **Manifest**: Documents both checksums and processing metadata

To verify that the standardized file has not been corrupted:
```bash
sha256sum --check met_inventory_standardized.tsv.sha256
```

Expected output:
```
met_inventory.tsv: OK
met_inventory_standardized.tsv: OK
```

## What Was Standardized

### Column Headers
- Removed extra whitespace from headers
- Headers now: `Object Date`, `Title`, `Object Number`, `Link Resource`

### Data Cells
- Stripped leading/trailing whitespace from all cells
- Preserved internal whitespace and special characters
- Maintained empty cells for missing data

### Line Endings
- Converted to Unix format (LF only)
- Ensures consistency across platforms

### Encoding
- Maintained UTF-8 encoding throughout
- Supports international characters (Chinese, Korean, Japanese)

## Data Integrity

The manifest file (`standardization_manifest.txt`) contains:
- Source file SHA256 hash
- Output file SHA256 hash  
- Processing timestamp (ISO format)
- Row and column counts
- Detailed change log

This information allows you to:
1. Verify the file hasn't been modified since standardization
2. Detect any corruption or tampering
3. Audit the standardization process

## Example: Verifying File Integrity

```bash
# Check that the standardized file matches its checksum
sha256sum -c met_inventory_standardized.tsv.sha256

# If you make any changes to the file and want to generate a new checksum:
sha256sum met_inventory_standardized.tsv > met_inventory_standardized.tsv.new.sha256
```

## Handling Large Files

The standardize_tsv.py script processes files efficiently:
- Reads entire file into memory for CSV parsing
- Processes 96 rows efficiently (4,096-byte chunks for checksum calculation)
- Suitable for files up to several gigabytes

For very large files, consider processing in chunks.

## Notes

- Original file is preserved in `/mnt/user-data/uploads/met_inventory.tsv`
- Standardized file is in `/mnt/user-data/outputs/met_inventory_standardized.tsv`
- All scripts include proper error handling and validation
- Scripts are executable from the command line
