# Usage Examples & Demonstrations

## Example 1: Basic Standardization

### Command
```bash
./standardize.sh met_inventory.tsv
```

### Expected Output
```
======================================
TSV Standardizer with Checksum Preservation
======================================

[INFO] Input file: met_inventory.tsv
[INFO] Output file: met_inventory_standardized.tsv

[INFO] Running standardization script...
  Input file: met_inventory.tsv
  Output file: met_inventory_standardized.tsv

Calculating source checksum...
Source SHA-256: a1b2c3d4e5f6789... [64 hex chars]

Standardizing TSV file...
Header columns: 4
Header: ['Object Date', 'Title', 'Object Number', 'Link Resource']
Data rows: 100
Max columns in data: 4

✓ File standardized successfully

Calculating output checksum...
Output SHA-256: f6e5d4c3b2a1987... [64 hex chars]

Logging checksums to checksums.json...

============================================================
STANDARDIZATION COMPLETE
============================================================
Source file: met_inventory.tsv
  SHA-256: a1b2c3d4e5f6789...

Output file: met_inventory_standardized.tsv
  SHA-256: f6e5d4c3b2a1987...

Checksum log: checksums.json
============================================================

File Statistics
================
Source file (met_inventory.tsv):
  Lines: 101 (header + 100 records)
  Size: 18.5K

Output file (met_inventory_standardized.tsv):
  Lines: 101 (header + 100 records)
  Size: 18.2K

[INFO] Verifying checksums...
[INFO] Verifying source file integrity...
✓ Source file integrity verified
[INFO] Verifying output file integrity...
✓ Output file integrity verified

[INFO] All verifications passed!
[INFO] Checksum verification report saved to: verification.txt
```

## Example 2: Validation After Standardization

### Command
```bash
python3 validate_tsv.py met_inventory.tsv met_inventory_standardized.tsv
```

### Expected Output
```
======================================================================
TSV FILE VALIDATION AND COMPARISON
======================================================================

[1] VALIDATING SOURCE FILE
----------------------------------------------------------------------
File: met_inventory.tsv
✓ Successfully loaded
  Rows: 100
  Columns: 4
  Size: 18456 bytes
  Column Consistency: ✗
  Issues found (5):
    - Column inconsistency in 3 rows
    - Not sorted: row 45 value '81.1.379' < 'C.I.46.9.189'

[2] VALIDATING OUTPUT FILE
----------------------------------------------------------------------
File: met_inventory_standardized.tsv
✓ Successfully loaded
  Rows: 100
  Columns: 4
  Size: 18210 bytes
  Column Consistency: ✓
  Sorted by Object Number: ✓
  Issues: None ✓

[3] COMPARISON
----------------------------------------------------------------------
✓ Row count preserved: 100
✓ Column count preserved: 4
✓ All rows have consistent column count

[4] EMPTY FIELDS ANALYSIS
----------------------------------------------------------------------
Source file empty fields by column:
  Object Date: 2 (2.0%)
  Title: 15 (15.0%)
  Object Number: 0 (0.0%)
  Link Resource: 0 (0.0%)

Output file empty fields by column:
  Object Date: 2 (2.0%)
  Title: 15 (15.0%)
  Object Number: 0 (0.0%)
  Link Resource: 0 (0.0%)

[5] UNICODE CONTENT
----------------------------------------------------------------------
✓ File contains Unicode characters (sample): ['明', '嘉', '靖', '日', '本']

[6] SUMMARY
----------------------------------------------------------------------
✓ STANDARDIZATION SUCCESSFUL
  - All data preserved
  - Column consistency verified
  - Data properly sorted
  - No outstanding issues

======================================================================
```

## Example 3: Future Verification

### Command (Six Months Later)
```bash
./verify_checksums.sh
```

