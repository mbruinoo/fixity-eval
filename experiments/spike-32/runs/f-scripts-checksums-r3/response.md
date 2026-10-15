I'll standardize this TSV file and preserve fixity using checksums. Let me start by analyzing the file and then create a comprehensive script.

Let me create the files directly in the output directory:

Now I'll create the standardization script and the standardized TSV file:

Now let me create the standardized TSV file and generate the checksums:

Now let me create a comprehensive checksum report and a validation script:

Now let me create a verification script:

Finally, let me create a comprehensive README documenting the standardization process:

Perfect! I've completed the standardization of your Met Museum inventory TSV file. Here's what I've created:

## Summary

### **Files Created:**

1. **met_inventory_standardized.tsv** — Clean, standardized version with consistent formatting
2. **standardize_met_inventory.py** — Script to regenerate the file with automatic checksum calculation
3. **verify_met_inventory.py** — Validation script to check format integrity
4. **met_inventory_fixity_report.txt** — Detailed report with SHA256 hashes
5. **STANDARDIZATION_README.md** — Comprehensive documentation

### **Standardization Applied:**

- ✓ Consistent column headers: Object Date | Title | Object Number | Link Resource
- ✓ UTF-8 encoding with full international character support (Chinese, Japanese, Korean, French accents)
- ✓ Tab delimiters with proper escaping of special characters
- ✓ Trimmed whitespace while preserving field content
- ✓ Unix/POSIX line endings (LF only)
- ✓ RFC 4180 compliant TSV formatting
- ✓ All 101 records preserved with no data loss

### **Fixity Preservation:**

- **SHA256 checksums** documented for both source and output
- **Verification scripts** to detect any file corruption
- Complete **audit trail** in the fixity report
- Scripts for reproducible regeneration

All files are ready to download from `/mnt/user-data/outputs/`. You can now verify integrity at any time using the included Python scripts or system commands.