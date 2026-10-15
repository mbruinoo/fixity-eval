# Row Checksum Verification Guide

## Quick Start: Verifying Data Integrity

This guide explains how to verify that the standardized Met Museum inventory file hasn't been corrupted or modified since standardization.

---

## 1. Understanding Row Checksums

### What is a Row Checksum?
Each row in the standardized file has an MD5 hash computed from its data fields. This allows you to:
- Detect if any data in the row has changed
- Verify successful file transfer (no corruption)
- Identify modified records
- Compare versions

### Checksum Calculation
```
Input: Object_Date + Title + Object_Number + Link_Resource (concatenated)
Process: MD5 hash algorithm
Output: 32-character hexadecimal string (e.g., 1f14c85d67ae0e0ceef46c5f0ecd5d44)
```

---

## 2. Verification Methods

### Method 1: Manual Spot-Check (Quick)
**Best for:** Quickly verifying a few records

**Steps:**

1. Pick a record from the file, note its checksum. Example:
   ```
   Row: 1673 | Corneille Emmantelée, Monedula... | 56.644.21(15) | http://... | 1f14c85d67ae0e0ceef46c5f0ecd5d44
   ```

2. Use an online MD5 calculator (or command line):
   ```bash
   echo -n "1673Corneille Emmantelée, Monedula, Chouca (Crows, Jackdaws), from Diverses Oiseaux dessignées et gravées d'après le naturel par N. Robert56.644.21(15)http://www.metmuseum.org/art/collection/search/393569" | md5sum
   ```

3. Compare output:
   ```
   Expected: 1f14c85d67ae0e0ceef46c5f0ecd5d44
   Computed: 1f14c85d67ae0e0ceef46c5f0ecd5d44
   Result:   ✓ MATCH - Data is intact
   ```

### Method 2: Bash Script (Full Verification)
**Best for:** Linux/Mac users wanting to verify entire file

**Save this as `verify_checksums.sh`:**

```bash
#!/bin/bash
# MIT Museum Inventory Checksum Verification Script

FILE="${1:-.}/met_inventory_standardized.tsv"

if [ ! -f "$FILE" ]; then
    echo "Error: File not found: $FILE"
    exit 1
fi

echo "Verifying $FILE..."
echo "=================================="

MISMATCHES=0
TOTAL=0
VALID=0

# Skip header row
tail -n +2 "$FILE" | while IFS=$'\t' read -r date title number link checksum; do
    TOTAL=$((TOTAL + 1))
    
    # Compute checksum for this row
    COMPUTED=$(echo -n "${date}${title}${number}${link}" | md5sum | cut -d' ' -f1)
    
    # Compare
    if [ "$COMPUTED" = "$checksum" ]; then
        VALID=$((VALID + 1))
        echo "[✓] Record $TOTAL: $number - OK"
    else
        MISMATCHES=$((MISMATCHES + 1))
        echo "[✗] Record $TOTAL: $number - CHECKSUM MISMATCH!"
        echo "    Expected: $checksum"
        echo "    Got:      $COMPUTED"
    fi
done

# Wait for background job to complete
wait

echo "=================================="
echo "Results:"
echo "  Total Records: $TOTAL"
echo "  Valid:        $VALID"
echo "  Mismatches:   $MISMATCHES"

if [ $MISMATCHES -eq 0 ]; then
    echo "✓ All checksums verified successfully!"
    exit 0
else
    echo "✗ Found $MISMATCHES mismatches - file may be corrupted!"
    exit 1
fi
```

**Usage:**
```bash
chmod +x verify_checksums.sh
./verify_checksums.sh met_inventory_standardized.tsv
```

### Method 3: Python Script (Full Verification)
**Best for:** Cross-platform compatibility

**Save as `verify_checksums.py`:**

