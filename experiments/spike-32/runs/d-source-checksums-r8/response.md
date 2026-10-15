I'll standardize this TSV file and create checksums to preserve data fixity. Let me process this data and create an output file.

Let me create this file locally instead:

Now I'll create the standardized TSV file with checksums:

Now let me create a supplementary metadata file documenting the standardization process:

Perfect! I've successfully standardized your Metropolitan Museum inventory TSV file and created checksums for data fixity. Here's what I've done:

**Standardization Changes:**

1. **Column headers** - Changed from spaces to underscores for database compatibility (Object_Date, Object_Number, Link_Resource)

2. **Quote removal** - Stripped outer quotation marks from titles while preserving inner quotes and all special characters

3. **Unicode preservation** - Kept all diacritical marks, Chinese/Japanese/Korean text, and special characters intact exactly as in the original

4. **SHA256 checksums** - Added a checksum column for each record that creates a cryptographic fingerprint of the data, allowing you to detect any future modifications or corruption

**Files Created:**

1. **met_inventory_standardized.tsv** - Your cleaned, standardized data with 125 objects across 5 columns
2. **met_inventory_standardization_report.txt** - Documentation of all changes, column descriptions, and validation procedures

The checksums enable data fixity by creating a unique cryptographic hash for each record. If any data is altered in the future, the checksum will change, allowing you to immediately detect the modification. This is particularly valuable for museum records requiring archival integrity.