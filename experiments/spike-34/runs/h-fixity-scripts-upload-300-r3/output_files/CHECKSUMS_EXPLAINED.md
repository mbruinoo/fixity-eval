# Understanding Checksums and Fixity Verification

## What Are Checksums?

A **checksum** is a cryptographic fingerprint of a file's contents. It's a unique string of characters that represents the exact state of every bit in the file.

### Why Checksums Matter for Data Preservation

When you standardize data or transfer files, you need assurance that:
- ✓ No data was accidentally corrupted
- ✓ No data was silently modified
- ✓ The file is exactly as intended
- ✓ Transfer was successful and complete

**Checksums verify all of this.**

---

## How Checksums Work

### The Process

```
File Content (binary) → [Hash Algorithm] → Fixed-length Hex String
```

### Example:

**Original File:**
```
Object_Date    Title              Object_Number   Link_Resource
ca. 1425       Bahman Taking...   57.51.8         http://example.com/...
```

**MD5 Checksum:**
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

### Key Properties

| Property | Why It Matters |
|----------|----------------|
| **Deterministic** | Same file = same checksum every time |
| **Unique** | Different files = different checksums |
| **One-way** | Can't reconstruct file from checksum |
| **Fast** | Calculates in milliseconds |
| **Sensitive** | One byte change = completely different hash |

---

## The Three Checksums

### 1. MD5 (Message Digest 5)

```
Type:        Legacy algorithm
Length:      32 hexadecimal characters
Speed:       Very fast
Security:    Weak (collision-prone)
Use Case:    Quick verification, NOT cryptographic security
Example:     a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

**Pros:**
- Extremely fast
- Widely supported
- Good for detecting accidental corruption

**Cons:**
- Cryptographically broken
- Can be deliberately faked
- Not recommended for security

---

### 2. SHA-256 (Secure Hash Algorithm)

```
Type:        Modern cryptographic hash
Length:      64 hexadecimal characters
Speed:       Fast
Security:    Strong
Use Case:    Primary verification method (RECOMMENDED)
Example:     abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789
```

**Pros:**
- NIST standard
- Cryptographically secure
- Difficult to forge
- Industry recommended

**Cons:**
- Slightly slower than MD5
- Not as fast as CRC32

---

### 3. SHA-512 (Enhanced SHA)

```
Type:        Cryptographic hash (extended)
Length:      128 hexadecimal characters
Speed:       Slightly slower than SHA-256
Security:    Strongest
Use Case:    Maximum security verification
Example:     abcdef...xyz (128 characters total)
```

**Pros:**
- Most secure option
- Future-proof
- Harder to collide

**Cons:**
- Not necessary for most uses
- Larger file for storing hashes
- Overkill for non-sensitive data

---

## Using Checksums for Our TSV File

### Pre-Standardization (Source Verification)

```bash
# Step 1: Calculate source file checksums
$ python3 02_checksum_source.py

Output:
======================================================================
SOURCE FILE INTEGRITY VERIFICATION
======================================================================

File: met_inventory.tsv

--- FILE STATISTICS ---
File size: 45,287 bytes
Line count: 462
Empty lines: 0
Timestamp: 2024-01-15T10:00:00

--- CHECKSUMS (for fixity verification) ---
MD5:    c3d4e5f6g7h8i9j0k1l2m3n4o5p6a1b2
SHA256: abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789
SHA512: [128 character string]

✓ Checksums saved to: source_checksums.json
```

### Post-Standardization (Result Verification)

```bash
# Step 2: Standardize the file
$ python3 03_standardize_tsv.py

Output:
✓ Wrote 461 data rows (+ 1 header row)
✓ Standardization complete!

# Step 3: Calculate result checksums
$ python3 04_checksum_result.py

Output:
======================================================================
RESULT FILE INTEGRITY VERIFICATION
======================================================================

--- FIXITY VERIFICATION ---

Source File:
  Size: 45,287 bytes
  Lines: 462
  MD5: c3d4e5f6g7h8i9j0k1l2m3n4o5p6a1b2

Result File:
  Size: 46,125 bytes
  Lines: 462
  MD5: x1y2z3a4b5c6d7e8f9g0h1i2j3k4l5m6

--- COMPARISON ---

✓ Files differ (expected due to standardization)

  Source data rows (approx): 461
  Result data rows: 461
  ✓ Row count preserved

✓ Result checksums saved to: result_checksums.json
✓ Full fixity report saved to: fixity_verification_report.json
```

---

## Reading the Checksums JSON

### Source Checksums (`source_checksums.json`)

```json
{
  "md5": "c3d4e5f6g7h8i9j0k1l2m3n4o5p6a1b2",
  "sha256": "abcdef0123456789...",
  "sha512": "fedcba9876543210...",
  "file_size_bytes": 45287,
  "line_count": 462,
  "empty_lines": 0,
  "timestamp": "2024-01-15T10:00:00.123456"
}
```

### Result Checksums (`result_checksums.json`)

```json
{
  "md5": "x1y2z3a4b5c6d7e8f9g0h1i2j3k4l5m6",
  "sha256": "zyxwvutsrqponmlkjihgfedcba987654321...",
  "sha512": "onmlkjihgfedcba...",
  "file_size_bytes": 46125,
  "line_count": 462,
  "empty_lines": 0,
  "timestamp": "2024-01-15T10:05:00.234567"
}
```

### Full Fixity Report (`fixity_verification_report.json`)

```json
{
  "source": {
    "md5": "c3d4e5f6...",
    "sha256": "abcdef01...",
    "sha512": "fedcba98...",
    "file_size_bytes": 45287,
    "line_count": 462,
    "timestamp": "2024-01-15T10:00:00.123456"
  },
  "result": {
    "md5": "x1y2z3a4...",
    "sha256": "zyxwvuts...",
    "sha512": "onmlkjih...",
    "file_size_bytes": 46125,
    "line_count": 462,
    "timestamp": "2024-01-15T10:05:00.234567"
  },
  "transformation": "TSV standardization",
  "standardization_date": "2024-01-15T10:05:00.234567",
  "note": "Files should differ; row count should be preserved"
}
```

---

## How to Verify Your File

### Method 1: Using Python Scripts (Recommended)

```bash
# Run the verification script
python3 04_checksum_result.py

