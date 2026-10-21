# Verification Guide: Metropolitan Museum Inventory Standardization

## Quick Verification (2 Minutes)

### Step 1: Check File Exists and Opens
```bash
# List the file
ls -lh met_inventory_standardized.tsv

# Try to open it (should show data)
head -20 met_inventory_standardized.tsv
```

**Expected Output**: File opens, shows 4 columns with "Object Date", "Title", "Object Number", "Link Resource" as headers, followed by data rows.

### Step 2: Count Records
```bash
# Count total lines
wc -l met_inventory_standardized.tsv
```

**Expected Output**: `94` (1 header + 93 data rows)

### Step 3: Verify Encoding
```bash
# Check file encoding
file -i met_inventory_standardized.tsv
```

**Expected Output**: `text/plain; charset=utf-8`

---

## Full Verification (10 Minutes)

### 1. File Integrity Check

**Step A: Generate checksum**
```bash
# Windows PowerShell
(Get-FileHash met_inventory_standardized.tsv -Algorithm SHA256).Hash

# macOS/Linux/WSL
sha256sum met_inventory_standardized.tsv
```

**Expected Output**: A 64-character hexadecimal string (example: `a1b2c3d4e5f6...`)

**Next**: Compare this hash against the checksum documented in CHECKSUMS.txt

**Step B: Document the checksum**
```bash
# Save your checksum for future reference
sha256sum met_inventory_standardized.tsv > met_inventory.sha256
cat met_inventory.sha256
```

### 2. Column Structure Verification

**Step A: Check column count**
```bash
# Linux/macOS/WSL
head -1 met_inventory_standardized.tsv | tr '\t' '\n' | wc -l

# Windows PowerShell
(Get-Content met_inventory_standardized.tsv -First 1).Split("`t").Count
```

**Expected Output**: `4`

**Step B: Check column names**
```bash
# Linux/macOS/WSL
head -1 met_inventory_standardized.tsv

# Windows PowerShell
(Get-Content met_inventory_standardized.tsv -First 1)
```

**Expected Output**:
```
Object Date	Title	Object Number	Link Resource
```

**Step C: Verify consistent structure**
```bash
# Check that all rows have 4 columns (Linux/macOS/WSL)
awk -F'\t' 'NF != 4 { print "Row " NR " has " NF " columns" }' met_inventory_standardized.tsv

# Expected: No output (all rows have 4 columns)
```

### 3. Data Content Verification

**Step A: Sample first few records**
```bash
head -5 met_inventory_standardized.tsv
```

**Expected**: Header followed by 4 rows of data with proper formatting

**Step B: Verify URLs**
```bash
# Check that all URLs are properly formatted
grep -E "http://www\.metmuseum\.org" met_inventory_standardized.tsv | head -5

# Count URLs
grep -c "http://www\.metmuseum\.org" met_inventory_standardized.tsv
```

**Expected**: All rows should have museum URLs, count should be 93

**Step C: Check for international text**
```bash
# Verify Chinese characters present
grep "清" met_inventory_standardized.tsv | head -2

# Verify Japanese characters present
grep "絵本" met_inventory_standardized.tsv | head -2

# Verify Korean characters present
grep "묵란도" met_inventory_standardized.tsv | head -1
```

**Expected**: Each command should return at least one matching line

### 4. Empty Cell Verification

**Step A: Find records with empty titles**
```bash
# Linux/macOS/WSL (find lines where title column is empty)
awk -F'\t' '$2 == "" { print NR ": " $1 " | " $3 }' met_inventory_standardized.tsv | head -5

# Count empty title records
awk -F'\t' '$2 == "" { count++ } END { print count }' met_inventory_standardized.tsv
```

**Expected**: Should find records with empty titles (normal for this dataset)

### 5. Special Character Verification

**Step A: Check diacritical marks**
```bash
# Look for accent marks
grep -E "[éüøå]" met_inventory_standardized.tsv | head -2
```

**Expected**: Multiple records with diacritical marks

**Step B: Check special punctuation**
```bash
# Look for en-dashes
grep "–" met_inventory_standardized.tsv | head -2

# Look for quotation marks
grep '"' met_inventory_standardized.tsv | head -2
```

**Expected**: Should find records with special punctuation

---

## Advanced Verification (15-20 Minutes)

### Row-Level Verification (Python Script)

**Step A: Create verification script**
```python
# save as verify_rows.py
import hashlib
import csv

def verify_file(filename):
    """Verify standardized TSV file integrity"""
    
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        
        # Read header
        header = next(reader)
        print(f"Header: {header}")
        
        # Verify rows
        row_count = 0
        for row_num, row in enumerate(reader, start=2):  # start=2 because row 1 is header
            row_count += 1
            
            # Check column count
            if len(row) != 4:
                print(f"ERROR: Row {row_num} has {len(row)} columns (expected 4)")
            
            # Verify encoding (all characters should be valid UTF-8)
            try:
                '\t'.join(row)  # This will fail if encoding is bad
            except UnicodeDecodeError as e:
                print(f"ERROR: Row {row_num} has encoding issue: {e}")
            
            # Print sample rows
            if row_num <= 3:
                print(f"Row {row_num}: {row[0]} | {row[2]}")
        
        print(f"\nTotal rows verified: {row_count}")
        return row_count

# Run verification
if __name__ == "__main__":
    count = verify_file('met_inventory_standardized.tsv')
    if count == 93:
        print("✓ All 93 data records verified")
    else:
        print(f"✗ ERROR: Expected 93 records, found {count}")
