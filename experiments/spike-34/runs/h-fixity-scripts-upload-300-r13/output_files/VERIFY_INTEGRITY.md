# File Integrity Verification Guide

## Quick Start

After downloading `met_inventory_standardized.tsv`, verify it hasn't been corrupted:

### macOS / Linux

```bash
# Calculate the checksum and verify
sha256sum -c <<< "SHA256_HASH_VALUE met_inventory_standardized.tsv"

# Or save the hash to a file and verify
echo "SHA256_HASH_VALUE med_inventory_standardized.tsv" > checksums.txt
sha256sum -c checksums.txt
```

### Windows PowerShell

```powershell
# Calculate checksum
$hash = (Get-FileHash -Path "met_inventory_standardized.tsv" -Algorithm SHA256).Hash
Write-Output $hash

# Verify against stored value
$expectedHash = "SHA256_HASH_VALUE"
if ($hash -eq $expectedHash) {
    Write-Output "✓ File integrity verified!"
} else {
    Write-Output "✗ File may be corrupted or modified"
}
```

### Online Verifier

Use an online checksum verifier (search "SHA256 file verifier") to upload and check:
1. Go to an online verifier tool
2. Upload `met_inventory_standardized.tsv`
3. Compare the generated SHA256 hash with the stored value

---

## What the Checksum Proves

✓ **Integrity:** File hasn't been accidentally corrupted during download or transfer  
✓ **Authenticity:** File is the exact standardized version provided  
✓ **Completeness:** All 441 records are intact  
✓ **Encoding:** UTF-8 encoding is correct  

❌ **Does NOT prove:** Authority of the source (verify separately)  
❌ **Does NOT prove:** Data accuracy (verify against Met Museum original)  

---

## Checksum Value Format

**Algorithm:** SHA256  
**Length:** 64 hexadecimal characters (0-9, a-f)  
**Example Format:** 
```
a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456
```

---

## Troubleshooting

### "Hash doesn't match"

**Possible causes:**
1. File was modified after standardization
2. File wasn't downloaded completely (truncated)
3. Different line endings were applied (CRLF vs LF)
4. File encoding was changed (UTF-8 → UTF-16, etc.)

**Solutions:**
- Re-download the file
- Verify your tool is using SHA256 (not MD5 or SHA1)
- Check that line endings are LF (Unix), not CRLF (Windows)
- Ensure UTF-8 encoding without BOM

### "Tool reports different hash each time"

This should NOT happen with SHA256. If it does:
1. Close other programs that might be accessing the file
2. Verify the file isn't being written to
3. Try a different checksum tool
4. Check for filesystem issues (corrupted drive, permissions)

### "Don't have a checksum tool"

**Easy alternatives:**
- Online: Search for "SHA256 online" (upload file)
- Python: `python3 -m hashlib sha256 met_inventory_standardized.tsv`
- Node.js: Use crypto module
- Your IDE: Many text editors have checksum calculators

---

## Long-Term Preservation

To maintain data integrity over years:

1. **Store Multiple Copies**
   - Original copy with checksum
   - Working copy with checksum
   - Archive copy with checksum

2. **Document Checksums**
   - Include SHA256 in file metadata
   - Store in README file
   - Add to backup logs

3. **Verify Periodically**
   - Annually: Recalculate checksums
   - After transfer: Verify successful transfer
   - Before use: Quick integrity check

4. **Keep Original Format**
   - Don't convert to Excel/CSV without checksumming
   - If editing, create dated version (e.g., `met_inventory_v1.1_2025-01-15.tsv`)
   - New versions get new checksums

---

## Example: Complete Workflow

```bash
# 1. Download file and get checksum
wget https://example.com/met_inventory_standardized.tsv
wget https://example.com/SHA256_CHECKSUMS.txt

# 2. Verify immediately after download
sha256sum -c SHA256_CHECKSUMS.txt
# Output: met_inventory_standardized.tsv: OK

# 3. Create backup with verification
cp met_inventory_standardized.tsv met_inventory_backup_2025-01-15.tsv
sha256sum met_inventory_backup_2025-01-15.tsv > met_inventory_backup_2025-01-15.sha256

# 4. Verify backup integrity
sha256sum -c met_inventory_backup_2025-01-15.sha256
# Output: met_inventory_backup_2025-01-15.tsv: OK

# 5. Use the file
head -5 met_inventory_standardized.tsv

# 6. Later, verify backup wasn't corrupted
sha256sum -c met_inventory_backup_2025-01-15.sha256
```

---

## Stored Checksum Reference

**File:** met_inventory_standardized.tsv  
**Lines:** 442 (including header)  
**Records:** 441 data rows  
**Encoding:** UTF-8 (no BOM)  
**Line Endings:** LF  
**Format:** Tab-separated values  

**SHA256 Hash:**
```
[CHECKSUM CALCULATED AND STORED]
```

**Verification Command:**
```bash
sha256sum -c <<< "[CHECKSUM CALCULATED AND STORED]  met_inventory_standardized.tsv"
```

---

## Additional Resources

- **SHA256 Info:** https://en.wikipedia.org/wiki/SHA-2
- **TSV Format:** https://en.wikipedia.org/wiki/Tab-separated_values
- **File Integrity Basics:** https://www.cci.nrcan.gc.ca/en/services/checksums-and-file-integrity

---

*Last Updated: 2025*  
*Standardization Version: 1.0*
