I'll standardize the TSV file and create a checksummed version for data integrity.

Let me work with the file you've provided directly. I'll standardize the TSV and add checksums for data integrity.

I'll create the standardized file locally for you to download. Let me prepare a properly formatted and checksummed version.

Now I'll create a standardized and checksummed version of your Met Museum inventory file:

Now let me create a companion checksum manifest file for validation:

Perfect! I've standardized your Met Museum inventory file and created two outputs for you:

**1. met_inventory_standardized.tsv** - The cleaned file with:
   - Normalized column headers (spaces replaced with underscores)
   - Standardized field formatting
   - All special characters and Unicode preserved (en-dashes, Chinese/Korean characters)
   - Row checksums added for data integrity

**2. met_inventory_checksum_manifest.txt** - A companion manifest explaining:
   - The standardization methodology
   - How the MD5 row checksums work
   - Instructions for verifying file integrity
   - Documentation of all changes made

The checksums allow you to verify that each row hasn't been corrupted or altered. Simply recalculate the MD5 hash of any row's data and compare it to the stored checksum. This preserves the fixity of your source data while making it more usable in structured formats.

Both files are ready to download from the outputs folder.