### Expected Output
```
[✓] Loading checksums from checksums.json...

================================
VERIFYING SOURCE FILE
================================
File: met_inventory.tsv

[✓] File verified: met_inventory.tsv
  Expected: a1b2c3d4e5f6789...
  Actual:   a1b2c3d4e5f6789...
  Status:   ✓ MATCH

================================
VERIFYING OUTPUT FILE
================================
File: met_inventory_standardized.tsv

[✓] File verified: met_inventory_standardized.tsv
  Expected: f6e5d4c3b2a1987...
  Actual:   f6e5d4c3b2a1987...
  Status:   ✓ MATCH

================================
VERIFICATION SUMMARY
================================

✓ ALL FILES VERIFIED SUCCESSFULLY
  Both source and output files match their stored checksums.
  Data integrity is confirmed.

[✓] Detailed report saved to: checksum_verification_report.txt
```

## Example 4: Checking Checksums

### Command
```bash
cat checksums.json | python3 -m json.tool
```

### Output
```json
{
  "algorithm": "SHA-256",
  "output_checksum_sha256": "f6e5d4c3b2a1987654321f6e5d4c3b2a1987654321f6e5d4c3b2a1987654321",
  "output_file": "met_inventory_standardized.tsv",
  "source_checksum_sha256": "a1b2c3d4e5f6789012345a1b2c3d4e5f6789012345a1b2c3d4e5f6789012345",
  "source_file": "met_inventory.tsv",
  "timestamp": "2025-01-15T10:30:45.123456"
}
```

## Example 5: Viewing Standardized Data

### Command
```bash
head -5 met_inventory_standardized.tsv | column -t -s $'\t'
```

### Output
```
Object Date             Title                                          Object Number           Link Resource
late 19th century                                                      C.I.46.9.189            http://www.metmuseum.org/art/collection/search/88288
19th century                                                           38.25.136               http://www.metmuseum.org/art/collection/search/58999
19th century                                                           81.1.377a, b            http://www.metmuseum.org/art/collection/search/59638
19th century                                                           81.1.379                http://www.metmuseum.org/art/collection/search/59814
```

## Example 6: File Statistics

### Command
```bash
wc -l met_inventory*.tsv
du -h met_inventory*.tsv
```

### Output
```
    101 met_inventory.tsv
    101 met_inventory_standardized.tsv
    202 total

 19K met_inventory.tsv
 18K met_inventory_standardized.tsv
```

## Example 7: Manual Checksum Verification

### Command
```bash
sha256sum met_inventory.tsv met_inventory_standardized.tsv
```

### Output
```
a1b2c3d4e5f6789012345a1b2c3d4e5f6789012345a1b2c3d4e5f6789012345  met_inventory.tsv
f6e5d4c3b2a1987654321f6e5d4c3b2a1987654321f6e5d4c3b2a1987654321  met_inventory_standardized.tsv
```

### Compare with checksums.json
```bash
echo "Expected source:"
grep "source_checksum" checksums.json

echo "Actual source:"
sha256sum met_inventory.tsv | awk '{print $1}'
# Should match!
```

## Example 8: Custom Output File

### Command
```bash
./standardize.sh met_inventory.tsv my_standardized_data.tsv
```

### Output
```
[INFO] Input file: met_inventory.tsv
[INFO] Output file: my_standardized_data.tsv

[INFO] Running standardization script...
...
[INFO] All verifications passed!
```

### Result
- ✓ `my_standardized_data.tsv` created
- ✓ `checksums.json` still created (with new filenames)
- ✓ `verification.txt` contains comparison

## Example 9: Detecting Corruption

### Simulate File Corruption
```bash
# Copy a character at the end
echo "x" >> met_inventory_standardized.tsv

# Try to verify
./verify_checksums.sh
```

### Expected Output
```
[✗] Checksum mismatch: met_inventory_standardized.tsv
  Expected: f6e5d4c3b2a1987...
  Actual:   a9b8c7d6e5f41234...
  Status:   ✗ MISMATCH - File may have been modified!

✗ VERIFICATION FAILED
  ✗ Output file checksum mismatch

This may indicate:
  - Files have been modified or corrupted
  - Files have been moved or renamed
  - Checksum log is for different files
```