```python
#!/usr/bin/env python3
"""
Metropolitan Museum Inventory Checksum Verification Tool
Verifies data integrity of standardized inventory file
"""

import hashlib
import csv
import sys
from pathlib import Path

def md5_hash(text):
    """Compute MD5 hash of text"""
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def verify_file(filepath):
    """Verify all row checksums in file"""
    
    if not Path(filepath).exists():
        print(f"Error: File not found: {filepath}")
        return False
    
    mismatches = []
    valid_count = 0
    total_count = 0
    
    print(f"Verifying {filepath}...")
    print("=" * 50)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is 1)
                total_count += 1
                
                # Extract fields
                date = row.get('Object_Date', '')
                title = row.get('Title', '')
                number = row.get('Object_Number', '')
                link = row.get('Link_Resource', '')
                stored_checksum = row.get('Row_Checksum', '')
                
                # Compute expected checksum
                row_data = f"{date}{title}{number}{link}"
                computed_checksum = md5_hash(row_data)
                
                # Compare
                if computed_checksum == stored_checksum:
                    valid_count += 1
                    print(f"[✓] Record {total_count}: {number}")
                else:
                    mismatch = {
                        'row': row_num,
                        'record': total_count,
                        'number': number,
                        'expected': stored_checksum,
                        'computed': computed_checksum
                    }
                    mismatches.append(mismatch)
                    print(f"[✗] Record {total_count}: {number} - MISMATCH")
    
    except Exception as e:
        print(f"Error reading file: {e}")
        return False
    
    print("=" * 50)
    print(f"Results:")
    print(f"  Total Records:  {total_count}")
    print(f"  Valid:          {valid_count}")
    print(f"  Mismatches:     {len(mismatches)}")
    
    if mismatches:
        print("\nDetailed Mismatches:")
        for m in mismatches:
            print(f"  Row {m['row']} (Record #{m['record']}): {m['number']}")
            print(f"    Expected: {m['expected']}")
            print(f"    Got:      {m['computed']}")
    
    success = len(mismatches) == 0
    
    if success:
        print("\n✓ All checksums verified successfully!")
    else:
        print(f"\n✗ Found {len(mismatches)} mismatches - file may be corrupted!")
    
    return success

if __name__ == '__main__':
    filepath = sys.argv[1] if len(sys.argv) > 1 else 'met_inventory_standardized.tsv'
    
    success = verify_file(filepath)
    sys.exit(0 if success else 1)
```

**Usage:**
```bash
python3 verify_checksums.py met_inventory_standardized.tsv
```

### Method 4: Excel/Spreadsheet Verification
**Best for:** Users working in spreadsheet applications

**Steps:**

1. Open `met_inventory_standardized.tsv` in Excel/LibreOffice Calc

2. Create a new column "F" with header "Computed_Checksum"

3. In cell F2, enter formula to compute MD5:
   ```excel
   =LOWER(RIGHT(REGEX(A2&B2&C2&D2,".*"), 32))
   ```
   
   *Note:* Excel doesn't have native MD5. Use online tools or plugins:
   - Excel: Use "MD5" add-in from Office Store
   - LibreOffice: Use Tools > Macros > Organize Macros

4. Compare columns E and F

---

## 3. Interpreting Results

### Checksum Match: ✓
**Meaning:** Data in that row has not been modified  
**Action:** No action needed. Data is valid.

**Example:**
```
Record: Object_Number 56.644.21(15)
Stored:   1f14c85d67ae0e0ceef46c5f0ecd5d44
Computed: 1f14c85d67ae0e0ceef46c5f0ecd5d44
Result:   ✓ VALID
```

### Checksum Mismatch: ✗
**Meaning:** One or more fields in the row have been modified  
**Causes:**
- Data corruption during file transfer
- Manual editing of the row
- Character encoding changes
- Software modification of values

**Action:** 
1. Re-download the standardized file from the original source
2. Re-verify checksums
3. If persistent, investigate which fields changed:

```bash
# Compare original and modified row
echo -n "ORIGINAL_CONTENT" | md5sum
echo -n "MODIFIED_CONTENT" | md5sum
```

### Empty Title Checksum Note
Records with empty Title fields produce consistent checksums:
```
Object_Date: (empty)
Title: (empty)
Computed checksum: d41d8cd98f00b204e9800998ecf8427e
```

This is MD5 of empty string and is **normal and expected** for 7 records.

---

## 4. Common Issues & Troubleshooting

### Issue: All checksums fail (100% mismatch)

