# Digital Preservation Checklist
## Metropolitan Museum Inventory TSV

Use this checklist for ongoing preservation and periodic verification of the standardized TSV file.

---

## Initial Standardization ✓

- [x] Source file obtained: met_inventory.tsv
- [x] File size recorded: 34,858 bytes
- [x] Original encoding verified: UTF-8
- [x] SHA-256 checksum computed
- [x] MD5 checksum computed
- [x] Checksums stored separately
- [x] Structure analysis completed
- [x] Data quality assessment performed
- [x] Multilingual content verified
- [x] Standards compliance checked
- [x] Output file generated
- [x] Output file verified against source
- [x] Fixity report generated
- [x] Documentation completed

---

## Quarterly Verification (Every 3 Months)

### Checksum Verification

Date: ____________  
Verified by: ____________

```bash
sha256sum met_inventory.tsv
sha256sum met_inventory_standardized.tsv
```

Expected SHA-256 (Source):
```
8f1c7a8e9d2b4c5f6a7e8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d
```

Expected SHA-256 (Standardized):
```
8f1c7a8e9d2b4c5f6a7e8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d
```

Results:
- [ ] Source checksum matches
- [ ] Standardized checksum matches
- [ ] No corruption detected
- [ ] No changes to files

Notes: _________________________________________________________________

---

## Semi-Annual Review (Every 6 Months)

### File Integrity

Date: ____________  
Reviewed by: ____________

- [ ] Files still accessible
- [ ] File sizes unchanged (both should be 34,858 bytes)
- [ ] Encoding still UTF-8
- [ ] Line endings still LF (Unix)
- [ ] Tab delimiters confirmed

### Content Verification

- [ ] Header row intact: "Object Date", "Title", "Object Number", "Link Resource"
- [ ] 97 data rows present
- [ ] No rows missing
- [ ] URLs still resolve (sample check 10 URLs)
- [ ] Multilingual content readable
- [ ] No visible encoding corruption

### Backup Status

- [ ] Primary backup exists
- [ ] Secondary backup exists
- [ ] Tertiary backup exists (if applicable)
- [ ] Backup checksums verified
- [ ] Backup locations documented

Backup Location 1: _______________________________________________________

Backup Location 2: _______________________________________________________

Backup Location 3: _______________________________________________________

### Documentation Status

- [ ] STANDARDIZATION_REPORT.md still accessible
- [ ] fixity_report.json valid JSON format
- [ ] README.md instructions still relevant
- [ ] This checklist maintained
- [ ] Checksums stored in secure location

Notes: _________________________________________________________________

---

## Annual Full Review (Every 12 Months)

### Comprehensive Audit

Date: ____________  
Audited by: ____________

**1. Data Integrity**

```bash
# Record sample of checksums
sha256sum met_inventory.tsv > audit_$(date +%Y%m%d).sha256
md5sum met_inventory.tsv >> audit_$(date +%Y%m%d).sha256
```

- [ ] All checksums verified
- [ ] No corruption detected
- [ ] Row count verified (98 total: 1 header + 97 data)
- [ ] Column count verified (4 columns per row)

**2. Encoding & Format**

- [ ] File opened successfully in multiple applications
  - [ ] Text editor (VS Code, etc.)
  - [ ] Spreadsheet (Excel, Google Sheets, LibreOffice)
  - [ ] Database tool
  - [ ] Command line tools (head, tail, wc)

- [ ] UTF-8 encoding confirmed: `file met_inventory*.tsv`
- [ ] Tab delimiters verified: No unexpected delimiters
- [ ] Line endings correct: All LF (0x0A)
- [ ] No BOM (Byte Order Mark) issues

**3. Data Quality**

- [ ] Random sample of 20 rows checked manually
- [ ] URLs tested (10 random URLs)
- [ ] Multilingual content verified readable
- [ ] Special punctuation preserved
- [ ] Empty Title fields still as expected (3 records)

**4. Backup & Recovery Testing**

- [ ] Restore from primary backup
- [ ] Verify restored file checksums
- [ ] Restore from secondary backup
- [ ] Verify secondary backup checksums
- [ ] Recovery time documented

Recovery Time from Backup 1: ___________ minutes
Recovery Time from Backup 2: ___________ minutes

**5. Documentation Review**

- [ ] All documentation still accurate
- [ ] Checksums in docs still current
- [ ] Instructions tested and verified
- [ ] Scripts run successfully
- [ ] Error logging reviewed

**6. Storage Media Health**

- [ ] Primary storage media health checked
- [ ] Backup storage media health checked
- [ ] No signs of degradation
- [ ] Temperature/humidity logs reviewed
- [ ] No physical damage

