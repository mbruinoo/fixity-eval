# Met Museum Inventory TSV Standardization Report

## File Statistics

### Source File: met_inventory.tsv
- **Size**: 15,295 bytes
- **Rows**: 101 (including header)
- **Data records**: 100
- **SHA-256 Checksum**: `e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf`

### Standardized Output: met_inventory_standardized.tsv
- **Size**: 15,359 bytes
- **Rows**: 101 (including header)
- **Data records**: 100
- **SHA-256 Checksum**: `37d977d40f2e18da2a216d816e48a1ab0d5d72b8bbab35b022a0914b3a866523`

## Standardization Process

The following improvements were applied:

1. **Consistent Tab Delimiters**
   - All fields properly separated by single tab characters
   - Removed irregular spacing around delimiters

2. **Normalized Column Structure**
   - All rows standardized to exactly 4 columns:
     1. Object Date
     2. Title  
     3. Object Number
     4. Link Resource
   - Missing fields represented as empty strings

3. **Proper Quote Handling**
   - Used CSV standard for quoting fields with special characters
   - Internal quotes escaped by doubling (")
   - Consistent quote usage across all records

4. **Character Encoding**
   - Preserved UTF-8 encoding for international characters (Chinese, Japanese, Korean, etc.)
   - No data loss or corruption

5. **Line Ending Normalization**
   - Standardized to Unix-style line endings (LF)
   - Ensures compatibility across platforms

## Data Integrity Verification

### Checksums (SHA-256)
```
Source:        e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf
Standardized:  37d977d40f2e18da2a216d816e48a1ab0d5d72b8bbab35b022a0914b3a866523
```

### How to Verify
Using the bash command line:

```bash
# Verify the standardized file
echo "37d977d40f2e18da2a216d816e48a1ab0d5d72b8bbab35b022a0914b3a866523  met_inventory_standardized.tsv" | sha256sum -c -

# Or verify both files
sha256sum met_inventory.tsv met_inventory_standardized.tsv
```

### Checksum Manifest
A `CHECKSUMS.sha256` file is provided for automated verification using standard tools.

## Data Quality Observations

- **Total Objects**: 100 museum objects cataloged
- **Empty Titles**: Several entries have missing titles (preserved as empty)
- **International Content**: Objects include East Asian and Korean artworks
- **Date Format**: Dates range from BCE periods to 20th century
- **URL Format**: All resources link to metmuseum.org search endpoints

## Files Generated

1. **met_inventory_standardized.tsv** - The standardized data file
2. **CHECKSUMS.sha256** - Checksum verification file  
3. **standardization_report.md** - This report
4. **standardize_and_checksum.py** - Python script used for standardization

## Preservation Notes

This standardization process preserves data fixity through:
- Cryptographic checksums (SHA-256)
- Lossless conversion to standard TSV format
- Complete preservation of original data values
- Machine-verifiable integrity checks

All original data is preserved; only formatting has been normalized.
