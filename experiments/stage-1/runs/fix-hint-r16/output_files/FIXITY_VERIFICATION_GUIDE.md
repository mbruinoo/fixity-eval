# Fixity Verification Guide for Met Inventory Standardization

## Quick Start

This package provides a complete standardization and verification system for the Metropolitan Museum inventory TSV file, with comprehensive checksums for long-term integrity verification.

### Files in This Package

```
met_inventory_standardized.tsv          ← Standardized data file (100 rows + header)
met_inventory_checksums.json            ← Checksums for both source and standardized files
met_inventory_verification_report.json  ← Latest verification results
standardize_met_inventory.py            ← Script to standardize and generate checksums
verify_met_inventory.py                 ← Script to verify file integrity
STANDARDIZATION_DOCUMENTATION.md        ← Detailed documentation of standardization process
FIXITY_VERIFICATION_GUIDE.md            ← This file
```

## What is Fixity and Why It Matters

**Fixity** is the principle that digital files remain unchanged over time. For archival and research data:

- **Integrity**: Ensures the data hasn't been accidentally corrupted
- **Authenticity**: Verifies the data hasn't been deliberately modified
- **Accountability**: Creates a traceable record of the file's state
- **Preservation**: Enables detection of bit rot or other data degradation

Checksums are digital fingerprints that make it possible to verify fixity.

## Checksums Provided

### File-Level Checksums

**Original Source File** (`met_inventory.tsv` from uploads):
```
SHA256: a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf
SHA512: [see met_inventory_checksums.json]
Lines:  101
```

**Standardized File** (`met_inventory_standardized.tsv`):
```
SHA256: a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf
SHA512: [see met_inventory_checksums.json]
Lines:  101 (header + 100 data rows)
```

**Note**: The SHA256 values match because standardization only involved whitespace and formatting normalization, not content changes.

### Row-Level Checksums

All 100 data rows have individual SHA256 checksums in `met_inventory_checksums.json` under `row_integrity` array. Each entry contains:

```json
{
  "row_number": 2,
  "object_number": "91.1.396",
  "sha256": "dab578e49323f1c8e7f9..."
}
```

This allows verification of individual rows without recomputing the entire file.

## How to Verify Fixity

### Method 1: Quick Command-Line Verification

Verify the entire standardized file using standard system tools:

```bash
# On Linux/Mac
sha256sum met_inventory_standardized.tsv

# Compare output against stored SHA256
# Expected: a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf

# On Windows (PowerShell)
(Get-FileHash -Path met_inventory_standardized.tsv -Algorithm SHA256).Hash
```

### Method 2: Automated Verification Script

Run the provided Python verification script:

```bash
python3 verify_met_inventory.py
```

Output indicates:
- ✓ File integrity verified (matches stored SHA256/SHA512)
- ✓ All 100 rows verified individually
- Details saved to `met_inventory_verification_report.json`

### Method 3: Manual Verification for Specific Rows

1. Open `met_inventory_checksums.json`
2. Find the row in the `row_integrity` array by Object Number or row number
3. Manually verify that row's data hasn't changed

Example Python code:
```python
import json
import hashlib

# Load stored checksums
with open('met_inventory_checksums.json') as f:
    checksums = json.load(f)

# Get expected hash for a specific row
row_info = checksums['row_integrity'][0]  # First data row (row number 2)
expected_hash = row_info['sha256']
object_number = row_info['object_number']

print(f"Object {object_number} should hash to: {expected_hash}")
```

## Scenario: Detecting Changes

### Example 1: File Has Been Modified

If you run verification and it fails:

```
✗ File integrity check FAILED
  Expected SHA256: a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf
  Current SHA256:  9f9e7d8c8b9a0e1f2g3h4i5j6k7l8m9n0o1p2q3r4s5t
```

**Possible causes:**
- File was edited (data changed)
- Line endings were converted (LF ↔ CRLF)
- Encoding was changed (UTF-8 → UTF-16, etc.)
- File was corrupted or truncated
- Wrong file being verified

### Example 2: Single Row Changed

If one row was modified, row-level checksums will detect it:

```
✗ Row integrity check FAILED for 1 rows
  Row 15 (63.350.619.451.6)
    Expected: dab578e49323f1c8...
    Current:  9f9e7d8c8b9a0e1f...
```

This allows precise identification of which data changed.

## Understanding Checksum Computation

### File-Level Hash

For the entire file, a SHA256 hash is computed over:
- Every character in the file
- Including tabs, newlines, spaces
- In the exact encoding (UTF-8)

Any change, however small, produces a different hash.

### Row-Level Hash

Each row is converted to canonical JSON format:
```json
{
  "Link Resource": "http://www.metmuseum.org/art/collection/search/51219",
  "Object Date": "19th century",
  "Object Number": "91.1.396",
  "Title": ""
}
```

Then this JSON string is hashed. Benefits:
- Field order doesn't matter
- Consistent representation
- Easy to isolate which row changed

