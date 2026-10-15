I'll standardize this TSV file for you. Let me first analyze it and then create a script to standardize it while preserving fixity with checksums.

Let me create these files in the output directory instead:

Now I'll create the standardization script and generate the standardized TSV file:

Now let me create a standardized version of the TSV file. I'll parse the original data and create a properly formatted version:

Now I'll create a checksum verification file and documentation:

Now let me create a comprehensive documentation file explaining the standardization:

Finally, let me create a quick reference guide for using the checksum verification:

Perfect! I've created a complete standardization kit for your Met Museum inventory TSV file. Here's what's been generated:

## 📦 Files Created

1. **met_inventory_standardized.tsv** - The standardized data file with consistent formatting
2. **standardize_tsv.py** - A reusable Python script that handles standardization and checksum generation
3. **CHECKSUMS.json** - Metadata file for fixity preservation with SHA-256 checksums
4. **STANDARDIZATION_REPORT.md** - Comprehensive documentation of what was standardized and why
5. **README.md** - Quick start guide

## ✨ Standardization Applied

- **UTF-8 encoding** normalized throughout
- **Unix line endings** (LF only) 
- **Consistent tab delimiters** (ASCII 0x09)
- **Whitespace trimmed** from headers and field edges
- **QUOTE_MINIMAL** quoting (RFC 4180 compliant)
- **Header fields normalized** for consistent parsing

## 🔐 Fixity Preservation

The checksums file documents:
- SHA-256 hash of source file
- SHA-256 hash of standardized file
- Detailed metadata about transformations applied
- Guidance for future verification

You can verify integrity anytime with:
```bash
sha256sum met_inventory_standardized.tsv
```

The script is reusable for other TSV files—it automatically calculates checksums, logs all changes, and generates verification files for audit trails and long-term preservation.