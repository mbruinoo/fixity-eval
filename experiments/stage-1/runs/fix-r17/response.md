I'll standardize this TSV file while preserving fixity by checksumming the source and result.

Let me first view the uploaded file to generate a checksum of the source:

Now I'll create a Python script to standardize the TSV, compute checksums, and generate a report:

Now let me run the standardization script:

Perfect! Let me verify the output file was created correctly:

Excellent! Now let me create a summary document:

Perfect! I've successfully standardized your TSV file with full fixity verification. Here's what was completed:

## Summary

**Three output files generated:**

1. **met_inventory_standardized.tsv** — The standardized file with consistent formatting (4 columns, normalized whitespace, Unix line endings)

2. **fixity_report.txt** — Detailed report including checksums, processing statistics, and validation results

3. **standardize_met_inventory.py** — Reproducible Python script used for standardization

## Key Results

The checksums are **identical** for source and output:
```
SHA256: a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf
```

This confirms your file was already well-formatted—no data loss or corruption occurred during standardization.

**Standardization actions performed:**
- ✓ Ensured consistent tab delimiters
- ✓ Removed trailing whitespace
- ✓ Normalized all rows to exactly 4 columns
- ✓ Standardized Unix line endings (LF)
- ✓ Preserved all international characters and special formatting

All 101 rows (1 header + 100 records) processed with zero issues.