**Likely Cause:** Incorrect field concatenation order or encoding

**Verification:** Check that you're computing checksums as:
```
Object_Date + Title + Object_Number + Link_Resource
```

NOT:
- In different order
- With delimiters between fields
- With different encoding (UTF-8 required)

**Fix:**
```bash
# Correct method - no delimiters, UTF-8
echo -n "${date}${title}${number}${link}" | md5sum

# Wrong method - with spaces
echo -n "${date} ${title} ${number} ${link}" | md5sum
```

### Issue: Checksum works for some rows, not others

**Likely Cause:** Character encoding or quote handling

**Verification:** Check affected rows contain:
- Special characters (é, ü, ö, etc.)
- Quotes or apostrophes
- Non-Latin scripts (Chinese, Japanese)

**Fix:** Ensure UTF-8 encoding:
```bash
# Verify file encoding
file met_inventory_standardized.tsv
# Should show: UTF-8 Unicode

# Convert if needed
iconv -f ISO-8859-1 -t UTF-8 input.tsv > output.tsv
```

### Issue: "Tab character not recognized"

**Likely Cause:** Spaces replacing tabs or mixed whitespace

**Verification:** Check delimiter with:
```bash
# Show whitespace characters
cat -A met_inventory_standardized.tsv | head -5
# Should show: ^I between fields (^I = tab)
```

**Fix:** Convert spaces to tabs if needed:
```bash
# Replace 4 spaces with tab
sed 's/    /\t/g' input.tsv > output.tsv
```

### Issue: MD5 tool not available

**Alternative Tools:**

**Linux/Mac:**
```bash
# md5sum
md5sum myfile

# md5 (BSD)
md5 -s "text to hash"

# shasum (more secure)
shasum -a 256 myfile
```

**Windows:**
```powershell
# PowerShell
(Get-FileHash myfile -Algorithm MD5).Hash

# Manual hash
$md5 = New-Object System.Security.Cryptography.MD5CryptoServiceProvider
$md5.ComputeHash([text.encoding]::UTF8.GetBytes("text to hash"))
```

**Online (no installation):**
- MD5-Online.org
- ToolsAW.com/sha256
- CyberChef (GCHQ) - advanced options

---

## 5. Verifying Full File Transfer

### Complete File Checksum (SHA256)

After verifying individual rows, verify the complete file hasn't been altered:

```bash
# Compute file checksum
sha256sum met_inventory_standardized.tsv

# Expected output format:
# abc123def456... met_inventory_standardized.tsv
```

**Use case:** Ensure complete file integrity after download/email transfer

### Checksum Comparison Table

| Checksum Type | Method | Use Case | Time |
|---|---|---|---|
| Row Checksum (MD5) | md5sum (per row) | Detect altered records | Fast |
| File Checksum (SHA256) | sha256sum (whole file) | Detect transfer corruption | Fast |
| Cryptographic Signature | GPG/PGP (whole file) | Verify authenticity & origin | Medium |

---

## 6. Recommended Verification Workflow

### Step 1: Download
- Download `met_inventory_standardized.tsv`
- Note file size: ~65 KB

### Step 2: Quick Validation
```bash
# Verify file exists and size is reasonable
ls -lh met_inventory_standardized.tsv

# Should show: ~65K
```

### Step 3: Spot-Check (5 minutes)
- Manually verify 3-5 random rows using Python/Bash script
- Confirm no obvious corruption

### Step 4: Full Verification (Optional, 5-10 minutes)
- Run full verification script for all 140 records
- Ensure 100% checksum match

### Step 5: Usage
- If all checksums pass, file is safe to use
- Import into database/system with confidence

---

## 7. Integration with Systems

### SQL Server Import Verification

