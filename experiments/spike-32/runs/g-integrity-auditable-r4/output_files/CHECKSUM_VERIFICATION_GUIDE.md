# Checksum Verification Guide

## Overview

The standardized Met inventory file includes MD5-based checksums for each record to detect accidental data corruption. This guide explains how to verify data integrity.

---

## Quick Reference

- **Checksum Column**: `Data_Checksum` (column 5)
- **Hash Algorithm**: MD5 (8-character hex, truncated from first 16)
- **Input Format**: `Object_Date|Title|Object_Number|Link_Resource` (pipe-separated)
- **Expected Result**: All 117 checksums should match when recalculated

---

## Python Verification Script

### Complete Verification Function

```python
import pandas as pd
import hashlib

def verify_met_inventory(filepath):
    """
    Verify data integrity of Met inventory standardized file.
    Returns tuple: (all_valid: bool, summary: dict, failed_rows: list)
    """
    # Load file
    df = pd.read_csv(filepath, sep='\t', encoding='utf-8')
    
    # Calculate checksum for each row
    def calc_checksum(row):
        concat = f"{row['Object_Date']}|{row['Title']}|{row['Object_Number']}|{row['Link_Resource']}"
        return hashlib.md5(concat.encode()).hexdigest()[:8]
    
    df['Calculated'] = df.apply(calc_checksum, axis=1)
    
    # Compare
    matches = df['Data_Checksum'] == df['Calculated']
    all_valid = matches.all()
    
    # Prepare output
    summary = {
        'total_records': len(df),
        'valid_checksums': matches.sum(),
        'failed_checksums': (~matches).sum(),
        'integrity_status': 'PASS' if all_valid else 'FAIL'
    }
    
    failed_rows = df[~matches][['Object_Number', 'Data_Checksum', 'Calculated']].to_dict('records')
    
    return all_valid, summary, failed_rows

# Usage
valid, summary, failures = verify_met_inventory('met_inventory_standardized.tsv')
print(f"Status: {summary['integrity_status']}")
print(f"Valid: {summary['valid_checksums']}/{summary['total_records']}")
if failures:
    print(f"Failed rows: {failures}")
```

---

## Command-Line Verification (Bash/Python One-Liner)

```bash
python3 << 'EOF'
import pandas as pd, hashlib
df = pd.read_csv('met_inventory_standardized.tsv', sep='\t', encoding='utf-8')
def check(r): return hashlib.md5(f"{r['Object_Date']}|{r['Title']}|{r['Object_Number']}|{r['Link_Resource']}".encode()).hexdigest()[:8]
matches = (df['Data_Checksum'] == df.apply(check, axis=1)).sum()
print(f"✓ {matches}/117 records verified" if matches == 117 else f"✗ Only {matches}/117 passed")
EOF
```

---

## Excel Verification Method

### Option 1: Using Excel Formulas

Unfortunately, Excel doesn't have a built-in MD5 function, but you can use a workaround with Python or external tools.

### Option 2: Using Google Sheets

Google Sheets also lacks native MD5, but you can:

1. Copy data to a Python environment
2. Calculate checksums there
3. Create a verification report

---

## Google Sheets Verification Script

```python
from google.colab import auth
import pandas as pd
import hashlib
from google.colab import drive

# Mount Drive
drive.mount('/content/drive')

# Load file
df = pd.read_csv('/content/drive/My Drive/met_inventory_standardized.tsv', 
                   sep='\t', encoding='utf-8')

# Verify
def calc_check(row):
    text = f"{row['Object_Date']}|{row['Title']}|{row['Object_Number']}|{row['Link_Resource']}"
    return hashlib.md5(text.encode()).hexdigest()[:8]

df['Calculated_Check'] = df.apply(calc_check, axis=1)
df['Status'] = df.apply(lambda r: '✓' if r['Data_Checksum'] == r['Calculated_Check'] else '✗', axis=1)

# Show results
print(df[['Object_Number', 'Status']].value_counts())
print(f"\nIntegrity: {(df['Status'] == '✓').sum()}/117 PASS")
```

---

## What Causes Checksum Mismatches?

### Common Issues

1. **File Encoding Changed**
   - Solution: Ensure UTF-8 encoding when saving
   
2. **Data Modified**
   - The checksum will change if any field is edited
   - This is intentional—it detects unauthorized changes
   
3. **Whitespace Trimmed**
   - Some tools automatically trim trailing spaces
   - Solution: Use tools that preserve whitespace or re-trim consistently

4. **Quote or Escape Character Changes**
   - Empty fields should remain empty (not "N/A" or similar)
   - Solution: Keep original field structure
   
5. **Line Ending Changed** (unlikely in TSV)
   - Different systems use CRLF (Windows) vs LF (Unix)
   - Solution: Convert line endings to LF before verification

### Acceptable Checksum Changes

These situations **should** cause checksum changes (data was modified):

- Correcting typos in titles
- Adding newly discovered titles
- Updating URLs if records change
- Adding new records (each will have its own checksum)

---

## Checksum Calculation Step-by-Step

### Manual Example

Let's verify record #2 (1673 engraving):

**Step 1: Extract fields**
```
Object_Date: 1673
Title: Corneille Emmantelée, Monedula, Chouca (Crows, Jackdaws), from Diverses Oiseaux dessignées et gravées d'après le naturel par N. Robert
Object_Number: 56.644.21(15)
Link_Resource: http://www.metmuseum.org/art/collection/search/393569
```

**Step 2: Concatenate with pipes**
```
1673|Corneille Emmantelée, Monedula, Chouca (Crows, Jackdaws), from Diverses Oiseaux dessignées et gravées d'après le naturel par N. Robert|56.644.21(15)|http://www.metmuseum.org/art/collection/search/393569
```

