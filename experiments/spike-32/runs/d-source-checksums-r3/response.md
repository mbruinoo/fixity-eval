I'll standardize this TSV file and create checksums to preserve data integrity.

Let me create the file locally instead:

Now I'll create the standardized TSV file with checksums and a metadata file documenting the standardization process:

Now let me create a metadata document explaining the standardization process:

Perfect! I've successfully standardized your Met Museum inventory file. Here's what I've done:

## Summary

**Created two files:**

1. **met_inventory_standardized.tsv** - Your cleaned and standardized data with SHA-256 checksums for each row

2. **STANDARDIZATION_METADATA.md** - Comprehensive documentation of all changes

## Key Standardization Actions

**Quote Normalization**: Fixed inconsistent quotation marks throughout the Title field for consistency

**Field Consistency**: Ensured all records have proper tab-delimited structure

**Character Preservation**: Maintained full Unicode support for CJK characters, diacritical marks, and all special characters

**Data Integrity**: Added a SHA-256 checksum column for each row, allowing you to verify data hasn't been corrupted or modified later

**Transparency**: Retained all original data including empty fields—nothing was inferred or filled in

## Checksum Benefits

The SHA-256 values let you:
- Verify each row's integrity after file transfers
- Detect accidental or intentional data modifications
- Ensure long-term digital preservation
- Validate the dataset in future migrations

Both files are ready to download from the outputs folder!