# How to Verify File Checksums

This guide explains how to use the checksums provided to verify the integrity of the standardized TSV file.

## What Are Checksums?

A checksum is a cryptographic hash of a file's contents. It acts like a digital fingerprint:
- **Same file = Same checksum**
- **Different file = Different checksum**
- **1 bit changed = Completely different checksum**

This makes checksums excellent for detecting any changes or corruption.

## Checksums Provided

Two types of checksums are provided for maximum compatibility:

### SHA-256 (Primary)
- **Strength**: Very strong (256-bit)
- **Security**: Cryptographically secure
- **Use Case**: Long-term verification and security
- **Size**: 64 hexadecimal characters

### MD5 (Secondary)
- **Strength**: Moderate (128-bit)
- **Security**: Fast but older algorithm
- **Use Case**: Quick verification and compatibility
- **Size**: 32 hexadecimal characters

Both checksums are stored in: **fixity_metadata.json**

## Step-by-Step Verification

### On macOS / Linux

#### Using SHA-256:
```bash
# Calculate checksum
sha256sum met_inventory_standardized.tsv

# Expected output format:
# a1b2c3d4e5f6... [space] met_inventory_standardized.tsv
```

**Compare** the output with the SHA-256 value in `fixity_metadata.json`.

#### Using MD5:
```bash
# Calculate checksum
md5sum met_inventory_standardized.tsv

# Expected output format:
# x1y2z3a4b5c6... [space] met_inventory_standardized.tsv
```

**Compare** the output with the MD5 value in `fixity_metadata.json`.

### On macOS (Alternative)

macOS includes `shasum` command:

```bash
# SHA-256 checksum
shasum -a 256 met_inventory_standardized.tsv

# MD5 checksum (deprecated but available)
md5 met_inventory_standardized.tsv
```

### On Windows

#### Using PowerShell (Windows 10+):
```powershell
# SHA-256 checksum
Get-FileHash met_inventory_standardized.tsv -Algorithm SHA256 | Format-List

# MD5 checksum
Get-FileHash met_inventory_standardized.tsv -Algorithm MD5 | Format-List
```

#### Using certUtil (Windows Command Prompt):
```cmd
# SHA-256 checksum
certutil -hashfile met_inventory_standardized.tsv SHA256

# MD5 checksum
certutil -hashfile met_inventory_standardized.tsv MD5
```

### Using Python (Any Platform)

```python
import hashlib
import json

# Read the file and calculate SHA-256
with open('met_inventory_standardized.tsv', 'rb') as f:
    file_hash = hashlib.sha256(f.read()).hexdigest()
    print(f"SHA-256: {file_hash}")

# Load expected checksum from metadata
with open('fixity_metadata.json', 'r') as f:
    metadata = json.load(f)
    expected = metadata['output_file']['checksums']['sha256']
    
    if file_hash == expected:
        print("✓ File integrity verified!")
    else:
        print("✗ File integrity check FAILED!")
```

### Using the Provided Scripts

The easiest method - use the provided Python scripts:

```bash
# Option 1: Generate and verify checksums
python3 generate_checksums.py

# Option 2: Comprehensive verification
python3 verify_and_document.py

# Option 3: Use the reusable standardization script
python3 standardize_and_checksum.py
```

## Reading fixity_metadata.json

The metadata file is JSON format and contains checksums for both files:

```json
{
  "source_file": {
    "filename": "met_inventory.tsv",
    "checksums": {
      "sha256": "...",
      "md5": "..."
    }
  },
  "output_file": {
    "filename": "met_inventory_standardized.tsv",
    "checksums": {
      "sha256": "...",
      "md5": "..."
    }
  }
}
```

### Using jq (JSON parser):
```bash
# Extract SHA-256 of output file
jq '.output_file.checksums.sha256' fixity_metadata.json

# Extract all checksums for output
jq '.output_file.checksums' fixity_metadata.json
```

### Using Python:
```python
import json

with open('fixity_metadata.json') as f:
    metadata = json.load(f)

# Get output file SHA-256
print(metadata['output_file']['checksums']['sha256'])

# Get source file MD5
print(metadata['source_file']['checksums']['md5'])
```