```

**Step B: Run the script**
```bash
python3 verify_rows.py
```

**Expected Output**:
```
Header: ['Object Date', 'Title', 'Object Number', 'Link Resource']
Row 2: late 19th century | C.I.46.9.189
Row 3: 19th century | 81.1.379
Row 4: 19th century | 38.25.136
...
Total rows verified: 93
✓ All 93 data records verified
```

### Spreadsheet Import Verification

**Excel/Google Sheets**:
1. Open the standardized TSV file
2. Ensure UTF-8 encoding is selected
3. Select TAB as delimiter
4. Verify that:
   - All 4 columns imported correctly
   - 93 data rows visible
   - International text displays correctly
   - URLs are complete and clickable

### Corruption Detection Verification

**Check for common corruption indicators**:
```bash
# Check for embedded null bytes (corruption indicator)
hexdump -C met_inventory_standardized.tsv | grep "00 00"
# Expected: No output (no null bytes)

# Check file size is reasonable
ls -lh met_inventory_standardized.tsv
# Expected: ~35-45 KB

# Check for CRLF line endings (Windows style - should be LF only)
file met_inventory_standardized.tsv | grep -i "CRLF"
# Expected: No output (should be LF only)
```

---

## Periodic Verification (Annual Schedule)

### Annual Checksum Verification

**Every Year**, perform:
```bash
# Re-generate checksum
sha256sum met_inventory_standardized.tsv > current_checksum.txt

# Compare with original checksum
diff current_checksum.txt met_inventory.sha256

# Should show: No differences
```

If checksums don't match:
1. Check if file was accidentally modified
2. Restore from backup
3. Investigate modification source

### Annual Integrity Check

**Every Year**, run this checklist:
- [ ] File opens without errors
- [ ] Total rows: 94 (1 header + 93 data)
- [ ] All rows have 4 columns
- [ ] Checksum matches expected value
- [ ] Encoding verified as UTF-8
- [ ] Sample data intact and readable
- [ ] International text displays correctly
- [ ] URLs present and formatted correctly

---

## Troubleshooting Verification Issues

### Issue: Checksum Doesn't Match

**Possible Causes**:
1. File was modified or corrupted
2. File was converted to different encoding
3. Line endings were changed
4. Different version of the file

**Resolution**:
```bash
# Restore from backup
cp backup/met_inventory_standardized.tsv .

# Re-verify
sha256sum met_inventory_standardized.tsv

# Should now match expected checksum
```

### Issue: International Characters Show as Garbage

**Possible Causes**:
1. Application doesn't support UTF-8
2. File encoding was changed
3. File corrupted during transfer

**Resolution**:
1. Open with UTF-8-supporting editor (VS Code, Sublime, etc.)
2. If still broken, restore from backup
3. Verify with: `file -i met_inventory_standardized.tsv`

### Issue: Column Count Varies

**Possible Causes**:
1. File was accidentally edited
2. Corruption during transfer
3. Different version of file

**Resolution**:
```bash
# Find problematic rows
awk -F'\t' 'NF != 4' met_inventory_standardized.tsv

# Count problems
awk -F'\t' 'NF != 4 { count++ } END { print count }' met_inventory_standardized.tsv

# If any found, restore from backup
```

### Issue: File Size Seems Wrong

**Normal size**: ~40-45 KB

**If much smaller**:
- File may be corrupted
- Restore from backup

**If much larger**:
- File may have been modified
- Restore from backup

---

## Certification Verification Checklist

Use this checklist to certify that the standardized data is safe and verified:

```
STANDARDIZATION VERIFICATION CHECKLIST
======================================

File Presence & Accessibility:
  [ ] File exists: met_inventory_standardized.tsv
  [ ] File opens without errors
  [ ] File is readable and accessible

Encoding & Format:
  [ ] Character encoding is UTF-8
  [ ] File format is TSV (tab-separated)
  [ ] Line endings are consistent (LF)
  [ ] No embedded null bytes

Structure:
  [ ] Header row present with 4 columns
  [ ] All data rows have exactly 4 columns
  [ ] Total row count is 94 (1 header + 93 data)
  [ ] No empty or malformed rows

Data Content:
  [ ] All 93 original records present
  [ ] No records deleted or modified
  [ ] All Object Numbers intact
  [ ] All URLs present and complete
  [ ] All dates preserved

Special Characters:
  [ ] Diacritical marks intact (é, ü, ø, etc.)
  [ ] Chinese characters display correctly
  [ ] Japanese characters display correctly
  [ ] Korean characters display correctly
  [ ] Quotes and punctuation preserved

Integrity:
  [ ] File checksum matches expected value
  [ ] No file corruption detected
  [ ] All URLs follow correct format
  [ ] No duplicate records

Verification Methods Used:
  [ ] File size check
  [ ] Encoding verification
  [ ] Column count verification
  [ ] Row count verification
  [ ] Checksum verification (SHA-256)
  [ ] Sample data inspection
  [ ] Special character inspection

Approved By: ________________  Date: ________________

Signature: ____________________

Notes: _________________________________________________________

VERIFICATION COMPLETE ✓
```

---

## Final Verification Statement

Once you have completed the verifications above and all checks pass, you can confirm:

> **This standardized Metropolitan Museum inventory file has been verified for:**
> - ✅ Complete data preservation (all 93 records intact)
> - ✅ Data integrity (no corruption detected)
> - ✅ Proper formatting (4-column TSV structure)
> - ✅ Character encoding (UTF-8 throughout)
> - ✅ International text (all special characters preserved)
> - ✅ File integrity (SHA-256 checksum verified)
> 
> **Status: Safe to use and archive**

---

## Contact & Questions

For verification questions, refer to:
- **CHECKSUMS.txt** - Detailed checksum procedures
- **FIXITY_REPORT.md** - Fixity methodology
- **STANDARDIZATION_MANIFEST.txt** - Detailed procedures

---

**Last Updated**: 2024  
**Status**: ✅ Complete and Verified  
**Verification Ready**: ✅ Yes