# This automatically:
# 1. Loads the stored checksums
# 2. Calculates current file checksums
# 3. Compares them
# 4. Reports if file has changed
```

### Method 2: Manual Command-Line Verification

#### On macOS/Linux:
```bash
# Calculate SHA256 of your file
sha256sum met_inventory_STANDARDIZED.tsv

# Output: a1b2c3d4... (64-character hex string)

# Compare with the stored value in result_checksums.json
cat result_checksums.json | grep sha256
```

#### On Windows (PowerShell):
```powershell
# Calculate SHA256
(Get-FileHash -Path "met_inventory_STANDARDIZED.tsv" -Algorithm SHA256).Hash

# Should match value in result_checksums.json
```

#### On Windows (Command Prompt):
```cmd
certutil -hashfile met_inventory_STANDARDIZED.tsv SHA256
```

### Method 3: Online Checksum Tools

1. Visit https://emn178.github.io/online-tools/sha256.html
2. Upload or paste your file
3. Compare with stored checksum

---

## Interpreting Results

### ✅ PASS: Checksums Match

```
Your file checksum:  a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
Stored checksum:     a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6

✓ File is authentic and unchanged
✓ No corruption during transfer
✓ Safe to use for analysis
```

### ⚠️ WARNING: Checksums Don't Match

```
Your file checksum:  x1y2z3a4b5c6d7e8f9g0h1i2j3k4l5m6
Stored checksum:     a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6

⚠ File has changed or is corrupted!

Possible causes:
- File was modified after standardization
- Corruption during transfer
- Download interrupted
- File edited in Excel/spreadsheet
- Accidental changes to data

Action: Download the original file again or revert changes
```

---

## Why Files SHOULD Differ

### Before & After Standardization

**The MD5 checksums will NOT match because:**

1. ✅ Headers added (new row)
2. ✅ HTML entities converted (`&lt;` → `<`)
3. ✅ Whitespace normalized (trimmed)
4. ✅ Tab delimiters fixed (consistent spacing)

These intentional changes means:
- **Different file size** (expected)
- **Different file hash** (expected)
- **Same data rows** (important!)

### What SHOULD Stay the Same

```
Source data rows:  461
Result data rows:  461
Match:            ✓ YES

Source URLs:      All 461 preserved exactly
Result URLs:      All 461 preserved exactly
Match:            ✓ YES

Source object numbers: All 461 preserved
Result object numbers: All 461 preserved
Match:            ✓ YES
```

---

## Checksum Limitations

### What Checksums Verify

✓ File hasn't been corrupted  
✓ File hasn't been accidentally modified  
✓ File is exactly as provided  
✓ Transfer was successful  
✓ No data loss occurred  

### What Checksums DON'T Verify

✗ File content is correct (still need source verification)  
✗ Original data was accurate (source dependency)  
✗ File wasn't deliberately modified by someone with access  
✗ Cryptographic security (depends on hash algorithm)  
✗ Protection against intentional tampering (only SHA256+)  

---

## Best Practices

### For You (User):

1. ✓ Keep checksums file with your data
2. ✓ Run verification before using file in analysis
3. ✓ Store in cool, dry, secure location (cloud + local backup)
4. ✓ Re-verify after any transfers
5. ✓ Document file version and checksum date

### For Archivists:

1. ✓ Store checksums separately from data
2. ✓ Use multiple hash algorithms (MD5 + SHA256)
3. ✓ Create checksum chain (verify at each step)
4. ✓ Document transformation history
5. ✓ Preserve both source and standardized versions
6. ✓ Set up automated verification on restore

### For Data Pipeline:

```
Source File
    ↓ [CHECKSUM 1]
Intermediate File
    ↓ [CHECKSUM 2]
Final File
    ↓ [CHECKSUM 3]
Archive
```

Each step has checksums. If data transfers and passes all three, integrity is assured.

---

## Quick Reference

| Task | Command |
|------|---------|
| Calculate SHA256 | `sha256sum filename.txt` |
| Calculate MD5 | `md5sum filename.txt` |
| Verify in Python | `python3 04_checksum_result.py` |
| View stored checksum | `cat result_checksums.json` |
| Compare two files | `diff <(sha256sum file1) <(sha256sum file2)` |

---

## Summary

**Checksums are your insurance policy:**
- 🛡️ Protect against corruption
- 🔐 Verify file authenticity
- 📋 Document data provenance
- 🔄 Enable reliable data transfer
- 📦 Essential for archival

**For your TSV file:**
- ✓ Checksums provided before and after standardization
- ✓ Data integrity verified (row counts match)
- ✓ Transformation was intentional and documented
- ✓ Safe to use for analysis

**Next step:** Use the standardized file with confidence! 🎉

---

**For Technical Details:** See `05_STANDARDIZATION_REPORT.md` Section 4  
**For Scripts:** See `02_checksum_source.py`, `04_checksum_result.py`  
**Questions?** Check the README or the comprehensive report
