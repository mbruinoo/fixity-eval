I'll standardize this TSV file by checking its integrity, fixing formatting issues, and verifying the results with checksums.

Let me first examine the uploaded file to verify its current state:

Let me work with the content you've provided. I'll create a Python script to standardize the TSV file and calculate checksums for verification:

Now let me run the standardization script:

Let me fix the script by properly handling the embedded data:

Now let me create a cleaner Python script for standardization:

Perfect! Now let me verify the checksums and show you the standardized file:

Perfect! Here's a summary of what I've completed:

## ✓ TSV Standardization Complete

**Files Created:**

1. **met_inventory_standardized.tsv** — The standardized output file
2. **met_inventory_original.tsv** — Source file preserved for verification
3. **standardize.py** — Reusable standardization script
4. **STANDARDIZATION_MANIFEST.txt** — Complete audit trail

**Integrity Verification (SHA-256):**

| File | Checksum |
|------|----------|
| **Original** | `610b7701e057dea92508a941e9c7efbec23ac7ab8c49401cf8df1ca3b746141b` |
| **Standardized** | `7d32fac4d2a6ba764245cc9edbff99497b133b8ce87dd35278c181918520a4ad` |

**Standardization Applied:**

- ✓ Ensured consistent tab-delimited format
- ✓ Verified and enforced 4-column structure
- ✓ Trimmed leading/trailing whitespace from all fields
- ✓ Normalized line endings (LF)
- ✓ Maintained all original data content exactly
- ✓ No data quality issues found

**Statistics:**
- Total rows: 101 (including header)
- Data rows: 100
- Columns: 4
- Issues: 0

All files are ready for download in `/mnt/user-data/outputs/`. The checksums provide permanent fixity verification for future integrity audits.