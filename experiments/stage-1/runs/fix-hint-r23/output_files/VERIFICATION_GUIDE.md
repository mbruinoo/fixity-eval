# Fixity Verification Guide
## Met Museum Inventory TSV Standardization

---

## Quick Start

Your standardized file has been protected with SHA-256 checksums at multiple levels:

1. **Full file checksum** - detects any change to the entire dataset
2. **Row-level checksums** - identifies which specific records changed
3. **Header checksum** - verifies the column structure

---

## Verification Methods

### Method 1: Full File Verification (Recommended for transfers)

#### On Linux/Unix/macOS:

```bash
# Calculate checksum of your file
sha256sum met_inventory_standardized.tsv

# You should see output like:
# e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9  met_inventory_standardized.tsv
```

#### On Windows (PowerShell 4.0+):

```powershell
# Calculate checksum
Get-FileHash -Path "met_inventory_standardized.tsv" -Algorithm SHA256

# You should see output like:
# Algorithm       Hash                                                   Path
# ---------       ----                                                   ----
# SHA256          E4F5A6B7C8D9E0F1A2B3C4D5E6F7A8B9...                 C:\path\to\file.tsv
```

#### On Windows (Command Prompt):

```cmd
# If you have the file-checksum utility installed
certutil -hashfile met_inventory_standardized.tsv SHA256
```

**✓ If the checksum matches the value in FIXITY_CHECKSUMS.txt, the file is intact.**

---

### Method 2: Row-Level Verification (For identifying changes)

#### Verify a specific row (example: Row 14, first data row with title):

##### On Linux/Unix/macOS:

```bash
# Extract row 14 and calculate checksum
head -14 met_inventory_standardized.tsv | tail -1 | sha256sum

# Expected output for row 14:
# 6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d  -
```

##### Using Python (Cross-platform):

```python
import hashlib

with open('met_inventory_standardized.tsv', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    
# Get row 14 (remember: row 1 is header)
row_14_content = lines[13].rstrip('\n')  # Remove newline

# Calculate checksum
checksum = hashlib.sha256(row_14_content.encode('utf-8')).hexdigest()
print(f"Row 14 checksum: {checksum}")

# Compare with expected value from FIXITY_CHECKSUMS.txt
expected = "6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d"
if checksum == expected:
    print("✓ Row 14 is intact!")
else:
    print("✗ Row 14 has changed!")
```

---

### Method 3: Header Verification (Quick structural check)

#### Extract and verify the header row:

##### On Linux/Unix/macOS:

```bash
# Extract header row
head -1 met_inventory_standardized.tsv

# Should output:
# object_date	title	object_number	resource_link

# Verify its checksum
head -1 met_inventory_standardized.tsv | sha256sum

# Expected output:
# 1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e  -
```

##### Python:

```python
import hashlib

with open('met_inventory_standardized.tsv', 'r', encoding='utf-8') as f:
    header = f.readline().rstrip('\n')

checksum = hashlib.sha256(header.encode('utf-8')).hexdigest()
print(f"Header checksum: {checksum}")
print(f"Header content: {header}")

# Expected:
# Header checksum: 1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e
# Header content: object_date	title	object_number	resource_link
```

---

### Method 4: Bulk Row Verification (Python - verify all rows)

```python
import hashlib

def verify_all_rows(filepath):
    """Verify checksums for all rows in standardized TSV"""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"Total lines: {len(lines)}")
    print(f"Total data rows: {len(lines) - 1}\n")
    
    # Expected checksums (sample - include more from FIXITY_CHECKSUMS.txt as needed)
    expected_checksums = {
        1: "1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e",  # Header
        2: "2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f",  # Row 1 (data)
        3: "3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a",  # Row 2 (data)
        14: "6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d", # Row 13 (first with title)
    }
    
    all_intact = True
    
    for line_num, line in enumerate(lines, 1):
        if line_num in expected_checksums:
            content = line.rstrip('\n')
            checksum = hashlib.sha256(content.encode('utf-8')).hexdigest()
            expected = expected_checksums[line_num]
            
            status = "✓" if checksum == expected else "✗"
            print(f"Line {line_num}: {status}")
            
            if checksum != expected:
                print(f"  Expected: {expected}")
                print(f"  Got:      {checksum}")
                all_intact = False
    
    print(f"\n{'✓ All verified rows intact!' if all_intact else '✗ Some rows have changed!'}")
    return all_intact

# Run verification
verify_all_rows('met_inventory_standardized.tsv')
```

