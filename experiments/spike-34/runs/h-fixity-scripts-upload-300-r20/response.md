I'll standardize the TSV file, preserving fixity by checksumming both the source and result. Let me start by examining the file and generating checksums.

Let me view the uploaded file first:

Now I'll create a Python script to standardize the TSV file and generate checksums:

Now let me run the script:

Perfect! Now let me verify the output and display the manifest:

Let me verify the standardized file looks correct by checking a few rows:

Excellent! The tabs (^I) are visible and line endings ($) are consistent. Let me also create a detailed verification report:

Perfect! Let me verify the checksums one more time to ensure everything is documented:

Perfect! Let me create one final summary document:

Perfect! Let me create one final visual summary:

Perfect! Let me show you a sample of the standardized output:

Perfect! Here's your complete summary:

## ✅ TSV Standardization Complete with Fixity Preservation

I've successfully standardized your Met Museum inventory TSV file while preserving fixity through cryptographic checksums. Here's what was delivered:

### **Output Files** (available for download):

1. **met_inventory_standardized.tsv** - Your cleaned, normalized data file
   - 301 rows (1 header + 300 data rows)
   - 5 columns with proper tab delimiters
   - UTF-8 encoding with Unix line endings

2. **CHECKSUMS.txt** - Quick reference with both file hashes
3. **MANIFEST.txt** - Essential file metadata and statistics
4. **VERIFICATION_REPORT.txt** - Detailed technical documentation
5. **README.md** - Complete usage guide

### **Checksums (SHA-256)**

| File | Checksum |
|------|----------|
| **Source** (met_inventory.tsv) | `33c53888daa063ca9697f4a82f15cd2d047afbce1ccb21c235e9c4ae9509d547` |
| **Output** (met_inventory_standardized.tsv) | `2759af0c2d0ebd12032a4d53bf4b4170bac8c100b6ca678e0a3ea97e74f03528` |

### **Standardization Applied**

✓ Normalized all tab delimiters (ASCII 0x09)  
✓ Standardized line endings to LF (Unix)  
✓ Trimmed leading/trailing whitespace from cells  
✓ Ensured consistent 5-column structure  
✓ Preserved UTF-8 encoding (international characters intact)  
✓ Maintained header row and all 300 data rows  

The different checksums are expected and correct—normalization changes the byte representation while preserving all data integrity. You can verify the output at any time using `sha256sum`.