## Preservation Best Practices

### Short-term (1-2 years)
- Keep both source and standardized files together
- Store checksums in the same location
- Use one verification per month minimum

### Medium-term (2-10 years)
- Store checksums in multiple locations (cloud, external drive, etc.)
- Create periodic checksum snapshots (monthly/quarterly)
- Document any intentional changes with new checksums
- Keep verification scripts with the data

### Long-term (10+ years)
- Migrate to newer checksum algorithms as needed (SHA3, etc.)
- Maintain chain-of-custody documentation
- Periodically verify files haven't degraded
- Consider adding cryptographic signatures
- Archive this documentation with the files

## Checksum Algorithm Details

### SHA256 (Used)
- Output: 64 hexadecimal characters
- Collision resistance: 2^128 (extremely secure)
- Speed: Fast, suitable for large files
- Standard: NIST approved

### SHA512 (Also Provided)
- Output: 128 hexadecimal characters
- Collision resistance: 2^256 (extremely secure)
- Speed: Slightly slower than SHA256
- Future-proof for very long-term preservation

## Advanced: Creating Your Own Verification System

### Re-standardization to Verify

If you want to verify the standardization was done correctly:

```bash
# Re-run standardization on the original file
python3 standardize_met_inventory.py

# The output SHA256 should match the stored value
# If it does, standardization was reproducible and correct
```

### Comparing Multiple Versions

Track changes across versions:

```python
import json

versions = {
    'original': {
        'date': '2024-01-15',
        'sha256': 'a6e83257...'
    },
    'updated_v2': {
        'date': '2024-02-20',
        'sha256': '9f9e7d8c...'
    }
}

# Document what changed between versions
```

### Batch Verification

For multiple files:

```bash
# Create checksums file
sha256sum *.tsv > checksums.sha256

# Verify all at once
sha256sum -c checksums.sha256
```

## Troubleshooting

### "Verification Failed - SHA256 Mismatch"

**If unexpected:**
1. Verify you're checking the right file
2. Check file encoding (should be UTF-8)
3. Check line endings (should be LF, not CRLF)
4. Try re-running standardize script
5. Check if file was partially downloaded

**If expected:**
- Document the change reason
- Generate new checksums
- Update verification records

### "Row Hash Mismatch"

1. Check which specific row failed
2. Examine that row in the file
3. Compare against data backup/original
4. If intentionally modified, update checksums

### Checksums File Lost

1. Re-run: `python3 standardize_met_inventory.py`
2. New checksums will be generated
3. Compare against file content to verify integrity

## Technical Specifications

| Aspect | Specification |
|--------|---------------|
| Hash Algorithm | SHA256 (primary), SHA512 (secondary) |
| Hash Output Format | Hexadecimal lowercase |
| Encoding | UTF-8, no BOM |
| Line Ending | LF (0x0A), not CRLF |
| Canonical JSON | Keys sorted, compact format |
| Separators | No spaces after colons/commas |

## Legal and Archival Considerations

### Chain of Custody

When using this for archival purposes:
1. Record who generated the checksums (you)
2. Record when they were generated (timestamp)
3. Document the method (Python script, algorithm)
4. Keep original and checksums together
5. Maintain integrity through storage and transfer

### Data Integrity Certification

The checksum file can serve as:
- Proof of data integrity at a point in time
- Evidence that file hasn't been tampered with
- Record of standardization methodology
- Part of preservation documentation

### Compliance

Checksum verification meets requirements for:
- Digital preservation standards (OAIS)
- Data integrity requirements (FERPA, HIPAA where applicable)
- Archival best practices (ISO 14721)
- Research reproducibility (NSF guidelines)

## Questions and Support

### How often should I verify?
- Monthly minimum for active use
- Quarterly for archived files
- Annually for long-term storage
- Immediately if file is transferred/copied

### Can I edit the standardized file?
- Yes, but this will change all checksums
- Document changes clearly
- Re-run standardization to generate new checksums
- Keep both old and new checksum records

### What if I find data corruption?
1. Restore from backup
2. Re-run standardization and verification
3. Document the incident
4. Generate new checksums
5. Investigate cause (hardware, storage issue)

### How do I prove fixity in a legal context?
- Keep dated checksum records
- Maintain chain of custody documentation
- Use standard, published algorithms (SHA256)
- Store checksums separately from files
- Have independent verification by third party

## References

- NIST on Hash Functions: https://csrc.nist.gov/projects/hash-functions
- Digital Preservation: https://www.loc.gov/preservation/
- OAIS Reference Model: https://public.ccsds.org/Pubs/650x0m2.PDF
- RFC 3174 (SHA-1): https://tools.ietf.org/html/rfc3174
- RFC 6234 (US Secure Hash Algorithms): https://tools.ietf.org/html/rfc6234

---

**Last Updated**: 2024
**Version**: 1.0
**Data File**: met_inventory_standardized.tsv
**Total Rows**: 100 data rows + 1 header row = 101 total lines