## What to Look For

### ✓ Checksums Match
If your calculated checksum matches the value in `fixity_metadata.json`:
- File is unchanged ✓
- No corruption detected ✓
- Data integrity verified ✓
- Safe to use for analysis ✓

### ✗ Checksums Don't Match
If checksums don't match:
- File may have been modified (intentionally or accidentally)
- File may be corrupted
- Wrong file was checked
- Investigation needed ⚠️

**What to do:**
1. Check if you're verifying the correct file
2. Check if the file has been accidentally modified
3. Try re-downloading or copying from backup
4. Investigate source of discrepancy
5. Contact data custodian if unsure

## Verification Checklist

When verifying a file, check:

- [ ] File name matches: `met_inventory_standardized.tsv`
- [ ] File path is correct
- [ ] Checksums file (`fixity_metadata.json`) is present
- [ ] Using same hash algorithm (SHA-256 preferred)
- [ ] Calculated checksum entered correctly for comparison
- [ ] Comparing apples to apples (source vs. output)

## Common Issues

### Issue: Different Checksums for Same File

**Cause**: File was modified after standardization

**Solutions**:
- Restore from backup
- Regenerate standardized file using scripts
- Investigate what changed

### Issue: Can't Calculate Checksum

**Cause**: File not found or permission denied

**Solutions**:
- Verify file exists: `ls -la met_inventory_standardized.tsv`
- Check permissions: `chmod 644 met_inventory_standardized.tsv`
- Use full file path: `/path/to/met_inventory_standardized.tsv`

### Issue: Different Result Each Time

**Cause**: Likely environment or file path issue

**Solutions**:
- Use consistent file location
- Verify file hasn't been modified
- Try different checksum method
- Check for hidden characters in filename

## Comparison Table: SHA-256 vs MD5

| Feature | SHA-256 | MD5 |
|---------|---------|-----|
| Hash Length | 256 bits (64 hex chars) | 128 bits (32 hex chars) |
| Security | Cryptographically strong | Older, moderate |
| Speed | Slower | Faster |
| Collisions | Theoretically none | Vulnerable |
| Recommendation | **Use this for important files** | Legacy/compatibility only |
| Future-proof | Yes | No |

## Best Practices

1. **Store checksums separately** - Keep `fixity_metadata.json` in a secure location
2. **Verify immediately** - Check integrity after first download/transfer
3. **Verify periodically** - Check annually or before important use
4. **Document results** - Keep records of verification dates and results
5. **Use SHA-256** - Prefer SHA-256 over MD5 for new verifications
6. **Automate checks** - Use scripts for regular verification
7. **Keep both files** - Store source and output for audit trail

## Advanced Verification

### Creating a Verification Report

```bash
# Create a verification report file
{
  echo "FILE VERIFICATION REPORT"
  echo "Date: $(date)"
  echo "File: met_inventory_standardized.tsv"
  echo ""
  echo "SHA-256 Checksum:"
  sha256sum met_inventory_standardized.tsv
  echo ""
  echo "MD5 Checksum:"
  md5sum met_inventory_standardized.tsv
  echo ""
  echo "Expected SHA-256 (from metadata):"
  jq '.output_file.checksums.sha256' fixity_metadata.json
} > verification_report_$(date +%Y%m%d).txt
```

### Batch Verification Script

```bash
#!/bin/bash
# verify_all.sh - Verify multiple files

for file in *.tsv; do
  echo "Verifying: $file"
  sha256sum "$file"
done
```

### Automated Daily Verification

```bash
# Add to crontab for daily verification
# Edit crontab: crontab -e
# Add line: 0 9 * * * /path/to/verify_and_document.py >> /var/log/data_verification.log
```

## Summary

1. **Download** both the standardized TSV and `fixity_metadata.json`
2. **Choose** SHA-256 or use provided scripts
3. **Calculate** checksum using appropriate command
4. **Compare** with value in `fixity_metadata.json`
5. **Document** results for audit trail
6. **Verify periodically** to detect any changes

For most users: **Use the provided Python scripts** - they automate all of this!

```bash
python3 verify_and_document.py
```

---

**Questions?** Refer to the other documentation files included in this package.
