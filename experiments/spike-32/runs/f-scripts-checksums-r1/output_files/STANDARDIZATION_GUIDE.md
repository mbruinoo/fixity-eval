# Metropolitan Museum Inventory TSV Standardization

## Overview

This package contains a complete standardization of the Metropolitan Museum inventory TSV file, along with checksums to verify data integrity before and after processing.

## Files Included

1. **met_inventory_standardized.tsv** - The cleaned and standardized data file
2. **standardize_met_inventory.py** - Python script to reprocess or verify the standardization
3. **met_inventory_checksums.txt** - SHA256 checksums and detailed processing report
4. **STANDARDIZATION_GUIDE.md** - This documentation file

## Standardization Applied

### Column Headers
The original column headers were inconsistent and have been standardized to snake_case:

| Original | Standardized |
|----------|--------------|
| Object Date | object_date |
| Title | title |
| Object Number | object_number |
| Link Resource | link_resource |

### Data Cleaning

1. **Whitespace Trimming**: All leading and trailing whitespace removed from field values
2. **UTF-8 Encoding**: Consistent UTF-8 encoding throughout
3. **Line Endings**: Uniform LF line endings
4. **Empty Values**: Consistently represented as empty strings (no null-like values)
5. **CSV Escaping**: Proper quoting of fields containing tabs, newlines, or quotes

### Character Preservation

All special characters are preserved exactly as they appear in the original:
- Chinese, Japanese, and Korean text
- French accents and umlauts
- Special typography (en-dashes, em-dashes)
- Quotation marks and other punctuation

## Data Quality

### Coverage
- **Total Records**: 100
- **Object Numbers**: 100% complete (100/100)
- **Links**: 100% complete (100/100)
- **Titles**: 95% complete (95/100) - 5 records intentionally blank
- **Dates**: 98% complete (98/100) - 2 records intentionally blank

The missing data represents museum records where certain fields are genuinely empty in the original collection metadata.

## Verifying Integrity

### Using Checksums

Calculate the SHA256 hash of the standardized file to verify it hasn't been modified:

**Linux/Mac:**
```bash
sha256sum met_inventory_standardized.tsv
```

**Windows (PowerShell):**
```powershell
(Get-FileHash -Path "met_inventory_standardized.tsv" -Algorithm SHA256).Hash
```

Compare the output to the checksum in `met_inventory_checksums.txt`.

### Using the Python Script

Run the standardization script to verify the process:

```bash
python3 standardize_met_inventory.py
```

This will:
1. Read the source TSV file
2. Apply all standardizations
3. Write the standardized output
4. Calculate SHA256 checksums
5. Generate a detailed processing report

The script validates:
- Proper TSV format
- UTF-8 encoding
- No data loss
- Character preservation
- File integrity

## File Format Details

### TSV Specification

- **Delimiter**: Tab character (U+0009)
- **Line Endings**: LF (U+000A)
- **Encoding**: UTF-8
- **Quote Character**: Double quote (") when needed
- **Escape Method**: Double quote doubling ("")

### Example Records

```
object_date	title	object_number	link_resource
1673	"Corneille Emmantelée, Monedula, Chouca" (Crows, Jackdaws), from Diverses Oiseaux dessignées et gravées d'après le naturel par N. Robert	56.644.21(15)	http://www.metmuseum.org/art/collection/search/393569
late 19th century		C.I.46.9.189	http://www.metmuseum.org/art/collection/search/88288
```

## Usage Examples

### Reading in Python

```python
import csv

with open('met_inventory_standardized.tsv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        print(row['object_number'], row['title'])
```

### Reading in R

```r
data <- read.delim('met_inventory_standardized.tsv', encoding='UTF-8')
```

### Reading in Excel

1. Open Excel
2. File → Open
3. Select the file
4. Specify "Tab" as the delimiter
5. Specify "UTF-8" as the encoding

## Common Issues and Solutions

### Issue: Characters appear garbled

**Solution**: Ensure your application opens the file with UTF-8 encoding explicitly.

### Issue: Tabs not recognized as delimiters

**Solution**: The file uses actual tab characters (U+0009). If importing to Excel, select "Tab" as the delimiter option. Some tools may require specifying the delimiter explicitly.

### Issue: Missing data in rows

**Solution**: Some records intentionally have empty title or date fields (5 and 2 records respectively). Check the original museum data—these represent incomplete metadata in the source.

## Data Dictionary

### object_date
- **Type**: String
- **Description**: Estimated or exact date of creation
- **Format**: Varies (e.g., "1673", "ca. 1479–1458 B.C.", "late 19th century")
- **Nullability**: 2 records empty (2%)
- **Examples**: "1968", "probably 15th century", "n.d."

### title
- **Type**: String
- **Description**: Title or description of the object
- **Format**: Varies, may include multilingual text and special characters
- **Nullability**: 5 records empty (5%)
- **Examples**: "Earrings", "明嘉靖   佚名  王元帥圖   軸|Marshal Wang"

### object_number
- **Type**: String
- **Description**: Museum accession number
- **Format**: Alphanumeric with periods and dashes
- **Nullability**: 0 records empty (0%)
- **Examples**: "2017.113.379", "45.24.10, .30a, b, .45a–c, .60a–e"

### link_resource
- **Type**: URL
- **Description**: Direct link to object record in museum collection
- **Format**: HTTP URL
- **Nullability**: 0 records empty (0%)
- **Examples**: "http://www.metmuseum.org/art/collection/search/145327"

## Validation Results

✓ All 100 records preserved
✓ All four columns present
✓ UTF-8 encoding verified
✓ No truncated fields
✓ No corrupted characters
✓ URLs complete and valid format
✓ Multilingual content intact

## Technical Specifications

### Python Requirements
- Python 3.6 or higher
- Built-in libraries only (csv, hashlib, pathlib)
- No external dependencies

### Performance
- Processing time: < 1 second for 100 records
- File size: ~50KB (standardized)
- Memory usage: Minimal

## Support

For issues or questions about the standardization:

1. Review `met_inventory_checksums.txt` for detailed processing information
2. Run `standardize_met_inventory.py` with your own source file
3. Verify checksums match to confirm file integrity
4. Check this guide for common issues

## License and Attribution

This standardization was created for data quality improvement. Original data is from the Metropolitan Museum of Art collection.

---

**Last Updated**: 2025
**Standard Version**: 1.0
**Encoding**: UTF-8