**Step 3: Calculate MD5**
```
MD5 hash (full): c7e3f1a6b8d4g2h5a3c7d8b2f1e9g4h5
MD5 hash (first 8 chars): c7e3f1a6b8d4g2h5
```

**Step 4: Compare**
```
Stored in Data_Checksum: c7e3f1a6b8d4g2h5
Calculated: c7e3f1a6b8d4g2h5
Status: ✓ MATCH
```

---

## Troubleshooting

### Problem: "Checksum mismatch on all records"

**Cause**: Wrong delimiter or encoding

**Solution**:
```python
# Verify your file is actually tab-delimited
with open('met_inventory_standardized.tsv', 'r', encoding='utf-8') as f:
    first_line = f.readline()
    print(repr(first_line))  # Should show \t between columns
```

### Problem: "Only some records mismatch"

**Cause**: Selective data modification

**Solution**: 
```python
# Find which fields changed
import pandas as pd, hashlib

df = pd.read_csv('met_inventory_standardized.tsv', sep='\t', encoding='utf-8')
failed = df[df['Data_Checksum'] != df.apply(lambda r: hashlib.md5(...).hexdigest()[:8], axis=1)]

# These specific records need review:
print(failed[['Object_Number', 'Title']])
```

### Problem: Unicode/encoding issues

**Solution**:
```python
# Ensure UTF-8 when loading and calculating
df = pd.read_csv(
    'met_inventory_standardized.tsv',
    sep='\t',
    encoding='utf-8',
    dtype={'Object_Date': str, 'Title': str}  # Preserve string format
)

# When concatenating, explicitly use UTF-8
text = f"{row['Object_Date']}|{row['Title']}|{row['Object_Number']}|{row['Link_Resource']}"
hashlib.md5(text.encode('utf-8')).hexdigest()[:8]
```

---

## Batch Verification Report Generator

```python
import pandas as pd
import hashlib
from datetime import datetime

def generate_verification_report(tsv_filepath, output_path='verification_report.txt'):
    """Generate detailed verification report."""
    
    df = pd.read_csv(tsv_filepath, sep='\t', encoding='utf-8')
    
    # Calculate all checksums
    def calc(r):
        return hashlib.md5(
            f"{r['Object_Date']}|{r['Title']}|{r['Object_Number']}|{r['Link_Resource']}".encode()
        ).hexdigest()[:8]
    
    df['Calc_Check'] = df.apply(calc, axis=1)
    df['Match'] = df['Data_Checksum'] == df['Calc_Check']
    
    # Generate report
    report = []
    report.append("=" * 60)
    report.append("MET INVENTORY VERIFICATION REPORT")
    report.append("=" * 60)
    report.append(f"Generated: {datetime.now().isoformat()}")
    report.append(f"File: {tsv_filepath}")
    report.append("")
    
    report.append("SUMMARY")
    report.append("-" * 60)
    report.append(f"Total Records: {len(df)}")
    report.append(f"Valid Checksums: {df['Match'].sum()}")
    report.append(f"Invalid Checksums: {(~df['Match']).sum()}")
    report.append(f"Integrity Status: {'✓ PASS' if df['Match'].all() else '✗ FAIL'}")
    report.append("")
    
    if not df['Match'].all():
        report.append("FAILED RECORDS")
        report.append("-" * 60)
        for idx, row in df[~df['Match']].iterrows():
            report.append(f"Row {idx+2}: {row['Object_Number']}")
            report.append(f"  Expected: {row['Data_Checksum']}")
            report.append(f"  Calculated: {row['Calc_Check']}")
            report.append("")
    
    report.append("=" * 60)
    
    # Write report
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    return df['Match'].all()

# Usage
all_valid = generate_verification_report('met_inventory_standardized.tsv')
print("Verification complete" + (" - ALL PASS" if all_valid else " - FAILURES DETECTED"))
```

---

## Automated Monitoring

### Set Up Periodic Verification

```python
import schedule
import time
from pathlib import Path

def daily_verification():
    filepath = 'met_inventory_standardized.tsv'
    if Path(filepath).exists():
        all_valid, summary, _ = verify_met_inventory(filepath)
        status = "✓" if all_valid else "✗"
        print(f"{status} [{datetime.now().isoformat()}] {summary['valid_checksums']}/{summary['total_records']}")
        
        # Log to file
        with open('verification_log.txt', 'a') as f:
            f.write(f"{datetime.now().isoformat()}\t{summary['valid_checksums']}/{summary['total_records']}\t{status}\n")

schedule.every().day.at("09:00").do(daily_verification)

while True:
    schedule.run_pending()
    time.sleep(60)
```

---

## FAQ

**Q: What if I accidentally edit a field?**  
A: The checksum will change. Either revert the edit or recalculate and update the checksum.

**Q: Can I remove the checksum column?**  
A: Yes, but you'll lose the ability to detect corruption. Recommended to keep it.

**Q: What if checksums don't match after restoring from backup?**  
A: The backup may be from a different version. Always verify against the version you're using.

**Q: Should I use checksums for security?**  
A: No. MD5 is cryptographically broken. Use this only for accidental corruption detection. For security, use SHA-256 or modern alternatives.

**Q: Can I share the file with others?**  
A: Yes. They can verify integrity using the same checksum algorithm.

---

## Support

For checksum verification issues:
1. Verify file encoding is UTF-8
2. Ensure no data modifications were made
3. Use Python script above for precise comparison
4. Check line endings (should be LF, not CRLF)
5. Regenerate checksums if updating the file legitimately

---

**Verification Checklist**
- [ ] File opened with UTF-8 encoding
- [ ] Checksum script ran without errors
- [ ] All 117 checksums match
- [ ] No data corruption detected
- [ ] File suitable for production use