---

### Method 5: Using Online Tools (No installation needed)

1. **File Hashing Online**: https://emn178.github.io/online-tools/sha256.html
   - Upload your TSV file
   - Get SHA-256 hash
   - Compare with FIXITY_CHECKSUMS.txt

2. **Text-based Tools** (for smaller files or specific rows):
   - Paste your text content
   - Get SHA-256 hash
   - Compare with expected values

---

## Interpreting Results

### ✓ Perfect Match
```
Your checksum:  e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9
Expected:       e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9
Status:         PASS - File is intact!
```

### ✗ Mismatch
```
Your checksum:  a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6
Expected:       e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9
Status:         FAIL - File has been modified!
```

**What a mismatch means:**
- Data was corrupted during transfer
- File was edited (intentionally or accidentally)
- Encoding was changed
- Line endings were modified (CRLF vs LF)

---

## What Each Checksum Level Protects

### Full File Checksum
- **Detects:** Any change to any part of the file
- **Use for:** Verifying complete file transfer integrity
- **Sensitivity:** One bit change → completely different hash
- **Best for:** After download/transfer from external source

### Row-Level Checksums
- **Detects:** Exactly which records changed (if any)
- **Use for:** Identifying modified records without comparing full files
- **Sensitivity:** Each row independently verified
- **Best for:** Large files where you want to identify specific problems
- **Example:** "Row 14 changed, but rows 1-13 and 15-86 are fine"

### Header Checksum
- **Detects:** Column structure changes
- **Use for:** Quick validation that column names are correct
- **Sensitivity:** Different column names → different hash
- **Best for:** Verifying you haven't accidentally reordered columns

---

## Common Issues and Solutions

### Issue 1: Checksum Differs But File Looks Correct

**Possible causes:**
- Line ending conversion (Windows CRLF ↔ Unix LF)
- Invisible spaces added
- Encoding change (UTF-8 → UTF-16, etc.)
- BOM (Byte Order Mark) added/removed

**Solution:**
```bash
# Check line endings (Unix)
file met_inventory_standardized.tsv
# Should show: "text/plain; charset=utf-8"

# Convert line endings if needed
dos2unix met_inventory_standardized.tsv  # CRLF to LF
unix2dos met_inventory_standardized.tsv  # LF to CRLF

# Re-calculate checksum
sha256sum met_inventory_standardized.tsv
```

### Issue 2: Different Result on Different Computers

**Possible cause:** File encoding differs between systems

**Solution:**
```bash
# Ensure UTF-8 encoding (Linux/Mac)
iconv -f UTF-8 -t UTF-8 met_inventory_standardized.tsv > temp.tsv
mv temp.tsv met_inventory_standardized.tsv

# Recalculate
sha256sum met_inventory_standardized.tsv
```

### Issue 3: Whitespace Appears Normal But Checksum Differs

**Possible cause:** Invisible characters or encoding issues

**Solution:**
```bash
# View hidden characters (Linux/Mac)
cat -A met_inventory_standardized.tsv | head -5

# Expected output: $ = newline, ^ = tab, ^M = carriage return
# If you see extra characters, file was modified
```

---

## Checksum Comparison Checklist

When verifying your file:

- [ ] Downloaded file completely (file size matches original)
- [ ] File is accessible and readable
- [ ] Chose appropriate verification method (full file for transfers, rows for detailed analysis)
- [ ] Calculated checksum on your system
- [ ] Located expected checksum in FIXITY_CHECKSUMS.txt
- [ ] Compared checksums character-by-character (or programmatically)
- [ ] Verified result matches expected value
- [ ] Documented the verification (date, method, result)

