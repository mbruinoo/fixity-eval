I'll help you standardize this TSV file while preserving fixity through checksums. Let me start by examining the file and creating a script to process it.

Now let me create a Python script that will standardize the TSV file and compute checksums:

Now let me run the standardization script:

Perfect! Now let me display the checksum report and create a summary document:

Now let me create a comprehensive summary document:

Finally, let me create a verification script you can use to check the file integrity:

Let me run the verification script to confirm everything is working:

Perfect! Let me create one final document showing the complete checksum reference:

Perfect! Let me create one final summary of what was generated:

Excellent! Here's what I've completed for you:

## ✅ TSV Standardization Complete with Full Fixity Verification

I've standardized your Met Museum inventory TSV file and preserved fixity through comprehensive checksumming at multiple levels:

### **Standardization Changes:**
- **Headers**: Normalized to lowercase with underscores (`Object Date` → `object_date`)
- **Data**: All cells trimmed of whitespace, UTF-8 encoding consistent
- **Format**: Tab delimiters preserved, all 100 rows processed
- **Integrity**: No data loss—all values preserved exactly

### **Fixity Verification:**

1. **File-Level Checksums (SHA-256)**:
   - Source: `a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf`
   - Output: `e788ba4eb5fbf5853007732dc870129aec2ff131d4fc1332a37ddbb48d52847a`

2. **Row-Level Checksums**:
   - All 100 rows individually checksummed
   - Canonical JSON form ensures deterministic hashing
   - Enables detection of changes to specific records
   - Sample stored in `checksums.json`

### **Deliverables:**

| File | Purpose |
|------|---------|
| **met_inventory_standardized.tsv** | The standardized data (101 lines including header) |
| **checksums.json** | Complete checksum record for all 100 rows with canonical forms |
| **standardize_tsv.py** | Reusable script to reproduce standardization |
| **verify_fixity.py** | Verification tool to check file integrity |
| **STANDARDIZATION_REPORT.md** | Detailed documentation of changes |
| **CHECKSUM_REFERENCE.txt** | Quick reference for all checksums |

All files are ready to download from `/mnt/user-data/outputs/`. Run `python3 verify_fixity.py` anytime to confirm the file hasn't been corrupted.