# TSV Standardization - Checklist & Workflow

## Pre-Standardization Checklist

- [ ] Input file `met_inventory.tsv` is present in `/mnt/user-data/uploads/`
- [ ] Sufficient disk space available (~10x file size recommended)
- [ ] Python 3.x installed (`python3 --version`)
- [ ] Bash shell available (`bash --version`)
- [ ] Write permissions to `/mnt/user-data/outputs/`
- [ ] Scripts are executable:
  ```bash
  chmod +x standardize_tsv.py run_standardization.sh verify_integrity.py
  ```
- [ ] Read the documentation (at least SUMMARY.md)

## Running Standardization

### Step 1: Execute Standardization
```bash
# Make scripts executable
chmod +x run_standardization.sh

# Run the standardization
./run_standardization.sh
```

- [ ] Script starts without errors
- [ ] Shows "Processing:" message
- [ ] Computes checksums
- [ ] Reads and standardizes data
- [ ] Writes output files
- [ ] Completes with "✓ Standardization complete!"

### Step 2: Check Output Files

```bash
ls -lah met_inventory_*
```

- [ ] `met_inventory_standardized.tsv` created (data file)
- [ ] `met_inventory_manifest.json` created (metadata)
- [ ] `standardization_audit.log` created (audit trail)

### Step 3: Verify Output

Run the verification script:

```bash
python3 verify_integrity.py
```

- [ ] File size check passes
- [ ] MD5 checksum matches
- [ ] SHA256 checksum matches
- [ ] TSV structure is valid
- [ ] Column count matches
- [ ] Row count matches
- [ ] Shows "✓ VERIFICATION PASSED"

### Step 4: Review Audit Log

```bash
cat standardization_audit.log
```

- [ ] Timestamp recorded
- [ ] Input file found
- [ ] Processing completed
- [ ] Output files created
- [ ] Verification successful
- [ ] No error messages

### Step 5: Examine Manifest

```bash
python3 -m json.tool met_inventory_manifest.json | head -30
```

- [ ] Contains timestamp
- [ ] Lists source file checksum
- [ ] Lists output file checksum
- [ ] Shows row/column statistics
- [ ] Notes any data issues
- [ ] Documents standardization rules

## Post-Standardization Checklist

### File Organization

- [ ] Original file still in `/mnt/user-data/uploads/`
- [ ] Standardized file in `/mnt/user-data/outputs/`
- [ ] Manifest alongside standardized file
- [ ] Audit log saved for reference
- [ ] Scripts saved for reproducibility

### Documentation

- [ ] README_STANDARDIZATION.md present
- [ ] IMPLEMENTATION_GUIDE.md present
- [ ] SUMMARY.md present
- [ ] QUICK_REFERENCE.txt present
- [ ] CHECKLIST.md present

### Data Quality Review

- [ ] Manifest reviewed for issues
- [ ] Any identified issues documented
- [ ] Data quality acceptable
- [ ] No corruption detected
- [ ] Plan for issue correction (if any)

### Checksum Preservation

- [ ] Checksums written to manifest.json
- [ ] Checksums backed up separately (optional)
- [ ] Backup location documented
- [ ] Checksums in secure storage
- [ ] Manifest not modified after creation

## Using the Standardized File

### Before Using

- [ ] Verification passed (checksums matched)
- [ ] Audit log reviewed for issues
- [ ] Data quality issues understood
- [ ] Use case validated against findings

### Import Process

- [ ] Try opening in your application
- [ ] Verify encoding recognized (UTF-8)
- [ ] Check all columns imported correctly
- [ ] Validate row counts match
- [ ] Sample rows inspected for quality

### After Import

- [ ] Keep standardized file as source of truth
- [ ] Document import process
- [ ] Note any transformations applied
- [ ] Archive both original and standardized
- [ ] Maintain this checklist in project records

## Periodic Verification (Annual or As-Needed)

### Step 1: Run Verification

```bash
python3 verify_integrity.py \
  met_inventory_standardized.tsv \
  met_inventory_manifest.json
```

- [ ] All checks still pass
- [ ] Checksums haven't changed
- [ ] File size matches
- [ ] Structure valid

### Step 2: Document Results

- [ ] Date of verification recorded
- [ ] Result: PASSED or FAILED
- [ ] Who performed verification
- [ ] Any issues found documented
- [ ] Action items identified (if any)

### Step 3: Take Action if Issues Found

