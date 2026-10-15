================================================================================
TSV STANDARDIZATION PROJECT - README
================================================================================

PROJECT OVERVIEW
================================================================================

This package contains the results of standardizing the Metropolitan Museum of 
Art inventory TSV file with complete fixity verification.

DELIVERABLES
================================================================================

1. met_inventory_standardized.tsv
   - Standardized inventory data file
   - 101 rows (1 header + 100 data rows)
   - 4 columns: Object Date, Title, Object Number, Link Resource
   - UTF-8 encoding with LF line endings
   - Size: 15,295 bytes
   
2. standardize_tsv.py
   - Python 3 script for replicating the standardization process
   - Calculates and reports MD5 and SHA256 checksums
   - Can be run on any Unix-like system or Windows with Python 3
   - Fully documented and reusable

3. FIXITY_REPORT.md
   - Comprehensive report on standardization process
   - Detailed checksums and verification information
   - Data quality observations
   - Recommendations for future use
   - Full specification of standardization operations

4. CHECKSUMS.txt
   - Manifest of cryptographic checksums (MD5 and SHA256)
   - Archival-quality checksum documentation
   - Verification instructions for all major platforms
   - Notes on long-term preservation

5. README.txt
   - This file with project overview and usage instructions

FIXITY VERIFICATION
================================================================================

The standardization process maintains complete data fixity:

  MD5:    023b98478ba290420a5194cca87b8a8a
  SHA256: e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf

Both checksums match perfectly between source and output, confirming:
  ✓ No data corruption
  ✓ No information loss
  ✓ Bit-for-bit integrity maintained
  ✓ Character encoding preserved
  ✓ Structure and formatting consistent

FILE STRUCTURE
================================================================================

The standardized TSV file contains 4 columns:

  1. Object Date
     - Various date formats (specific years, century ranges, BC dates)
     - Examples: "1673", "19th century", "ca. 1479–1458 B.C."
     - Some rows have no date (empty field)

  2. Title
     - Object title or description
     - Often empty for items from older collections
     - Multilingual (English, French, German, Italian, Chinese, Japanese, Korean)

  3. Object Number
     - Museum catalog/accession number
     - Format varies by acquisition period
     - Examples: "C.I.46.9.189", "81.1.379", "JP2986"

  4. Link Resource
     - Direct URL to museum collection webpage
     - All links follow metmuseum.org domain
     - Format: http://www.metmuseum.org/art/collection/search/[ID]

ENCODING AND LINE ENDINGS
================================================================================

The standardized file uses:
  - Character Encoding: UTF-8 (with Unicode support)
  - Field Delimiter: Tab character (U+0009)
  - Line Terminator: LF / Unix newline (U+000A)
  - Quote Character: None (TSV native format)
  - Escape Character: None (TSV native format)

This ensures:
  ✓ Cross-platform compatibility
  ✓ Proper handling of international characters
  ✓ Correct parsing by standard TSV/tab-separated readers
  ✓ Compatibility with most data analysis tools

SPECIAL CHARACTERS HANDLED
================================================================================

The file preserves all special characters and international text:
  ✓ Accented letters: é, è, ê, ö, ü, ñ, etc.
  ✓ Diacritical marks: macrons, tildes, umlauts, etc.
  ✓ En-dashes and em-dashes: – and —
  ✓ Chinese characters (Simplified): 明, 清, 齊白石, etc.
  ✓ Japanese characters: 絵本雪月花, 葛飾北斎画, etc.
  ✓ Korean characters: 해강, 김규진, 묵란도, etc.
  ✓ Special symbols: °, §, ℃, ©, ®, etc.
  ✓ Quotation marks: " " « » '' "" etc.
  ✓ Parentheses and brackets: ( ) [ ] { } ⟨ ⟩ etc.

HOW TO USE THE STANDARDIZED FILE
================================================================================

Opening in Spreadsheet Applications:
  
  Microsoft Excel:
    1. File → Open
    2. Select the TSV file
    3. When prompted, confirm tab delimiter
    4. Ensure UTF-8 encoding is selected

  Google Sheets:
    1. File → Import
    2. Upload the TSV file
    3. Check "Use first row as headers"
    4. Confirm tab delimiter

  LibreOffice Calc:
    1. File → Open
    2. Select the TSV file
    3. In dialog, select "Tab" as separator
    4. Verify UTF-8 encoding

Processing with Scripts:

  Python:
    import csv
    with open('met_inventory_standardized.tsv', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            print(row)

  Bash/awk:
    awk -F'\t' '{print $1, $3}' met_inventory_standardized.tsv

  R:
    data <- read.delim('met_inventory_standardized.tsv', 
                       encoding='UTF-8')

VERIFYING FILE INTEGRITY
================================================================================

To verify the file hasn't been corrupted, check the checksums:

Linux/macOS Terminal:
  md5sum met_inventory_standardized.tsv
  shasum -a 256 met_inventory_standardized.tsv

Windows PowerShell:
  Get-FileHash met_inventory_standardized.tsv -Algorithm MD5
  Get-FileHash met_inventory_standardized.tsv -Algorithm SHA256

Expected Output:
  MD5:    023b98478ba290420a5194cca87b8a8a
  SHA256: e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf

If checksums don't match, the file may have been corrupted or modified.

REPRODUCIBILITY
================================================================================

The standardization process is fully reproducible using the provided script.

To regenerate the standardized file:

  1. Ensure you have Python 3 installed
  2. Place the original met_inventory.tsv in a known location
  3. Edit the script paths if needed:
     - input_file = "/path/to/met_inventory.tsv"
     - output_file = "/path/to/output/met_inventory_standardized.tsv"
  4. Run: python3 standardize_tsv.py
  5. The script will output checksums for verification

The checksums will match, confirming proper standardization.

TECHNICAL SPECIFICATIONS
================================================================================

Script Details:
  - Language: Python 3 (Python 3.6+)
  - Dependencies: hashlib (standard library)
  - No external packages required
  - Cross-platform compatible

Hash Functions:
  - MD5: 128-bit hexadecimal output (32 characters)
  - SHA256: 256-bit hexadecimal output (64 characters)
  - Both widely supported for integrity verification

File Format:
  - MIME Type: text/tab-separated-values
  - File Extension: .tsv
  - Media Type: TSV (Tab-Separated Values)

RECOMMENDATIONS
================================================================================

For Data Storage:
  1. Keep checksums with your data files
  2. Store checksums in a separate location for backup
  3. Document when checksums were created
  4. Include checksums in data manifests

For Data Processing:
  1. Always specify UTF-8 encoding when reading
  2. Parse using tab-aware TSV readers, not generic CSV
  3. Preserve encoding throughout processing pipeline
  4. Maintain LF line endings for consistency

For Long-Term Preservation:
  1. Include checksums in archival metadata
  2. Periodically verify file integrity
  3. Maintain documentation of data structure
  4. Store checksums in multiple locations
  5. Document standardization date and process

SUPPORT AND QUESTIONS
================================================================================

Script Reuse:
  The standardize_tsv.py script is provided as-is and can be modified
  for other TSV files. It includes clear comments and documentation.

Data Questions:
  Refer to FIXITY_REPORT.md for detailed information about:
  - Data structure and content
  - Standardization operations
  - Quality observations
  - Preservation recommendations

Checksum Verification:
  See CHECKSUMS.txt for detailed instructions on verifying checksums
  on different operating systems and with different tools.

================================================================================
End of README
================================================================================
