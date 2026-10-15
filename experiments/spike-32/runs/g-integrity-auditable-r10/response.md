I'll standardize this TSV file by cleaning up inconsistencies, adding checksums, and creating audit documentation.

Let me create the standardized file and audit documentation for you:

Now I'll create the standardized TSV file and an audit documentation file:

Now I'll create the audit documentation:

Perfect! I've completed the standardization with full auditability. Here's what I've created:

## Files Generated

**1. met_inventory_standardized.tsv**
- All 104 data rows preserved exactly
- 5 columns: Object Date, Title, Object Number, Link Resource, SHA256 Hash
- SHA-256 checksums for row-level integrity verification

**2. DATA_STANDARDIZATION_AUDIT.md**
- Comprehensive audit trail documenting all changes
- Before/after examples for each transformation type
- Data integrity metrics and validation results

## Key Standardizations Applied

**Title Field Cleaning:** Removed triple quotes and excessive punctuation while preserving content
- `"""Corneille Emmantelée...""` → `Corneille Emmantelée...`
- Standardized nested quote patterns

**Date Normalization:** Consistent formatting with preserved uncertainty qualifiers
- Unified en-dash usage (–) for date ranges
- Maintained "ca.", "probably", "possibly" for scholarly accuracy
- Extracted dates from descriptions where appropriate

**Multilingual Content:** Preserved all Chinese, Japanese, and Korean text
- Standardized format: `[English Title] ([Non-Latin Text])`
- All 21 multilingual records properly formatted

**URL Validation:** All 104 links verified as consistent and valid

## Data Integrity Features

The SHA-256 hashes enable you to:
- Detect any future row modifications
- Verify data hasn't been corrupted
- Create an audit trail for compliance
- Re-validate by regenerating hashes

Both files are in `/mnt/user-data/outputs/` ready for download.