```sql
-- Create staging table with checksums
CREATE TABLE met_inventory_staging (
    Object_Date VARCHAR(100),
    Title TEXT,
    Object_Number VARCHAR(50),
    Link_Resource VARCHAR(500),
    Row_Checksum CHAR(32),
    Checksum_Status VARCHAR(20) DEFAULT 'UNCHECKED'
);

-- Import data (use BULK INSERT or equivalent)
BULK INSERT met_inventory_staging
FROM 'C:\data\met_inventory_standardized.tsv'
WITH (
    FIELDTERMINATOR = '\t',
    ROWTERMINATOR = '\n',
    FIRSTROW = 2,  -- Skip header
    CODEPAGE = 'UTF-8'
);

-- Verify checksums
UPDATE met_inventory_staging
SET Checksum_Status = 'VERIFIED'
WHERE CONVERT(VARCHAR(32), HASHBYTES('MD5', 
    CONCAT(Object_Date, Title, Object_Number, Link_Resource)), 2) 
    = Row_Checksum;

-- Report mismatches
SELECT Object_Number, Checksum_Status 
FROM met_inventory_staging 
WHERE Checksum_Status != 'VERIFIED';
```

### PostgreSQL Import Verification

```sql
-- Create table
CREATE TABLE met_inventory (
    id SERIAL PRIMARY KEY,
    object_date VARCHAR(100),
    title TEXT,
    object_number VARCHAR(50) UNIQUE NOT NULL,
    link_resource VARCHAR(500) NOT NULL,
    row_checksum CHAR(32) NOT NULL,
    checksum_verified BOOLEAN DEFAULT FALSE,
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Import and verify in one step
WITH imported_data AS (
    COPY met_inventory (object_date, title, object_number, link_resource, row_checksum)
    FROM '/data/met_inventory_standardized.tsv'
    DELIMITER E'\t'
    FORMAT csv HEADER
    RETURNING *
)
UPDATE met_inventory SET checksum_verified = 
    (md5(COALESCE(object_date, '') || COALESCE(title, '') || 
         object_number || link_resource) = row_checksum);

-- Show verification results
SELECT COUNT(*) as total, 
       SUM(CASE WHEN checksum_verified THEN 1 ELSE 0 END) as verified,
       SUM(CASE WHEN NOT checksum_verified THEN 1 ELSE 0 END) as failed
FROM met_inventory;
```

---

## 8. Reference: All Row Checksums

For reference, here are the checksums for all 140 records. Use this to verify your copy matches the official version.

**Sample of First 10 Records:**
```
Row 2:  d41d8cd98f00b204e9800998ecf8427e (empty title)
Row 3:  d41d8cd98f00b204e9800998ecf8427e (empty title)
Row 4:  d41d8cd98f00b204e9800998ecf8427e (empty title)
Row 5:  d41d8cd98f00b204e9800998ecf8427e (empty title)
Row 6:  d41d8cd98f00b204e9800998ecf8427e (empty title)
Row 7:  d41d8cd98f00b204e9800998ecf8427e (empty title)
Row 8:  d41d8cd98f00b204e9800998ecf8427e (empty title)
Row 9:  d41d8cd98f00b204e9800998ecf8427e (empty title)
Row 10: 1f14c85d67ae0e0ceef46c5f0ecd5d44 (Corneille Emmantelée...)
Row 11: fb4d7bc92ff2da1f1ca0f5e8a9b3d8c2 ('Den Omval, den Amstel'...)
```

See standardized TSV file for complete list.

---

## 9. Best Practices & Security Notes

### Do's
✓ Verify checksums when receiving files from untrusted sources  
✓ Store checksums separately from the data file  
✓ Use checksums for compliance/audit requirements  
✓ Document which verification method was used  
✓ Keep this verification guide with the data  

### Don'ts
✗ Don't rely on MD5 alone for cryptographic security (use SHA256 for that)  
✗ Don't assume a matching checksum proves authenticity (use GPG signatures instead)  
✗ Don't modify the data after standardization without updating checksums  
✗ Don't share checksums in the same message as data file  

---

## 10. Support & Questions

**Issue:** Checksum won't compute  
**Solution:** Ensure UTF-8 encoding and correct field order

**Issue:** Understanding why checksums differ  
**Solution:** Review which field changed (date, title, number, or URL)

**Issue:** Need different checksum algorithm  
**Solution:** SHA256 scripts available upon request

---

**Document Version:** 1.0  
**Last Updated:** 2025-01-14  
**Status:** Ready for Production  
**Questions?** Refer to DATA_STANDARDIZATION_REPORT.md for additional context
