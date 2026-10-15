# TSV Standardization - Implementation Guide

## Quick Start

### 1. Run the Standardization

```bash
cd /mnt/user-data/outputs
chmod +x run_standardization.sh
./run_standardization.sh
```

### 2. Verify the Results

```bash
python3 verify_integrity.py \
  met_inventory_standardized.tsv \
  met_inventory_manifest.json
```

### 3. Review the Audit Trail

```bash
cat standardization_audit.log
```

---

## What Gets Standardized

### Issues Fixed

| Issue | Before | After |
|-------|--------|-------|
| Inconsistent encoding | Possibly mixed | UTF-8 throughout |
| Line endings | Mixed (CRLF/LF) | Unix LF only |
| Header spacing | Extra spaces | Normalized |
| Field trimming | Inconsistent | All trimmed |
| Tab delimiters | Possible inconsistency | Consistent tabs |
| Data validation | Unchecked | Quality issues identified |

### Data Preserved

- ✓ All original values intact
- ✓ Special characters and Unicode
- ✓ Formatting within cells (quotes, etc.)
- ✓ Relative row and column order
- ✓ All 100+ records processed

---

## Output Files Explained

### met_inventory_standardized.tsv

The cleaned, standardized data file:
- UTF-8 encoding
- Tab-delimited
- Unix line endings (LF)
- Normalized headers
- Cleaned values

**Use this file for:**
- Data import into databases
- Spreadsheet applications
- Data processing pipelines
- Archives and preservation

### met_inventory_manifest.json

Machine-readable metadata and checksums:

```
Contains:
  - Timestamp of standardization
  - File paths and sizes
  - MD5 and SHA256 hashes
  - Row and column counts
  - Data quality issues
  - Applied standardization rules
```

**Use this file for:**
- Integrity verification
- Documenting provenance
- Automated validation
- Audit trails
- Long-term preservation records

### standardization_audit.log

Human-readable operation log:

```
Contains:
  - All processing steps
  - File size changes
  - Validation results
  - Issue summaries
  - Timestamps
```

**Use this for:**
- Understanding what happened
- Troubleshooting problems
- Quality assurance documentation
- Change management records

---

## Checksum Verification Process

### What are Checksums?

Checksums are cryptographic fingerprints that detect any changes to a file:

- **MD5**: 32-character hex string (legacy, fast)
- **SHA256**: 64-character hex string (secure, standard)

### How Verification Works

```
Source File
    ↓
[Process]
    ↓
Output File + Manifest
    ↓
[Compute Checksums]
    ↓
Compare with Manifest
    ↓
✓ MATCH = File Integrity Confirmed
✗ MISMATCH = File Corruption Detected
```

### Interpreting Results

**Checksum Match:**
```
✓ SHA256 matches: 3f4d5e6f7g8h9i0j1k2l...
File integrity confirmed - safe to use
```

**Checksum Mismatch:**
```
✗ SHA256 mismatch!
  Expected: 3f4d5e6f7g8h9i0j1k2l...
  Actual:   different_hash_1234567...
File may be corrupted - investigate before use
```

### Why This Matters

Checksums ensure:
1. File hasn't been corrupted during transfer
2. File hasn't been tampered with
3. File is identical to what was created
4. Long-term preservation integrity

---

## Data Quality Issues

The standardization process identified potential issues. Review the manifest:

```bash
# Extract issues from manifest
python3 << 'EOF'
import json
with open('met_inventory_manifest.json') as f:
    manifest = json.load(f)
    issues = manifest['statistics']['issues']
    if issues and issues != 'None':
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("No issues found")
EOF
```

### Common Issues

- **Missing required fields** - Object Date, Title, or Object Number empty
- **Incomplete records** - Rows with minimal data
- **Encoding problems** - Special characters not handled correctly

### Resolution

1. Review the issues listed in the manifest
2. Examine the original file for these records
3. Decide: correct data or document as-is
4. Re-run standardization if corrections made

---

## Advanced Usage

### Custom Processing

Modify `standardize_tsv.py` to add rules like:

```python
# Add validation rule
if row['Object Date'] == '':
    issues.append(f"Row {row_num}: Empty Object Date")

# Add transformation
row['Object Date'] = row['Object Date'].upper()

# Add filtering
if row['Object Number'].startswith('EXCLUDE_'):
    continue  # Skip this row
```

### Batch Processing

Process multiple files:

```bash
for file in /mnt/user-data/uploads/*.tsv; do
    python3 standardize_tsv.py \
        "$file" \
        "${file%.*}_standardized.tsv" \
        "${file%.*}_manifest.json"
done
```

### Integration with Pipelines

Export checksums for downstream systems:

```python
import json

with open('met_inventory_manifest.json') as f:
    manifest = json.load(f)
    
    # For CI/CD pipelines
    print(f"SOURCE_CHECKSUM={manifest['source_file']['checksums']['sha256']}")
    print(f"OUTPUT_CHECKSUM={manifest['output_file']['checksums']['sha256']}")
```

---

## Preservation Best Practices

### File Organization

```
project/
├── source/
│   └── met_inventory.tsv
├── standardized/
│   ├── met_inventory_standardized.tsv
│   ├── met_inventory_manifest.json
│   └── standardization_audit.log
└── scripts/
    ├── standardize_tsv.py
    ├── verify_integrity.py
    ├── run_standardization.sh
    └── README_STANDARDIZATION.md
```

### Documentation to Keep

1. **README** - What was done and why
2. **Manifest** - Technical metadata
3. **Audit Log** - Processing history
4. **Original File** - For comparison
5. **Scripts** - For reproducibility

### Checksum Storage

Keep checksums in multiple locations:

```
# In manifest (JSON)
{
  "checksums": {
    "md5": "...",
    "sha256": "..."
  }
}

# In README or separate file
SOURCE_MD5: a1b2c3d4e5f6...
SOURCE_SHA256: 0a1b2c3d4e5f6g7h8i9j...

OUTPUT_MD5: x9y8z7w6v5u4...
OUTPUT_SHA256: 1a2b3c4d5e6f7g8h9i0j...
```

### Long-Term Verification

Every few years, verify file integrity:

```bash
python3 verify_integrity.py \
  met_inventory_standardized.tsv \
  met_inventory_manifest.json
```

If checksums still match, file is preserved correctly.

---

## Common Questions

### Q: Why different file sizes?

**A:** Standardization may:
- Remove redundant whitespace (usually shrinks)
- Normalize line endings (may affect size)
- Add necessary formatting (may grow slightly)

Size change is normal. Checksums verify content.

### Q: Can I edit the standardized file?

**A:** Yes, but:
- Checksums will no longer match
- Document changes in a new audit log
- Re-run standardization if needed
- Keep original as reference

### Q: What if verification fails?

**A:** 
1. Don't use the file until resolved
2. Check file isn't corrupted (try opening in editor)
3. Verify manifest hasn't been modified
4. Re-run standardization from source
5. Contact support if issue persists

### Q: How long do checksums stay valid?

**A:** Indefinitely. Checksums are mathematical constants - they never expire. As long as the file hasn't changed, checksums will always match.

### Q: Which checksum should I use?

**A:** Use SHA256 for:
- New projects (cryptographically secure)
- Long-term preservation
- Security-sensitive applications

Use MD5 for:
- Legacy systems
- Quick reference (with SHA256 as backup)
- Non-security-critical uses

Use BOTH for maximum assurance.

---

## Troubleshooting

### Script won't run

```bash
# Make executable
chmod +x standardize_tsv.py
chmod +x run_standardization.sh
chmod +x verify_integrity.py

# Run with explicit Python
python3 standardize_tsv.py
```

### Encoding errors

```bash
# Check input file encoding
file -b --mime-encoding met_inventory.tsv

# If not UTF-8, convert first
iconv -f ISO-8859-1 -t UTF-8 input.tsv > input_utf8.tsv
```

### Verification failures

```bash
# Debug verification step-by-step
python3 -c "
import hashlib
with open('met_inventory_standardized.tsv', 'rb') as f:
    print('MD5:', hashlib.md5(f.read()).hexdigest())
"

# Compare with manifest value
python3 -c "
import json
with open('met_inventory_manifest.json') as f:
    m = json.load(f)
    print('Expected MD5:', m['output_file']['checksums']['md5'])
"
```

### Missing files

```bash
# Check what was created
ls -lah /mnt/user-data/outputs/

# Verify paths in script
head -20 standardize_tsv.py
```

---

## Next Steps

1. **Review** - Examine the standardized file and manifest
2. **Verify** - Run the integrity verification script
3. **Document** - Record any data issues found
4. **Preserve** - Archive standardized file and manifest together
5. **Share** - Use standardized file for your project

---

## Additional Resources

- **Python Documentation**: https://docs.python.org/3/library/csv.html
- **Checksum Standards**: https://csrc.nist.gov/projects/hash-functions
- **Data Preservation**: https://www.loc.gov/preservation/
- **TSV Format**: https://en.wikipedia.org/wiki/Tab-separated_values

---

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2024-01-15 | 1.0 | Initial standardization |

---

**Document Created**: 2024-01-15
**For**: Met Inventory TSV Standardization
**Standardization Script**: v1.0