If verification FAILED:
- [ ] File likely corrupted
- [ ] Do NOT use this file
- [ ] Restore from backup
- [ ] Investigate cause of corruption
- [ ] Document incident

If verification PASSED:
- [ ] File integrity confirmed
- [ ] Safe to continue using
- [ ] No action needed
- [ ] Schedule next verification

## Quality Assurance Checklist

### Data Integrity

- [ ] No data loss during standardization
- [ ] All original rows present
- [ ] All columns preserved
- [ ] Values unchanged (only formatting cleaned)
- [ ] Special characters intact

### Format Compliance

- [ ] UTF-8 encoding throughout
- [ ] Unix line endings (LF only)
- [ ] Tab delimiters consistent
- [ ] Headers normalized
- [ ] Values trimmed properly

### Metadata Completeness

- [ ] Manifest has all required fields
- [ ] Checksums present and valid
- [ ] Statistics accurate
- [ ] Issues properly documented
- [ ] Timestamp recorded

### Documentation Quality

- [ ] Audit log complete
- [ ] README included
- [ ] Manifest readable
- [ ] Guides provided
- [ ] Version documented

## Troubleshooting Checklist

### Issue: Script Won't Run

- [ ] File is executable: `chmod +x script.py`
- [ ] Python 3 installed: `python3 --version`
- [ ] Bash available: `bash --version`
- [ ] File path correct
- [ ] No syntax errors in output

### Issue: File Not Found

- [ ] Input file in correct location
- [ ] Output directory has write permission
- [ ] Paths use forward slashes (or backslashes on Windows)
- [ ] No spaces in file paths (or quoted properly)
- [ ] Full paths specified if relative paths fail

### Issue: Encoding Problems

- [ ] File already UTF-8 compatible
- [ ] Script handles encoding conversion
- [ ] Check output with: `file -b --mime-encoding`
- [ ] Try opening output file manually
- [ ] Review audit log for errors

### Issue: Verification Fails

- [ ] Manifest file not modified
- [ ] Output file not corrupted
- [ ] Using correct file paths
- [ ] Both source and output files exist
- [ ] Re-run standardization if unsure

## Archive Checklist (For Long-Term Preservation)

When archiving standardized files:

- [ ] Original and standardized files together
- [ ] Manifest alongside data file
- [ ] Audit log preserved
- [ ] All scripts included for reproducibility
- [ ] Documentation complete

Archive in:
- [ ] Multiple physical locations
- [ ] Verified backup system
- [ ] Accessible format (TSV, JSON)
- [ ] With access logs
- [ ] In sealed containers (if physical)

## Compliance Checklist (If Required)

If used for compliance, audit, or regulation:

- [ ] Checksums recorded in permanent log
- [ ] Standardization date documented
- [ ] Operator/technician identified
- [ ] Authority/standards referenced
- [ ] Audit trail preserved
- [ ] Change management followed
- [ ] Version control in place
- [ ] Access logs maintained

## Sign-Off

**Standardization Performed**

- [ ] Date: _______________
- [ ] Operator: _______________
- [ ] Verified by: _______________

**Initial Verification**

- [ ] ✓ All tests passed
- [ ] Date: _______________
- [ ] Verified by: _______________

**Annual Verification** (if applicable)

- [ ] ✓ Passed on: _______________
- [ ] ✓ Passed on: _______________
- [ ] ✓ Passed on: _______________

## Next Steps

1. ✓ **Complete all pre-standardization checks**
2. ✓ **Run standardization script**
3. ✓ **Verify all output files created**
4. ✓ **Run integrity verification**
5. ✓ **Review audit log and manifest**
6. ✓ **Test with your application**
7. ✓ **Archive standardized file**
8. ✓ **Document for future reference**
9. ✓ **Schedule annual verifications**
10. ✓ **Maintain this checklist**

---

## Quick Command Reference

```bash
# Setup
chmod +x *.sh *.py

# Standardize
./run_standardization.sh

# Verify
python3 verify_integrity.py

# Check audit log
cat standardization_audit.log

# View manifest
cat met_inventory_manifest.json

# Validate
python3 verify_integrity.py met_inventory_standardized.tsv met_inventory_manifest.json
```

---

**Print this checklist and keep with your project records.**

For detailed information, refer to:
- SUMMARY.md (Overview)
- QUICK_REFERENCE.txt (Commands)
- README_STANDARDIZATION.md (Complete guide)
- IMPLEMENTATION_GUIDE.md (Advanced topics)