## Example 10: HTML Report Generation

### Command
```bash
./verify_checksums.sh --html
```

### Output
```
[✓] File verified: met_inventory.tsv
[✓] File verified: met_inventory_standardized.tsv

✓ ALL FILES VERIFIED SUCCESSFULLY

[✓] Detailed report saved to: checksum_verification_report.txt
HTML report generated: checksum_verification_report.html
```

### Result
- `checksum_verification_report.txt` - Text format
- `checksum_verification_report.html` - Web viewable format

## Example 11: Using Different Checksum Log

### Command
```bash
# First standardization with default log
./standardize.sh source1.tsv output1.tsv
# Creates: checksums.json

# Later, verify output1.tsv using default log
./verify_checksums.sh

# Or verify with explicit reference
./verify_checksums.sh --checksum checksums.json
```

## Example 12: Archival Workflow

### Setup Directory Structure
```bash
mkdir -p archive/met_inventory_2025-01
cd archive/met_inventory_2025-01

# Copy original
cp ../../met_inventory.tsv .

# Run standardization
../../standardize.sh met_inventory.tsv

# Result:
# ├── met_inventory.tsv (original, unchanged)
# ├── met_inventory_standardized.tsv (processed)
# ├── checksums.json (verification data)
# └── verification.txt (processing report)

# Later, verify integrity
../../verify_checksums.sh
```

## Example 13: Integration with Data Pipeline

### Python Script Integration
```python
import subprocess
import json

# Run standardization
result = subprocess.run([
    'python3', 'standardize_tsv.py',
    'met_inventory.tsv',
    'met_inventory_standardized.tsv'
], capture_output=True, text=True)

# Load checksums
with open('checksums.json') as f:
    checksums = json.load(f)

# Proceed with analysis
print(f"Source checksum: {checksums['source_checksum_sha256']}")
print(f"Output checksum: {checksums['output_checksum_sha256']}")
```

## Example 14: Batch Processing Multiple Files

### Bash Script
```bash
#!/bin/bash
for file in *.tsv; do
    echo "Processing $file..."
    ./standardize.sh "$file" "${file%.tsv}_standardized.tsv"
    
    # Move to archive with checksums
    mkdir -p "archive/$file"
    mv "$file" "${file%.tsv}_standardized.tsv" \
       checksums.json verification.txt \
       "archive/$file/"
done
```

## Example 15: Documenting the Process

### Create Processing Report
```bash
cat > PROCESSING_REPORT.txt << EOF
TSV STANDARDIZATION REPORT
===========================

Date: $(date)
Source File: met_inventory.tsv
Output File: met_inventory_standardized.tsv
Checksum Log: checksums.json

Standardization Steps:
1. Loaded TSV file
2. Normalized whitespace
3. Standardized column structure
4. Sorted by Object Number
5. Verified data integrity
6. Generated checksums
7. Created verification report

Results:
- Records processed: 100
- Columns standardized: 4
- Data integrity: ✓ Verified
- Checksums generated: ✓

For verification, see checksums.json and verification.txt
EOF
```

---

## Tips & Tricks

### Quick Verification Shortcut
```bash
# One-liner to verify both files
for file in met_inventory.tsv met_inventory_standardized.tsv; do
    echo -n "$file: "
    sha256sum "$file" | awk '{print $1}'
done
# Compare with checksums.json values
```

### Show Only Changed Records
```bash
# Compare before/after sorting
diff <(sort -t$'\t' -k3 met_inventory.tsv | tail -n +2) \
     <(tail -n +2 met_inventory_standardized.tsv) | head -20
```

### Export to CSV
```bash
# Convert TSV to CSV
tr '\t' ',' < met_inventory_standardized.tsv > met_inventory_standardized.csv
```

### Pretty Print
```bash
# View with better formatting
column -t -s $'\t' -W 180 met_inventory_standardized.tsv | less -S
```

---

**Need more examples? Check README.md for advanced usage patterns!**