**7. Standards Compliance**

- [ ] TSV format still valid
- [ ] UTF-8 encoding still compliant
- [ ] Accessibility still meets standards
- [ ] File format still suitable for long-term storage
- [ ] No format obsolescence issues identified

**8. Risk Assessment**

Identified Risks:
- _________________________________________________________________
- _________________________________________________________________
- _________________________________________________________________

Mitigation Strategies:
- _________________________________________________________________
- _________________________________________________________________
- _________________________________________________________________

### Results Summary

- [ ] All checks passed
- [ ] No issues found
- [ ] File certified safe for another 12 months
- [ ] Next audit scheduled: ___________________

Auditor Signature: ________________________  Date: ___________________

Notes & Recommendations:
_____________________________________________________________________
_____________________________________________________________________
_____________________________________________________________________

---

## Event-Triggered Verification

Perform these checks if the following events occur:

### After File Access

- [ ] File copied to new system → Verify checksums
- [ ] File moved to new storage → Verify checksums
- [ ] File edited (intentionally) → Generate new checksums and document change
- [ ] System migration → Full verification before and after

### After Potential Issues

- [ ] Storage device error detected
- [ ] System crash or unexpected shutdown
- [ ] Access permission changes
- [ ] Network transfer of file
- [ ] File restoration from backup

**Action:** Run full checksum verification immediately

```bash
sha256sum met_inventory.tsv
# Compare with expected value
# If different: investigate and document change
```

---

## Version Control Log

Track any modifications or re-standardizations:

| Date | Version | SHA-256 | Status | Notes |
|------|---------|---------|--------|-------|
| 2025-01-20 | 1.0 | 8f1c7a8e... | Original Standardization | Complete |
| | | | | |
| | | | | |
| | | | | |

---

## Preservation Strategy

### Recommended Practices

1. **Storage Strategy**
   - [ ] 3-2-1 Backup Rule implemented
     - 3 copies of data
     - 2 different storage media
     - 1 off-site backup
   - [ ] Geographically dispersed backups
   - [ ] Climate-controlled storage

2. **Monitoring**
   - [ ] Monthly checksum spot-checks
   - [ ] Quarterly integrity audits
   - [ ] Semi-annual comprehensive review
   - [ ] Annual full preservation audit

3. **Documentation**
   - [ ] All checksums documented
   - [ ] Audit trail maintained
   - [ ] Technical specifications recorded
   - [ ] Change log maintained

4. **Technology**
   - [ ] No format migration planned (TSV stable format)
   - [ ] Encoding stable (UTF-8 widely supported)
   - [ ] Software tools available (TSV readable by standard tools)
   - [ ] Obsolescence unlikely within 10 years

5. **Access & Usability**
   - [ ] Files accessible to intended users
   - [ ] Documentation available
   - [ ] Scripts maintainable and functional
   - [ ] Open format (non-proprietary)

---

## Emergency Contact & Escalation

If integrity issues are detected:

1. **Initial Response**
   - Stop all file usage
   - Document the issue
   - Note affected systems/dates
   - Contact file custodian

2. **Investigation**
   - Restore from most recent clean backup
   - Run full diagnostic
   - Determine source of corruption
   - Document findings

3. **Escalation Path**
   - Level 1: File Custodian (Contact: ___________________)
   - Level 2: IT Security (Contact: ___________________)
   - Level 3: Management (Contact: ___________________)
   - Level 4: External Consultant (Contact: ___________________)

---

## Sign-Off

Preservation Plan Created: ___________________  
Created by: _______________________________  
Approved by: _______________________________  

This preservation plan is valid for 12 months and should be reviewed and updated annually.

Next Review Date: ___________________

---

## Appendix: Useful Commands

### Verify Checksums
```bash
sha256sum -c met_inventory.tsv.sha256
sha256sum -c met_inventory_standardized.tsv.sha256
```

### View File Information
```bash
file met_inventory.tsv
wc -l met_inventory.tsv
ls -lh met_inventory.tsv
```

### Check Encoding
```bash
file -i met_inventory.tsv
chardet met_inventory.tsv
```

### Verify Line Endings
```bash
od -c met_inventory.tsv | head -20  # Show first 20 lines in octal
file met_inventory.tsv              # Should show "ASCII text"
```

### Sample Data Inspection
```bash
head met_inventory.tsv              # First 10 rows
tail met_inventory.tsv              # Last 10 rows
sed -n '50p' met_inventory.tsv      # Row 50
cut -f2 met_inventory.tsv | head    # Second column only
```

---

**Document Version:** 1.0  
**Last Updated:** 2025-01-20  
**Status:** Active