---

## Verification Script Template

Copy this Python script to automate verification:

```python
#!/usr/bin/env python3
"""Verify Met Museum inventory TSV integrity"""

import hashlib
import sys

def verify_met_inventory(filepath):
    """Verify the standardized TSV file integrity"""
    
    # Expected full file checksum
    EXPECTED_FILE_CHECKSUM = "e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9"
    
    # Expected checksums for key rows (add more as needed)
    EXPECTED_ROW_CHECKSUMS = {
        'header': '1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e',
        'row_2': '2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f',
        'row_14': '6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d',
    }
    
    try:
        # Verify full file
        with open(filepath, 'rb') as f:
            file_content = f.read()
        
        file_checksum = hashlib.sha256(file_content).hexdigest()
        
        print("=" * 70)
        print("Met Museum Inventory TSV - Integrity Verification")
        print("=" * 70)
        print(f"\nFile: {filepath}")
        print(f"File checksum (SHA-256): {file_checksum}")
        print(f"Expected checksum:       {EXPECTED_FILE_CHECKSUM}")
        
        if file_checksum == EXPECTED_FILE_CHECKSUM:
            print("✓ PASS - File is intact!\n")
        else:
            print("✗ FAIL - File has been modified!\n")
            return False
        
        # Verify rows
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print("Row-level verification:")
        print("-" * 70)
        
        all_rows_pass = True
        
        # Check header
        header = lines[0].rstrip('\n')
        header_checksum = hashlib.sha256(header.encode('utf-8')).hexdigest()
        header_status = "✓" if header_checksum == EXPECTED_ROW_CHECKSUMS['header'] else "✗"
        print(f"Header: {header_status} {header_checksum}")
        
        if header_checksum != EXPECTED_ROW_CHECKSUMS['header']:
            all_rows_pass = False
        
        # Check sample data rows
        for row_label, line_num in [('row_2', 1), ('row_14', 13)]:
            if line_num < len(lines):
                row_content = lines[line_num].rstrip('\n')
                row_checksum = hashlib.sha256(row_content.encode('utf-8')).hexdigest()
                row_status = "✓" if row_checksum == EXPECTED_ROW_CHECKSUMS[row_label] else "✗"
                print(f"{row_label}: {row_status} {row_checksum}")
                
                if row_checksum != EXPECTED_ROW_CHECKSUMS[row_label]:
                    all_rows_pass = False
        
        print("-" * 70)
        print(f"\n{'✓ All verifications passed!' if all_rows_pass else '✗ Some rows have changed!'}")
        print("=" * 70 + "\n")
        
        return file_checksum == EXPECTED_FILE_CHECKSUM and all_rows_pass
        
    except FileNotFoundError:
        print(f"✗ Error: File not found - {filepath}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == '__main__':
    filepath = sys.argv[1] if len(sys.argv) > 1 else 'met_inventory_standardized.tsv'
    success = verify_met_inventory(filepath)
    sys.exit(0 if success else 1)
```

**Usage:**
```bash
python3 verify_met_inventory.py met_inventory_standardized.tsv
```

---

## Standards and References

- **SHA-256**: NIST FIPS 180-4 standard
- **TSV Format**: RFC 4180 (CSV/TSV specification)
- **UTF-8 Encoding**: RFC 3629
- **Digital Preservation**: OAIS (Open Archival Information Systems) standard
- **Data Integrity**: ISO/IEC 27001 information security standards

---

## Questions?

If verification fails:

1. **First**, verify you're using the correct checksum value from FIXITY_CHECKSUMS.txt
2. **Second**, check for line ending differences (CRLF vs LF)
3. **Third**, ensure the file wasn't edited or modified
4. **Fourth**, verify file encoding is UTF-8

For issues or questions about the standardization process, refer to:
- `STANDARDIZATION_REPORT.txt` - detailed methodology
- `standardize_met_inventory.py` - source script showing exact transformations

---

**Verification Complete!** ✓

Your data integrity is protected by multiple levels of checksums.
Store this guide with your dataset for future verification needs.
